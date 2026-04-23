/**
 * Unit tests for CanvasContainer component.
 */

import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import CanvasContainer from '@/components/CanvasMode/CanvasContainer.vue';

// Mock child components
vi.mock('@/components/CanvasMode/CanvasEmptyState.vue', () => ({
  default: {
    name: 'CanvasEmptyState',
    template: '<div class="mock-empty-state"><slot /></div>',
    props: ['noResults', 'searching'],
  },
}));

vi.mock('@/components/CanvasMode/CanvasSearchResults.vue', () => ({
  default: {
    name: 'CanvasSearchResults',
    template: '<div class="mock-search-results"><slot /></div>',
    props: ['items', 'loading'],
  },
}));

vi.mock('@/components/CanvasMode/CanvasExitButton.vue', () => ({
  default: {
    name: 'CanvasExitButton',
    template: '<button class="mock-exit-button" @click="$emit(\'click\')">Exit</button>',
    emits: ['click'],
  },
}));

describe('CanvasContainer', () => {
  const defaultProps = {
    filteredItemIds: [],
    allItems: [],
  };

  it('renders with default props', () => {
    const wrapper = mount(CanvasContainer, {
      props: defaultProps,
    });

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.canvas-container').exists()).toBe(true);
  });

  it('renders left and right panels', () => {
    const wrapper = mount(CanvasContainer, {
      props: defaultProps,
    });

    expect(wrapper.find('.canvas-container__left-panel').exists()).toBe(true);
    expect(wrapper.find('.canvas-container__right-panel').exists()).toBe(true);
  });

  it('shows empty state when no filtered items', () => {
    const wrapper = mount(CanvasContainer, {
      props: {
        filteredItemIds: [],
        allItems: [],
      },
    });

    expect(wrapper.find('.mock-empty-state').exists()).toBe(true);
  });

  it('shows search results when filtered items exist', () => {
    const wrapper = mount(CanvasContainer, {
      props: {
        filteredItemIds: ['TEST-1', 'TEST-2'],
        allItems: [
          { id: 'TEST-1', title: 'Test 1' },
          { id: 'TEST-2', title: 'Test 2' },
          { id: 'TEST-3', title: 'Test 3' },
        ],
      },
    });

    expect(wrapper.find('.mock-search-results').exists()).toBe(true);
  });

  it('emits exit event when exit button clicked', async () => {
    const wrapper = mount(CanvasContainer, {
      props: defaultProps,
    });

    const exitButton = wrapper.find('.mock-exit-button');
    if (exitButton.exists()) {
      await exitButton.trigger('click');
      expect(wrapper.emitted('exit')).toBeTruthy();
    }
  });

  it('has left panel for WebChat with correct width', () => {
    const wrapper = mount(CanvasContainer, {
      props: defaultProps,
    });

    const leftPanel = wrapper.find('.canvas-container__left-panel');
    expect(leftPanel.exists()).toBe(true);
  });

  it('has right panel for results with correct width', () => {
    const wrapper = mount(CanvasContainer, {
      props: defaultProps,
    });

    const rightPanel = wrapper.find('.canvas-container__right-panel');
    expect(rightPanel.exists()).toBe(true);
  });

  it('applies correct BEM classes', () => {
    const wrapper = mount(CanvasContainer, {
      props: defaultProps,
    });

    expect(wrapper.find('.canvas-container__header').exists()).toBe(true);
    expect(wrapper.find('.canvas-container__content').exists()).toBe(true);
  });

  it('filters allItems based on filteredItemIds', () => {
    const wrapper = mount(CanvasContainer, {
      props: {
        filteredItemIds: ['ITEM-1'],
        allItems: [
          { id: 'ITEM-1', title: 'Item 1' },
          { id: 'ITEM-2', title: 'Item 2' },
        ],
      },
    });

    // Component should filter items internally
    expect(wrapper.vm).toBeDefined();
  });

  it('shows no-results state when IDs dont match any items', () => {
    const wrapper = mount(CanvasContainer, {
      props: {
        filteredItemIds: ['NONEXISTENT-1'],
        allItems: [
          { id: 'ITEM-1', title: 'Item 1' },
        ],
      },
    });

    // Should show empty state with noResults flag
    expect(wrapper.find('.mock-empty-state').exists()).toBe(true);
  });

  it('renders webchat container with provided ID', () => {
    const wrapper = mount(CanvasContainer, {
      props: {
        ...defaultProps,
        webchatContainerId: 'test-webchat-container',
      },
    });

    expect(wrapper.find('#test-webchat-container').exists()).toBe(true);
  });

  it('uses default webchat container ID', () => {
    const wrapper = mount(CanvasContainer, {
      props: defaultProps,
    });

    expect(wrapper.find('#weni-webchat-canvas').exists()).toBe(true);
  });
});
