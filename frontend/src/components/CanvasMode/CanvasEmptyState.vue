<script setup lang="ts">
/**
 * CanvasEmptyState - Empty state for canvas search mode.
 *
 * Display an inviting prompt encouraging users to ask questions
 * about the roadmap through the WebChat.
 */

interface Props {
  /** Whether to show "no results found" state */
  noResults?: boolean;
  /** Whether currently searching/waiting for results */
  searching?: boolean;
}

withDefaults(defineProps<Props>(), {
  noResults: false,
  searching: false,
});
</script>

<template>
  <section
    :class="[
      'canvas-empty-state',
      { 'canvas-empty-state--searching': searching },
      { 'canvas-empty-state--no-results': noResults },
    ]"
    aria-label="Search prompt"
  >
    <div class="canvas-empty-state__icon">
      <svg
        width="64"
        height="64"
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
      >
        <circle
          cx="32"
          cy="32"
          r="28"
          stroke="currentColor"
          stroke-width="2"
          stroke-dasharray="4 4"
        />
        <path
          d="M24 28C24 25.7909 25.7909 24 28 24H36C38.2091 24 40 25.7909 40 28V36C40 38.2091 38.2091 40 36 40H28C25.7909 40 24 38.2091 24 36V28Z"
          fill="currentColor"
          opacity="0.2"
        />
        <path
          d="M28 32H36M32 28V36"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        />
      </svg>
    </div>

    <h2 class="canvas-empty-state__title">
      <template v-if="noResults"> No matching items found </template>
      <template v-else> Ask me about the roadmap </template>
    </h2>

    <p class="canvas-empty-state__description">
      <template v-if="noResults">
        Try a different search query to find what you're looking for.
      </template>
      <template v-else>
        I can help you discover features and updates. Try asking about specific
        topics or capabilities.
      </template>
    </p>

    <div v-if="!noResults" class="canvas-empty-state__suggestions">
      <p class="canvas-empty-state__suggestions-label">Try asking:</p>
      <ul class="canvas-empty-state__suggestions-list">
        <li>"What AI features are coming?"</li>
        <li>"Show me engagement updates"</li>
        <li>"What's new in Q1?"</li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
/* BEM: Block - canvas-empty-state */
.canvas-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--unnnic-spacing-stack-xl, 48px);
  text-align: center;
  min-height: 400px;

  /* No entry animation - parent handles transitions */
}

/* BEM: Element - icon */
.canvas-empty-state__icon {
  color: #dd1259;
  margin-bottom: var(--unnnic-spacing-stack-md, 20px);
}

/* BEM: Modifier - searching */
.canvas-empty-state--searching {
  opacity: 0.7;
}

.canvas-empty-state--searching .canvas-empty-state__icon {
  animation: canvas-empty-pulse 1.5s ease-in-out infinite;
}

@keyframes canvas-empty-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }

  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
}

/* BEM: Modifier - no-results */
.canvas-empty-state--no-results .canvas-empty-state__icon {
  color: var(--unnnic-color-neutral-cloudy, #67738b);
}

/* BEM: Element - title */
.canvas-empty-state__title {
  font-size: var(--unnnic-font-size-title-sm, 24px);
  font-weight: var(--unnnic-font-weight-bold, 600);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
  margin: 0 0 var(--unnnic-spacing-stack-sm, 12px) 0;
}

/* BEM: Element - description */
.canvas-empty-state__description {
  font-size: var(--unnnic-font-size-body-lg, 16px);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  max-width: 400px;
  line-height: 1.5;
  margin: 0 0 var(--unnnic-spacing-stack-lg, 24px) 0;
}

/* BEM: Element - suggestions */
.canvas-empty-state__suggestions {
  background: var(--unnnic-color-background-carpet, #f9f9f9);
  border-radius: var(--unnnic-border-radius-md, 12px);
  padding: var(--unnnic-spacing-stack-md, 20px);
  max-width: 320px;
}

/* BEM: Element - suggestions-label */
.canvas-empty-state__suggestions-label {
  font-size: var(--unnnic-font-size-body-sm, 13px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  margin: 0 0 var(--unnnic-spacing-stack-xs, 8px) 0;
}

/* BEM: Element - suggestions-list */
.canvas-empty-state__suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-xs, 8px);
}

.canvas-empty-state__suggestions-list li {
  font-size: var(--unnnic-font-size-body-md, 14px);
  color: var(--unnnic-color-neutral-dark, #4a4a4a);
  font-style: italic;
}

/* Responsive */
@media (width <= 768px) {
  .canvas-empty-state {
    padding: var(--unnnic-spacing-stack-lg, 32px);
    min-height: 300px;
  }

  .canvas-empty-state__title {
    font-size: var(--unnnic-font-size-title-xs, 20px);
  }

  .canvas-empty-state__description {
    font-size: var(--unnnic-font-size-body-md, 14px);
  }
}
</style>
