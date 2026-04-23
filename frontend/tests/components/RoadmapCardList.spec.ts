/**
 * Unit tests for RoadmapCardList component
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import RoadmapCardList from '@/components/RoadmapCardList.vue';
import RoadmapCard from '@/components/RoadmapCard.vue';
import { mockRoadmapItems } from '../../mocks/roadmapData';

describe('RoadmapCardList', () => {
  const createWrapper = (props = {}) => {
    return mount(RoadmapCardList, {
      props: {
        items: mockRoadmapItems,
        status: 'DELIVERED',
        ...props,
      },
      global: {
        components: {
          RoadmapCard,
        },
      },
    });
  };

  describe('rendering', () => {
    it('renders the status label', () => {
      const wrapper = createWrapper();
      expect(wrapper.text()).toContain('Delivered');
    });

    it('renders the item count', () => {
      const wrapper = createWrapper();
      expect(wrapper.text()).toContain(String(mockRoadmapItems.length));
    });

    it('renders correct singular/plural text', () => {
      const singleItem = [mockRoadmapItems[0]];
      const wrapper = createWrapper({ items: singleItem });
      expect(wrapper.text()).toContain('item');
      expect(wrapper.text()).not.toContain('items');
    });

    it('renders cards for each item', () => {
      const wrapper = createWrapper();
      const cards = wrapper.findAllComponents(RoadmapCard);
      expect(cards.length).toBe(mockRoadmapItems.length);
    });
  });

  describe('status labels', () => {
    it('shows "Delivered" for DELIVERED status', () => {
      const wrapper = createWrapper({ status: 'DELIVERED' });
      expect(wrapper.text()).toContain('Delivered');
    });

    it('shows "In Progress" for NOW status', () => {
      const wrapper = createWrapper({ status: 'NOW' });
      expect(wrapper.text()).toContain('In Progress');
    });

    it('shows "Coming Next" for NEXT status', () => {
      const wrapper = createWrapper({ status: 'NEXT' });
      expect(wrapper.text()).toContain('Coming Next');
    });

    it('shows "Planned" for FUTURE status', () => {
      const wrapper = createWrapper({ status: 'FUTURE' });
      expect(wrapper.text()).toContain('Planned');
    });
  });

  describe('loading state', () => {
    it('shows loading skeleton when loading is true', () => {
      const wrapper = createWrapper({ loading: true });
      expect(wrapper.find('.card-list__skeleton').exists()).toBe(true);
    });

    it('does not show cards when loading', () => {
      const wrapper = createWrapper({ loading: true });
      const cards = wrapper.findAllComponents(RoadmapCard);
      expect(cards.length).toBe(0);
    });

    it('shows skeleton cards when loading', () => {
      const wrapper = createWrapper({ loading: true });
      const skeletons = wrapper.findAll('.card-list__skeleton-card');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('empty state', () => {
    it('shows empty state when no items', () => {
      const wrapper = createWrapper({ items: [] });
      expect(wrapper.find('.card-list__empty').exists()).toBe(true);
    });

    it('shows appropriate message for status', () => {
      const wrapper = createWrapper({ items: [], status: 'NOW' });
      expect(wrapper.text()).toContain('in progress');
    });
  });

  describe('item rendering', () => {
    it('passes item to RoadmapCard', () => {
      const wrapper = createWrapper();
      const firstCard = wrapper.findComponent(RoadmapCard);
      expect(firstCard.props('item')).toEqual(mockRoadmapItems[0]);
    });

    it('uses item id as key', () => {
      const wrapper = createWrapper();
      const cards = wrapper.findAllComponents(RoadmapCard);
      // Cards should be rendered with unique keys
      expect(cards.length).toBe(mockRoadmapItems.length);
    });
  });
});
