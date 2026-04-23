<script setup lang="ts">
/**
 * ImageCarouselModal - Modal for viewing enlarged epic images with navigation.
 *
 * Displays images in full-screen modal overlay with keyboard and mouse navigation.
 * Supports loading states, error handling, and accessibility features.
 */

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

const currentImage = computed(() => props.images[localIndex.value]);

const positionLabel = computed(() => {
  if (props.images.length <= 1) return '';
  return `${localIndex.value + 1} of ${props.images.length}`;
});

const showNavigation = computed(() => props.images.length > 1);

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

// Keyboard navigation
useKeyboardNavigation(
  {
    onEscape: onClose,
    onArrowLeft: navigatePrev,
    onArrowRight: navigateNext,
  },
  {
    isActive: computed(() => props.show),
  },
);

// Sync with props
watch(
  () => props.currentIndex,
  (newIndex) => {
    localIndex.value = newIndex;
  },
);
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
            <img
              :src="currentImage"
              :alt="`${epicTitle} - Image ${localIndex + 1}`"
              class="image-carousel-modal__image"
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
  clip-path: inset(50%);
  white-space: nowrap;
  border-width: 0;
}

.image-carousel-modal {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-carousel-modal__backdrop {
  position: absolute;
  inset: 0;
  background: rgb(0 0 0 / 85%);
  cursor: pointer;
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
  line-height: 1;
  cursor: pointer;
  z-index: 2;
  color: var(--unnnic-color-neutral-dark, #4a4a4a);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-carousel-modal__close-btn:hover {
  background: var(--unnnic-color-neutral-soft, #e8e8e8);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
}

.image-carousel-modal__image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  position: relative;
}

.image-carousel-modal__image {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
  border-radius: var(--unnnic-border-radius-sm, 8px);
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
  backdrop-filter: blur(8px);
}

.image-carousel-modal__nav-btn {
  width: 40px;
  height: 40px;
  background: var(--unnnic-color-background-snow, #fff);
  border: none;
  border-radius: 50%;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--unnnic-color-neutral-dark, #4a4a4a);
  transition: all 0.2s ease;
}

.image-carousel-modal__nav-btn:hover {
  background: #ffe0ef;
  color: #dd1259;
}

.image-carousel-modal__position {
  color: white;
  font-size: var(--unnnic-font-size-body-md, 14px);
  font-weight: var(--unnnic-font-weight-medium, 500);
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

/* Responsive */
@media (width <= 640px) {
  .image-carousel-modal__container {
    max-width: 95vw;
    max-height: 95vh;
  }

  .image-carousel-modal__close-btn {
    top: 8px;
    right: 8px;
    width: 36px;
    height: 36px;
    font-size: 20px;
  }

  .image-carousel-modal__navigation {
    bottom: 16px;
    padding: 8px 16px;
    gap: 12px;
  }

  .image-carousel-modal__nav-btn {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }

  .image-carousel-modal__position {
    font-size: var(--unnnic-font-size-body-sm, 12px);
    min-width: 50px;
  }
}
</style>
