# Quickstart: Epic Viewer Enhancements Implementation

**Feature**: Epic Viewer Enhancements
**Branch**: `008-epic-viewer-enhancements`
**Prerequisites**: Vue 3.4+, TypeScript 5.3+, Unnnic Design System

## Overview

This guide provides step-by-step instructions for implementing image carousel and share functionality. Follow phases sequentially for organized development.

## Implementation Phases

### Phase 1: Composables (Foundation)

Create reusable logic for clipboard and keyboard operations.

#### 1.1 Create `useClipboard.ts`

**File**: `frontend/src/composables/useClipboard.ts`

```typescript
import { ref, readonly } from 'vue';

export interface UseClipboardOptions {
  onSuccess?: (text: string) => void;
  onError?: (error: Error) => void;
  copiedStateDuration?: number;
}

export interface UseClipboardReturn {
  copy: (text: string) => Promise<boolean>;
  isLoading: Readonly<Ref<boolean>>;
  isCopied: Readonly<Ref<boolean>>;
  error: Readonly<Ref<string | null>>;
  isSupported: Readonly<Ref<boolean>>;
}

/**
 * Composable for clipboard operations with fallback support.
 */
export function useClipboard(
  options: UseClipboardOptions = {}
): UseClipboardReturn {
  const { onSuccess, onError, copiedStateDuration = 2000 } = options;

  const isLoading = ref(false);
  const isCopied = ref(false);
  const error = ref<string | null>(null);
  
  const isSupported = ref(
    typeof navigator !== 'undefined' &&
      'clipboard' in navigator &&
      typeof navigator.clipboard.writeText === 'function'
  );

  let copiedTimeoutId: number | null = null;

  async function copy(text: string): Promise<boolean> {
    if (!text) {
      error.value = 'No text provided';
      return false;
    }

    isLoading.value = true;
    error.value = null;

    try {
      if (isSupported.value) {
        await navigator.clipboard.writeText(text);
      } else {
        throw new Error('Clipboard API not supported');
      }

      isCopied.value = true;
      onSuccess?.(text);

      // Reset copied state after duration
      if (copiedTimeoutId !== null) {
        clearTimeout(copiedTimeoutId);
      }
      copiedTimeoutId = window.setTimeout(() => {
        isCopied.value = false;
      }, copiedStateDuration);

      return true;
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error(String(err));
      error.value = errorObj.message;
      onError?.(errorObj);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    copy,
    isLoading: readonly(isLoading),
    isCopied: readonly(isCopied),
    error: readonly(error),
    isSupported: readonly(isSupported),
  };
}
```

**Tests**: `frontend/tests/composables/useClipboard.spec.ts`

```typescript
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useClipboard } from '@/composables/useClipboard';

describe('useClipboard', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should copy text successfully', async () => {
    const { copy, isCopied } = useClipboard();
    const result = await copy('test text');

    expect(result).toBe(true);
    expect(isCopied.value).toBe(true);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('test text');
  });

  it('should handle clipboard API not supported', async () => {
    Object.assign(navigator, { clipboard: undefined });
    const { copy, error, isSupported } = useClipboard();

    expect(isSupported.value).toBe(false);
    const result = await copy('test');
    expect(result).toBe(false);
    expect(error.value).toBeTruthy();
  });

  it('should reset copied state after duration', async () => {
    vi.useFakeTimers();
    const { copy, isCopied } = useClipboard({ copiedStateDuration: 1000 });

    await copy('test');
    expect(isCopied.value).toBe(true);

    vi.advanceTimersByTime(1000);
    expect(isCopied.value).toBe(false);

    vi.useRealTimers();
  });

  it('should call onSuccess callback', async () => {
    const onSuccess = vi.fn();
    const { copy } = useClipboard({ onSuccess });

    await copy('test');
    expect(onSuccess).toHaveBeenCalledWith('test');
  });

  it('should call onError callback on failure', async () => {
    const onError = vi.fn();
    navigator.clipboard.writeText = vi
      .fn()
      .mockRejectedValue(new Error('Permission denied'));

    const { copy } = useClipboard({ onError });
    await copy('test');

    expect(onError).toHaveBeenCalled();
  });
});
```

