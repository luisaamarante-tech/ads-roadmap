<script setup lang="ts">
/**
 * MagicSearchBar - A beautiful search bar with magical sparkle animations.
 *
 * When user submits a query, it triggers a magical transition with
 * sparkling stars before opening the canvas mode.
 */

import { ref, onMounted, onUnmounted } from 'vue';

interface Props {
  placeholder?: string;
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Ask me anything about our roadmap...',
  disabled: false,
});

const emit = defineEmits<{
  search: [query: string];
}>();

const query = ref('');
const isFocused = ref(false);
const isAnimating = ref(false);
const sparkles = ref<
  { id: number; x: number; y: number; size: number; delay: number }[]
>([]);
const searchBarRef = ref<HTMLElement | null>(null);

let sparkleId = 0;

function createSparkle(x: number, y: number): void {
  const id = sparkleId++;
  const size = Math.random() * 8 + 4;
  const delay = Math.random() * 0.3;

  sparkles.value.push({ id, x, y, size, delay });

  setTimeout(() => {
    sparkles.value = sparkles.value.filter((s) => s.id !== id);
  }, 600);
}

function createSparklesBurst(): void {
  if (!searchBarRef.value) return;

  const rect = searchBarRef.value.getBoundingClientRect();
  const centerX = rect.width / 2;
  const centerY = rect.height / 2;

  // Create a burst of sparkles around the search bar (faster)
  for (let i = 0; i < 20; i++) {
    setTimeout(() => {
      const angle = (i / 20) * Math.PI * 2;
      const distance = Math.random() * 120 + 40;
      const x = centerX + Math.cos(angle) * distance;
      const y = centerY + Math.sin(angle) * distance;
      createSparkle(x, y);
    }, i * 8);
  }
}

function handleSubmit(): void {
  if (!query.value.trim() || props.disabled || isAnimating.value) return;

  isAnimating.value = true;
  createSparklesBurst();

  // Quick transition - emit almost immediately for snappy feel
  setTimeout(() => {
    emit('search', query.value.trim());
    query.value = '';
    isAnimating.value = false;
  }, 200);
}

function handleKeydown(e: KeyboardEvent): void {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSubmit();
  }
}

// Create occasional sparkles when focused
let sparkleInterval: ReturnType<typeof setInterval> | null = null;

function startIdleSparkles(): void {
  if (sparkleInterval) return;
  sparkleInterval = setInterval(() => {
    if (isFocused.value && searchBarRef.value && !isAnimating.value) {
      const rect = searchBarRef.value.getBoundingClientRect();
      const x = Math.random() * rect.width;
      const y = Math.random() * rect.height;
      if (Math.random() > 0.7) {
        createSparkle(x, y);
      }
    }
  }, 300);
}

function stopIdleSparkles(): void {
  if (sparkleInterval) {
    clearInterval(sparkleInterval);
    sparkleInterval = null;
  }
}

onMounted(() => {
  startIdleSparkles();
});

onUnmounted(() => {
  stopIdleSparkles();
});
</script>

<template>
  <div
    ref="searchBarRef"
    :class="[
      'magic-search',
      {
        'magic-search--focused': isFocused,
        'magic-search--animating': isAnimating,
        'magic-search--disabled': disabled,
      },
    ]"
  >
    <!-- Sparkles container -->
    <div class="magic-search__sparkles" aria-hidden="true">
      <TransitionGroup name="sparkle">
        <span
          v-for="sparkle in sparkles"
          :key="sparkle.id"
          class="magic-search__sparkle"
          :style="{
            left: `${sparkle.x}px`,
            top: `${sparkle.y}px`,
            width: `${sparkle.size}px`,
            height: `${sparkle.size}px`,
            animationDelay: `${sparkle.delay}s`,
          }"
        />
      </TransitionGroup>
    </div>

    <!-- Glow effect -->
    <div class="magic-search__glow" aria-hidden="true" />

    <!-- Search input wrapper -->
    <div class="magic-search__wrapper">
      <!-- Magic icon -->
      <div class="magic-search__icon">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M12 2L14.4 7.2L20 8L16 12.4L17.2 18L12 15.2L6.8 18L8 12.4L4 8L9.6 7.2L12 2Z"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="magic-search__star-path"
          />
        </svg>
      </div>

      <!-- Input field -->
      <input
        v-model="query"
        type="text"
        class="magic-search__input"
        :placeholder="placeholder"
        :disabled="disabled || isAnimating"
        @focus="isFocused = true"
        @blur="isFocused = false"
        @keydown="handleKeydown"
      />

      <!-- Submit button -->
      <button
        type="button"
        class="magic-search__submit"
        :disabled="!query.trim() || disabled || isAnimating"
        @click="handleSubmit"
      >
        <svg
          v-if="!isAnimating"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M22 2L11 13"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <path
            d="M22 2L15 22L11 13L2 9L22 2Z"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        <span v-else class="magic-search__loading">
          <span class="magic-search__loading-dot" />
          <span class="magic-search__loading-dot" />
          <span class="magic-search__loading-dot" />
        </span>
      </button>
    </div>

    <!-- Hint text -->
    <p class="magic-search__hint">
      <span class="magic-search__hint-icon">✨</span>
      Try: "What AI features are planned?" or "Show me Q1 updates"
    </p>
  </div>
</template>

