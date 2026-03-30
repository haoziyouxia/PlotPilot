# aitext 可视化统计系统设计文档

**项目**: aitext - AI驱动的小说创作系统
**功能**: 全局统计看板、数据可视化、架构优化
**日期**: 2026-03-31
**版本**: 1.0

---

## 目录

1. [概述](#概述)
2. [用户需求](#用户需求)
3. [技术方案](#技术方案)
4. [架构设计](#架构设计)
5. [UI设计](#ui设计)
6. [功能模块](#功能模块)
7. [现有问题分析](#现有问题分析)
8. [实施计划](#实施计划)
9. [风险与挑战](#风险与挑战)

---

## 概述

### 项目背景

aitext 是一个 AI 驱动的长篇小说创作系统，目前已实现：
- 完整的创作流水线（规划、写作、导出）
- FastAPI 后端 + Vue 3 前端
- 人物关系图、知识图谱可视化
- 实时对话工作台

### 当前痛点

1. **缺少全局视角** - 无法快速了解所有项目的整体情况
2. **数据不可见** - 写作进度、内容质量等数据无法直观展示
3. **架构问题** - 前后端代码存在耦合、重复、性能问题
4. **图表库不统一** - vis-network 和未来的图表库混用

### 设计目标

1. **添加可视化统计** - 主页侧边栏 + 工作台顶部条
2. **统一图表库** - 全部使用 ECharts，移除 vis-network
3. **优化架构** - 前后端分层重构，提升代码质量
4. **提升性能** - 并行请求、缓存优化、渲染优化

---

## 用户需求

### 功能需求

用户选择了以下 6 个统计模块（全选）：

1. **📊 写作进度统计** - 字数统计、章节完成度、写作速度趋势、目标达成率
2. **📈 内容质量分析** - 人物出场频率、情节密度、对话比例、场景分布
3. **🕸️ 知识图谱可视化** - 人物关系网络、事件时间线、地点地图、设定关联
4. **🤖 AI 使用统计** - API 调用次数、Token 消耗、成本估算、模型性能
5. **💊 项目健康度** - 一致性检查、设定冲突、时间线错误、待办事项
6. **📚 多书籍对比** - 跨项目统计、写作习惯分析、效率对比、风格差异

### 布局需求

**主页布局**：侧边栏布局
- 左侧：280px 固定侧边栏，展示全局统计卡片
- 右侧：创建表单 + 书籍列表

**工作台布局**：顶部统计条
- 顶部：横向统计条，展示当前书籍的关键指标
- 下方：保持现有三栏布局（章节导航 + 对话区 + 设定面板）

### 技术需求

**图表库**：ECharts
- 功能强大，支持所有需要的图表类型
- 中文文档完善
- 统一替换现有的 vis-network

**实施策略**：混合渐进方案
- 第一阶段：实现核心功能（3个模块）
- 第二阶段：扩展高级功能（3个模块）
- 架构完整，功能渐进增强

---

## 技术方案

### 技术栈

#### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.5+ | 框架 |
| TypeScript | 5.9+ | 类型安全 |
| Pinia | 3.0+ | 状态管理 |
| vue-echarts | 7.0+ | 图表库 |
| Naive UI | 2.44+ | UI 组件库 |
| Axios | 1.14+ | HTTP 客户端 |

#### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 语言 |
| FastAPI | 0.100+ | Web 框架 |
| Pydantic | 2.0+ | 数据验证 |

### 图表库统一方案

**当前状态**：
- vis-network (~500KB) - 用于人物关系图、知识图谱

**目标状态**：
- ECharts (~300KB，按需加载) - 统一所有图表

**迁移清单**：
1. `Cast.vue` - vis-network → ECharts Graph
2. `CastGraphCompact.vue` - vis-network → ECharts Graph（简化版）
3. `KnowledgeTripleGraph.vue` - vis-network → ECharts Graph

**收益**：
- 包体积减少 200KB
- 视觉风格统一
- 维护成本降低

---

## 架构设计

### 数据架构

#### 统计数据来源

```
📁 manifest.json          → 基础信息（书名、章数、阶段）
📁 chapters/*/body.md     → 字数统计、内容分析
📁 bible.json             → 人物、地点数量
📁 cast_graph.json        → 人物关系、出场频率
📁 novel_knowledge.json   → 知识图谱、三元组
📁 running_summary.json   → 章节摘要
📁 chat/thread.json       → AI对话记录、Token统计
```

#### 新增 API 端点

```
GET /api/stats/global              → 全局统计（所有书籍）
GET /api/stats/book/{slug}         → 单本书统计
GET /api/stats/book/{slug}/trends  → 趋势数据（时间序列）
GET /api/stats/book/{slug}/health  → 健康度分析
GET /api/stats/comparison          → 多书对比
```

### 后端架构重构

#### 当前问题

- **单体文件** - app.py 745行，包含30+个路由
- **缺少分层** - 路由、业务逻辑、数据访问混在一起
- **错误处理不统一** - 相同代码重复20+次
- **日志混乱** - print 和 logger 混用

#### 新架构设计

```
web/
├── routers/              # 路由层（处理HTTP请求）
│   ├── books.py          # 书籍相关路由
│   ├── chapters.py       # 章节相关路由
│   ├── settings.py       # 设定相关路由
│   ├── jobs.py           # 后台任务路由
│   ├── chat.py           # 对话相关路由
│   └── stats.py          # 统计相关路由（新增）
│
├── services/             # 服务层（业务逻辑）
│   ├── book_service.py
│   ├── chapter_service.py
│   ├── stats_service.py  # 统计业务逻辑（新增）
│   └── chat_service.py
│
├── repositories/         # 数据访问层
│   ├── book_repo.py
│   ├── chapter_repo.py
│   └── stats_repo.py     # 统计数据读取（新增）
│
├── models/               # 数据模型（Pydantic）
│   ├── requests.py       # 请求模型
│   ├── responses.py      # 响应模型
│   └── stats.py          # 统计数据模型（新增）
│
├── middleware/           # 中间件
│   ├── error_handler.py  # 统一错误处理
│   └── logging.py        # 统一日志
│
├── utils/                # 工具函数
│   ├── cache.py
│   └── validators.py
│
├── app.py                # 主应用（只负责组装）
└── config.py             # 配置
```

**优势**：
- 每个文件 < 200行
- 职责清晰，易于维护
- 可单独测试每一层
- 易于扩展新功能

### 前端架构优化

#### 组件结构

```
web-app/src/
├── components/
│   ├── stats/
│   │   ├── StatCard.vue           # 统计卡片（可复用）
│   │   ├── StatsSidebar.vue       # 主页侧边栏
│   │   ├── StatsTopBar.vue        # 工作台顶部条
│   │   ├── ChartWrapper.vue       # ECharts包装器
│   │   └── charts/
│   │       ├── TrendChart.vue     # 趋势图
│   │       ├── ProgressChart.vue  # 进度图
│   │       ├── DistributionChart.vue # 分布图
│   │       └── GraphChart.vue     # 关系图（替换vis-network）
│   └── ...
├── stores/
│   └── statsStore.ts              # 统计数据状态管理
├── api/
│   └── stats.ts                   # 统计API封装
├── types/
│   └── api.ts                     # API类型定义（新增）
└── views/
    ├── Home.vue                   # 添加侧边栏
    └── Workbench.vue              # 添加顶部条
```

#### 数据流设计

```
1. 页面加载 → 调用 API 获取统计数据
2. Pinia Store → 缓存数据，避免重复请求
3. 组件订阅 → 响应式更新UI
4. 用户操作 → 触发数据刷新（写作、编辑后）
```

---

## UI设计

### 主页侧边栏设计

**布局**：
- 左侧：280px 固定宽度
- 背景：浅灰色 (#f8f9fa)
- 卡片：白色背景，圆角阴影

**统计卡片**（4个）：
1. **总书籍数** - 显示总数 + 活跃项目数
2. **总字数** - 显示总字数 + 平均字数
3. **今日进度** - 显示今日新增 + 更新书籍数
4. **AI调用** - 显示本月累计调用次数

**响应式**：
- 桌面端（>1200px）：侧边栏固定展开
- 平板端（768-1200px）：侧边栏可折叠

### 工作台顶部条设计

**布局**：
- 高度：80px
- 背景：渐变色（#667eea → #764ba2）
- 文字：白色

**统计指标**（5个）：
1. **总字数** - 当前书籍总字数
2. **完成章节** - 完成数/目标数
3. **健康度** - 百分比评分
4. **AI调用** - 本书累计调用
5. **今日新增** - 今日新增字数

**交互**：
- 鼠标悬停显示详细信息
- 点击跳转到详细统计页面（未来扩展）

---

## 功能模块

### 第一阶段：核心模块（第1-2周）

#### 模块1：写作进度统计

**数据指标**：
- 总字数：所有章节 body.md 字数累加
- 完成章节：manifest.completed_chapters
- 目标进度：完成数/目标章数 × 100%
- 今日新增：对比文件修改时间
- 平均章节字数：总字数/完成章数
- 预计完成时间：基于写作速度估算

**图表设计**：
1. **字数趋势图**（折线图）
   - X轴：日期
   - Y轴：累计字数
   - 数据来源：文件修改时间 + 字数统计

2. **章节进度**（环形图）
   - 显示完成百分比
   - 中心显示具体数字（3/5章）

#### 模块2：内容质量分析

**数据指标**：
- 人物出场频率：从 cast_graph.json 统计
- 对话比例：识别引号内容占比
- 场景分布：从 chapter.json 的 scenes 统计
- 情节密度：每章事件数量

**图表设计**：
1. **人物出场频率**（柱状图）
   - X轴：人物名称
   - Y轴：出场次数

2. **内容类型分布**（饼图）
   - 对话、动作、描写、心理占比

#### 模块3：知识图谱可视化

**数据指标**：
- 人物关系网络：cast_graph.json 可视化
- 关系强度：基于共同出场次数
- 知识三元组：novel_knowledge.json
- 事件时间线：按章节排序的关键事件

**图表设计**：
1. **关系网络图**（ECharts Graph）
   - 替换现有的 vis-network
   - 力导向布局
   - 节点：人物
   - 边：关系

2. **事件时间线**（横向时间轴）
   - 显示关键事件
   - 按章节排序

### 第二阶段：扩展模块（第3周+）

#### 模块4：AI 使用统计

**数据指标**：
- API 调用次数：从 chat/thread.json 统计
- Token 消耗：累计输入/输出 token
- 成本估算：基于 token 价格计算
- 模型性能：平均响应时间

#### 模块5：项目健康度

**数据指标**：
- 一致性检查：人物设定前后对比
- 设定冲突：检测矛盾的描述
- 时间线错误：事件顺序检查
- 待办事项：未完成的章节、审稿

#### 模块6：多书籍对比

**数据指标**：
- 跨项目统计：所有书籍的汇总数据
- 写作习惯分析：每日写作时间、字数分布
- 效率对比：不同书籍的写作速度
- 风格差异：对话比例、描写风格对比

---

## 现有问题分析

### 前端问题

#### 问题1：API 类型不安全

**位置**：`web-app/src/api/book.ts`

**问题描述**：
- 大量使用 `as Promise<any>` 类型断言
- 无类型检查、无自动补全
- 运行时错误难以发现

**解决方案**：
- 创建 `types/api.ts` 定义所有响应类型
- 为每个 API 端点添加具体类型
- 统一错误响应模型

#### 问题2：组件耦合度过高

**位置**：`Workbench.vue` (400+行)

**问题描述**：
- 混合数据加载、状态管理、UI 逻辑
- 直接调用 API，无业务逻辑层
- 用 window 事件通信

**解决方案**：
- 提取 Composables（`useWorkbench.ts`）
- 使用 Pinia 管理全局状态
- 用事件总线替代 window 事件
- 拆分为多个小组件

#### 问题3：重复的 API 请求

**位置**：`Chapter.vue`

**问题描述**：
- 页面加载时串行发起 4 个请求
- 每次路由参数变化都重新加载所有数据
- 没有缓存机制

**解决方案**：
- 使用 `Promise.all()` 并行化请求
- 实现客户端缓存（TanStack Query）
- 后端提供聚合端点

#### 问题4：Markdown 渲染卡顿

**位置**：`Chapter.vue`

**问题描述**：
- 每次输入都重新解析整个文档
- 无防抖/节流
- 大文档导致 UI 冻结

**解决方案**：
- 添加防抖（300ms）
- 使用 Web Worker 解析
- 实现虚拟滚动

#### 问题5：流式聊天频繁更新

**位置**：`Workbench.vue`

**问题描述**：
- 每个 SSE chunk 都触发响应式更新
- 频繁的 DOM 操作
- 滚动抖动

**解决方案**：
- 使用 `requestAnimationFrame` 批量更新
- 实现虚拟滚动
- 优化滚动逻辑

### 后端问题

#### 问题1：单体路由文件

**位置**：`web/app.py` (745行)

**问题描述**：
- 30+ 个路由全在一个文件
- 难以维护和扩展
- 职责不清

**解决方案**：
- 按功能模块分离路由
- 创建 `routers/` 目录
- 每个模块独立文件

#### 问题2：缺少分层架构

**位置**：所有路由函数

**问题描述**：
- 路由、业务逻辑、数据访问混在一起
- 无法单独测试
- 代码重复

**解决方案**：
- 创建三层架构：Router → Service → Repository
- 分离关注点
- 提高可测试性

#### 问题3：错误处理不统一

**位置**：所有路由函数

**问题描述**：
- 相同的错误处理代码重复 20+ 次
- 错误信息不友好
- 没有统一的响应格式

**解决方案**：
- 创建统一的错误处理中间件
- 定义标准错误响应格式
- 友好的错误提示

#### 问题4：日志输出混乱

**位置**：`web/app.py` 中间件

**问题描述**：
- 同时使用 print 和 logger
- 重复输出
- 难以管理和过滤

**解决方案**：
- 统一使用 logger
- 移除所有 print 语句
- 配置日志级别和格式

---

## 实施计划

### 总体策略

**前后端协同优化**：
- 第1周：重点优化基础设施
- 第2周：实现核心功能
- 第3周：优化和扩展

### 第1周：基础设施（Day 1-7）

#### 后端任务

**Day 1-2：创建模块化结构**
- [ ] 创建 `web/routers/` 目录
- [ ] 创建 `web/services/` 目录
- [ ] 创建 `web/repositories/` 目录
- [ ] 创建 `web/models/` 目录
- [ ] 创建 `web/middleware/` 目录

**Day 3-4：统一错误处理和日志**
- [ ] 实现 `middleware/error_handler.py`
- [ ] 实现 `middleware/logging.py`
- [ ] 移除所有 print 语句
- [ ] 统一错误响应格式

**Day 5-7：实现统计 API**
- [ ] 创建 `routers/stats.py`
- [ ] 创建 `services/stats_service.py`
- [ ] 创建 `repositories/stats_repo.py`
- [ ] 创建 `models/stats.py`
- [ ] 实现 5 个统计端点

#### 前端任务

**Day 2-3：创建类型定义**
- [ ] 创建 `types/api.ts`
- [ ] 定义所有 API 响应类型
- [ ] 定义统计数据类型
- [ ] 更新 `api/book.ts` 使用新类型

**Day 4-5：创建状态管理**
- [ ] 创建 `stores/statsStore.ts`
- [ ] 实现数据缓存逻辑
- [ ] 实现自动刷新机制

**Day 6-7：安装和配置 ECharts**
- [ ] 安装 `vue-echarts` 和 `echarts`
- [ ] 创建 `components/stats/ChartWrapper.vue`
- [ ] 配置按需加载

### 第2周：核心功能（Day 8-14）

#### 后端任务

**Day 8-10：实现统计数据计算**
- [ ] 实现字数统计逻辑
- [ ] 实现人物出场频率统计
- [ ] 实现趋势数据计算
- [ ] 添加缓存机制

**Day 11-14：优化性能**
- [ ] 实现数据缓存
- [ ] 优化文件读取
- [ ] 添加聚合端点

#### 前端任务

**Day 8-9：主页侧边栏**
- [ ] 创建 `components/stats/StatsSidebar.vue`
- [ ] 创建 `components/stats/StatCard.vue`
- [ ] 集成到 `Home.vue`
- [ ] 实现响应式布局

**Day 10-11：工作台顶部条**
- [ ] 创建 `components/stats/StatsTopBar.vue`
- [ ] 集成到 `Workbench.vue`
- [ ] 实现渐变背景样式

**Day 12-14：核心图表组件**
- [ ] 创建 `charts/TrendChart.vue`（字数趋势）
- [ ] 创建 `charts/ProgressChart.vue`（章节进度）
- [ ] 创建 `charts/DistributionChart.vue`（内容分布）
- [ ] 创建 `charts/GraphChart.vue`（关系图）

**Day 12-14：迁移 vis-network**
- [ ] 替换 `Cast.vue` 中的 vis-network
- [ ] 替换 `CastGraphCompact.vue`
- [ ] 替换 `KnowledgeTripleGraph.vue`
- [ ] 移除 vis-network 依赖

### 第3周：优化扩展（Day 15-21）

#### 后端任务

**Day 15-17：迁移现有路由**
- [ ] 迁移书籍路由到 `routers/books.py`
- [ ] 迁移章节路由到 `routers/chapters.py`
- [ ] 迁移设定路由到 `routers/settings.py`

**Day 18-19：性能优化**
- [ ] 性能监控和分析
- [ ] 数据库查询优化
- [ ] 缓存策略优化

**Day 20-21：测试和文档**
- [ ] 编写单元测试
- [ ] 生成 API 文档
- [ ] 性能测试

#### 前端任务

**Day 15-16：响应式优化**
- [ ] 平板端适配
- [ ] 移动端适配（可选）
- [ ] 测试不同屏幕尺寸

**Day 17-18：性能优化**
- [ ] Markdown 防抖优化
- [ ] 并行化 API 请求
- [ ] 实现骨架屏

**Day 19-20：组件重构**
- [ ] 拆分 `Workbench.vue`
- [ ] 提取 Composables
- [ ] 优化流式聊天

**Day 21：测试和优化**
- [ ] 端到端测试
- [ ] 性能测试
- [ ] Bug 修复

---

## 风险与挑战

### 技术风险

#### 风险1：ECharts 迁移复杂度

**描述**：vis-network 和 ECharts Graph 的 API 差异较大，迁移可能遇到功能不匹配

**缓解措施**：
- 提前验证 ECharts Graph 是否支持所有现有功能
- 准备降级方案（保留 vis-network 作为备选）
- 分步迁移，先迁移简单的图表

#### 风险2：后端重构影响现有功能

**描述**：大规模重构可能引入新的 bug，影响现有功能

**缓解措施**：
- 渐进式迁移，保持新旧代码共存
- 充分的单元测试和集成测试
- 每次迁移后进行回归测试

#### 风险3：性能优化效果不明显

**描述**：优化后性能提升可能不如预期

**缓解措施**：
- 提前进行性能基准测试
- 使用性能监控工具量化改进
- 优先优化瓶颈点

### 进度风险

#### 风险1：开发时间超出预期

**描述**：3周时间可能不够完成所有任务

**缓解措施**：
- 采用 MVP 优先策略，先实现核心功能
- 第二阶段功能可以延后
- 每周进行进度评估和调整

#### 风险2：前后端协调问题

**描述**：前后端开发进度不同步，可能导致等待

**缓解措施**：
- 提前定义好 API 接口
- 前端可以先用 Mock 数据开发
- 每日同步进度

---

## 附录

### API 接口定义

#### GET /api/stats/global

**响应**：
```json
{
  "total_books": 12,
  "total_words": 156000,
  "active_books": 2,
  "today_words": 3200,
  "ai_calls_month": 248
}
```

#### GET /api/stats/book/{slug}

**响应**：
```json
{
  "total_words": 12500,
  "completed_chapters": 3,
  "target_chapters": 5,
  "health_score": 92,
  "ai_calls": 48,
  "today_words": 2100
}
```

#### GET /api/stats/book/{slug}/trends

**响应**：
```json
{
  "word_count_history": [
    {"date": "2026-03-25", "words": 5000},
    {"date": "2026-03-26", "words": 7500}
  ],
  "character_frequency": [
    {"name": "主角", "count": 45},
    {"name": "配角A", "count": 28}
  ]
}
```

### 依赖变更

#### 移除

```bash
npm uninstall vis-network
```

#### 添加

```bash
npm install echarts vue-echarts
```

### 参考资料

- [ECharts 官方文档](https://echarts.apache.org/zh/index.html)
- [vue-echarts 文档](https://github.com/ecomfe/vue-echarts)
- [FastAPI 最佳实践](https://fastapi.tiangolo.com/tutorial/)
- [Vue 3 组合式 API](https://cn.vuejs.org/guide/introduction.html)

---

**文档结束**