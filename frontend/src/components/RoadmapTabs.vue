<script setup lang="ts">
/**
 * RoadmapTabs - Status navigation tabs for the roadmap.
 *
 * Displays tabs for each delivery status (Delivered, Now, Next, Future)
 * with optional item counts.
 */

import { computed } from 'vue';
import type { DeliveryStatus, RoadmapStats } from '@/types/roadmap';
import { STATUS_TABS } from '@/types/roadmap';

interface Props {
  modelValue: DeliveryStatus;
  stats?: RoadmapStats | null;
}

const props = withDefaults(defineProps<Props>(), {
  stats: null,
});

const emit = defineEmits<{
  'update:modelValue': [value: DeliveryStatus];
}>();

const activeTab = computed({
  get: () => props.modelValue,
  set: (value: DeliveryStatus) => emit('update:modelValue', value),
});

function getCount(status: DeliveryStatus): number | undefined {
  if (!props.stats) return undefined;
  return props.stats[status];
}

// Event handler: use "on" prefix for user interactions
function onTabClick(status: DeliveryStatus): void {
  activeTab.value = status;
}
</script>

<template>
  <nav class="tabs" aria-label="Roadmap status navigation">
    <div class="tabs__container" role="tablist">
      <button
        v-for="tab in STATUS_TABS"
        :key="tab.value"
        :class="['tabs__tab', { 'tabs__tab--active': activeTab === tab.value }]"
        role="tab"
        :aria-selected="activeTab === tab.value"
        :aria-controls="`panel-${tab.value}`"
        :title="tab.description"
        @click="onTabClick(tab.value)"
      >
        <span class="tabs__label">{{ tab.label }}</span>
        <span v-if="getCount(tab.value) !== undefined" class="tabs__count">
          {{ getCount(tab.value) }}
        </span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
/* BEM: Block - tabs */
.tabs {
  margin-bottom: var(--unnnic-spacing-stack-lg, 24px);
}

/* BEM: Element - container */
.tabs__container {
  display: flex;
  gap: var(--unnnic-spacing-inline-xs, 8px);
  border-bottom: 2px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  padding-bottom: 0;
}

/* BEM: Element - tab */
.tabs__tab {
  display: flex;
  align-items: center;
  gap: var(--unnnic-spacing-inline-xs, 8px);
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  font-size: var(--unnnic-font-size-body-md, 14px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  transition: all 0.2s ease;
}

.tabs__tab:hover {
  color: #dd1259;
  background: rgb(247 25 99 / 5%);
}

/* BEM: Modifier - active */
.tabs__tab--active {
  color: #dd1259;
  border-bottom-color: #dd1259;
}

/* BEM: Element - label */
.tabs__label {
  white-space: nowrap;
}

/* BEM: Element - count */
.tabs__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 20px;
  padding: 0 6px;
  background: var(--unnnic-color-neutral-light, #f0f0f0);
  border-radius: 10px;
  font-size: var(--unnnic-font-size-body-sm, 12px);
  font-weight: var(--unnnic-font-weight-bold, 600);
}

.tabs__tab--active .tabs__count {
  background: #F71963;
  color: #fff;
}

/* Responsive */
@media (width <= 640px) {
  .tabs__container {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .tabs__tab {
    padding: 10px 16px;
    font-size: var(--unnnic-font-size-body-sm, 13px);
  }
}
</style>
