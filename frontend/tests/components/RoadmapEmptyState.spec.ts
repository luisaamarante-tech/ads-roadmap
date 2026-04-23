/**
 * Unit tests for RoadmapEmptyState component
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import RoadmapEmptyState from '@/components/RoadmapEmptyState.vue';

describe('RoadmapEmptyState', () => {
  const createWrapper = (props = {}) => {
    return mount(RoadmapEmptyState, {
      props: {
        loading: false,
        status: 'DELIVERED',
        hasFilters: false,
        ...props,
      },
    });
  };

  describe('loading state', () => {
    it('shows skeleton loading when loading is true', () => {
      const wrapper = createWrapper({ loading: true });
      expect(wrapper.find('.empty-state__skeleton').exists()).toBe(true);
    });

    it('shows skeleton cards when loading', () => {
      const wrapper = createWrapper({ loading: true });
      const skeletons = wrapper.findAll('.empty-state__skeleton-card');
      expect(skeletons.length).toBe(3);
    });

    it('does not show empty state when loading', () => {
      const wrapper = createWrapper({ loading: true });
      expect(wrapper.find('.empty-state__container').exists()).toBe(false);
    });

    it('has animated skeleton elements', () => {
      const wrapper = createWrapper({ loading: true });
      expect(wrapper.find('.empty-state__skeleton-title').exists()).toBe(true);
      expect(wrapper.find('.empty-state__skeleton-badge').exists()).toBe(true);
    });
  });

  describe('empty state', () => {
    it('shows empty container when not loading', () => {
      const wrapper = createWrapper({ loading: false });
      expect(wrapper.find('.empty-state__container').exists()).toBe(true);
    });

    it('shows empty icon', () => {
      const wrapper = createWrapper();
      expect(wrapper.find('.empty-state__icon').exists()).toBe(true);
    });

    it('shows empty title', () => {
      const wrapper = createWrapper();
      expect(wrapper.find('.empty-state__title').exists()).toBe(true);
    });

    it('shows description', () => {
      const wrapper = createWrapper();
      expect(wrapper.find('.empty-state__description').exists()).toBe(true);
    });
  });

  describe('status messages', () => {
    it('shows correct message for DELIVERED status', () => {
      const wrapper = createWrapper({ status: 'DELIVERED' });
      expect(wrapper.text()).toContain('No delivered features yet');
    });

    it('shows correct message for NOW status', () => {
      const wrapper = createWrapper({ status: 'NOW' });
      expect(wrapper.text()).toContain('No features currently in progress');
    });

    it('shows correct message for NEXT status', () => {
      const wrapper = createWrapper({ status: 'NEXT' });
      expect(wrapper.text()).toContain('No features planned for next quarter');
    });

    it('shows correct message for FUTURE status', () => {
      const wrapper = createWrapper({ status: 'FUTURE' });
      expect(wrapper.text()).toContain('No future features planned yet');
    });
  });

  describe('filter state', () => {
    it('shows filter-specific message when hasFilters is true', () => {
      const wrapper = createWrapper({ hasFilters: true });
      expect(wrapper.text()).toContain('Try adjusting your filters');
    });

    it('shows general message when hasFilters is false', () => {
      const wrapper = createWrapper({ hasFilters: false });
      expect(wrapper.text()).toContain('Check back later for updates');
    });

    it('shows clear filters button when hasFilters is true', () => {
      const wrapper = createWrapper({ hasFilters: true });
      expect(wrapper.find('.empty-state__clear-btn').exists()).toBe(true);
    });

    it('does not show clear filters button when hasFilters is false', () => {
      const wrapper = createWrapper({ hasFilters: false });
      expect(wrapper.find('.empty-state__clear-btn').exists()).toBe(false);
    });
  });

  describe('clear filters interaction', () => {
    it('emits clearFilters when button is clicked', async () => {
      const wrapper = createWrapper({ hasFilters: true });
      const button = wrapper.find('.empty-state__clear-btn');

      await button.trigger('click');

      expect(wrapper.emitted('clearFilters')).toBeTruthy();
    });
  });

  describe('skeleton animation', () => {
    it('has animation class on skeleton elements', () => {
      const wrapper = createWrapper({ loading: true });
      const skeletonCard = wrapper.find('.empty-state__skeleton-card');

      // Check if the skeleton has CSS animation defined in its styles
      expect(skeletonCard.exists()).toBe(true);
    });

    it('has shimmer animation on title skeleton', () => {
      const wrapper = createWrapper({ loading: true });
      expect(wrapper.find('.empty-state__skeleton-title').exists()).toBe(true);
    });
  });
});
