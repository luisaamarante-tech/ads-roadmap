<script setup lang="ts">
/**
 * CanvasExitButton - Exit button for canvas search mode.
 *
 * Provide a clear way for users to exit canvas mode
 * and return to the normal roadmap view.
 */

const emit = defineEmits<{
  click: [];
}>();

function onClick(): void {
  emit('click');
}
</script>

<template>
  <button
    type="button"
    class="canvas-exit-button"
    aria-label="Exit canvas search mode"
    @click="onClick"
  >
    <svg
      class="canvas-exit-button__icon"
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M15 5L5 15M5 5L15 15"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    <span class="canvas-exit-button__text">Exit Search</span>
  </button>
</template>

<style scoped>
/* BEM: Block - canvas-exit-button */
.canvas-exit-button {
  display: flex;
  align-items: center;
  gap: var(--unnnic-spacing-inline-xs, 8px);
  padding: var(--unnnic-spacing-stack-xs, 8px)
    var(--unnnic-spacing-inline-sm, 16px);
  font-size: var(--unnnic-font-size-body-md, 14px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  background: transparent;
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-sm, 8px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.canvas-exit-button:hover {
  color: var(--unnnic-color-neutral-black, #1a1a1a);
  background: var(--unnnic-color-neutral-light, #f5f5f5);
  border-color: var(--unnnic-color-neutral-cleanest, #d0d3d9);
}

.canvas-exit-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgb(247 25 99 / 15%);
  border-color: #F71963;
}

.canvas-exit-button:active {
  transform: scale(0.98);
}

/* BEM: Element - icon */
.canvas-exit-button__icon {
  flex-shrink: 0;
}

/* BEM: Element - text */
.canvas-exit-button__text {
  white-space: nowrap;
}

/* Responsive */
@media (width <= 768px) {
  .canvas-exit-button__text {
    display: none;
  }

  .canvas-exit-button {
    padding: var(--unnnic-spacing-stack-xs, 8px);
  }
}
</style>
