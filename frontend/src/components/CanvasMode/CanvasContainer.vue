<script setup lang="ts">
/**
 * CanvasContainer - Main layout container for canvas search mode.
 *
 * Provide a split-panel layout with WebChat on the left (40%)
 * and search results on the right (60%).
 *
 * Uses WebChat's embedded mode for proper inline integration.
 */

import { computed } from 'vue';
import type { RoadmapItem } from '@/types/roadmap';
import CanvasEmptyState from './CanvasEmptyState.vue';
import CanvasSearchResults from './CanvasSearchResults.vue';
import CanvasExitButton from './CanvasExitButton.vue';

interface Props {
  /** IDs of roadmap items to display */
  filteredItemIds: string[];
  /** All roadmap items (for filtering) */
  allItems: RoadmapItem[];
  /** Loading state */
  loading?: boolean;
  /** WebChat container element ID */
  webchatContainerId?: string;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  webchatContainerId: 'weni-webchat-canvas',
});

const emit = defineEmits<{
  exit: [];
}>();

// Computed: Filter items based on IDs
const filteredItems = computed(() => {
  if (props.filteredItemIds.length === 0) {
    return [];
  }

  return props.allItems.filter((item) =>
    props.filteredItemIds.includes(item.id),
  );
});

// Computed: Show states
const hasResults = computed(() => filteredItems.value.length > 0);
const hasSearchedButNoResults = computed(
  () => props.filteredItemIds.length > 0 && filteredItems.value.length === 0,
);
const showEmptyState = computed(
  () => !hasResults.value || hasSearchedButNoResults.value,
);

// Event handlers
function onExitClick(): void {
  emit('exit');
}
</script>

<template>
  <div class="canvas-container">
    <!-- Header with exit button -->
    <header class="canvas-container__header">
      <div class="canvas-container__header-content">
        <h1 class="canvas-container__title">AI Search</h1>
        <p class="canvas-container__subtitle">
          Ask questions to discover roadmap items
        </p>
      </div>
      <CanvasExitButton @click="onExitClick" />
    </header>

    <!-- Main content area -->
    <div class="canvas-container__content">
      <!-- Left panel: WebChat container (embedded mode) -->
      <aside class="canvas-container__left-panel" aria-label="Chat panel">
        <div class="canvas-container__webchat-wrapper">
          <!-- WebChat will be initialized here in embedded mode -->
          <div :id="webchatContainerId" class="canvas-container__webchat" />
        </div>
      </aside>

      <!-- Right panel: Search results -->
      <main class="canvas-container__right-panel" aria-label="Search results">
        <!-- Empty state (no results yet or no matches) -->
        <Transition name="canvas-panel-fade" mode="out-in">
          <CanvasEmptyState
            v-if="showEmptyState"
            key="empty"
            :no-results="hasSearchedButNoResults"
            :searching="loading"
          />

          <!-- Search results -->
          <CanvasSearchResults
            v-else
            key="results"
            :items="filteredItems"
            :loading="loading"
          />
        </Transition>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* BEM: Block - canvas-container */
.canvas-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--unnnic-color-background-snow, #fff);

  /* Animation handled by Vue Transition in parent */
}

/* BEM: Element - header */
.canvas-container__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--unnnic-spacing-stack-md, 16px)
    var(--unnnic-spacing-inline-lg, 24px);
  border-bottom: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  background: var(--unnnic-color-background-snow, #fff);
}

/* BEM: Element - header-content */
.canvas-container__header-content {
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-nano, 4px);
}

/* BEM: Element - title */
.canvas-container__title {
  font-size: var(--unnnic-font-size-title-sm, 20px);
  font-weight: var(--unnnic-font-weight-bold, 600);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
  margin: 0;
}

/* BEM: Element - subtitle */
.canvas-container__subtitle {
  font-size: var(--unnnic-font-size-body-sm, 13px);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  margin: 0;
}

/* BEM: Element - content */
.canvas-container__content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* BEM: Element - left-panel */
.canvas-container__left-panel {
  width: 40%;
  min-width: 320px;
  max-width: 500px;
  border-right: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  background: var(--unnnic-color-background-carpet, #f9f9f9);
  display: flex;
  flex-direction: column;
  position: relative;
}

/* BEM: Element - webchat-wrapper */
.canvas-container__webchat-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
}

