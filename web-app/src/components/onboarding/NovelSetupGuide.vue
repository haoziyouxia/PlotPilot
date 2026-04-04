<template>
  <n-modal
    v-model:show="modalOpen"
    :mask-closable="false"
    :close-on-esc="false"
    :closable="false"
    preset="card"
    title="新书设置向导"
    style="width: 90%; max-width: 600px; max-height: 90vh"
  >
    <n-steps :current="currentStep" :status="stepStatus" size="small">
      <n-step title="世界观" description="5维度框架" />
      <n-step title="人物" description="主要角色" />
      <n-step title="地图" description="地图系统" />
      <n-step title="故事线" description="主线支线" />
      <n-step title="情节弧" description="剧情曲线" />
      <n-step title="开始" description="进入工作台" />
    </n-steps>

    <div class="step-content">
      <!-- Step 1: Generate Worldbuilding + Style -->
      <div v-if="currentStep === 1" class="step-panel">
        <n-alert v-if="bibleError" type="error" :title="bibleError" style="margin-bottom: 16px" />
        <n-spin :show="generatingBible">
          <div v-if="!bibleGenerated" class="step-info">
            <n-icon size="48" color="#18a058">
              <IconBook />
            </n-icon>
            <h3>{{ bibleStatusText }}</h3>
            <p>AI 正在分析您的故事创意，生成世界观（5维度框架）和文风公约...</p>
          </div>

          <!-- 生成完成后显示预览 -->
          <div v-else class="bible-preview">
            <n-alert type="success" title="世界观生成完成" style="margin-bottom: 16px">
              请查看并确认世界观设定和文风公约，下一步将基于此生成人物和地点。
            </n-alert>

            <n-collapse default-expanded-names="worldbuilding">
              <n-collapse-item title="世界观（5维度框架）" name="worldbuilding">
                <n-space vertical>
                  <n-card size="small" title="核心法则">
                    <n-space vertical size="small">
                      <div><strong>力量体系：</strong>{{ worldbuildingData.core_rules?.power_system || '待生成' }}</div>
                      <div><strong>物理规律：</strong>{{ worldbuildingData.core_rules?.physics_rules || '待生成' }}</div>
                      <div><strong>魔法/科技：</strong>{{ worldbuildingData.core_rules?.magic_tech || '待生成' }}</div>
                    </n-space>
                  </n-card>
                  <n-card size="small" title="地理生态">
                    <n-space vertical size="small">
                      <div><strong>地形：</strong>{{ worldbuildingData.geography?.terrain || '待生成' }}</div>
                      <div><strong>气候：</strong>{{ worldbuildingData.geography?.climate || '待生成' }}</div>
                      <div><strong>资源：</strong>{{ worldbuildingData.geography?.resources || '待生成' }}</div>
                      <div><strong>生态：</strong>{{ worldbuildingData.geography?.ecology || '待生成' }}</div>
                    </n-space>
                  </n-card>
                  <n-card size="small" title="社会结构">
                    <n-space vertical size="small">
                      <div><strong>政治：</strong>{{ worldbuildingData.society?.politics || '待生成' }}</div>
                      <div><strong>经济：</strong>{{ worldbuildingData.society?.economy || '待生成' }}</div>
                      <div><strong>阶级：</strong>{{ worldbuildingData.society?.class_system || '待生成' }}</div>
                    </n-space>
                  </n-card>
                  <n-card size="small" title="历史文化">
                    <n-space vertical size="small">
                      <div><strong>历史：</strong>{{ worldbuildingData.culture?.history || '待生成' }}</div>
                      <div><strong>宗教：</strong>{{ worldbuildingData.culture?.religion || '待生成' }}</div>
                      <div><strong>禁忌：</strong>{{ worldbuildingData.culture?.taboos || '待生成' }}</div>
                    </n-space>
                  </n-card>
                  <n-card size="small" title="沉浸感细节">
                    <n-space vertical size="small">
                      <div><strong>衣食住行：</strong>{{ worldbuildingData.daily_life?.food_clothing || '待生成' }}</div>
                      <div><strong>俚语口音：</strong>{{ worldbuildingData.daily_life?.language_slang || '待生成' }}</div>
                      <div><strong>娱乐方式：</strong>{{ worldbuildingData.daily_life?.entertainment || '待生成' }}</div>
                    </n-space>
                  </n-card>
                </n-space>
              </n-collapse-item>

              <n-collapse-item title="文风公约" name="style">
                <n-card size="small">
                  {{ bibleData.style || '待生成' }}
                </n-card>
              </n-collapse-item>
            </n-collapse>
          </div>
        </n-spin>
      </div>

      <!-- Step 2: Generate Characters -->
      <div v-else-if="currentStep === 2" class="step-panel">
        <n-spin :show="generatingCharacters">
          <div v-if="!charactersGenerated" class="step-info">
            <n-icon size="48" color="#2080f0">
              <IconPeople />
            </n-icon>
            <h3>生成人物</h3>
            <p>基于世界观设定，AI 正在生成3-5个主要角色...</p>
          </div>

          <!-- 生成完成后显示预览 -->
          <div v-else class="bible-preview">
            <n-alert type="success" title="人物生成完成" style="margin-bottom: 16px">
              请查看并确认角色设定。
            </n-alert>

            <n-list bordered>
              <n-list-item v-for="char in bibleData.characters" :key="char.name">
                <n-thing :title="char.name" :description="char.description">
                  <template #header-extra>
                    <n-tag size="small">{{ char.role }}</n-tag>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
          </div>
        </n-spin>
      </div>

      <!-- Step 3: Generate Locations -->
      <div v-else-if="currentStep === 3" class="step-panel">
        <n-spin :show="generatingLocations">
          <div v-if="!locationsGenerated" class="step-info">
            <n-icon size="48" color="#f0a020">
              <IconMap />
            </n-icon>
            <h3>生成地图</h3>
            <p>基于世界观和人物设定，AI 正在生成完整的地点系统（地图）...</p>
          </div>

          <!-- 生成完成后显示预览 -->
          <div v-else class="bible-preview">
            <n-alert type="success" title="地图生成完成" style="margin-bottom: 16px">
              请查看并确认地点设定。
            </n-alert>

            <n-list bordered>
              <n-list-item v-for="loc in bibleData.locations" :key="loc.name">
                <n-thing :title="loc.name" :description="loc.description">
                  <template #header-extra>
                    <n-tag size="small" type="info">{{ loc.type }}</n-tag>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
          </div>
        </n-spin>
      </div>

      <!-- Step 2: Generate Characters -->
      <div v-else-if="currentStep === 2" class="step-panel">
        <n-alert v-if="!generatingCharacters && !charactersGenerated" type="info" style="margin-bottom: 16px">
          点击"生成人物"按钮，AI 将基于世界观生成3-5个主要角色
        </n-alert>
        <n-spin :show="generatingCharacters">
          <div v-if="!charactersGenerated" class="step-info">
            <n-icon size="48" color="#2080f0">
              <IconPeople />
            </n-icon>
            <h3>{{ generatingCharacters ? '正在生成人物...' : '准备生成人物' }}</h3>
            <p>基于世界观设定生成主要角色</p>
          </div>
          <div v-else class="bible-preview">
            <n-alert type="success" title="人物生成完成" style="margin-bottom: 16px">
              人物已生成，下一步将生成完整地图
            </n-alert>
          </div>
        </n-spin>
      </div>

      <!-- Step 3: Generate Locations -->
      <div v-else-if="currentStep === 3" class="step-panel">
        <n-alert v-if="!generatingLocations && !locationsGenerated" type="info" style="margin-bottom: 16px">
          点击"生成地图"按钮，AI 将基于世界观和人物生成完整地点系统
        </n-alert>
        <n-spin :show="generatingLocations">
          <div v-if="!locationsGenerated" class="step-info">
            <n-icon size="48" color="#f0a020">
              <IconMap />
            </n-icon>
            <h3>{{ generatingLocations ? '正在生成地图...' : '准备生成地图' }}</h3>
            <p>基于世界观和人物生成完整地点系统</p>
          </div>
          <div v-else class="bible-preview">
            <n-alert type="success" title="地图生成完成" style="margin-bottom: 16px">
              地图已生成，可以继续规划故事线
            </n-alert>
          </div>
        </n-spin>
      </div>

      <!-- Step 4: Storylines -->
      <div v-else-if="currentStep === 4" class="step-panel">
        <div class="step-info">
          <n-icon size="48" color="#2080f0">
            <IconTimeline />
          </n-icon>
          <h3>规划故事线</h3>
          <p>建议先设计故事的主线、支线和暗线，这将帮助 AI 更好地规划章节结构。</p>
          <n-space vertical size="small" style="margin-top: 16px; text-align: left">
            <div>• 主线：故事的核心发展脉络</div>
            <div>• 支线：丰富情节的次要线索</div>
            <div>• 暗线：隐藏的伏笔和线索</div>
          </n-space>
        </div>
      </div>

      <!-- Step 5: Plot Arc -->
      <div v-else-if="currentStep === 5" class="step-panel">
        <div class="step-info">
          <n-icon size="48" color="#f0a020">
            <IconChart />
          </n-icon>
          <h3>设计情节弧线</h3>
          <p>规划故事的起承转合，设置关键剧情点和张力变化。</p>
          <n-space vertical size="small" style="margin-top: 16px; text-align: left">
            <div>• 开端：故事的起点</div>
            <div>• 上升：矛盾逐渐激化</div>
            <div>• 转折：关键转折点</div>
            <div>• 高潮：矛盾最激烈时刻</div>
            <div>• 结局：故事的收尾</div>
          </n-space>
        </div>
      </div>

      <!-- Step 6: Complete -->
      <div v-else-if="currentStep === 6" class="step-panel">
        <div class="step-info">
          <n-icon size="48" color="#18a058">
            <IconCheck />
          </n-icon>
          <h3>准备就绪！</h3>
          <p>所有基础设置已完成，现在可以开始创作了。</p>
          <p style="margin-top: 12px; color: #666">您可以随时在工作台的"设置"面板中调整这些内容。</p>
        </div>
      </div>
    </div>

    <template #footer>
      <n-space justify="space-between">
        <n-button v-if="currentStep > 3 && currentStep < 6" @click="handleSkip">
          跳过向导
        </n-button>
        <div v-else></div>
        <n-space>
          <n-button
            v-if="(currentStep === 1 && bibleGenerated) || (currentStep === 2 && charactersGenerated) || (currentStep === 3 && locationsGenerated)"
            type="primary"
            @click="handleNext"
          >
            确认并继续
          </n-button>
          <n-button v-if="currentStep >= 4 && currentStep <= 5" @click="handleNext">
            {{ currentStep === 5 ? '完成设置' : '下一步' }}
          </n-button>
          <n-button v-if="currentStep === 6" type="primary" @click="handleComplete">
            进入工作台
          </n-button>
        </n-space>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { h, ref, watch, computed, onUnmounted } from 'vue'
