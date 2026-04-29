<script setup lang="ts">
/**
 * RoadmapFilters - Filter controls for year, quarter, and module.
 */

import { computed, ref, onMounted, onUnmounted } from 'vue';
import type { Goal, Module, Pillar, Quarter, RoadmapFilters } from '@/types/roadmap';

interface Props {
  modelValue: RoadmapFilters;
  modules: Module[];
  goals: Goal[];
  pillars: Pillar[];
  availableYears?: number[];
}

const props = withDefaults(defineProps<Props>(), {
  availableYears: () => {
    const currentYear = new Date().getFullYear();
    return [currentYear - 1, currentYear, currentYear + 1, currentYear + 2];
  },
});

const emit = defineEmits<{
  'update:modelValue': [value: RoadmapFilters];
}>();

const quarters: { value: Quarter | ''; label: string }[] = [
  { value: '', label: 'All Quarters' },
  { value: 'Q1', label: 'Q1' },
  { value: 'Q2', label: 'Q2' },
  { value: 'Q3', label: 'Q3' },
  { value: 'Q4', label: 'Q4' },
];

const isModuleDropdownOpen = ref(false);
const moduleDropdownRef = ref<HTMLElement | null>(null);
const isGoalDropdownOpen = ref(false);
const goalDropdownRef = ref<HTMLElement | null>(null);
const isPillarDropdownOpen = ref(false);
const pillarDropdownRef = ref<HTMLElement | null>(null);

const selectedYear = computed({
  get: () => props.modelValue.year ?? 0,
  set: (value: number) => {
    emit('update:modelValue', {
      ...props.modelValue,
      year: value || undefined,
    });
  },
});

const selectedQuarter = computed({
  get: () => props.modelValue.quarter ?? '',
  set: (value: Quarter | '') => {
    emit('update:modelValue', {
      ...props.modelValue,
      quarter: value || undefined,
    });
  },
});

const selectedModules = computed({
  get: (): string[] => {
    const module = props.modelValue.module;
    if (!module) return [];
    if (Array.isArray(module)) return module;
    return [module]; // Convert single string to array for compatibility
  },
  set: (value: string[]) => {
    emit('update:modelValue', {
      ...props.modelValue,
      module: value.length > 0 ? value : undefined,
    });
  },
});

const moduleButtonLabel = computed(() => {
  const count = selectedModules.value.length;
  if (count === 0) return 'All Media';
  if (count === 1) {
    const module = props.modules.find((m) => m.id === selectedModules.value[0]);
    return module?.name || 'All Media';
  }
  return `${count} Modules`;
});

const selectedGoals = computed({
  get: (): string[] => {
    const goal = props.modelValue.goal;
    if (!goal) return [];
    if (Array.isArray(goal)) return goal;
    return [goal];
  },
  set: (value: string[]) => {
    emit('update:modelValue', {
      ...props.modelValue,
      goal: value.length > 0 ? value : undefined,
    });
  },
});

const goalButtonLabel = computed(() => {
  const count = selectedGoals.value.length;
  if (count === 0) return 'All Goals';
  if (count === 1) {
    const goal = props.goals.find((g) => g.id === selectedGoals.value[0]);
    return goal?.name || 'All Goals';
  }
  return `${count} Goals`;
});

const selectedPillars = computed({
  get: (): string[] => {
    const pillar = props.modelValue.pillar;
    if (!pillar) return [];
    if (Array.isArray(pillar)) return pillar;
    return [pillar];
  },
  set: (value: string[]) => {
    emit('update:modelValue', {
      ...props.modelValue,
      pillar: value.length > 0 ? value : undefined,
    });
  },
});

const pillarButtonLabel = computed(() => {
  const count = selectedPillars.value.length;
  if (count === 0) return 'All Pillars';
  if (count === 1) {
    const pillar = props.pillars.find((p) => p.id === selectedPillars.value[0]);
    return pillar?.name || 'All Pillars';
  }
  return `${count} Pillars`;
});

const hasActiveFilters = computed(() => {
  return !!(
    props.modelValue.year ||
    props.modelValue.quarter ||
    props.modelValue.module ||
    props.modelValue.goal ||
    props.modelValue.pillar
  );
});

// Event handlers: use "on" prefix for user interactions
function onQuarterClick(quarterValue: Quarter | ''): void {
  selectedQuarter.value = quarterValue;
}

function onModuleToggle(moduleId: string): void {
  const current = selectedModules.value;
  if (current.includes(moduleId)) {
    // Remove module
    selectedModules.value = current.filter((id) => id !== moduleId);
  } else {
    // Add module
    selectedModules.value = [...current, moduleId];
  }
}

