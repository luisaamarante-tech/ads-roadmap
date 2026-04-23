/**
 * Unit tests for RoadmapTabs component
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import RoadmapTabs from '@/components/RoadmapTabs.vue';
import { mockStats } from '../../mocks/roadmapData';

describe('RoadmapTabs', () => {
  const createWrapper = (props = {}) => {
    return mount(RoadmapTabs, {
      props: {
        modelValue: 'DELIVERED',
        stats: mockStats,
        ...props,
      },
    });
  };

  describe('rendering', () => {
    it('renders all status tabs', () => {
      const wrapper = createWrapper();
      const tabs = wrapper.findAll('.tabs__tab');
      expect(tabs.length).toBe(4);
    });

    it('renders tab labels', () => {
      const wrapper = createWrapper();
      expect(wrapper.text()).toContain('Delivered');
      expect(wrapper.text()).toContain('Now');
      expect(wrapper.text()).toContain('Next');
      expect(wrapper.text()).toContain('Future');
    });

    it('renders counts when stats provided', () => {
      const wrapper = createWrapper();
      expect(wrapper.text()).toContain(String(mockStats.DELIVERED));
      expect(wrapper.text()).toContain(String(mockStats.NOW));
    });

    it('does not render counts when stats is null', () => {
      const wrapper = createWrapper({ stats: null });
      const counts = wrapper.findAll('.tabs__count');
      expect(counts.length).toBe(0);
    });
  });

  describe('active state', () => {
    it('marks active tab correctly', () => {
      const wrapper = createWrapper({ modelValue: 'NOW' });
      const tabs = wrapper.findAll('.tabs__tab');
      const nowTab = tabs[1];

      expect(nowTab.classes()).toContain('tabs__tab--active');
    });

    it('only one tab is active at a time', () => {
      const wrapper = createWrapper();
      const activeTabs = wrapper.findAll('.tabs__tab--active');
      expect(activeTabs.length).toBe(1);
    });
  });

  describe('tab interaction', () => {
    it('emits update when tab is clicked', async () => {
      const wrapper = createWrapper();
      const tabs = wrapper.findAll('.tabs__tab');

      await tabs[1].trigger('click'); // NOW tab

      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted).toBeTruthy();
      expect(emitted![0][0]).toBe('NOW');
    });

    it('updates active state when different tab clicked', async () => {
      const wrapper = createWrapper({ modelValue: 'DELIVERED' });
      const tabs = wrapper.findAll('.tabs__tab');

      await tabs[2].trigger('click'); // NEXT tab

      const emitted = wrapper.emitted('update:modelValue');
      expect(emitted![0][0]).toBe('NEXT');
    });
  });

  describe('tab descriptions', () => {
    it('has title attribute for accessibility', () => {
      const wrapper = createWrapper();
      const tabs = wrapper.findAll('.tabs__tab');

      tabs.forEach((tab) => {
        expect(tab.attributes('title')).toBeTruthy();
      });
    });
  });

  describe('count display', () => {
    it('shows count for each status', () => {
      const wrapper = createWrapper({ stats: mockStats });
      const counts = wrapper.findAll('.tabs__count');

      expect(counts.length).toBe(4);
    });

    it('applies active styling to count on active tab', () => {
      const wrapper = createWrapper({ modelValue: 'DELIVERED' });
      const activeTab = wrapper.find('.tabs__tab--active');
      const activeCount = activeTab.find('.tabs__count');

      expect(activeCount.exists()).toBe(true);
    });
  });

  describe('all statuses', () => {
    it('handles DELIVERED status', async () => {
      const wrapper = createWrapper();
      const deliveredTab = wrapper.findAll('.tabs__tab')[0];

      await deliveredTab.trigger('click');

      expect(wrapper.emitted('update:modelValue')![0][0]).toBe('DELIVERED');
    });

    it('handles NOW status', async () => {
      const wrapper = createWrapper();
      const nowTab = wrapper.findAll('.tabs__tab')[1];

      await nowTab.trigger('click');

      expect(wrapper.emitted('update:modelValue')![0][0]).toBe('NOW');
    });

    it('handles NEXT status', async () => {
      const wrapper = createWrapper();
      const nextTab = wrapper.findAll('.tabs__tab')[2];

      await nextTab.trigger('click');

      expect(wrapper.emitted('update:modelValue')![0][0]).toBe('NEXT');
    });

    it('handles FUTURE status', async () => {
      const wrapper = createWrapper();
      const futureTab = wrapper.findAll('.tabs__tab')[3];

      await futureTab.trigger('click');

      expect(wrapper.emitted('update:modelValue')![0][0]).toBe('FUTURE');
    });
  });
});