#### 1.2 Create `useKeyboardNavigation.ts`

**File**: `frontend/src/composables/useKeyboardNavigation.ts`

```typescript
import { onMounted, onUnmounted, type Ref } from 'vue';

export interface UseKeyboardNavigationCallbacks {
  onEscape?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  onHome?: () => void;
  onEnd?: () => void;
}

export interface UseKeyboardNavigationOptions {
  isActive?: Ref<boolean>;
  preventDefault?: boolean;
}

/**
 * Composable for keyboard event handling in modals.
 */
export function useKeyboardNavigation(
  callbacks: UseKeyboardNavigationCallbacks,
  options: UseKeyboardNavigationOptions = {}
): void {
  const { isActive, preventDefault = true } = options;

  function handleKeydown(event: KeyboardEvent): void {
    // Check if navigation is active
    if (isActive && !isActive.value) {
      return;
    }

    const handlers: Record<string, (() => void) | undefined> = {
      Escape: callbacks.onEscape,
      ArrowLeft: callbacks.onArrowLeft,
      ArrowRight: callbacks.onArrowRight,
      Home: callbacks.onHome,
      End: callbacks.onEnd,
    };

    const handler = handlers[event.key];
    if (handler) {
      if (preventDefault) {
        event.preventDefault();
      }
      handler();
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
  });

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
  });
}
```

**Tests**: `frontend/tests/composables/useKeyboardNavigation.spec.ts`

```typescript
import { describe, it, expect, vi } from 'vitest';
import { ref } from 'vue';
import { mount } from '@vue/test-utils';
import { useKeyboardNavigation } from '@/composables/useKeyboardNavigation';

describe('useKeyboardNavigation', () => {
  it('should call onEscape when Escape key pressed', () => {
    const onEscape = vi.fn();

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onEscape });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'Escape' });
    window.dispatchEvent(event);

    expect(onEscape).toHaveBeenCalled();
  });

  it('should call onArrowLeft when ArrowLeft key pressed', () => {
    const onArrowLeft = vi.fn();

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onArrowLeft });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
    window.dispatchEvent(event);

    expect(onArrowLeft).toHaveBeenCalled();
  });

  it('should not call handlers when isActive is false', () => {
    const onEscape = vi.fn();
    const isActive = ref(false);

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onEscape }, { isActive });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'Escape' });
    window.dispatchEvent(event);

    expect(onEscape).not.toHaveBeenCalled();
  });

  it('should call handlers when isActive becomes true', () => {
    const onEscape = vi.fn();
    const isActive = ref(false);

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onEscape }, { isActive });
        return () => null;
      },
    };

    mount(TestComponent);

    isActive.value = true;

    const event = new KeyboardEvent('keydown', { key: 'Escape' });
    window.dispatchEvent(event);

    expect(onEscape).toHaveBeenCalled();
  });
});
```

---

### Phase 2: ShareButton Component

Simple component with minimal dependencies - good starting point.

#### 2.1 Create ShareButton Component

**File**: `frontend/src/components/ShareButton.vue`