import { bibleApi } from '@/api/bible'
import { worldbuildingApi } from '@/api/worldbuilding'

function formatApiError(error: unknown): string {
  const e = error as {
    response?: { data?: { detail?: unknown } }
    message?: string
  }
  const d = e?.response?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d))
    return d.map((x: { msg?: string }) => x?.msg || JSON.stringify(x)).join('；')
  if (d != null && typeof d === 'object') return JSON.stringify(d)
  if (e?.message) return e.message
  return ''
}

const IconBook = () =>
  h(
    'svg',
    { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'currentColor' },
    h('path', { d: 'M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z' })
  )

const IconPeople = () =>
  h(
    'svg',
    { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'currentColor' },
    h('path', { d: 'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z' })
  )

const IconMap = () =>
  h(
    'svg',
    { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'currentColor' },
    h('path', { d: 'M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z' })
  )

const IconTimeline = () =>
  h(
    'svg',
    { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'currentColor' },
    h('path', { d: 'M23 8c0 1.1-.9 2-2 2-.18 0-.35-.02-.51-.07l-3.56 3.55c.05.16.07.34.07.52 0 1.1-.9 2-2 2s-2-.9-2-2c0-.18.02-.36.07-.52l-2.55-2.55c-.16.05-.34.07-.52.07s-.36-.02-.52-.07l-4.55 4.56c.05.16.07.33.07.51 0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2c.18 0 .35.02.51.07l4.56-4.55C8.02 9.36 8 9.18 8 9c0-1.1.9-2 2-2s2 .9 2 2c0 .18-.02.36-.07.52l2.55 2.55c.16-.05.34-.07.52-.07s.36.02.52.07l3.55-3.56C19.02 8.35 19 8.18 19 8c0-1.1.9-2 2-2s2 .9 2 2z' })
  )

