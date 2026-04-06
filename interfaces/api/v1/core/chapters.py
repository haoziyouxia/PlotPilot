"""Chapter API 路由"""
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path
from typing import List, Literal
from pydantic import BaseModel, Field

from application.core.services.chapter_service import ChapterService
from application.core.services.novel_service import NovelService
from application.core.dtos.chapter_dto import ChapterDTO
from application.core.dtos.novel_dto import NovelDTO
from application.audit.dtos.chapter_review_dto import ChapterReviewDTO
from application.core.dtos.chapter_structure_dto import ChapterStructureDTO
from interfaces.api.dependencies import (
    get_chapter_service, get_novel_service,
    get_chapter_indexing_service, get_voice_drift_service,
)
from domain.shared.exceptions import EntityNotFoundError

logger = logging.getLogger(__name__)


async def _try_index_chapter(novel_id: str, chapter_number: int, content: str, indexing_svc) -> None:
    """后台异步索引章节内容，失败仅记日志不影响主流程。"""
    if indexing_svc is None:
        return
    summary = content[:800].strip()
    if not summary:
        return
    try:
        await indexing_svc.ensure_collection(novel_id)
        await indexing_svc.index_chapter_summary(novel_id, chapter_number, summary)
        logger.debug("章节索引完成 novel=%s ch=%d", novel_id, chapter_number)
    except Exception as e:
        logger.warning("章节索引失败 novel=%s ch=%d: %s", novel_id, chapter_number, e)


def _try_score_drift(novel_id: str, chapter_number: int, content: str, drift_svc) -> None:
    """后台同步计算章节文风相似度，写入 chapter_style_scores，失败仅记日志。"""
    if drift_svc is None or not content.strip():
        return
    try:
        result = drift_svc.score_chapter(
            novel_id=novel_id,
            chapter_number=chapter_number,
            content=content,
        )
        score = result.get("similarity_score")
        alert = result.get("drift_alert", False)
        if alert:
            logger.warning(
                "文风漂移告警 novel=%s 最近连续章节相似度偏低", novel_id
            )
        else:
            logger.debug(
                "文风评分完成 novel=%s ch=%d score=%s", novel_id, chapter_number, score
            )
    except Exception as e:
        logger.warning("文风评分失败 novel=%s ch=%d: %s", novel_id, chapter_number, e)


async def _try_infer_kg_chapter(novel_id: str, chapter_number: int) -> None:
    """后台异步对章节做知识图谱增量推断，失败仅记日志。

    通过 story_node 表找到对应章节节点 UUID，再调用 KnowledgeGraphService。
    如果找不到节点（结构树未规划），静默跳过。
    """
    try:
        from application.paths import get_db_path
        from infrastructure.persistence.database.connection import get_database
        from infrastructure.persistence.database.sqlite_knowledge_repository import SqliteKnowledgeRepository
        from infrastructure.persistence.database.triple_repository import TripleRepository
        from infrastructure.persistence.database.chapter_element_repository import ChapterElementRepository
        from infrastructure.persistence.database.story_node_repository import StoryNodeRepository
        from application.world.services.knowledge_graph_service import KnowledgeGraphService

        db_path = get_db_path()
        kr = SqliteKnowledgeRepository(get_database())
        story_node_id = kr.find_story_node_id_for_chapter_number(novel_id, chapter_number)
        if not story_node_id:
            logger.debug("KG 推断跳过：章节 %d 无故事节点 novel=%s", chapter_number, novel_id)
            return

        kg_service = KnowledgeGraphService(
            TripleRepository(),
            ChapterElementRepository(db_path),
            StoryNodeRepository(db_path),
        )
        triples = await kg_service.infer_from_chapter(story_node_id)
        logger.debug("KG 推断完成 novel=%s ch=%d 新三元组=%d", novel_id, chapter_number, len(triples))
    except Exception as e:
        logger.warning("KG 推断失败 novel=%s ch=%d: %s", novel_id, chapter_number, e)


router = APIRouter(tags=["chapters"])


# Request Models
class UpdateChapterContentRequest(BaseModel):
    """更新章节内容请求"""
    content: str = Field(..., min_length=0, max_length=100000, description="章节内容")


