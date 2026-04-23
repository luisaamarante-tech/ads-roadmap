<script setup lang="ts">
/**
 * RoadmapCardList - Container for roadmap cards with item count.
 * Features cascading animation when items appear.
 */

import { ref, onMounted, watch } from 'vue';
import type { RoadmapItem, DeliveryStatus } from '@/types/roadmap';
import RoadmapCard from './RoadmapCard.vue';

interface Props {
  items: RoadmapItem[];
  status: DeliveryStatus;
  loading?: boolean;
  autoExpandEpicId?: string | null;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  autoExpandEpicId: null,
});

const statusLabels: Record<DeliveryStatus, string> = {
  DELIVERED: 'Delivered',
  NOW: 'In Progress',
  NEXT: 'Next',
  FUTURE: 'Future',
};

// Animation state - tracks if cards should animate in
const isAnimating = ref(false);

// Trigger animation on mount
onMounted(() => {
  if (props.items.length > 0) {
    // Small delay to ensure DOM is ready
    requestAnimationFrame(() => {
      isAnimating.value = true;
    });
  }
});

// Re-trigger animation when items change significantly
watch(
  () => props.items.length,
  (newLen, oldLen) => {
    if (newLen > 0 && oldLen === 0) {
      isAnimating.value = false;
      requestAnimationFrame(() => {
        isAnimating.value = true;
      });
    }
  },
);
</script>

<template>
  <section class="card-list">
    <!-- Header with count -->
    <header class="card-list__header">
      <div class="card-list__status-info">
        <strong class="card-list__count">{{ items.length }}</strong>
        <span class="card-list__status-label">{{ statusLabels[status] }}</span>
        <span class="card-list__count-text">
          {{ items.length === 1 ? 'Item' : 'Items' }}
        </span>
      </div>
    </header>

    <!-- Loading skeleton -->
    <div v-if="loading" class="card-list__skeleton">
      <div v-for="i in 3" :key="i" class="card-list__skeleton-card">
        <div class="card-list__skeleton-title" />
        <div class="card-list__skeleton-badge" />
      </div>
    </div>

    <!-- Card list with cascading animation -->
    <div v-else-if="items.length > 0" class="card-list__grid">
      <RoadmapCard
        v-for="(item, index) in items"
        :key="item.id"
        :class="[
          'card-list__item',
          { 'card-list__item--visible': isAnimating },
        ]"
        :item="item"
        :auto-expand="autoExpandEpicId === item.id"
        :style="{ '--card-index': index }"
      />
    </div>

    <!-- Empty state -->
    <div v-else class="card-list__empty">
      <div class="card-list__empty-icon">📋</div>
      <p class="card-list__empty-message">
        No {{ statusLabels[status].toLowerCase() }} items to display.
      </p>
      <p class="card-list__empty-hint">Check back later for updates!</p>
    </div>
  </section>
</template>

<style scoped>
/* BEM: Block - card-list */
.card-list {
  margin-top: var(--unnnic-spacing-stack-lg, 24px);
}

/* BEM: Element - header */
.card-list__header {
  margin-bottom: var(--unnnic-spacing-stack-md, 20px);
}

/* BEM: Element - status-info */
.card-list__status-info {
  display: flex;
  align-items: baseline;
  gap: var(--unnnic-spacing-inline-xs, 8px);
  font-size: var(--unnnic-font-size-body-lg, 18px);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
}

/* BEM: Element - status-label */
.card-list__status-label {
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  font-weight: var(--unnnic-font-weight-regular, 400);
}

/* BEM: Element - count */
.card-list__count {
  font-size: var(--unnnic-font-size-title-sm, 24px);
  color: #dd1259;
}

/* BEM: Element - count-text */
.card-list__count-text {
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  font-size: var(--unnnic-font-size-body-md, 14px);
}

/* BEM: Element - grid */
.card-list__grid {
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-sm, 16px);
}

/* Cascading animation for cards */
.card-list__item {
  opacity: 0;
  transform: translateY(16px);
  transition:
    opacity 0.4s cubic-bezier(0.16, 1, 0.3, 1),
    transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  transition-delay: calc(var(--card-index, 0) * 80ms);
}

.card-list__item--visible {
  opacity: 1;
  transform: translateY(0);
}

/* BEM: Element - skeleton (Loading state) */
.card-list__skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-sm, 16px);
}

/* BEM: Element - skeleton-card */
.card-list__skeleton-card {
  background: var(--unnnic-color-neutral-light, #f5f5f5);
  border-radius: var(--unnnic-border-radius-md, 12px);
  padding: var(--unnnic-spacing-stack-md, 20px);
  animation: card-list-pulse 1.5s ease-in-out infinite;
}

/* BEM: Element - skeleton-title */
.card-list__skeleton-title {
  height: 20px;
  background: var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: 4px;
  width: 70%;
  margin-bottom: var(--unnnic-spacing-stack-sm, 12px);
}

/* BEM: Element - skeleton-badge */
.card-list__skeleton-badge {
  height: 24px;
  background: var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-sm, 6px);
  width: 100px;
}

@keyframes card-list-pulse {
  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}

/* BEM: Element - empty */
.card-list__empty {
  text-align: center;
  padding: 60px var(--unnnic-spacing-inline-md, 20px);
  background: var(--unnnic-color-background-carpet, #f9f9f9);
  border-radius: var(--unnnic-border-radius-md, 12px);
}

/* BEM: Element - empty-icon */
.card-list__empty-icon {
  font-size: 48px;
  margin-bottom: var(--unnnic-spacing-stack-sm, 16px);
}

/* BEM: Element - empty-message */
.card-list__empty-message {
  font-size: var(--unnnic-font-size-body-lg, 16px);
  color: var(--unnnic-color-neutral-dark, #4a4a4a);
  margin: 0 0 var(--unnnic-spacing-stack-xs, 8px) 0;
}

/* BEM: Element - empty-hint */
.card-list__empty-hint {
  font-size: var(--unnnic-font-size-body-md, 14px);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  margin: 0;
}

/* Responsive */
@media (width <= 640px) {
  .card-list__status-info {
    font-size: var(--unnnic-font-size-body-lg, 16px);
  }

  .card-list__count {
    font-size: var(--unnnic-font-size-title-xs, 20px);
  }
}
</style>