const IconChart = () =>
  h(
    'svg',
    { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'currentColor' },
    h('path', { d: 'M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z' })
  )

const IconCheck = () =>
  h(
    'svg',
    { xmlns: 'http://www.w3.org/2000/svg', viewBox: '0 0 24 24', fill: 'currentColor' },
    h('path', { d: 'M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z' })
  )

const props = defineProps<{
  novelId: string
  show: boolean
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'complete'): void
  (e: 'skip'): void
}>()

/** 与父组件 show 单一数据源，避免本地 visible 与 props 打架导致误 emit(false) 把向导关掉 */
const modalOpen = computed({
  get: () => props.show,
  set: (v: boolean) => emit('update:show', v),
})

const currentStep = ref(1)
const stepStatus = ref<'process' | 'finish' | 'error' | 'wait'>('process')

// 第1步：生成世界观和文风
const generatingBible = ref(false)
const bibleGenerated = ref(false)
const bibleStatusText = ref('正在生成世界观...')
const bibleError = ref('')
const bibleData = ref<any>({ style: '' })
const worldbuildingData = ref<any>({
  core_rules: {},
  geography: {},
  society: {},
  culture: {},
  daily_life: {}
})

// 第2步：生成人物和地点
const generatingCharacters = ref(false)
const charactersGenerated = ref(false)