function toggleModuleDropdown(): void {
  isModuleDropdownOpen.value = !isModuleDropdownOpen.value;
}

function onGoalToggle(goalId: string): void {
  const current = selectedGoals.value;
  if (current.includes(goalId)) {
    selectedGoals.value = current.filter((id) => id !== goalId);
  } else {
    selectedGoals.value = [...current, goalId];
  }
}

function toggleGoalDropdown(): void {
  isGoalDropdownOpen.value = !isGoalDropdownOpen.value;
}

function onPillarToggle(pillarId: string): void {
  const current = selectedPillars.value;
  if (current.includes(pillarId)) {
    selectedPillars.value = current.filter((id) => id !== pillarId);
  } else {
    selectedPillars.value = [...current, pillarId];
  }
}

function togglePillarDropdown(): void {
  isPillarDropdownOpen.value = !isPillarDropdownOpen.value;
}

function handleClickOutside(event: MouseEvent): void {
  if (
    moduleDropdownRef.value &&
    !moduleDropdownRef.value.contains(event.target as Node)
  ) {
    isModuleDropdownOpen.value = false;
  }
  if (
    goalDropdownRef.value &&
    !goalDropdownRef.value.contains(event.target as Node)
  ) {
    isGoalDropdownOpen.value = false;
  }
  if (
    pillarDropdownRef.value &&
    !pillarDropdownRef.value.contains(event.target as Node)
  ) {
    isPillarDropdownOpen.value = false;
  }
}

function onClearFiltersClick(): void {
  emit('update:modelValue', {});
}

// Click outside handling
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <div class="filters">
    <div class="filters__container">
      <!-- Year select -->
      <div class="filters__group">
        <label for="year-select" class="filters__label"> Year </label>
        <select id="year-select" v-model="selectedYear" class="filters__select">
          <option :value="0">All Years</option>
          <option v-for="year in availableYears" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>

      <!-- Quarter buttons -->
      <div class="filters__group filters__group--quarter">
        <span class="filters__label">Quarter</span>
        <div
          class="filters__quarter-buttons"
          role="group"
          aria-label="Quarter filter"
        >
          <button
            v-for="q in quarters"
            :key="q.value"
            :class="[
              'filters__quarter-btn',
              { 'filters__quarter-btn--active': selectedQuarter === q.value },
            ]"
            :aria-pressed="selectedQuarter === q.value"
            @click="onQuarterClick(q.value)"
          >
            {{ q.label }}
          </button>
        </div>
      </div>

      <!-- Module multi-select dropdown -->
      <div
        ref="moduleDropdownRef"
        class="filters__group filters__group--modules"
      >
        <label class="filters__label">Media</label>
        <div class="filters__module-dropdown">
          <button
            type="button"
            class="filters__module-toggle"
            :aria-expanded="isModuleDropdownOpen"
            aria-haspopup="true"
            @click="toggleModuleDropdown"
          >
            <span>{{ moduleButtonLabel }}</span>
            <svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              :class="[
                'filters__module-toggle-icon',
                { 'filters__module-toggle-icon--open': isModuleDropdownOpen },
              ]"
              aria-hidden="true"
            >
              <path
                d="M3 4.5L6 7.5L9 4.5"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
          <div
            v-if="isModuleDropdownOpen"
            class="filters__module-list"
            role="menu"
          >
            <label
              v-for="mod in modules"
              :key="mod.id"
              class="filters__module-item"
              role="menuitemcheckbox"
              :aria-checked="selectedModules.includes(mod.id)"
            >
              <input
                type="checkbox"
                :value="mod.id"
                :checked="selectedModules.includes(mod.id)"
                class="filters__module-checkbox"
                @change="onModuleToggle(mod.id)"
              />
              <span class="filters__module-label">
                {{ mod.name }}
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- Goal multi-select dropdown -->
      <div
        ref="goalDropdownRef"
        class="filters__group filters__group--modules"
      >
        <label class="filters__label">Goal</label>
        <div class="filters__module-dropdown">
          <button
            type="button"
            class="filters__module-toggle"
            :aria-expanded="isGoalDropdownOpen"
            aria-haspopup="true"
            @click="toggleGoalDropdown"
          >
            <span>{{ goalButtonLabel }}</span>
            <svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              :class="[
                'filters__module-toggle-icon',
                { 'filters__module-toggle-icon--open': isGoalDropdownOpen },
              ]"
              aria-hidden="true"
            >
              <path
                d="M3 4.5L6 7.5L9 4.5"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
          <div
            v-if="isGoalDropdownOpen"
            class="filters__module-list"
            role="menu"
          >
            <label
              v-for="goal in goals"
              :key="goal.id"
              class="filters__module-item"
              role="menuitemcheckbox"
              :aria-checked="selectedGoals.includes(goal.id)"
            >
              <input
                type="checkbox"
                :value="goal.id"
                :checked="selectedGoals.includes(goal.id)"
                class="filters__module-checkbox"
                @change="onGoalToggle(goal.id)"
              />
              <span class="filters__module-label">
                {{ goal.name }}
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- Pillar multi-select dropdown -->
      <div
        ref="pillarDropdownRef"
        class="filters__group filters__group--modules"
      >
        <label class="filters__label">Pillar</label>
        <div class="filters__module-dropdown">
          <button
            type="button"
            class="filters__module-toggle"
            :aria-expanded="isPillarDropdownOpen"
            aria-haspopup="true"
            @click="togglePillarDropdown"
          >
            <span>{{ pillarButtonLabel }}</span>
            <svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
              fill="none"
              :class="[
                'filters__module-toggle-icon',
                { 'filters__module-toggle-icon--open': isPillarDropdownOpen },
              ]"
              aria-hidden="true"
            >
              <path
                d="M3 4.5L6 7.5L9 4.5"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
          <div
            v-if="isPillarDropdownOpen"
            class="filters__module-list"
            role="menu"
          >
            <label
              v-for="pillar in pillars"
              :key="pillar.id"
              class="filters__module-item"
              role="menuitemcheckbox"
              :aria-checked="selectedPillars.includes(pillar.id)"
            >
              <input
                type="checkbox"
                :value="pillar.id"
                :checked="selectedPillars.includes(pillar.id)"
                class="filters__module-checkbox"
                @change="onPillarToggle(pillar.id)"
              />
              <span class="filters__module-label">
                {{ pillar.name }}
              </span>
            </label>
          </div>
        </div>
      </div>

      <!-- Clear filters -->
      <div v-if="hasActiveFilters" class="filters__group">
        <button class="filters__clear-btn" @click="onClearFiltersClick">
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            aria-hidden="true"
          >
            <path
              d="M12 4L4 12M4 4L12 12"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          Clear Filters
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* BEM: Block - filters */
.filters {
  margin-bottom: 12px;
}