```vue
<script setup lang="ts">
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

const { copy, isLoading, isCopied, error, isSupported } = useClipboard({
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

  if (!success && !isSupported.value) {
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
        viewBox="0 0 16 16"
        fill="none"
        aria-hidden="true"
      >
        <!-- Share icon -->
        <path
          v-if="buttonIcon === 'share-2'"
          d="M12 5L12 2L16 6L12 10L12 7C8 7 5 9 3 12C4 8 6 4 12 4V5Z"
          stroke="currentColor"
          stroke-width="1.5"
        />
        <!-- Check icon -->
        <path
          v-else-if="buttonIcon === 'check'"
          d="M3 8L6 11L13 4"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
        />
        <!-- Alert icon -->
        <circle
          v-else
          cx="8"
          cy="8"
          r="7"
          stroke="currentColor"
          stroke-width="1.5"
        />
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
        @focus="($event.target as HTMLInputElement).select()"
      />
      <button class="share-button__fallback-close" @click="onFallbackClose">
        Close
      </button>
    </div>
  </div>
</template>

<style scoped>
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

.share-button:hover:not(:disabled) {
  border-color: var(--unnnic-color-weni-500, #00bfbf);
  color: var(--unnnic-color-weni-600, #00a8a8);
}

.share-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Size variants */
.share-button--small {
  padding: 4px 8px;
  font-size: var(--unnnic-font-size-body-sm, 12px);
}

.share-button--large {
  padding: 12px 16px;
  font-size: var(--unnnic-font-size-body-lg, 16px);
}

/* Style variants */
.share-button--primary {
  background: var(--unnnic-color-weni-600, #00a8a8);
  border-color: var(--unnnic-color-weni-600, #00a8a8);
  color: var(--unnnic-color-background-snow, #fff);
}

.share-button--ghost {
  border-color: transparent;
}

/* State modifiers */
.share-button--copied {
  border-color: var(--unnnic-color-feedback-green, #52c41a);
  color: var(--unnnic-color-feedback-green, #52c41a);
}

.share-button--error {
  border-color: var(--unnnic-color-feedback-red, #ff4d4f);
  color: var(--unnnic-color-feedback-red, #ff4d4f);
}

/* Fallback */
.share-button__fallback {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  padding: 12px;
  background: var(--unnnic-color-background-snow, #fff);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-md, 8px);
  box-shadow: 0 4px 12px rgb(0 0 0 / 10%);
  z-index: 1000;
}

.share-button__fallback-input {
  width: 300px;
  padding: 8px;
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-sm, 6px);
  font-size: var(--unnnic-font-size-body-sm, 12px);
  margin: 8px 0;
}

.share-button__fallback-close {
  padding: 6px 12px;
  background: var(--unnnic-color-weni-600, #00a8a8);
  color: white;
  border: none;
  border-radius: var(--unnnic-border-radius-sm, 6px);
  cursor: pointer;
}
</style>
```

#### 2.2 Add ShareButton Tests

**File**: `frontend/tests/components/ShareButton.spec.ts`

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import ShareButton from '@/components/ShareButton.vue';

describe('ShareButton', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
    
    Object.assign(window, {
      location: { origin: 'https://roadmap.weni.ai' },
    });
  });

  it('should render button with default props', () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123' },
    });

    expect(wrapper.find('.share-button').exists()).toBe(true);
    expect(wrapper.text()).toContain('Share');
  });

  it('should generate correct share URL', async () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-456' },
    });

    await wrapper.find('.share-button').trigger('click');

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      'https://roadmap.weni.ai/roadmap?epic=WENI-456'
    );
  });

  it('should emit copied event on success', async () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-789' },
    });

    await wrapper.find('.share-button').trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.emitted('copied')).toBeTruthy();
    expect(wrapper.emitted('copied')![0]).toEqual([
      'https://roadmap.weni.ai/roadmap?epic=WENI-789',
    ]);
  });

  it('should show "Copied!" state after successful copy', async () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123' },
    });

    await wrapper.find('.share-button').trigger('click');
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain('Copied!');
    expect(wrapper.find('.share-button--copied').exists()).toBe(true);
  });

  it('should disable button when epicId is empty', () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: '' },
    });

    const button = wrapper.find('.share-button');
    expect(button.attributes('disabled')).toBeDefined();
  });
});
```

---

### Phase 3: ImageCarouselModal Component

More complex component with navigation and keyboard handling.

#### 3.1 Create ImageCarouselModal Component

**File**: `frontend/src/components/ImageCarouselModal.vue`

```vue
<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useKeyboardNavigation } from '@/composables/useKeyboardNavigation';

interface Props {
  images: string[];
  currentIndex: number;
  epicTitle: string;
  show: boolean;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'close'): void;
  (e: 'indexChange', newIndex: number): void;
}