<style scoped>
.magic-search {
  position: relative;
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

/* Sparkles container */
.magic-search__sparkles {
  position: absolute;
  inset: -100px;
  pointer-events: none;
  z-index: 10;
  overflow: visible;
}

.magic-search__sparkle {
  position: absolute;
  background: radial-gradient(
    circle,
    #ffd700 0%,
    #ffb700 30%,
    #F71963 60%,
    transparent 70%
  );
  border-radius: 50%;
  animation: sparkle-float 0.5s ease-out forwards;
  box-shadow:
    0 0 6px 2px rgb(255 215 0 / 60%),
    0 0 12px 4px rgb(0 212 170 / 40%);
}

@keyframes sparkle-float {
  0% {
    opacity: 0;
    transform: scale(0) translateY(0);
  }

  20% {
    opacity: 1;
    transform: scale(1.2) translateY(-10px);
  }

  100% {
    opacity: 0;
    transform: scale(0.5) translateY(-60px);
  }
}

.sparkle-enter-active,
.sparkle-leave-active {
  transition: all 0.3s ease;
}

.sparkle-enter-from {
  opacity: 0;
  transform: scale(0);
}

.sparkle-leave-to {
  opacity: 0;
  transform: scale(0);
}

/* Glow effect */
.magic-search__glow {
  position: absolute;
  inset: -4px;
  background: linear-gradient(
    135deg,
    rgb(247 25 99 / 30%) 0%,
    rgb(247 25 99 / 20%) 50%,
    rgb(255 215 0 / 30%) 100%
  );
  border-radius: 20px;
  filter: blur(20px);
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: -1;
}

.magic-search--focused .magic-search__glow,
.magic-search--animating .magic-search__glow {
  opacity: 1;
}

.magic-search--animating .magic-search__glow {
  animation: glow-pulse 0.6s ease-in-out;
}

@keyframes glow-pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: 1;
    transform: scale(1.1);
    filter: blur(30px);
  }
}

/* Search wrapper */
.magic-search__wrapper {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #fff 0%, #fff8fa 100%);
  border: 2px solid transparent;
  border-radius: 16px;
  box-shadow:
    0 4px 20px rgb(247 25 99 / 10%),
    0 1px 3px rgb(0 0 0 / 5%),
    inset 0 1px 0 rgb(255 255 255 / 80%);
  transition: all 0.3s ease;
  z-index: 1;
}

.magic-search--focused .magic-search__wrapper {
  border-color: #F71963;
  box-shadow:
    0 8px 32px rgb(247 25 99 / 20%),
    0 2px 8px rgb(0 0 0 / 8%),
    inset 0 1px 0 rgb(255 255 255 / 80%);
}

.magic-search--animating .magic-search__wrapper {
  transform: scale(0.98);
  border-color: #ffd700;
  box-shadow:
    0 0 40px rgb(255 215 0 / 40%),
    0 0 80px rgb(0 212 170 / 20%);
}

/* Icon */
.magic-search__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  color: #F71963;
  transition: all 0.3s ease;
}

.magic-search--focused .magic-search__icon {
  color: #ffd700;
}

.magic-search--animating .magic-search__icon {
  animation: icon-spin 0.6s ease-in-out;
}

@keyframes icon-spin {
  0% {
    transform: rotate(0deg) scale(1);
  }

  50% {
    transform: rotate(180deg) scale(1.2);
    color: #ffd700;
  }

  100% {
    transform: rotate(360deg) scale(1);
  }
}

.magic-search__star-path {
  stroke-dasharray: 100;
  stroke-dashoffset: 0;
  transition: all 0.3s ease;
}

.magic-search--focused .magic-search__star-path {
  fill: rgb(255 215 0 / 20%);
}

/* Input */
.magic-search__input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 16px;
  font-weight: 400;
  color: var(--unnnic-color-neutral-dark, #272833);
  outline: none;
}

.magic-search__input::placeholder {
  color: var(--unnnic-color-neutral-clean, #9ca3af);
}

.magic-search__input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Submit button */
.magic-search__submit {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #F71963 0%, #dd1259 100%);
  color: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.magic-search__submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--unnnic-color-neutral-soft, #e8e8e8);
  color: var(--unnnic-color-neutral-clean, #9ca3af);
}

.magic-search__submit:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgb(247 25 99 / 40%);
}

.magic-search__submit:active:not(:disabled) {
  transform: scale(0.95);
}

/* Loading dots */
.magic-search__loading {
  display: flex;
  gap: 4px;
}

.magic-search__loading-dot {
  width: 6px;
  height: 6px;
  background: #fff;
  border-radius: 50%;
  animation: loading-bounce 1s ease-in-out infinite;
}

.magic-search__loading-dot:nth-child(2) {
  animation-delay: 0.1s;
}

.magic-search__loading-dot:nth-child(3) {
  animation-delay: 0.2s;
}

@keyframes loading-bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
  }

  40% {
    transform: translateY(-6px);
  }
}

/* Hint text */
.magic-search__hint {
  margin-top: 12px;
  font-size: 13px;
  color: var(--unnnic-color-neutral-clean, #9ca3af);
  text-align: center;
  opacity: 0;
  transform: translateY(-8px);
  transition: all 0.3s ease;
}

.magic-search--focused .magic-search__hint {
  opacity: 1;
  transform: translateY(0);
}

.magic-search__hint-icon {
  margin-right: 4px;
}

/* Disabled state */
.magic-search--disabled {
  opacity: 0.6;
  pointer-events: none;
}
</style>
