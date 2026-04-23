<script setup lang="ts">
/**
 * RoadmapCard - Expandable card for a single roadmap item.
 *
 * Displays title and module badge in collapsed state.
 * Expands to show full description, images, and documentation link.
 * Supports liking the epic with optimistic UI updates.
 */

import { ref, computed, watch } from 'vue';
import type { RoadmapItem } from '@/types/roadmap';
import { likeEpic } from '@/services/roadmapService';
import ImageCarouselModal from '@/components/ImageCarouselModal.vue';
import ShareButton from '@/components/ShareButton.vue';

interface Props {
  item: RoadmapItem;
  autoExpand?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  autoExpand: false,
});

const isExpanded = ref(props.autoExpand);
const cardElement = ref<HTMLElement | null>(null);

// Watch for autoExpand changes (for shared links)
watch(
  () => props.autoExpand,
  (shouldExpand) => {
    if (shouldExpand) {
      isExpanded.value = true;
      // Scroll to this card after expansion
      setTimeout(() => {
        cardElement.value?.scrollIntoView({
          behavior: 'smooth',
          block: 'center',
        });
      }, 100);
    }
  },
  { immediate: true },
);
const localLikeCount = ref<number>(props.item.likes ?? 0);
const isLikeLoading = ref(false);
const likeError = ref<string | null>(null);
let likeDebounceTimer: number | null = null;

// localStorage key for tracking liked items
const LIKED_ITEMS_KEY = 'vtex-ads-roadmap-liked-items';

/**
 * Check if the user has already liked this item (stored in localStorage).
 */
function hasUserLikedItem(itemId: string): boolean {
  try {
    const likedItems = JSON.parse(
      localStorage.getItem(LIKED_ITEMS_KEY) || '[]',
    );
    return Array.isArray(likedItems) && likedItems.includes(itemId);
  } catch {
    return false;
  }
}

/**
 * Mark an item as liked in localStorage.
 */
function markItemAsLiked(itemId: string): void {
  try {
    const likedItems = JSON.parse(
      localStorage.getItem(LIKED_ITEMS_KEY) || '[]',
    );
    if (Array.isArray(likedItems) && !likedItems.includes(itemId)) {
      likedItems.push(itemId);
      localStorage.setItem(LIKED_ITEMS_KEY, JSON.stringify(likedItems));
    }
  } catch {
    // If localStorage fails, continue silently
  }
}

// Track if user has already liked this item
const hasAlreadyLiked = ref(hasUserLikedItem(props.item.id));

// Image modal state
const showImageModal = ref(false);
const clickedImageIndex = ref(0);

// Event handler: uses "on" prefix for user interactions
function onCardClick(): void {
  isExpanded.value = !isExpanded.value;
}

/**
 * Handle image click to open carousel modal.
 * Stops event propagation to prevent card expansion.
 */
function onImageClick(event: Event, index: number): void {
  event.stopPropagation();
  clickedImageIndex.value = index;
  showImageModal.value = true;
}

/**
 * Handle modal close request.
 */
function onModalClose(): void {
  showImageModal.value = false;
}

const hasImages = computed(
  () => props.item.images && props.item.images.length > 0,
);
const hasDocumentation = computed(() => !!props.item.documentationUrl);

const releaseInfo = computed(() => {
  const { releaseQuarter, releaseYear, releaseMonth } = props.item;
  if (releaseMonth) {
    const monthName = new Date(2000, releaseMonth - 1).toLocaleString('en', {
      month: 'short',
    });
    return `${monthName} ${releaseYear}`;
  }
  return `${releaseQuarter} ${releaseYear}`;
});

const likeCount = computed(() => {
  return localLikeCount.value;
});

const likeButtonLabel = computed(() => {
  if (hasAlreadyLiked.value) {
    return `You already liked this epic (${likeCount.value} like${likeCount.value !== 1 ? 's' : ''})`;
  }
  return `Like this epic (${likeCount.value} like${likeCount.value !== 1 ? 's' : ''})`;
});

const isLikeDisabled = computed(() => {
  return isLikeLoading.value || hasAlreadyLiked.value;
});

/**
 * Handle like button click with optimistic update and debouncing.
 * Prevents card expansion when clicking the like button.
 * Prevents multiple likes from the same user using localStorage.
 */