// 第3步：生成地点
const generatingLocations = ref(false)
const locationsGenerated = ref(false)

const pollTimerRef = ref<ReturnType<typeof setTimeout> | null>(null)
const timeoutTimerRef = ref<ReturnType<typeof setTimeout> | null>(null)
/** 递增以作废上一轮流询中的异步回调（避免超时/关闭后仍进入「完成」分支） */
const biblePollEpoch = ref(0)

function clearGenerationTimers() {
  if (pollTimerRef.value != null) {
    clearTimeout(pollTimerRef.value)
    pollTimerRef.value = null
  }
  if (timeoutTimerRef.value != null) {
    clearTimeout(timeoutTimerRef.value)
    timeoutTimerRef.value = null
  }
}

onUnmounted(() => {
  clearGenerationTimers()
})

/** 仅清理轮询定时器，保留总超时 timer（由 clearGenerationTimers 统一清理） */
function clearPollTimer() {
  if (pollTimerRef.value != null) {
    clearTimeout(pollTimerRef.value)
    pollTimerRef.value = null
  }
}

/**
 * 轮询：串行 setTimeout，避免 setInterval+async 叠请求。
 * 必须用 function 声明放在 watch 之前：`watch(..., { immediate: true })` 会同步调用回调，
 * `const startBibleGeneration = ...` 尚在暂存死区会导致运行时报错 / 逻辑异常。
 */
