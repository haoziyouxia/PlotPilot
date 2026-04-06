<template>
  <div class="ce-panel">
    <!-- 无当前章节 -->
    <n-empty v-if="!currentChapterNumber" description="请先从左侧选择一个章节" style="margin-top: 40px" />

    <template v-else>
      <n-alert v-if="readOnly" type="warning" :show-icon="true" style="margin-bottom: 8px; font-size: 12px">
        托管运行中：仅可查看元素列表，不可增删。
      </n-alert>
      <!-- 顶栏 -->
      <div class="ce-header">
        <n-text strong>第 {{ currentChapterNumber }} 章元素关联</n-text>
        <n-space :size="6">
          <n-select
            v-model:value="filterType"
            :options="elementTypeOptions"
            size="tiny"
            style="width: 90px"
            clearable
            placeholder="类型"
            @update:value="loadElements"
          />
          <n-button size="tiny" secondary :loading="loading" @click="loadElements">刷新</n-button>
        </n-space>
      </div>

      <!-- 无 story node 提示 -->
      <n-alert v-if="storyNodeNotFound" type="warning" :show-icon="true" style="margin: 8px 0">
        未在结构树中找到第 {{ currentChapterNumber }} 章的规划节点。请先在左侧「宏观规划」中创建章节结构。
      </n-alert>

      <!-- 元素列表 -->
      <n-spin :show="loading">
        <n-scrollbar style="max-height: 280px; padding-right: 4px">
          <n-space vertical :size="5" style="padding: 4px 0">
            <div v-for="elem in elements" :key="elem.id" class="ce-item">
              <div class="ce-item-info">
                <n-tag :type="elemTypeColor(elem.element_type)" size="tiny" round>{{ elemTypeLabel(elem.element_type) }}</n-tag>
                <n-text style="font-size:12px; flex:1">{{ elem.element_id }}</n-text>
                <n-tag size="tiny" round>{{ elem.relation_type }}</n-tag>
                <n-tag :type="elem.importance === 'major' ? 'error' : elem.importance === 'minor' ? 'default' : 'info'" size="tiny" round>
                  {{ importanceLabel(elem.importance) }}
                </n-tag>
              </div>
              <n-button
                v-if="!readOnly"
                size="tiny"
                type="error"
                text
                :loading="deletingId === elem.id"
                @click="doDelete(elem)"
              >删除</n-button>
            </div>
            <n-empty v-if="!loading && elements.length === 0 && !storyNodeNotFound" description="暂无关联元素" />
          </n-space>
        </n-scrollbar>
      </n-spin>

      <!-- 添加表单 -->
      <n-card
        v-if="storyNodeId && !storyNodeNotFound && !readOnly"
        title="添加元素关联"
        size="small"
        :bordered="false"
        style="margin-top: 8px; border-top: 1px solid var(--n-divider-color, rgba(0,0,0,.07))"
      >
        <n-space vertical :size="8">
          <n-space :size="6" wrap>
            <n-select
              v-model:value="form.element_type"
              :options="elementTypeOptions"
              size="small"
              style="width: 90px"
              placeholder="类型"
            />
            <n-input
              v-model:value="form.element_id"
              size="small"
              placeholder="元素 ID（人物/地点名称）"
              style="flex: 1; min-width: 120px"
            />
          </n-space>
          <n-space :size="6" wrap>
            <n-select
              v-model:value="form.relation_type"
              :options="relationTypeOptions"
              size="small"
              style="width: 100px"
              placeholder="关联类型"
            />
            <n-select
              v-model:value="form.importance"
              :options="importanceOptions"
              size="small"
              style="width: 80px"
              placeholder="重要性"
            />
            <n-input
              v-model:value="form.notes"
              size="small"
              placeholder="备注（可选）"
              style="flex: 1; min-width: 80px"
            />
          </n-space>
          <n-button
            type="primary"
            size="small"
            :loading="adding"
            :disabled="!form.element_type || !form.element_id || !form.relation_type"
            @click="doAdd"
          >
            添加关联
          </n-button>
        </n-space>
      </n-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { chapterElementApi } from '../../api/chapterElement'
import type { ChapterElementDTO, ElementType, RelationType, Importance } from '../../api/chapterElement'
import { planningApi } from '../../api/planning'
import type { StoryNode } from '../../api/planning'

const props = withDefaults(
  defineProps<{
    slug: string
    currentChapterNumber?: number | null
    /** 托管运行时只读，不可增删元素 */
    readOnly?: boolean
  }>(),
  { currentChapterNumber: null, readOnly: false }
)

const message = useMessage()

