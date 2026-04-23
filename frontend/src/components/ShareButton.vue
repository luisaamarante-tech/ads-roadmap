<script setup lang="ts">
/**
 * ShareButton - Generate and copy shareable epic link.
 *
 * Provides button to copy shareable link to clipboard with visual feedback.
 * Includes fallback for browsers without Clipboard API support.
 */

import { ref, computed } from 'vue';
import { useClipboard } from '@/composables/useClipboard';

interface Props {
  epicId: string;
  size?: 'small' | 'medium' | 'large';
  variant?: 'primary' | 'secondary' | 'outlined' | 'ghost';
  customClass?: string;
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  variant: 'outlined',
  customClass: '',
});

interface Emits {
  (e: 'copied', url: string): void;
  (e: 'copyError', error: Error): void;
}

const emit = defineEmits<Emits>();

const showFallback = ref(false);
const fallbackInputRef = ref<HTMLInputElement | null>(null);

const { copy, isLoading, isCopied, error } = useClipboard({
  onSuccess: (url) => emit('copied', url),
  onError: (err) => emit('copyError', err),
});

const shareUrl = computed(() => {
  const origin = window.location.origin;
  return `${origin}/roadmap?epic=${props.epicId}`;
});

const buttonLabel = computed(() => {
  if (isCopied.value) return 'Copied!';
  if (error.value) return 'Failed';
  return 'Share';
});

const buttonIcon = computed(() => {
  if (isCopied.value) return 'check';
  if (error.value) return 'alert-circle';
  return 'share-2';
});

const isDisabled = computed(() => {
  return isLoading.value || !props.epicId || props.epicId.trim() === '';
});

async function onShareClick(): Promise<void> {
  const success = await copy(shareUrl.value);

  // Show fallback if copy failed (regardless of reason)
  if (!success) {
    showFallback.value = true;
  }
}

function onFallbackClose(): void {
  showFallback.value = false;
}
</script>

<template>
  <div class="share-button-wrapper">
    <button
      :class="[
        'share-button',
        `share-button--${size}`,
        `share-button--${variant}`,
        {
          'share-button--loading': isLoading,
          'share-button--copied': isCopied,
          'share-button--error': !!error,
        },
        customClass,
      ]"
      :disabled="isDisabled"
      :aria-label="`Share link to epic ${epicId}`"
      :aria-busy="isLoading"
      @click="onShareClick"
    >
      <svg
        class="share-button__icon"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        aria-hidden="true"
        style="flex-shrink: 0"
      >
        <!-- Share icon - 3 connected circles -->
        <g v-if="buttonIcon === 'share-2'">
          <circle cx="18" cy="6" r="3" stroke="currentColor" stroke-width="2" />
          <circle cx="6" cy="12" r="3" stroke="currentColor" stroke-width="2" />
          <circle
            cx="18"
            cy="18"
            r="3"
            stroke="currentColor"
            stroke-width="2"
          />
          <path
            d="M8.5 10.5L15.5 7.5M8.5 13.5L15.5 16.5"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          />
        </g>
        <!-- Check icon -->
        <path
          v-else-if="buttonIcon === 'check'"
          d="M5 13L9 17L19 7"
          stroke="currentColor"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <!-- Alert icon -->
        <g v-else>
          <circle
            cx="12"
            cy="12"
            r="9"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
          />
          <path d="M12 8V13" stroke="currentColor" stroke-width="2" />
          <circle cx="12" cy="16" r="1" fill="currentColor" />
        </g>
      </svg>
      <span class="share-button__label">{{ buttonLabel }}</span>
    </button>

    <!-- Fallback input for manual copy -->
    <div v-if="showFallback" class="share-button__fallback" role="dialog">
      <p class="share-button__fallback-text">Copy link manually:</p>
      <input
        ref="fallbackInputRef"
        :value="shareUrl"
        readonly
        class="share-button__fallback-input"
        aria-label="Shareable link"
        @focus="($event.target as HTMLInputElement).select()"
      />
      <button class="share-button__fallback-close" @click="onFallbackClose">
        Close
      </button>
    </div>
  </div>
</template>

<style scoped>
.share-button-wrapper {
  position: relative;
  display: inline-block;
}

/* Base button styles */
.share-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-sm, 6px);
  background: transparent;
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  font-size: var(--unnnic-font-size-body-md, 14px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  cursor: pointer;
  transition: all 0.2s ease;
}

.share-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.share-button:hover:not(:disabled) {
  border-color: #F71963;
  color: #dd1259;
  background: rgb(247 25 99 / 5%);
}

/* Size variants */
.share-button--small {
  padding: 4px 8px;
  font-size: var(--unnnic-font-size-body-sm, 12px);
}

.share-button--small .share-button__icon {
  width: 14px;
  height: 14px;
}

.share-button--large {
  padding: 12px 16px;
  font-size: var(--unnnic-font-size-body-lg, 16px);
}

.share-button--large .share-button__icon {
  width: 18px;
  height: 18px;
}

/* Style variants */
.share-button--primary {
  background: #dd1259;
  border-color: #dd1259;
  color: var(--unnnic-color-background-snow, #fff);
}

.share-button--primary:hover:not(:disabled) {
  background: #b80f4c;
  border-color: #b80f4c;
}

.share-button--secondary {
  background: var(--unnnic-color-neutral-light, #f5f5f5);
  border-color: var(--unnnic-color-neutral-soft, #e8e8e8);
  color: var(--unnnic-color-neutral-dark, #4a4a4a);
}

.share-button--ghost {
  border-color: transparent;
}

/* State modifiers */
.share-button--copied {
  border-color: var(--unnnic-color-feedback-green, #52c41a);
  color: var(--unnnic-color-feedback-green, #52c41a);
  background: rgb(82 196 26 / 10%);
}

.share-button--error {
  border-color: var(--unnnic-color-feedback-red, #ff4d4f);
  color: var(--unnnic-color-feedback-red, #ff4d4f);
  background: rgb(255 77 79 / 10%);
}

.share-button--loading .share-button__icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

/* Fallback */
.share-button__fallback {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  padding: 16px;
  background: var(--unnnic-color-background-snow, #fff);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-md, 8px);
  box-shadow: 0 4px 12px rgb(0 0 0 / 15%);
  z-index: 1000;
  min-width: 320px;
}

.share-button__fallback-text {
  margin: 0 0 8px;
  font-size: var(--unnnic-font-size-body-sm, 12px);
  color: var(--unnnic-color-neutral-dark, #4a4a4a);
}

.share-button__fallback-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-sm, 6px);
  font-size: var(--unnnic-font-size-body-sm, 12px);
  font-family: monospace;
  margin-bottom: 12px;
  background: var(--unnnic-color-background-carpet, #f8fafa);
}

.share-button__fallback-input:focus {
  outline: 2px solid #F71963;
  outline-offset: 2px;
}

.share-button__fallback-close {
  width: 100%;
  padding: 8px 16px;
  background: #dd1259;
  color: var(--unnnic-color-background-snow, #fff);
  border: none;
  border-radius: var(--unnnic-border-radius-sm, 6px);
  font-size: var(--unnnic-font-size-body-sm, 12px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  cursor: pointer;
  transition: background 0.2s ease;
}

.share-button__fallback-close:hover {
  background: #b80f4c;
}
</style>