async function onLikeClick(event: Event): Promise<void> {
  event.stopPropagation(); // Prevent card expansion

  // Prevent if already liked
  if (hasAlreadyLiked.value) {
    return;
  }

  // Clear any existing error
  likeError.value = null;

  // Debounce: prevent rapid clicks
  if (likeDebounceTimer !== null) {
    return; // Already processing a like
  }

  // Save the original count for rollback
  const originalCount = localLikeCount.value;

  // Optimistic update: increment immediately and mark as liked
  localLikeCount.value += 1;
  hasAlreadyLiked.value = true;
  isLikeLoading.value = true;

  // Set debounce timer (500ms)
  likeDebounceTimer = window.setTimeout(async () => {
    try {
      // Call API to update JIRA
      const response = await likeEpic(props.item.id);

      // Server reconciliation: use the count from the server
      if (response.success && response.likes !== undefined) {
        localLikeCount.value = response.likes;
        // Persist liked status to localStorage on success
        markItemAsLiked(props.item.id);
      }
    } catch (error) {
      // Rollback on error
      localLikeCount.value = originalCount;
      hasAlreadyLiked.value = false; // Allow retry on error
      likeError.value =
        error instanceof Error
          ? error.message
          : 'Failed to like this epic. Please try again.';
    } finally {
      isLikeLoading.value = false;
      likeDebounceTimer = null;
    }
  }, 500);
}

// Expose for URL navigation (needed for shared epic links)
defineExpose({
  isExpanded,
});
</script>

<template>
  <article
    ref="cardElement"
    :class="['roadmap-card', { 'roadmap-card--expanded': isExpanded }]"
    @click="onCardClick"
  >
    <!-- Header (always visible) -->
    <header class="roadmap-card__header">
      <div class="roadmap-card__main">
        <h3 class="roadmap-card__title">{{ item.title }}</h3>
        <div class="roadmap-card__meta">
          <span class="roadmap-card__badge">{{ item.module }}</span>
          <span class="roadmap-card__release">{{ releaseInfo }}</span>
          <button
            class="roadmap-card__like-btn"
            :class="{
              'roadmap-card__like-btn--loading': isLikeLoading,
              'roadmap-card__like-btn--liked': hasAlreadyLiked,
            }"
            :disabled="isLikeDisabled"
            :aria-label="likeButtonLabel"
            @click="onLikeClick"
          >
            <svg
              class="roadmap-card__like-icon"
              width="16"
              height="16"
              viewBox="0 0 20 20"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M10 17.5l-1.5-1.35C4.4 12.36 2 10.28 2 7.5 2 5.5 3.5 4 5.5 4c1.54 0 3.04.99 3.57 2.36h1.87C11.46 4.99 12.96 4 14.5 4 16.5 4 18 5.5 18 7.5c0 2.78-2.4 4.86-6.5 8.65L10 17.5z"
                fill="currentColor"
              />
            </svg>
            <span class="roadmap-card__like-count">{{ likeCount }}</span>
          </button>
          <ShareButton
            :epic-id="item.id"
            size="small"
            variant="ghost"
            @click.stop
          />
        </div>
      </div>
      <button
        class="roadmap-card__expand-btn"
        :aria-expanded="isExpanded"
        aria-label="Expand card details"
      >
        <svg
          :class="[
            'roadmap-card__chevron',
            { 'roadmap-card__chevron--rotated': isExpanded },
          ]"
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M5 7.5L10 12.5L15 7.5"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </header>

    <!-- Expanded content -->
    <div v-if="isExpanded" class="roadmap-card__content" @click.stop>
      <!--
        v-html is safe here: content is pre-sanitized by backend HTMLSanitizer
        (allowlist-based, XSS prevention, URL validation, security headers)
      -->
      <!-- eslint-disable-next-line vue/no-v-html -->
      <div class="roadmap-card__description" v-html="item.description"></div>

      <!-- Image gallery -->
      <div v-if="hasImages" class="roadmap-card__images">
        <div class="roadmap-card__images-grid">
          <img
            v-for="(imageUrl, index) in item.images"
            :key="index"
            :src="imageUrl"
            :alt="`${item.title} - Image ${index + 1}`"
            class="roadmap-card__image"
            loading="lazy"
            @click="(e) => onImageClick(e, index)"
          />
        </div>
      </div>

      <!-- Documentation link -->
      <a
        v-if="hasDocumentation"
        :href="item.documentationUrl!"
        target="_blank"
        rel="noopener noreferrer"
        class="roadmap-card__link"
        @click.stop
      >
        Read More
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M4 12L12 4M12 4H5M12 4V11"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </a>

      <!-- Share button in expanded view -->
      <div class="roadmap-card__share-expanded">
        <ShareButton :epic-id="item.id" size="medium" variant="outlined" />
      </div>
    </div>

    <!-- Error message -->
    <div v-if="likeError" class="roadmap-card__error" role="alert">
      {{ likeError }}
    </div>

    <!-- Image carousel modal -->
    <ImageCarouselModal
      :images="item.images || []"
      :current-index="clickedImageIndex"
      :epic-title="item.title"
      :show="showImageModal"
      @close="onModalClose"
    />
  </article>
