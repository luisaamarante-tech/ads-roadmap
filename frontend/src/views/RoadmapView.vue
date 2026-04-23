<script setup lang="ts">
/**
 * RoadmapView - Main roadmap page composing tabs, filters, and card list.
 */

import { ref, computed, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import type {
  DeliveryStatus,
  RoadmapItem,
  RoadmapStats,
  RoadmapFilters,
  Module,
  Goal,
  Pillar,
} from '@/types/roadmap';
import {
  getRoadmapItems,
  getStats,
  getModules,
  getGoals,
  getPillars,
} from '@/services/roadmapService';
import RoadmapTabs from '@/components/RoadmapTabs.vue';
import RoadmapCardList from '@/components/RoadmapCardList.vue';
import RoadmapFiltersComponent from '@/components/RoadmapFilters.vue';
import RoadmapFeatureRequestForm from '@/components/RoadmapFeatureRequestForm.vue';

// Router
const router = useRouter();
const route = useRoute();

// State
const activeStatus = ref<DeliveryStatus>('DELIVERED');
const items = ref<RoadmapItem[]>([]);
const stats = ref<RoadmapStats | null>(null);
const modules = ref<Module[]>([]);
const goals = ref<Goal[]>([]);
const pillars = ref<Pillar[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

// Filters
const filters = ref<RoadmapFilters>({});

// Feature request modal
const showFeatureRequestModal = ref(false);

// Shared epic handling
const sharedEpicId = ref<string | null>(null);
const isProcessingSharedEpic = ref(false);

/**
 * Helper: Calculate an approximate timestamp for release date sorting.
 * Uses releaseYear, releaseQuarter, and releaseMonth if available.
 */
function getReleaseDateTimestamp(item: RoadmapItem): number {
  const year = item.releaseYear;

  // If month is available, use it for more precise sorting
  if (item.releaseMonth) {
    return new Date(year, item.releaseMonth - 1, 1).getTime();
  }

  // Otherwise, use quarter (Q1 = Jan, Q2 = Apr, Q3 = Jul, Q4 = Oct)
  const quarterMonths: Record<string, number> = {
    Q1: 0, // January
    Q2: 3, // April
    Q3: 6, // July
    Q4: 9, // October
  };

  const month = quarterMonths[item.releaseQuarter] ?? 0;
  return new Date(year, month, 1).getTime();
}

// Computed: Sort items by release date based on status
const sortedItems = computed<RoadmapItem[]>(() => {
  if (items.value.length === 0) {
    return [];
  }

  // Create a shallow copy to avoid mutating original array
  const itemsCopy = [...items.value];

  // Sort based on status:
  // DELIVERED: most recent first (descending)
  // Others (NOW, NEXT, FUTURE): closest date first (ascending)
  return itemsCopy.sort((a, b) => {
    const dateA = getReleaseDateTimestamp(a);
    const dateB = getReleaseDateTimestamp(b);

    if (activeStatus.value === 'DELIVERED') {
      // Descending: most recent first
      return dateB - dateA;
    } else {
      // Ascending: closest date first
      return dateA - dateB;
    }
  });
});

// State handlers: use "handle" prefix for state updates
async function handleFetchItems(): Promise<void> {
  loading.value = true;
  error.value = null;

  try {
    const response = await getRoadmapItems({
      ...filters.value,
      status: activeStatus.value,
    });
    items.value = response.items;
  } catch (e) {
    console.error('Failed to fetch items:', e);
    error.value = 'Failed to load roadmap items. Please try again.';
  } finally {
    loading.value = false;
  }
}

async function handleFetchStats(): Promise<void> {
  try {
    const response = await getStats(filters.value);
    stats.value = response.stats;
  } catch (e) {
    console.error('Failed to fetch stats:', e);
  }
}

async function handleFetchModules(): Promise<void> {
  try {
    const response = await getModules();
    modules.value = response.modules;
  } catch (e) {
    console.error('Failed to fetch modules:', e);
  }
}

async function handleFetchGoals(): Promise<void> {
  try {
    const response = await getGoals();
    goals.value = response.goals;
  } catch (e) {
    console.error('Failed to fetch goals:', e);
  }
}

async function handleFetchPillars(): Promise<void> {
  try {
    const response = await getPillars();
    pillars.value = response.pillars;
  } catch (e) {
    console.error('Failed to fetch pillars:', e);
  }
}

// URL sync helpers
function parseFiltersFromURL(): void {
  const query = route.query;
  const parsedFilters: RoadmapFilters = {};

  if (query.year) {
    parsedFilters.year = parseInt(query.year as string, 10);
  }

  if (query.quarter) {
    parsedFilters.quarter = query.quarter as RoadmapFilters['quarter'];
  }

  // Handle module: can be single value or array
  if (query.module) {
    if (Array.isArray(query.module)) {
      parsedFilters.module = query.module as string[];
    } else {
      parsedFilters.module = [query.module as string];
    }
  }

  filters.value = parsedFilters;
}

function updateURLFromFilters(): void {
  const query: Record<string, string | string[]> = {};

  if (filters.value.year) {
    query.year = String(filters.value.year);
  }

  if (filters.value.quarter) {
    query.quarter = filters.value.quarter;
  }

  // Handle module: serialize as repeated params
  if (filters.value.module) {
    if (Array.isArray(filters.value.module)) {
      query.module = filters.value.module;
    } else {
      query.module = filters.value.module;
    }
  }

  router.replace({ query });
}

// Event handler: use "on" prefix for user interactions
function onRetryClick(): void {
  handleFetchItems();
}

function onRequestFeatureClick(): void {
  showFeatureRequestModal.value = true;
}

function onFeatureRequestClose(): void {
  showFeatureRequestModal.value = false;
}

function onFeatureRequestSubmitted(_issueKey: string): void {
  // Feature request submitted successfully
  // Could show a toast notification here if needed
}

/**
 * Handle shared epic link on mount.
 * Clears filters, fetches ALL items across all statuses, finds and expands epic.
 */
async function handleSharedEpicLink(): Promise<void> {
  const epicId = route.query.epic;

  if (!epicId || typeof epicId !== 'string') {
    return;
  }

  isProcessingSharedEpic.value = true;
  sharedEpicId.value = epicId;

  try {
    // Clear all filters to ensure epic is visible
    filters.value = {};

    // Fetch items from ALL statuses by trying each one
    const allStatuses: DeliveryStatus[] = [
      'DELIVERED',
      'NOW',
      'NEXT',
      'FUTURE',
    ];
    let foundStatus: DeliveryStatus | null = null;
    let allItems: RoadmapItem[] = [];

    for (const status of allStatuses) {
      try {
        const response = await getRoadmapItems({ status });
        allItems = [...allItems, ...response.items];

        // Check if epic is in this status
        const found = response.items.find((item) => item.id === epicId);
        if (found) {
          foundStatus = status;
        }
      } catch (e) {
        console.error(`Failed to fetch items for status ${status}:`, e);
      }
    }

    if (foundStatus) {
      // Set the active status to where the epic was found
      activeStatus.value = foundStatus;
      // Keep the shared epic ID temporarily for auto-expansion
      // Will be cleared after render
      console.info(`Found shared epic ${epicId} in status: ${foundStatus}`);

      // Fetch items for that status to display
      await handleFetchItems();

      // Wait for next tick to ensure cards are rendered, then clear
      setTimeout(() => {
        sharedEpicId.value = null;
        isProcessingSharedEpic.value = false;
        // Remove epic parameter from URL after expansion
        router.replace({ query: {} });
      }, 500);
    } else {
      error.value = `Epic ${epicId} not found or no longer available.`;
      // Clean up immediately on error
      router.replace({ query: {} });
      sharedEpicId.value = null;
      isProcessingSharedEpic.value = false;
    }
  } catch (e) {
    console.error('Failed to process shared epic link:', e);
    error.value = 'Failed to load shared epic. Please try again.';
    // Clean up on error
    router.replace({ query: {} });
    sharedEpicId.value = null;
    isProcessingSharedEpic.value = false;
  }
}

// Watch for status changes
watch(activeStatus, () => {
  handleFetchItems();
});

// Watch for filter changes
watch(
  filters,
  () => {
    updateURLFromFilters();
    handleFetchItems();
    handleFetchStats();
  },
  { deep: true },
);

// Watch for route changes (shared epic links)
watch(
  () => route.query.epic,
  (newEpicId) => {
    if (newEpicId && typeof newEpicId === 'string') {
      handleSharedEpicLink();
    }
  },
);

// Initial load
onMounted(async () => {
  // Check for shared epic link FIRST
  if (route.query.epic) {
    await handleSharedEpicLink();
    // Don't load modules/stats yet, wait for user interaction
    await handleFetchModules();
    await handleFetchGoals();
    await handleFetchPillars();
    return;
  }

  // Normal flow: parse filters from URL
  parseFiltersFromURL();
  handleFetchItems();
  handleFetchStats();
  handleFetchModules();
  handleFetchGoals();
  handleFetchPillars();
});
</script>

<template>
  <div class="roadmap-page">
    <!-- Normal View -->
    <template v-if="true">
      <!-- Top bar with Request Feature button -->
      <nav class="roadmap-page__navbar">
        <div class="roadmap-page__navbar-content">
          <div class="roadmap-page__navbar-spacer"></div>
          <unnnic-button
            type="primary"
            text="Request Feature"
            @click="onRequestFeatureClick"
          />
        </div>
      </nav>

      <!-- Hero section -->
      <header class="roadmap-page__header">
        <h1 class="roadmap-page__title">
          Roadmap of <span class="roadmap-page__brand">VTEX Ads</span>
        </h1>
        <p class="roadmap-page__description">
          We are building a series of solutions for our platform. Here you can
          see our plans and goals for each quarter. Stay engaged and know what
          we're up to!
        </p>

      </header>

      <!-- Main content -->
      <main class="roadmap-page__content">
        <!-- Filters -->
        <RoadmapFiltersComponent v-model="filters" :modules="modules" :goals="goals" :pillars="pillars" />

        <!-- Status tabs -->
        <RoadmapTabs v-model="activeStatus" :stats="stats" />

        <!-- Error message -->
        <div v-if="error" class="roadmap-page__error" role="alert">
          <p class="roadmap-page__error-text">{{ error }}</p>
          <button class="roadmap-page__retry-btn" @click="onRetryClick">
            Try Again
          </button>
        </div>

        <!-- Card list with transition on tab/filter change -->
        <Transition name="list-swap" mode="out-in">
          <RoadmapCardList
            v-if="!loading"
            :key="`${activeStatus}-${filters.module}-${filters.quarter}-${filters.year}`"
            :items="sortedItems"
            :status="activeStatus"
            :loading="loading"
            :auto-expand-epic-id="sharedEpicId"
          />
          <RoadmapCardList
            v-else
            :items="[]"
            :status="activeStatus"
            :loading="true"
          />
        </Transition>
      </main>

      <!-- Footer -->
      <footer class="roadmap-page__footer">
        <p>
          &copy; {{ new Date().getFullYear() }} VTEX Ads. All rights
          reserved.
        </p>
      </footer>
    </template>

    <!-- Feature Request Modal -->
    <RoadmapFeatureRequestForm
      :show="showFeatureRequestModal"
      :available-modules="modules"
      @close="onFeatureRequestClose"
      @submitted="onFeatureRequestSubmitted"
    />
  </div>
</template>

<style scoped>
/* BEM: Block - roadmap-page */
.roadmap-page {
  min-height: 100vh;
  background: linear-gradient(
    180deg,
    var(--unnnic-color-background-carpet, #f8fafa) 0%,
    var(--unnnic-color-background-snow, #fff) 100%
  );
}

/* BEM: Element - navbar */
.roadmap-page__navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--unnnic-color-background-snow, #fff);
  border-bottom: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  padding: var(--unnnic-spacing-stack-sm, 12px)
    var(--unnnic-spacing-inline-lg, 24px);
}

.roadmap-page__navbar-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: var(--unnnic-spacing-inline-sm, 12px);
}

.roadmap-page__navbar-spacer {
  flex: 1;
}

/* BEM: Element - header */
.roadmap-page__header {
  text-align: center;
  padding: 60px var(--unnnic-spacing-inline-lg, 24px) 40px;
  max-width: 800px;
  margin: 0 auto;
}

/* BEM: Element - title */
.roadmap-page__title {
  font-size: var(--unnnic-font-size-title-lg, 42px);
  font-weight: var(--unnnic-font-weight-black, 700);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
  margin: 0 0 var(--unnnic-spacing-stack-sm, 16px) 0;
  line-height: 1.2;
}

/* BEM: Element - brand */
.roadmap-page__brand {
  color: #dd1259;
}

/* BEM: Element - description */
.roadmap-page__description {
  font-size: var(--unnnic-font-size-body-lg, 18px);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  line-height: 1.6;
  margin: 0;
}

/* BEM: Element - search-container */
.roadmap-page__search-container {
  margin-top: 32px;
  padding: 0 16px;
}

/* BEM: Element - content */
.roadmap-page__content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 var(--unnnic-spacing-inline-lg, 24px) 60px;
}

/* BEM: Element - error */
.roadmap-page__error {
  text-align: center;
  padding: 40px;
  background: var(--unnnic-color-aux-red-100, #fff5f5);
  border-radius: var(--unnnic-border-radius-md, 12px);
  margin-top: var(--unnnic-spacing-stack-lg, 24px);
}

/* BEM: Element - error-text */
.roadmap-page__error-text {
  color: var(--unnnic-color-aux-red-500, #e53e3e);
  margin: 0 0 var(--unnnic-spacing-stack-sm, 16px) 0;
}

/* BEM: Element - retry-btn */
.roadmap-page__retry-btn {
  padding: 10px 24px;
  background: var(--unnnic-color-aux-red-500, #e53e3e);
  color: var(--unnnic-color-background-snow, #fff);
  border: none;
  border-radius: var(--unnnic-border-radius-sm, 8px);
  font-size: var(--unnnic-font-size-body-md, 14px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  cursor: pointer;
  transition: background 0.2s;
}

.roadmap-page__retry-btn:hover {
  background: var(--unnnic-color-aux-red-700, #c53030);
}

/* BEM: Element - footer */
.roadmap-page__footer {
  text-align: center;
  padding: var(--unnnic-spacing-stack-lg, 24px);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  font-size: var(--unnnic-font-size-body-md, 14px);
  border-top: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
}

/* Responsive */
@media (width <= 768px) {
  .roadmap-page__header {
    padding: 40px var(--unnnic-spacing-inline-md, 20px) 30px;
  }

  .roadmap-page__title {
    font-size: var(--unnnic-font-size-title-md, 32px);
  }

  .roadmap-page__description {
    font-size: var(--unnnic-font-size-body-lg, 16px);
  }

  .roadmap-page__content {
    padding: 0 var(--unnnic-spacing-inline-sm, 16px) 40px;
  }
}

/* Canvas mode transition - instant swap with subtle fade */
.canvas-fade-enter-active,
.canvas-fade-leave-active {
  transition: opacity 0.12s ease-out;
}

.canvas-fade-enter-from,
.canvas-fade-leave-to {
  opacity: 0;
}

/* Filters fade transition */
.filters-fade-enter-active,
.filters-fade-leave-active {
  transition: all 0.3s ease;
}

.filters-fade-enter-from,
.filters-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* List swap transition - smooth crossfade when changing tabs/filters */
.list-swap-enter-active {
  transition: opacity 0.35s ease-out;
}

.list-swap-leave-active {
  transition: opacity 0.15s ease-in;
}

.list-swap-enter-from {
  opacity: 0;
}

.list-swap-leave-to {
  opacity: 0;
}

/* Override Unnnic primary button with VTEX pink */
:deep(.unnnic-button--primary) {
  background-color: #F71963;
  border-color: #F71963;
}

:deep(.unnnic-button--primary:hover) {
  background-color: #dd1259;
  border-color: #dd1259;
}

:deep(.unnnic-button--primary:active) {
  background-color: #b80f4c;
  border-color: #b80f4c;
}
</style>