/* BEM: Element - container */
.filters__container {
  display: flex;
  flex-wrap: nowrap;
  align-items: flex-end;
  gap: 12px;
  padding: var(--unnnic-spacing-stack-md, 20px);
  background: var(--unnnic-color-background-snow, #fff);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-md, 12px);
}

/* BEM: Element - group */
.filters__group {
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-xs, 8px);
  flex: 1 1 0;
  min-width: 0;
}

/* BEM: Element - label */
.filters__label {
  font-size: var(--unnnic-font-size-body-sm, 13px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
}

/* BEM: Element - select */
.filters__select {
  padding: 10px 14px;
  font-size: var(--unnnic-font-size-body-md, 14px);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-sm, 8px);
  background: var(--unnnic-color-background-snow, #fff);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
  cursor: pointer;
  width: 100%;
  min-width: 0;
  transition: all 0.2s;
}

.filters__select:hover {
  border-color: #dd1259;
}

.filters__select:focus {
  outline: none;
  border-color: #dd1259;
  box-shadow: 0 0 0 3px rgb(247 25 99 / 10%);
}

/* BEM: Element - quarter-buttons */
.filters__quarter-buttons {
  display: flex;
  gap: 0;
}

/* BEM: Element - quarter-btn */
.filters__quarter-btn {
  padding: 10px 16px;
  font-size: var(--unnnic-font-size-body-md, 14px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  background: var(--unnnic-color-background-snow, #fff);
  color: var(--unnnic-color-neutral-cloudy, #67738b);
  cursor: pointer;
  transition: all 0.2s;
}

.filters__quarter-btn:first-child {
  border-radius: var(--unnnic-border-radius-sm, 8px) 0 0
    var(--unnnic-border-radius-sm, 8px);
}

.filters__quarter-btn:last-child {
  border-radius: 0 var(--unnnic-border-radius-sm, 8px)
    var(--unnnic-border-radius-sm, 8px) 0;
}

.filters__quarter-btn:not(:last-child) {
  border-right: none;
}

.filters__quarter-btn:hover {
  background: var(--unnnic-color-neutral-light, #f5f5f5);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
}

.filters__quarter-btn:not(:first-child, :last-child) {
  border-radius: 0;
}

/* BEM: Modifier - active */
.filters__quarter-btn--active {
  background: #dd1259;
  border-color: #dd1259;
  color: var(--unnnic-color-background-snow, #fff);
}

/* BEM: Modifier - quarter */
.filters__group--quarter {
  flex: 0 0 auto;
}

/* BEM: Modifier - modules */
.filters__group--modules {
  min-width: 0;
  position: relative;
}

/* BEM: Element - module-dropdown */
.filters__module-dropdown {
  position: relative;
}

/* BEM: Element - module-toggle */
.filters__module-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-width: 0;
  padding: 10px 14px;
  font-size: var(--unnnic-font-size-body-md, 14px);
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-sm, 8px);
  background: var(--unnnic-color-background-snow, #fff);
  color: var(--unnnic-color-neutral-black, #1a1a1a);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.filters__module-toggle:hover {
  border-color: #dd1259;
}

.filters__module-toggle:focus {
  outline: none;
  border-color: #dd1259;
  box-shadow: 0 0 0 3px rgb(247 25 99 / 10%);
}

/* BEM: Element - module-toggle-icon */
.filters__module-toggle-icon {
  transition: transform 0.2s;
  flex-shrink: 0;
  margin-left: 8px;
}

.filters__module-toggle-icon--open {
  transform: rotate(180deg);
}

/* BEM: Element - module-list */
.filters__module-list {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: auto;
  min-width: 220px;
  width: max-content;
  max-width: 360px;
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: var(--unnnic-spacing-stack-xs, 4px);
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid var(--unnnic-color-neutral-soft, #e8e8e8);
  border-radius: var(--unnnic-border-radius-sm, 8px);
  background: var(--unnnic-color-background-snow, #fff);
  box-shadow: 0 4px 12px rgb(0 0 0 / 10%);
}

/* BEM: Element - module-item */
.filters__module-item {
  display: flex;
  align-items: center;
  gap: var(--unnnic-spacing-inline-xs, 8px);
  padding: 8px 10px;
  border-radius: var(--unnnic-border-radius-sm, 6px);
  cursor: pointer;
  transition: background 0.2s;
}

.filters__module-item:hover {
  background: var(--unnnic-color-neutral-light, #f5f5f5);
}

/* BEM: Element - module-checkbox */
.filters__module-checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  flex-shrink: 0;
  appearance: none;
  border: 2px solid var(--unnnic-color-neutral-cleanest, #d0d3d9);
  border-radius: 3px;
  background-color: var(--unnnic-color-background-snow, #fff);
  position: relative;
  transition: all 0.2s ease;
}

.filters__module-checkbox:hover {
  border-color: #F71963;
}

.filters__module-checkbox:checked {
  background-color: #dd1259;
  border-color: #dd1259;
}

.filters__module-checkbox:checked::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: solid var(--unnnic-color-background-snow, #fff);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.filters__module-checkbox:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgb(247 25 99 / 20%);
}

/* BEM: Element - module-label */
.filters__module-label {
  font-size: var(--unnnic-font-size-body-md, 14px);
  color: var(--unnnic-color-neutral-dark, #4a4a4a);
  cursor: pointer;
  user-select: none;
}

/* BEM: Element - clear-btn */
.filters__clear-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  font-size: var(--unnnic-font-size-body-md, 14px);
  font-weight: var(--unnnic-font-weight-medium, 500);
  border: none;
  background: transparent;
  color: var(--unnnic-color-aux-red-500, #e53e3e);
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 21px; /* Align with selects */
}

.filters__clear-btn:hover {
  background: var(--unnnic-color-aux-red-100, #fff5f5);
  border-radius: var(--unnnic-border-radius-sm, 8px);
}

/* Truncate label text in dropdowns when space is tight */
.filters__module-toggle > span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Responsive — tablet: wrap into 2 columns */
@media (width <= 1024px) {
  .filters__container {
    flex-wrap: wrap;
    gap: 16px;
  }

  .filters__group {
    flex: 1 1 calc(50% - 8px);
  }

  .filters__group--quarter {
    flex: 1 1 100%;
  }

  .filters__quarter-buttons {
    width: 100%;
  }

  .filters__quarter-btn {
    flex: 1;
  }

  .filters__clear-btn {
    margin-top: 0;
    justify-content: center;
  }
}

/* Responsive — mobile: single column */
@media (width <= 600px) {
  .filters__container {
    flex-direction: column;
    align-items: stretch;
  }

  .filters__group,
  .filters__group--quarter,
  .filters__group--modules {
    flex: 1 1 100%;
    width: 100%;
  }
}
</style>