</template>

<style scoped>
/* BEM: Block - roadmap-card */
.roadmap-card {
  background: var(--unnnic-color-background-snow, #fff);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-md, 12px);
  padding: var(--unnnic-spacing-stack-md, 20px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.roadmap-card:hover {
  border-color: #dd1259;
  box-shadow: 0 4px 12px rgb(247 25 99 / 10%);
}

/* BEM: Modifier - expanded */
.roadmap-card--expanded {
  cursor: default;
}

/* BEM: Element - header */
.roadmap-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--unnnic-spacing-inline-md, 16px);
}

/* BEM: Element - main */
.roadmap-card__main {
  flex: 1;
  min-width: 0;
}

/* BEM: Element - title */
.roadmap-card__title {
  margin: 0 0 var(--unnnic-spacing-stack-xs, 8px) 0;
  font-size: var(--unnnic-font-size-body-lg, 16px);
  font-weight: var(--unnnic-font-weight-bold, 600);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
  line-height: 1.4;
}

/* BEM: Element - meta */
.roadmap-card__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--unnnic-spacing-inline-sm, 12px);
}

/* BEM: Element - badge */
.roadmap-card__badge {
  display: inline-block;
  padding: 4px 10px;
  background: #F71963;
  color: #fff;
  border-radius: var(--unnnic-border-radius-sm, 6px);
  font-size: var(--unnnic-font-size-body-sm, 12px);
  font-weight: var(--unnnic-font-weight-medium, 500);
}

/* BEM: Element - release */
.roadmap-card__release {
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  font-size: var(--unnnic-font-size-body-md, 13px);
}

/* BEM: Element - like-btn */
.roadmap-card__like-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--unnnic-border-radius-sm, 6px);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  font-size: var(--unnnic-font-size-body-md, 13px);
  cursor: pointer;
  transition: all 0.2s ease;
}

.roadmap-card__like-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.roadmap-card__like-btn:hover:not(:disabled) {
  background: rgb(247 25 99 / 5%);
  border-color: #F71963;
  color: #dd1259;
}

/* BEM: Element - like-icon */
.roadmap-card__like-icon {
  width: 14px;
  height: 14px;
  color: currentcolor;
}

/* BEM: Modifier - loading */
.roadmap-card__like-btn--loading {
  opacity: 0.6;
}

.roadmap-card__like-btn--loading .roadmap-card__like-icon {
  animation: pulse 1.5s ease-in-out infinite;
}

/* BEM: Modifier - liked (already liked by user) */
.roadmap-card__like-btn--liked {
  background: #ffe0ef;
  border-color: #F71963;
  color: #dd1259;
  cursor: default;
}

.roadmap-card__like-btn--liked .roadmap-card__like-icon {
  color: #F71963;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.5;
  }
}

/* BEM: Element - like-count */
.roadmap-card__like-count {
  font-weight: var(--unnnic-font-weight-medium, 500);
}

