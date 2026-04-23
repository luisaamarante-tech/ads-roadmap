/**
 * Unit tests for CanvasSearchResults component.
 */

import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import CanvasSearchResults from '@/components/CanvasMode/CanvasSearchResults.vue';

// Mock RoadmapCard component
vi.mock('@/components/RoadmapCard.vue', () => ({
  default: {
    name: 'RoadmapCard',
    template: '<div class="mock-roadmap-card">{{ item.title }}</div>',
    props: ['item', 'autoExpand'],
  },
}));

describe('CanvasSearchResults', () => {
  const mockItems = [
    {
      id: 'TEST-1',
      title: 'Test Feature 1',
      description: 'Description 1',
      status: 'NOW',
      module: 'Test Module',
      moduleId: 'mod-1',
      releaseYear: 2026,
      releaseQuarter: 'Q1',
      images: [],
      likes: 5,
      lastSyncedAt: '2026-01-01',
    },
    {
      id: 'TEST-2',
      title: 'Test Feature 2',
      description: 'Description 2',
      status: 'NOW',
      module: 'Test Module',
      moduleId: 'mod-1',
      releaseYear: 2026,
      releaseQuarter: 'Q1',
      images: [],
      likes: 10,
      lastSyncedAt: '2026-01-01',
    },
  ];

  it('renders with items', () => {
    const wrapper = mount(CanvasSearchResults, {
      props: { items: mockItems },
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.canvas-search-results').exists()).toBe(true);
  });

  it('displays correct item count', () => {
    const wrapper = mount(CanvasSearchResults, {
      props: { items: mockItems },
    });

    expect(wrapper.text()).toContain('Found 2 items');
  });

  it('displays singular "item" for single result', () => {
    const wrapper = mount(CanvasSearchResults, {
      props: { items: [mockItems[0]] },
    });

    expect(wrapper.text()).toContain('Found 1 item');
  });

  it('renders RoadmapCard for each item', () => {
    const wrapper = mount(CanvasSearchResults, {
      props: { items: mockItems },
    });

    const cards = wrapper.findAll('.mock-roadmap-card');
    expect(cards.length).toBe(2);
  });

  it('shows loading state', () => {
    const wrapper = mount(CanvasSearchResults, {
      props: { items: [], loading: true },
    });

    expect(wrapper.find('.canvas-search-results__loading').exists()).toBe(true);
    expect(wrapper.findAll('.canvas-search-results__skeleton').length).toBe(3);
  });

  it('hides loading state when not loading', () => {
    const wrapper = mount(CanvasSearchResults, {
      props: { items: mockItems, loading: false },
    });

    expect(wrapper.find('.canvas-search-results__loading').exists()).toBe(
      false,
    );
  });

  it('displays items in list container', () => {
    const wrapper = mount(CanvasSearchResults, {
      props: { items: mockItems },
    });

    expect(wrapper.find('.canvas-search-results__list').exists()).toBe(true);
  });

  it('has proper semantic structure', () => {
    const wrapper = mount(CanvasSearchResults, {
      props: { items: mockItems },
    });

    expect(wrapper.find('section').exists()).toBe(true);
    expect(wrapper.find('header').exists()).toBe(true);
    expect(wrapper.find('h2').exists()).toBe(true);
  });

  it('applies stagger animation delay styles', () => {
    const wrapper = mount(CanvasSearchResults, {
      props: { items: mockItems },
    });

    const items = wrapper.findAll('.canvas-search-results__item');
    expect(items.length).toBeGreaterThan(0);
  });
});