async function startBibleGeneration() {
  clearGenerationTimers()
  biblePollEpoch.value += 1
  const epoch = biblePollEpoch.value
  generatingBible.value = true
  bibleError.value = ''

  try {
    // 第1步：只生成世界观和文风
    await bibleApi.generateBible(props.novelId, 'worldbuilding')
    if (biblePollEpoch.value !== epoch || !generatingBible.value) return
    bibleStatusText.value = '正在生成世界观和文风...'

    const schedulePoll = (delayMs: number) => {
      clearPollTimer()
      pollTimerRef.value = window.setTimeout(() => {
        void runPoll()
      }, delayMs)
    }

    const runPoll = async () => {
      if (biblePollEpoch.value !== epoch || !generatingBible.value) return
      try {
        const status = await bibleApi.getBibleStatus(props.novelId)
        if (biblePollEpoch.value !== epoch || !generatingBible.value) return
        if (status.ready) {
          clearGenerationTimers()
          generatingBible.value = false
          bibleStatusText.value = '世界观生成完成！'

          // 加载生成的数据
          try {
            const [bible, worldbuilding] = await Promise.all([
              bibleApi.getBible(props.novelId),
              worldbuildingApi.getWorldbuilding(props.novelId)
            ])
            bibleData.value = bible
            worldbuildingData.value = worldbuilding
            bibleGenerated.value = true
          } catch (error: unknown) {
            console.error('Failed to load generated data:', error)
            bibleGenerated.value = true // 即使加载失败也标记为完成
          }
          return
        }
      } catch (error: unknown) {
        if (biblePollEpoch.value !== epoch) return
        clearGenerationTimers()
        generatingBible.value = false
        const detail = formatApiError(error)
        bibleError.value =
          detail || '检查状态失败（网络或后端不可用），请确认本机已启动 API 并刷新重试'
        return
      }
      if (biblePollEpoch.value !== epoch || !generatingBible.value) return
      schedulePoll(2000)
    }

    timeoutTimerRef.value = window.setTimeout(() => {
      if (biblePollEpoch.value !== epoch) return
      biblePollEpoch.value += 1
      clearGenerationTimers()
      generatingBible.value = false
      bibleError.value = '生成超时，请稍后在工作台手动重试'
    }, 120000)

    schedulePoll(0)
  } catch (error: unknown) {
    if (biblePollEpoch.value !== epoch) return
    generatingBible.value = false
    const detail = formatApiError(error)
    bibleError.value = detail || '生成失败，请重试'
  }
}

watch(
  () => props.show,
  (val) => {
    if (val) {
      currentStep.value = 1
      stepStatus.value = 'process'
      void startBibleGeneration()
    } else {
      biblePollEpoch.value += 1
      clearGenerationTimers()
      generatingBible.value = false
    }
  },
  { immediate: true }
)

const handleNext = async () => {
  if (currentStep.value === 1) {
    // 进入第2步：生成人物
    currentStep.value = 2
    generatingCharacters.value = true
    try {
      await bibleApi.generateBible(props.novelId, 'characters')
      // 轮询检查人物生成状态
      const checkCharacters = async () => {
        const status = await bibleApi.getBibleStatus(props.novelId)
        if (status.ready) {
          generatingCharacters.value = false
          charactersGenerated.value = true
        } else {
          window.setTimeout(checkCharacters, 2000)
        }
      }
      await checkCharacters()
    } catch (error) {
      console.error('Failed to generate characters:', error)
      generatingCharacters.value = false
    }
  } else if (currentStep.value === 2) {
    // 进入第3步：生成地点
    currentStep.value = 3
    generatingLocations.value = true
    try {
      await bibleApi.generateBible(props.novelId, 'locations')
      // 轮询检查地点生成状态
      const checkLocations = async () => {
        const status = await bibleApi.getBibleStatus(props.novelId)
        if (status.ready) {
          generatingLocations.value = false
          locationsGenerated.value = true
        } else {
          window.setTimeout(checkLocations, 2000)
        }
      }
      await checkLocations()
    } catch (error) {
      console.error('Failed to generate locations:', error)
      generatingLocations.value = false
    }
  } else if (currentStep.value < 6) {
    currentStep.value++
  }
}

const handleSkip = () => {
  emit('skip')
  emit('update:show', false)
}

const handleComplete = () => {
  emit('complete')
  emit('update:show', false)
}
</script>

<style scoped>
.step-content {
  margin: 32px 0;
  min-height: 280px;
  max-height: calc(90vh - 280px);
  overflow-y: auto;
}

.step-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.step-info {
  text-align: center;
  max-width: 480px;
}

.step-info h3 {
  margin: 16px 0 8px;
  font-size: 20px;
  font-weight: 600;
}

.step-info p {
  color: #666;
  line-height: 1.6;
  margin: 8px 0;
}
</style>
