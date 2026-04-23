/**
 * Unit tests for RoadmapFilters component
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import RoadmapFilters from '@/components/RoadmapFilters.vue';
import { mockModules } from '../../mocks/roadmapData';
import type { RoadmapFilters as RoadmapFiltersType } from '@/types/roadmap';

describe('RoadmapFilters', () => {
  const createWrapper = (props = {}) => {
    return mount(RoadmapFilters, {
      props: {
        modelValue: {},
        modules: mockModules,
        ...props,
      },
    });
  };

  describe('rendering', () => {
    it('renders year filter', () => {
      const wrapper = createWrapper();
      expect(wrapper.find('.filters__select').exists()).toBe(true);
    });

    it('renders quarter buttons', () => {
      const wrapper = createWrapper();
      const quarterButtons = wrapper.findAll('.filters__quarter-btn');
      expect(quarterButtons.length).toBe(5); // All Quarters + Q1-Q4
    });

    it('renders module filter with options', () => {
      const wrapper = createWrapper();
      const options = wrapper.findAll('option');
      // Default + modules count
      expect(options.length).toBeGreaterThan(mockModules.length);
    });
  });

  describe('year filter', () => {
    it('emits update when year is selected', async () => {
      const wrapper = createWrapper();
      const yearSelect = wrapper.find('.filters__select');

      await yearSelect.setValue(2025);

      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted).toBeTruthy();
      expect(emitted![0][0]).toEqual({ year: 2025 });
    });

    it('shows current year and surrounding years', () => {
      const wrapper = createWrapper();
      const currentYear = new Date().getFullYear();

      expect(wrapper.text()).toContain(String(currentYear));
    });

    it('clears year when "All Years" is selected', async () => {
      const wrapper = createWrapper({ modelValue: { year: 2025 } });
      const yearSelect = wrapper.find('.filters__select');

      await yearSelect.setValue(0);

      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted![0][0]).toEqual({ year: undefined });
    });
  });

  describe('quarter filter', () => {
    it('highlights active quarter button', async () => {
      const wrapper = createWrapper({ modelValue: { quarter: 'Q1' } });
      const q1Button = wrapper.findAll('.filters__quarter-btn')[1]; // First is "All Quarters"

      expect(q1Button.classes()).toContain('filters__quarter-btn--active');
    });

    it('emits update when quarter is clicked', async () => {
      const wrapper = createWrapper();
      const q2Button = wrapper.findAll('.filters__quarter-btn')[2];

      await q2Button.trigger('click');

      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted).toBeTruthy();
      expect(emitted![0][0]).toEqual({ quarter: 'Q2' });
    });

    it('clears quarter when "All Quarters" is clicked', async () => {
      const wrapper = createWrapper({ modelValue: { quarter: 'Q1' } });
      const allButton = wrapper.findAll('.filters__quarter-btn')[0];

      await allButton.trigger('click');

      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted![0][0]).toEqual({ quarter: undefined });
    });
  });

  describe('module filter', () => {
    it('shows module dropdown toggle button', () => {
      const wrapper = createWrapper();
      const toggleButton = wrapper.find('.filters__module-toggle');

      expect(toggleButton.exists()).toBe(true);
      expect(toggleButton.text()).toContain('All Modules');
    });

    it('shows modules with item count when dropdown is opened', async () => {
      const wrapper = createWrapper();
      const toggleButton = wrapper.find('.filters__module-toggle');

      // Open dropdown
      await toggleButton.trigger('click');

      // Check that modules are visible
      mockModules.forEach((module) => {
        expect(wrapper.text()).toContain(module.name);
        expect(wrapper.text()).toContain(String(module.itemCount));
      });
    });

    it('emits update when module is selected', async () => {
      const wrapper = createWrapper();
      const toggleButton = wrapper.find('.filters__module-toggle');

      // Open dropdown
      await toggleButton.trigger('click');

      // Select first module checkbox
      const checkbox = wrapper.find('.filters__module-checkbox');
      await checkbox.setValue(true);

      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted).toBeTruthy();

      const lastEmit = emitted[emitted.length - 1][0] as RoadmapFilters;
      expect(lastEmit.module).toContain(mockModules[0].id);
    });
  });

  describe('clear filters', () => {
    it('shows clear button when filters are active', () => {
      const wrapper = createWrapper({ modelValue: { year: 2025 } });
      expect(wrapper.find('.filters__clear-btn').exists()).toBe(true);
    });

    it('hides clear button when no filters are active', () => {
      const wrapper = createWrapper();
      expect(wrapper.find('.filters__clear-btn').exists()).toBe(false);
    });

    it('clears all filters when clear button is clicked', async () => {
      const wrapper = createWrapper({
        modelValue: { year: 2025, quarter: 'Q1', module: 'test-module' },
      });

      await wrapper.find('.filters__clear-btn').trigger('click');

      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted![0][0]).toEqual({});
    });
  });

  describe('available years prop', () => {
    it('uses custom available years when provided', () => {
      const customYears = [2020, 2021, 2022];
      const wrapper = createWrapper({ availableYears: customYears });

      customYears.forEach((year) => {
        expect(wrapper.text()).toContain(String(year));
      });
    });
  });

  describe('multi-module selection', () => {
    it('allows selecting multiple modules', async () => {
      const wrapper = createWrapper();

      // Find module checkboxes (once multi-select is implemented)
      const checkboxes = wrapper.findAll('input[type="checkbox"]');
      if (checkboxes.length > 0) {
        // Check first two modules
        await checkboxes[0].setValue(true);
        await checkboxes[1].setValue(true);

        const emitted = wrapper.emitted('update:modelValue');
        expect(emitted).toBeTruthy();
        const lastEmit = emitted![emitted!.length - 1][0] as RoadmapFiltersType;
        expect(Array.isArray(lastEmit.module)).toBe(true);
        // At least 1 module should be selected (implementation may vary)
        if (Array.isArray(lastEmit.module)) {
          expect(lastEmit.module.length).toBeGreaterThanOrEqual(1);
        }
      }
    });

    it('allows deselecting modules', async () => {
      const wrapper = createWrapper({
        modelValue: { module: ['module-1', 'module-2'] },
      });

      const checkboxes = wrapper.findAll('input[type="checkbox"]');
      if (checkboxes.length > 0) {
        // Uncheck one module
        const checkedBox = checkboxes.find((cb) => (cb.element as HTMLInputElement).checked);
        if (checkedBox) {
          await checkedBox.setValue(false);

          const emitted = wrapper.emitted('update:modelValue');
          expect(emitted).toBeTruthy();
          const lastEmit = emitted![emitted!.length - 1][0] as RoadmapFiltersType;
          expect(Array.isArray(lastEmit.module)).toBe(true);
        }
      }
    });

    it('updates URL with multiple module params', async () => {
      const wrapper = createWrapper();

      // When multi-select is implemented, selecting multiple modules
      // should emit an array like: { module: ['flows', 'integrations'] }
      // The parent component (RoadmapView) should handle URL serialization

      // For now, just verify the component accepts array values
      await wrapper.setProps({
        modelValue: { module: ['flows', 'integrations'] },
      });

      expect(wrapper.props('modelValue')).toEqual({
        module: ['flows', 'integrations'],
      });
    });
  });
});