/* BEM: Element - webchat (container for embedded WebChat) */
.canvas-container__webchat {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: 0;
  width: 100%;
}

/* BEM: Element - right-panel */
.canvas-container__right-panel {
  flex: 1;
  overflow-y: auto;
  padding: var(--unnnic-spacing-stack-lg, 24px);
  background: var(--unnnic-color-background-snow, #fff);
  position: relative;
}

/* Transition for panel content switching */
.canvas-panel-fade-enter-active,
.canvas-panel-fade-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.canvas-panel-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.canvas-panel-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Responsive */
@media (width <= 1024px) {
  .canvas-container__left-panel {
    width: 45%;
    min-width: 280px;
  }
}

@media (width <= 768px) {
  .canvas-container__content {
    flex-direction: column;
  }

  .canvas-container__left-panel {
    width: 100%;
    max-width: none;
    height: 50%;
    border-right: none;
    border-bottom: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  }

  .canvas-container__right-panel {
    height: 50%;
    padding: var(--unnnic-spacing-stack-md, 16px);
  }
}
</style>

<!-- Global styles to constrain WebChat within its container -->
<style>
/* stylelint-disable selector-class-pattern, no-descending-specificity */

/*
 * Canvas WebChat Embedded Styles
 * ==============================
 * The vendor widget uses position:fixed internally.
 * We must override this to make it flow within our container.
 * Also hides header and "Powered by" footer for cleaner integration.
 */

/* Main container - establish positioning context */
#weni-webchat-canvas {
  position: relative !important;
  display: flex !important;
  flex-direction: column !important;
  width: 100% !important;
  height: 100% !important;
  min-height: 0 !important;
  overflow: hidden !important;
}

/* Widget aside wrapper */
#weni-webchat-canvas > aside.weni-widget {
  position: relative !important;
  display: flex !important;
  flex-direction: column !important;
  flex: 1 1 auto !important;
  width: 100% !important;
  height: 100% !important;
  min-height: 0 !important;
  max-width: none !important;
  max-height: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
  border: none !important;
  overflow: hidden !important;
}

/* CRITICAL: Override the fixed positioning on .weni-chat */
#weni-webchat-canvas .weni-chat {
  position: relative !important;
  inset: auto !important;
  display: flex !important;
  flex-direction: column !important;
  flex: 1 1 auto !important;
  width: 100% !important;
  height: 100% !important;
  min-height: 0 !important;
  max-width: none !important;
  max-height: none !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

/* HIDE: Chat header (we have our own header) */
#weni-webchat-canvas .weni-chat-header {
  display: none !important;
}

/* Messages container - fill remaining space (high specificity) */
#weni-webchat-canvas .weni-chat .weni-messages-list,
#weni-webchat-canvas section.weni-messages-list,
section.weni-messages-list {
  flex: 1 1 auto !important;
  min-height: 0 !important;
  overflow: hidden auto !important;
  position: relative !important;
  height: auto !important;
}

/* Messages inner content - natural height */
#weni-webchat-canvas .weni-message,
#weni-webchat-canvas .weni-message-text,
#weni-webchat-canvas [class*='weni-message'] {
  flex: 0 0 auto !important;
  height: auto !important;
}

/* Message sections - natural content */
#weni-webchat-canvas .weni-message section,
#weni-webchat-canvas .weni-message-text section {
  height: auto !important;
  flex: none !important;
}

/* Chat footer (input area) - natural height at bottom with spacing */
#weni-webchat-canvas .weni-chat__footer {
  flex: 0 0 auto !important;
  position: relative !important;
  background: #fff !important;
  padding-bottom: 16px !important;
}

/* HIDE: "Powered by Weni by VTEX" branding */
#weni-webchat-canvas .weni-poweredby,
#weni-webchat-canvas [class*='poweredby'],
#weni-webchat-canvas a[href*='weni.ai'] {
  display: none !important;
}

/* Hide any floating launcher buttons */
#weni-webchat-canvas [class*='launcher'],
#weni-webchat-canvas .weni-launcher__container {
  display: none !important;
}

/* stylelint-enable selector-class-pattern, no-descending-specificity */
</style>
