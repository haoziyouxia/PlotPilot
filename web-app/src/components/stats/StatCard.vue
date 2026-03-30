<template>
  <article class="stat-card">
    <div class="stat-card-header">
      <span v-if="icon" class="stat-icon">{{ icon }}</span>
      <span class="stat-title">{{ title }}</span>
    </div>
    <div class="stat-card-body">
      <n-skeleton v-if="loading" :width="120" :height="40" />
      <template v-else>
        <span class="stat-value">{{ formattedValue }}</span>
        <span v-if="unit" class="stat-unit">{{ unit }}</span>
      </template>
    </div>
    <div v-if="trend && !loading" class="stat-trend" :class="`trend-${trend.direction}`" :aria-label="`Trend ${trend.direction} by ${trendValue} percent`">
      <span :class="['trend-indicator', `trend-${trend.direction}`]">
        {{ trend.direction === 'up' ? '↑' : '↓' }}
        {{ trendValue }}%
      </span>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { NSkeleton } from 'naive-ui'

interface TrendData {
  value: number
  direction: 'up' | 'down'
}

interface Props {
  title: string
  value: number | string
  icon?: string
  trend?: TrendData
  loading?: boolean
  unit?: string
}

const props = defineProps<Props>()

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})

const trendValue = computed(() => props.trend ? Math.abs(props.trend.value) : 0)
</script>

<style scoped>
.stat-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s ease-in-out;
  cursor: default;
}

.stat-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.stat-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.stat-icon {
  font-size: 24px;
  line-height: 1;
}

.stat-title {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.stat-card-body {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #111827;
  line-height: 1;
}

.stat-unit {
  font-size: 14px;
  color: #6b7280;
  font-weight: normal;
}

.stat-trend {
  display: flex;
  align-items: center;
}

.trend-indicator {
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.trend-up {
  color: #10b981;
}

.trend-down {
  color: #ef4444;
}
</style>