const emit = defineEmits<Emits>();

const localIndex = ref(props.currentIndex);
const imageLoadingStates = ref<Record<number, 'loading' | 'loaded' | 'error'>>(
  {}
);

const currentImage = computed(() => props.images[localIndex.value]);

const positionLabel = computed(() => {
  if (props.images.length <= 1) return '';
  return `${localIndex.value + 1} of ${props.images.length}`;
});

const showNavigation = computed(() => props.images.length > 1);

const currentImageState = computed(
  () => imageLoadingStates.value[localIndex.value] || 'loading'
);

function navigateNext(): void {
  if (!showNavigation.value) return;

  const nextIndex = (localIndex.value + 1) % props.images.length;
  localIndex.value = nextIndex;
  emit('indexChange', nextIndex);
}

function navigatePrev(): void {
  if (!showNavigation.value) return;

  const prevIndex =
    (localIndex.value - 1 + props.images.length) % props.images.length;
  localIndex.value = prevIndex;
  emit('indexChange', prevIndex);
}

function onClose(): void {
  emit('close');
}

function onImageLoad(index: number): void {
  imageLoadingStates.value[index] = 'loaded';
}

function onImageError(index: number): void {
  imageLoadingStates.value[index] = 'error';
}

// Keyboard navigation
useKeyboardNavigation(
  {
    onEscape: onClose,
    onArrowLeft: navigatePrev,
    onArrowRight: navigateNext,
  },
  {
    isActive: computed(() => props.show),
  }
);

// Reset loading state when index changes
watch(localIndex, (newIndex) => {
  if (!imageLoadingStates.value[newIndex]) {
    imageLoadingStates.value[newIndex] = 'loading';
  }
});

// Sync with props
watch(() => props.currentIndex, (newIndex) => {
  localIndex.value = newIndex;
});
</script>

<template>
  <Teleport to="body">
    <Transition name="image-carousel-modal">
      <div
        v-if="show"
        class="image-carousel-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <!-- Backdrop -->
        <div class="image-carousel-modal__backdrop" @click="onClose"></div>

        <!-- Modal container -->
        <div class="image-carousel-modal__container">
          <!-- Hidden title for screen readers -->
          <h2 id="modal-title" class="sr-only">{{ epicTitle }} - Images</h2>

          <!-- Close button -->
          <button
            class="image-carousel-modal__close-btn"
            aria-label="Close image viewer"
            @click="onClose"
          >
            ✕
          </button>

          <!-- Image display -->
          <div class="image-carousel-modal__image-wrapper">
            <div
              v-if="currentImageState === 'loading'"
              class="image-carousel-modal__loading"
            >
              Loading...
            </div>

            <div
              v-else-if="currentImageState === 'error'"
              class="image-carousel-modal__error"
            >
              <p>Failed to load image</p>
              <p>{{ epicTitle }} - Image {{ localIndex + 1 }}</p>
            </div>

            <img
              v-else
              :src="currentImage"
              :alt="`${epicTitle} - Image ${localIndex + 1}`"
              class="image-carousel-modal__image"
              @load="onImageLoad(localIndex)"
              @error="onImageError(localIndex)"
            />
          </div>

          <!-- Navigation -->
          <div v-if="showNavigation" class="image-carousel-modal__navigation">
            <button
              class="image-carousel-modal__nav-btn image-carousel-modal__nav-btn--prev"
              aria-label="Previous image"
              @click="navigatePrev"
            >
              ←
            </button>

            <span class="image-carousel-modal__position">
              {{ positionLabel }}
            </span>

            <button
              class="image-carousel-modal__nav-btn image-carousel-modal__nav-btn--next"
              aria-label="Next image"
              @click="navigateNext"
            >
              →
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.image-carousel-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-carousel-modal__backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgb(0 0 0 / 85%);
}

.image-carousel-modal__container {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  z-index: 1;
}

.image-carousel-modal__close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  background: var(--unnnic-color-background-snow, #fff);
  border: none;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  z-index: 2;
}