/* BEM: Element - error */
.roadmap-card__error {
  margin-top: var(--unnnic-spacing-stack-sm, 12px);
  padding: 12px 16px;
  background: rgb(255 77 79 / 10%);
  border-left: 3px solid var(--unnnic-color-feedback-red, #ff4d4f);
  border-radius: var(--unnnic-border-radius-sm, 6px);
  color: var(--unnnic-color-feedback-red, #ff4d4f);
  font-size: var(--unnnic-font-size-body-sm, 12px);
  line-height: 1.5;
}

/* BEM: Element - expand-btn */
.roadmap-card__expand-btn {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--unnnic-color-neutral-light, #f5f5f5);
  border: none;
  border-radius: var(--unnnic-border-radius-sm, 8px);
  cursor: pointer;
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  transition: all 0.2s ease;
}

.roadmap-card__expand-btn:hover {
  background: var(--unnnic-color-neutral-soft, #e8e8e8);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
}

/* BEM: Element - chevron */
.roadmap-card__chevron {
  transition: transform 0.2s ease;
}

/* BEM: Modifier - rotated */
.roadmap-card__chevron--rotated {
  transform: rotate(180deg);
}

/* BEM: Element - content */
.roadmap-card__content {
  margin-top: var(--unnnic-spacing-stack-md, 20px);
  padding-top: var(--unnnic-spacing-stack-md, 20px);
  border-top: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  cursor: default;
}

/* BEM: Element - description */
.roadmap-card__description {
  margin: 0 0 var(--unnnic-spacing-stack-md, 20px) 0;
  color: var(--unnnic-color-neutral-dark, #4a4a4a);
  font-size: var(--unnnic-font-size-body-md, 14px);
  line-height: 1.6;
}

/* Formatted content styles using :deep() for v-html */
.roadmap-card__description :deep(p) {
  margin: 0 0 12px;
}

.roadmap-card__description :deep(p:last-child) {
  margin-bottom: 0;
}

.roadmap-card__description :deep(strong) {
  font-weight: var(--unnnic-font-weight-bold, 600);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
}

.roadmap-card__description :deep(em) {
  font-style: italic;
}

.roadmap-card__description :deep(u) {
  text-decoration: underline;
}

.roadmap-card__description :deep(s) {
  text-decoration: line-through;
  opacity: 0.7;
}

.roadmap-card__description :deep(ul),
.roadmap-card__description :deep(ol) {
  margin: 12px 0;
  padding-left: 24px;
}

.roadmap-card__description :deep(li) {
  margin: 6px 0;
}

.roadmap-card__description :deep(a) {
  color: #dd1259;
  text-decoration: underline;
  transition: color 0.2s ease;
}

.roadmap-card__description :deep(a:hover) {
  color: #b80f4c;
}

.roadmap-card__description :deep(h1),
.roadmap-card__description :deep(h2),
.roadmap-card__description :deep(h3),
.roadmap-card__description :deep(h4),
.roadmap-card__description :deep(h5),
.roadmap-card__description :deep(h6) {
  margin: 16px 0 8px;
  font-weight: var(--unnnic-font-weight-bold, 600);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
  line-height: 1.4;
}

.roadmap-card__description :deep(h1) {
  font-size: 1.5em;
}

.roadmap-card__description :deep(h2) {
  font-size: 1.3em;
}

.roadmap-card__description :deep(h3) {
  font-size: 1.1em;
}

.roadmap-card__description :deep(h4),
.roadmap-card__description :deep(h5),
.roadmap-card__description :deep(h6) {
  font-size: 1em;
}

.roadmap-card__description :deep(code) {
  background: var(--unnnic-color-neutral-soft, #f5f5f5);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9em;
}

.roadmap-card__description :deep(pre) {
  background: var(--unnnic-color-neutral-soft, #f5f5f5);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.roadmap-card__description :deep(pre code) {
  background: none;
  padding: 0;
}

.roadmap-card__description :deep(blockquote) {
  border-left: 4px solid #F71963;
  padding-left: 16px;
  margin: 12px 0;
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  font-style: italic;
}

/* BEM: Element - images */
.roadmap-card__images {
  margin-bottom: var(--unnnic-spacing-stack-md, 20px);
}

/* BEM: Element - images-grid */
.roadmap-card__images-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--unnnic-spacing-inline-sm, 12px);
}

/* BEM: Element - image */
.roadmap-card__image {
  width: 100%;
  height: 100%;
  max-height: 280px;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  border-radius: var(--unnnic-border-radius-sm, 8px);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  cursor: pointer;
  transition: transform 0.2s ease;
}

.roadmap-card__image:hover {
  transform: scale(1.02);
  border-color: #F71963;
  box-shadow: 0 4px 12px rgb(247 25 99 / 20%);
}

/* BEM: Element - link */
.roadmap-card__link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: #dd1259;
  color: var(--unnnic-color-background-snow, #fff);
  border: none;
  border-radius: var(--unnnic-border-radius-sm, 8px);
  font-size: var(--unnnic-font-size-body-md, 14px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.roadmap-card__link:hover {
  background: #b80f4c;
}

/* BEM: Element - share-expanded */
.roadmap-card__share-expanded {
  margin-top: var(--unnnic-spacing-stack-md, 16px);
  padding-top: var(--unnnic-spacing-stack-md, 16px);
  border-top: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
}

/* Responsive */
@media (width <= 640px) {
  .roadmap-card {
    padding: var(--unnnic-spacing-stack-sm, 16px);
  }

  .roadmap-card__title {
    font-size: 15px;
  }

  .roadmap-card__images-grid {
    grid-template-columns: 1fr;
  }

  .roadmap-card__image {
    max-height: 220px;
  }
}
</style>
