<script setup lang="ts">
/**
 * CanvasSearchResults - Display filtered roadmap items in canvas mode.
 *
 * Show roadmap items that match the search results from the
 * conversational AI in a clean, scrollable list.
 */

import type { RoadmapItem } from '@/types/roadmap';
import RoadmapCard from '@/components/RoadmapCard.vue';

interface Props {
  /** Filtered roadmap items to display */
  items: RoadmapItem[];
  /** Loading state */
  loading?: boolean;
}

withDefaults(defineProps<Props>(), {
  loading: false,
});
</script>

<template>
  <section class="canvas-search-results" aria-label="Search results">
    <!-- Results header -->
    <header class="canvas-search-results__header">
      <h2 class="canvas-search-results__title">
        Found {{ items.length }} {{ items.length === 1 ? 'item' : 'items' }}
      </h2>
    </header>

    <!-- Loading state -->
    <div v-if="loading" class="canvas-search-results__loading">
      <div v-for="i in 3" :key="i" class="canvas-search-results__skeleton" />
    </div>

    <!-- Results list -->
    <TransitionGroup
      v-if="!loading"
      name="canvas-results"
      tag="div"
      class="canvas-search-results__list"
      appear
    >
      <RoadmapCard
        v-for="(item, index) in items"
        :key="item.id"
        :item="item"
        class="canvas-search-results__item"
        :style="{ '--stagger-delay': `${index * 100}ms` }"
      />
    </TransitionGroup>
  </section>
</template>

<style scoped>
/* BEM: Block - canvas-search-results */
.canvas-search-results {
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-md, 16px);
}

/* BEM: Element - header */
.canvas-search-results__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* BEM: Element - title */
.canvas-search-results__title {
  font-size: var(--unnnic-font-size-body-lg, 16px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  margin: 0;
}

/* BEM: Element - loading */
.canvas-search-results__loading {
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-sm, 12px);
}

/* BEM: Element - skeleton */
.canvas-search-results__skeleton {
  height: 100px;
  background: linear-gradient(
    90deg,
    var(--unnnic-color-neutral-light, #f5f5f5) 25%,
    var(--unnnic-color-neutral-soft, #e8e8e8) 50%,
    var(--unnnic-color-neutral-light, #f5f5f5) 75%
  );
  background-size: 200% 100%;
  border-radius: var(--unnnic-border-radius-md, 12px);
  animation: canvas-skeleton-shimmer 1.5s ease-in-out infinite;
}

@keyframes canvas-skeleton-shimmer {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -200% 0;
  }
}

/* BEM: Element - list */
.canvas-search-results__list {
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-sm, 12px);
}

/* BEM: Element - item */
.canvas-search-results__item {
  /* Use stagger delay for progressive reveal animation */
  transition-delay: var(--stagger-delay, 0ms);
  margin-bottom: var(--unnnic-spacing-stack-sm, 12px);
}

.canvas-search-results__item:last-child {
  margin-bottom: 0;
}
</style>

<!-- Unscoped styles for TransitionGroup animations -->
<style>
/* Vue TransitionGroup animations - smooth and visible */
.canvas-results-enter-active,
.canvas-results-appear-active {
  transition:
    opacity 0.8s cubic-bezier(0.34, 1.56, 0.64, 1),
    transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
  transition-delay: var(--stagger-delay, 0ms);
}

.canvas-results-leave-active {
  transition:
    opacity 0.4s ease-in,
    transform 0.4s ease-in;
}

.canvas-results-enter-from,
.canvas-results-appear-from {
  opacity: 0;
  transform: translateY(30px) scale(0.9);
}

.canvas-results-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.canvas-results-move {
  transition: transform 0.5s ease;
}
</style>