.image-carousel-modal__image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.image-carousel-modal__image {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
}

.image-carousel-modal__loading,
.image-carousel-modal__error {
  color: white;
  text-align: center;
  padding: 40px;
}

.image-carousel-modal__navigation {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgb(0 0 0 / 60%);
  padding: 12px 20px;
  border-radius: 24px;
}

.image-carousel-modal__nav-btn {
  width: 40px;
  height: 40px;
  background: var(--unnnic-color-background-snow, #fff);
  border: none;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
}

.image-carousel-modal__position {
  color: white;
  font-size: 14px;
  min-width: 60px;
  text-align: center;
}

/* Transitions */
.image-carousel-modal-enter-active,
.image-carousel-modal-leave-active {
  transition: opacity 0.3s ease;
}

.image-carousel-modal-enter-from,
.image-carousel-modal-leave-to {
  opacity: 0;
}
</style>
```

See contracts for full tests specification.

---

### Phase 4: Integrate into RoadmapCard

Modify existing component to add share button and image modal.

#### 4.1 Update RoadmapCard.vue

**File**: `frontend/src/components/RoadmapCard.vue`

Add to script setup (after existing code):

```typescript
import ImageCarouselModal from '@/components/ImageCarouselModal.vue';
import ShareButton from '@/components/ShareButton.vue';

// New state for image modal
const showImageModal = ref(false);
const clickedImageIndex = ref(0);

// Event handlers
function onImageClick(index: number): void {
  clickedImageIndex.value = index;
  showImageModal.value = true;
}

function onModalClose(): void {
  showImageModal.value = false;
}

// Expose for URL navigation
defineExpose({
  isExpanded,
});
```

Update template - add share button in header:

```vue
<header class="roadmap-card__header">
  <div class="roadmap-card__main">
    <h3 class="roadmap-card__title">{{ item.title }}</h3>
    <div class="roadmap-card__meta">
      <span class="roadmap-card__badge">{{ item.module }}</span>
      <span class="roadmap-card__release">{{ releaseInfo }}</span>
      <!-- Like button (existing) -->
      <button ...>...</button>
      
      <!-- NEW: Share button -->
      <ShareButton
        :epic-id="item.id"
        size="small"
        variant="ghost"
        @click.stop
      />
    </div>
  </div>
  <!-- ... expand button ... -->
</header>
```

Update template - make images clickable and add modal:

```vue
<!-- In expanded content -->
<div v-if="hasImages" class="roadmap-card__images">
  <div class="roadmap-card__images-grid">
    <img
      v-for="(imageUrl, index) in item.images"
      :key="index"
      :src="imageUrl"
      :alt="`${item.title} - Image ${index + 1}`"
      class="roadmap-card__image"
      loading="lazy"
      @click="onImageClick(index)"
    />
  </div>
</div>

<!-- NEW: Image carousel modal -->
<ImageCarouselModal
  :images="item.images || []"
  :current-index="clickedImageIndex"
  :epic-title="item.title"
  :show="showImageModal"
  @close="onModalClose"
/>
```

Add CSS for clickable images:

```css
.roadmap-card__image {
  /* ... existing styles ... */
  cursor: pointer;
  transition: transform 0.2s ease;
}

.roadmap-card__image:hover {
  transform: scale(1.05);
}
```

#### 4.2 Update RoadmapCard Tests

**File**: `frontend/tests/components/RoadmapCard.spec.ts`

Add tests:

```typescript
describe('RoadmapCard - Image Modal', () => {
  it('should open image modal when clicking image', async () => {
    const wrapper = mount(RoadmapCard, {
      props: {
        item: {
          ...mockItem,
          images: ['https://example.com/image1.png'],
        },
      },
    });

    await wrapper.find('.roadmap-card__expand-btn').trigger('click');
    await wrapper.find('.roadmap-card__image').trigger('click');

    expect(wrapper.vm.showImageModal).toBe(true);
  });

  it('should render share button', () => {
    const wrapper = mount(RoadmapCard, {
      props: { item: mockItem },
      global: {
        stubs: { ShareButton: true },
      },
    });

    expect(wrapper.findComponent({ name: 'ShareButton' }).exists()).toBe(true);
  });
});
```

---

### Phase 5: Handle Shared Epic Links in RoadmapView

Final integration for URL-based epic navigation.

#### 5.1 Update RoadmapView.vue

**File**: `frontend/src/views/RoadmapView.vue`

Add to script setup:

```typescript
// New state for shared epic handling
const sharedEpicId = ref<string | null>(null);
const isProcessingSharedEpic = ref(false);
const cardListRef = ref<InstanceType<typeof RoadmapCardList> | null>(null);

// Handle shared epic link
async function handleSharedEpicLink(): Promise<void> {
  const epicId = route.query.epic;

  if (!epicId || typeof epicId !== 'string') {
    return;
  }

  isProcessingSharedEpic.value = true;
  sharedEpicId.value = epicId;

  try {
    // Clear filters
    filters.value = {};

    // Fetch all items
    await handleFetchItems();

    // Find and expand epic
    const found = expandEpicById(epicId);

    if (!found) {
      error.value = `Epic ${epicId} not found or no longer available.`;
    }
  } catch (e) {
    console.error('Failed to process shared epic link:', e);
    error.value = 'Failed to load shared epic.';
  } finally {
    // Clean up
    router.replace({ query: {} });
    sharedEpicId.value = null;
    isProcessingSharedEpic.value = false;
  }
}

function expandEpicById(epicId: string): boolean {
  // Implementation depends on RoadmapCardList exposing card refs
  // See URLParameters contract for full implementation
  return false; // Placeholder
}

// Update onMounted
onMounted(async () => {
  if (route.query.epic) {
    await handleSharedEpicLink();
    return;
  }

  parseFiltersFromURL();
  handleFetchItems();
  handleFetchStats();
  handleFetchModules();
});
```

---

## Testing Strategy

### Run Tests Individually

```bash
# Composables
npm test tests/composables/useClipboard.spec.ts
npm test tests/composables/useKeyboardNavigation.spec.ts

# Components
npm test tests/components/ShareButton.spec.ts
npm test tests/components/ImageCarouselModal.spec.ts
npm test tests/components/RoadmapCard.spec.ts

# View
npm test tests/views/RoadmapView.spec.ts
```

### Coverage Check

```bash
npm run test:coverage

# Verify all metrics ≥80%
# - Statements: 80%
# - Branches: 80%
# - Functions: 80%
# - Lines: 80%
```

---

## Pre-Commit Checklist

- [ ] Run formatters: `npm run format`
- [ ] Fix linting: `npm run lint -- --fix`
- [ ] Check linting: `npm run lint:check`
- [ ] Check styles: `npm run stylelint:check`
- [ ] Run tests: `npm test`
- [ ] Verify 80% coverage: `npm run test:coverage`
- [ ] Manual testing in browser

---

## Manual Testing Checklist

### Image Carousel
- [ ] Click image to open modal
- [ ] Navigate with arrow buttons
- [ ] Navigate with keyboard (Left/Right arrows)
- [ ] Close with ESC key
- [ ] Close with backdrop click
- [ ] Close with X button
- [ ] Test with single image (no arrows shown)
- [ ] Test with broken image URL

### Share Button
- [ ] Click share button
- [ ] Verify "Copied!" appears
- [ ] Paste URL in browser
- [ ] Verify URL format correct
- [ ] Test permission denied (disable clipboard in dev tools)
- [ ] Verify fallback input appears

### Shared Epic Links
- [ ] Open `/roadmap?epic=VALID-ID` in new tab
- [ ] Verify epic expands automatically
- [ ] Verify filters are cleared
- [ ] Verify URL cleans to `/roadmap`
- [ ] Test invalid epic ID
- [ ] Test with existing filters active

---

## Deployment Notes

- No backend changes required
- No database migrations
- No environment variables needed
- Frontend assets only
- Compatible with existing infrastructure