const elements = ref<ChapterElementDTO[]>([])
const loading = ref(false)
const adding = ref(false)
const deletingId = ref<string | null>(null)
const storyNodeId = ref<string | null>(null)
const storyNodeNotFound = ref(false)
const filterType = ref<ElementType | undefined>(undefined)

const form = ref<{
  element_type: ElementType | undefined
  element_id: string
  relation_type: RelationType | undefined
  importance: Importance
  notes: string
}>({ element_type: undefined, element_id: '', relation_type: undefined, importance: 'normal', notes: '' })

const elementTypeOptions = [
  { label: '人物', value: 'character' },
  { label: '地点', value: 'location' },
  { label: '道具', value: 'item' },
  { label: '组织', value: 'organization' },
  { label: '事件', value: 'event' },
]

const relationTypeOptions = [
  { label: '出场', value: 'appears' },
  { label: '提及', value: 'mentioned' },
  { label: '场景', value: 'scene' },
  { label: '使用', value: 'uses' },
  { label: '参与', value: 'involved' },
  { label: '发生', value: 'occurs' },
]

const importanceOptions = [
  { label: '主要', value: 'major' },
  { label: '一般', value: 'normal' },
  { label: '次要', value: 'minor' },
]

const elemTypeLabel = (t: string) => elementTypeOptions.find(o => o.value === t)?.label ?? t
const elemTypeColor = (t: string): 'error' | 'warning' | 'info' | 'success' | 'default' => {
  const map: Record<string, 'error' | 'warning' | 'info' | 'success' | 'default'> = {
    character: 'error', location: 'success', item: 'warning', organization: 'info', event: 'default'
  }
  return map[t] ?? 'default'
}
const importanceLabel = (i: string) => importanceOptions.find(o => o.value === i)?.label ?? i

/** 在结构树里找第 chapterNumber 章的 story node */
const findChapterNode = (node: StoryNode, num: number): StoryNode | null => {
  if (node.type === 'chapter' && node.number === num) return node
  for (const child of node.children ?? []) {
    const found = findChapterNode(child, num)
    if (found) return found
  }
  return null
}

const resolveStoryNode = async () => {
  storyNodeId.value = null
  storyNodeNotFound.value = false
  if (!props.currentChapterNumber) return
  try {
    const res = await planningApi.getStructure(props.slug)
    const node = findChapterNode(res.data, props.currentChapterNumber)
    if (node) {
      storyNodeId.value = node.id
    } else {
      storyNodeNotFound.value = true
    }
  } catch {
    storyNodeNotFound.value = true
  }
}

const loadElements = async () => {
  if (!storyNodeId.value) return
  loading.value = true
  try {
    const res = await chapterElementApi.getElements(storyNodeId.value, filterType.value)
    elements.value = res.data
  } catch {
    message.error('加载章节元素失败')
  } finally {
    loading.value = false
  }
}

const doAdd = async () => {
  if (!storyNodeId.value || !form.value.element_type || !form.value.element_id || !form.value.relation_type) return
  adding.value = true
  try {
    const res = await chapterElementApi.addElement(storyNodeId.value, {
      element_type: form.value.element_type,
      element_id: form.value.element_id,
      relation_type: form.value.relation_type,
      importance: form.value.importance,
      notes: form.value.notes || undefined,
    })
    elements.value.push(res.data)
    form.value.element_id = ''
    form.value.notes = ''
    message.success('已添加')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    message.error(err?.response?.data?.detail || '添加失败')
  } finally {
    adding.value = false
  }
}

const doDelete = async (elem: ChapterElementDTO) => {
  if (!storyNodeId.value) return
  deletingId.value = elem.id
  try {
    await chapterElementApi.deleteElement(storyNodeId.value, elem.id)
    elements.value = elements.value.filter(e => e.id !== elem.id)
    message.success('已删除')
  } catch {
    message.error('删除失败')
  } finally {
    deletingId.value = null
  }
}

// 换书时重置并重新解析
watch(() => props.slug, async (slug) => {
  if (slug) {
    elements.value = []
    storyNodeId.value = null
    storyNodeNotFound.value = false
    await resolveStoryNode()
    await loadElements()
  }
})

// 监听章节变化
watch(() => props.currentChapterNumber, async () => {
  await resolveStoryNode()
  await loadElements()
}, { immediate: false })

onMounted(async () => {
  await resolveStoryNode()
  await loadElements()
})
</script>

<style scoped>
.ce-panel {
  padding: 10px 12px;
  height: 100%;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.ce-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.ce-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 8px;
  border-radius: 8px;
  background: rgba(0,0,0,.03);
  gap: 6px;
}
.ce-item-info {
  display: flex;
  align-items: center;
  gap: 5px;
  flex: 1;
  overflow: hidden;
  flex-wrap: wrap;
  font-size: 12px;
}
</style>