class SaveChapterReviewRequest(BaseModel):
    """保存章节审阅请求"""
    status: Literal["draft", "reviewed", "approved"] = Field(..., description="审阅状态")
    memo: str = Field(default="", description="审阅备注")


class ChapterReviewResponse(BaseModel):
    """章节审阅响应"""
    status: str
    memo: str
    created_at: str
    updated_at: str


class ChapterStructureResponse(BaseModel):
    """章节结构响应"""
    word_count: int
    paragraph_count: int
    dialogue_ratio: float
    scene_count: int
    pacing: str


class CreateChapterRequest(BaseModel):
    """创建章节请求"""
    chapter_id: str = Field(..., description="章节 ID")
    number: int = Field(..., gt=0, description="章节编号")
    title: str = Field(..., min_length=1, max_length=200, description="章节标题")
    content: str = Field(..., min_length=1, description="章节内容")


class EnsureChapterRequest(BaseModel):
    """确保章节存在请求（可选 title，不传则用「第N章」）"""
    title: str = Field(default="", max_length=200, description="章节标题（可选）")


# Routes
@router.get("/{novel_id}/chapters", response_model=List[ChapterDTO])
async def list_chapters(
    novel_id: str,
    service: ChapterService = Depends(get_chapter_service)
):
    """列出小说的所有章节

    Args:
        novel_id: 小说 ID
        service: Chapter 服务

    Returns:
        章节 DTO 列表
    """
    return service.list_chapters_by_novel(novel_id)


@router.post("/{novel_id}/chapters", response_model=NovelDTO, status_code=201)
async def create_chapter(
    novel_id: str,
    request: CreateChapterRequest,
    novel_service: NovelService = Depends(get_novel_service)
):
    """创建章节

    Args:
        novel_id: 小说 ID
        request: 创建章节请求
        novel_service: Novel 服务

    Returns:
        更新后的小说 DTO
    """
    try:
        return novel_service.add_chapter(
            novel_id=novel_id,
            chapter_id=request.chapter_id,
            number=request.number,
            title=request.title,
            content=request.content
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{novel_id}/chapters/{chapter_number}", response_model=ChapterDTO)
async def get_chapter(
    novel_id: str,
    chapter_number: int = Path(..., gt=0, description="章节编号"),
    service: ChapterService = Depends(get_chapter_service)
):
    """获取章节详情

    Args:
        novel_id: 小说 ID
        chapter_number: 章节号
        service: Chapter 服务

    Returns:
        章节 DTO

    Raises:
        HTTPException: 如果章节不存在
    """
    chapter = service.get_chapter_by_novel_and_number(novel_id, chapter_number)
    if chapter is None:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter not found: {novel_id}/chapter-{chapter_number}"
        )
    return chapter


@router.post("/{novel_id}/chapters/{chapter_number}/ensure", response_model=ChapterDTO)
async def ensure_chapter(
    novel_id: str,
    request: EnsureChapterRequest,
    chapter_number: int = Path(..., gt=0, description="章节编号"),
    service: ChapterService = Depends(get_chapter_service)
):
    """确保章节在正文库中存在；若不存在则创建空白记录（不校验章节号连续性）。

    适用于结构树手动添加章节节点后、用户点击想直接开始写作的场景。
    """
    return service.ensure_chapter(novel_id, chapter_number, request.title)


