<script setup lang="ts">
/**
 * RoadmapEmptyState - Empty and loading state displays.
 */

import type { DeliveryStatus } from '@/types/roadmap';

interface Props {
  loading?: boolean;
  status?: DeliveryStatus;
  hasFilters?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
  status: 'DELIVERED',
  hasFilters: false,
});

const emit = defineEmits<{
  clearFilters: [];
}>();

const statusMessages: Record<DeliveryStatus, string> = {
  DELIVERED: 'No delivered features yet.',
  NOW: 'No features currently in progress.',
  NEXT: 'No features planned for next quarter.',
  FUTURE: 'No future features planned yet.',
};

// Event handler: use "on" prefix for user interactions
function onClearFiltersClick(): void {
  emit('clearFilters');
}
</script>

<template>
  <div class="empty-state">
    <!-- Loading skeleton -->
    <template v-if="loading">
      <div class="empty-state__skeleton">
        <div v-for="i in 3" :key="i" class="empty-state__skeleton-card">
          <div class="empty-state__skeleton-header">
            <div class="empty-state__skeleton-title" />
            <div class="empty-state__skeleton-button" />
          </div>
          <div class="empty-state__skeleton-badges">
            <div class="empty-state__skeleton-badge" />
            <div class="empty-state__skeleton-date" />
          </div>
        </div>
      </div>
    </template>

    <!-- Empty state -->
    <template v-else>
      <div class="empty-state__container">
        <div class="empty-state__icon">
          <svg
            width="64"
            height="64"
            viewBox="0 0 64 64"
            fill="none"
            aria-hidden="true"
          >
            <circle
              cx="32"
              cy="32"
              r="28"
              stroke="#e8e8e8"
              stroke-width="2"
              stroke-dasharray="4 4"
            />
            <path
              d="M24 32h16M32 24v16"
              stroke="#d0d0d0"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
        </div>
        <h3 class="empty-state__title">
          {{ statusMessages[status] }}
        </h3>
        <p v-if="hasFilters" class="empty-state__description">
          Try adjusting your filters to see more items.
        </p>
        <p v-else class="empty-state__description">
          Check back later for updates on our roadmap!
        </p>
        <button
          v-if="hasFilters"
          class="empty-state__clear-btn"
          @click="onClearFiltersClick"
        >
          Clear Filters
        </button>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* BEM: Block - empty-state */
.empty-state {
  padding: var(--unnnic-spacing-stack-md, 20px) 0;
}

/* BEM: Element - skeleton */
.empty-state__skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-sm, 16px);
}

/* BEM: Element - skeleton-card */
.empty-state__skeleton-card {
  background: var(--unnnic-color-background-snow, #fff);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-md, 12px);
  padding: var(--unnnic-spacing-stack-md, 20px);
  animation: empty-state-pulse 1.5s ease-in-out infinite;
}

/* BEM: Element - skeleton-header */
.empty-state__skeleton-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--unnnic-spacing-stack-sm, 12px);
}

/* BEM: Element - skeleton-title */
.empty-state__skeleton-title {
  height: 20px;
  width: 65%;
  background: linear-gradient(
    90deg,
    var(--unnnic-color-neutral-light, #f0f0f0) 25%,
    var(--unnnic-color-neutral-soft, #e8e8e8) 50%,
    var(--unnnic-color-neutral-light, #f0f0f0) 75%
  );
  background-size: 200% 100%;
  animation: empty-state-shimmer 1.5s infinite;
  border-radius: 4px;
}

/* BEM: Element - skeleton-button */
.empty-state__skeleton-button {
  width: 32px;
  height: 32px;
  background: var(--unnnic-color-neutral-light, #f0f0f0);
  border-radius: var(--unnnic-border-radius-sm, 8px);
}

/* BEM: Element - skeleton-badges */
.empty-state__skeleton-badges {
  display: flex;
  gap: var(--unnnic-spacing-inline-sm, 12px);
}

/* BEM: Element - skeleton-badge */
.empty-state__skeleton-badge {
  width: 80px;
  height: 24px;
  background: linear-gradient(
    90deg,
    var(--unnnic-color-neutral-light, #f0f0f0) 25%,
    var(--unnnic-color-neutral-soft, #e8e8e8) 50%,
    var(--unnnic-color-neutral-light, #f0f0f0) 75%
  );
  background-size: 200% 100%;
  animation: empty-state-shimmer 1.5s infinite;
  border-radius: var(--unnnic-border-radius-sm, 6px);
}

/* BEM: Element - skeleton-date */
.empty-state__skeleton-date {
  width: 60px;
  height: 20px;
  background: var(--unnnic-color-neutral-light, #f0f0f0);
  border-radius: 4px;
}

@keyframes empty-state-pulse {
  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.7;
  }
}

@keyframes empty-state-shimmer {
  0% {
    background-position: -200% 0;
  }

  100% {
    background-position: 200% 0;
  }
}

/* BEM: Element - container */
.empty-state__container {
  text-align: center;
  padding: 60px var(--unnnic-spacing-inline-md, 20px);
  background: var(--unnnic-color-background-carpet, #fafafa);
  border-radius: var(--unnnic-border-radius-lg, 16px);
  border: 2px dashed var(--unnnic-color-neutral-soft, #e8e8e8);
}

/* BEM: Element - icon */
.empty-state__icon {
  margin-bottom: var(--unnnic-spacing-stack-md, 20px);
}

/* BEM: Element - title */
.empty-state__title {
  font-size: var(--unnnic-font-size-body-lg, 18px);
  font-weight: var(--unnnic-font-weight-bold, 600);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
  margin: 0 0 var(--unnnic-spacing-stack-xs, 8px) 0;
}

/* BEM: Element - description */
.empty-state__description {
  font-size: var(--unnnic-font-size-body-md, 14px);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  margin: 0 0 var(--unnnic-spacing-stack-md, 20px) 0;
}

/* BEM: Element - clear-btn */
.empty-state__clear-btn {
  padding: 12px 24px;
  background: transparent;
  border: 2px solid #dd1259;
  color: #dd1259;
  border-radius: var(--unnnic-border-radius-sm, 8px);
  font-size: var(--unnnic-font-size-body-md, 14px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  cursor: pointer;
  transition: all 0.2s;
}

.empty-state__clear-btn:hover {
  background: #dd1259;
  color: var(--unnnic-color-background-snow, #fff);
}

/* Responsive */
@media (width <= 640px) {
  .empty-state__container {
    padding: 40px var(--unnnic-spacing-inline-sm, 16px);
  }
}
</style>