@router.put("/{novel_id}/chapters/{chapter_number}", response_model=ChapterDTO)
async def update_chapter(
    novel_id: str,
    request: UpdateChapterContentRequest,
    background_tasks: BackgroundTasks,
    chapter_number: int = Path(..., gt=0, description="章节编号"),
    service: ChapterService = Depends(get_chapter_service),
    indexing_svc=Depends(get_chapter_indexing_service),
    drift_svc=Depends(get_voice_drift_service),
):
    """更新章节内容，保存成功后后台触发：
    1. 向量索引（QDRANT_ENABLED=true 时）
    2. 文风漂移评分（与作者指纹对比，写入 chapter_style_scores）
    3. 知识图谱增量推断（章节元素关联 → 新三元组）
    """
    try:
        chapter = service.update_chapter_by_novel_and_number(
            novel_id,
            chapter_number,
            request.content
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    content = request.content
    background_tasks.add_task(_try_index_chapter, novel_id, chapter_number, content, indexing_svc)
    background_tasks.add_task(_try_score_drift, novel_id, chapter_number, content, drift_svc)
    background_tasks.add_task(_try_infer_kg_chapter, novel_id, chapter_number)
    return chapter


@router.get("/{novel_id}/chapters/{chapter_number}/review", response_model=ChapterReviewResponse)
async def get_chapter_review(
    novel_id: str,
    chapter_number: int = Path(..., gt=0, description="章节编号"),
    service: ChapterService = Depends(get_chapter_service)
):
    """获取章节审阅

    Args:
        novel_id: 小说 ID
        chapter_number: 章节号
        service: Chapter 服务

    Returns:
        章节审阅信息

    Raises:
        HTTPException: 如果章节不存在
    """
    try:
        review = service.get_chapter_review(novel_id, chapter_number)
        return ChapterReviewResponse(
            status=review.status,
            memo=review.memo,
            created_at=review.created_at.isoformat(),
            updated_at=review.updated_at.isoformat()
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{novel_id}/chapters/{chapter_number}/review", response_model=ChapterReviewResponse)
async def save_chapter_review(
    novel_id: str,
    request: SaveChapterReviewRequest,
    chapter_number: int = Path(..., gt=0, description="章节编号"),
    service: ChapterService = Depends(get_chapter_service)
):
    """保存章节审阅

    Args:
        novel_id: 小说 ID
        chapter_number: 章节号
        request: 审阅请求
        service: Chapter 服务

    Returns:
        保存后的审阅信息

    Raises:
        HTTPException: 如果章节不存在
    """
    try:
        review = service.save_chapter_review(
            novel_id,
            chapter_number,
            request.status,
            request.memo
        )
        return ChapterReviewResponse(
            status=review.status,
            memo=review.memo,
            created_at=review.created_at.isoformat(),
            updated_at=review.updated_at.isoformat()
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{novel_id}/chapters/{chapter_number}/review-ai")
async def ai_review_chapter(
    novel_id: str,
    chapter_number: int = Path(..., gt=0, description="章节编号"),
    service: ChapterService = Depends(get_chapter_service)
):
    """AI 审阅章节

    Args:
        novel_id: 小说 ID
        chapter_number: 章节号
        service: Chapter 服务

    Returns:
        AI 审阅结果

    Raises:
        HTTPException: 如果章节不存在或内容为空
    """
    try:
        # 获取章节
        chapter = service.get_chapter_by_novel_and_number(novel_id, chapter_number)
        if chapter is None:
            raise HTTPException(status_code=404, detail=f"Chapter not found: {novel_id}/chapter-{chapter_number}")

        # 检查内容是否为空
        if not chapter.content or not chapter.content.strip():
            raise HTTPException(status_code=400, detail="Chapter content is empty")

        # TODO: 实现 AI 审阅逻辑
        # 这里需要集成 LLM 服务进行审阅
        return {
            "message": "AI review not yet implemented",
            "status": "pending"
        }
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{novel_id}/chapters/{chapter_number}/structure", response_model=ChapterStructureResponse)
async def get_chapter_structure(
    novel_id: str,
    chapter_number: int = Path(..., gt=0, description="章节编号"),
    service: ChapterService = Depends(get_chapter_service)
):
    """获取章节结构分析

    Args:
        novel_id: 小说 ID
        chapter_number: 章节号
        service: Chapter 服务

    Returns:
        章节结构分析

    Raises:
        HTTPException: 如果章节不存在
    """
    try:
        structure = service.get_chapter_structure(novel_id, chapter_number)
        return ChapterStructureResponse(
            word_count=structure.word_count,
            paragraph_count=structure.paragraph_count,
            dialogue_ratio=structure.dialogue_ratio,
            scene_count=structure.scene_count,
            pacing=structure.pacing
        )
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
