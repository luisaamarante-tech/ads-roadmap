/**
 * Unit tests for CanvasEmptyState component.
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import CanvasEmptyState from '@/components/CanvasMode/CanvasEmptyState.vue';

describe('CanvasEmptyState', () => {
  it('renders with default props', () => {
    const wrapper = mount(CanvasEmptyState);

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.canvas-empty-state').exists()).toBe(true);
  });

  it('displays search prompt message', () => {
    const wrapper = mount(CanvasEmptyState);

    expect(wrapper.text()).toContain('Ask me about the roadmap');
  });

  it('displays icon element', () => {
    const wrapper = mount(CanvasEmptyState);

    expect(wrapper.find('.canvas-empty-state__icon').exists()).toBe(true);
  });

  it('displays suggestion text', () => {
    const wrapper = mount(CanvasEmptyState);

    expect(wrapper.text()).toContain('Try asking');
  });

  it('shows "no results" state when noResults prop is true', () => {
    const wrapper = mount(CanvasEmptyState, {
      props: { noResults: true },
    });

    expect(wrapper.text()).toContain('No matching items');
  });

  it('shows "searching" state when searching prop is true', () => {
    const wrapper = mount(CanvasEmptyState, {
      props: { searching: true },
    });

    expect(wrapper.find('.canvas-empty-state--searching').exists()).toBe(true);
  });

  it('has proper semantic structure', () => {
    const wrapper = mount(CanvasEmptyState);

    expect(wrapper.find('section').exists()).toBe(true);
    expect(wrapper.find('h2').exists()).toBe(true);
  });

  it('applies BEM classes correctly', () => {
    const wrapper = mount(CanvasEmptyState);

    expect(wrapper.find('.canvas-empty-state__title').exists()).toBe(true);
    expect(wrapper.find('.canvas-empty-state__description').exists()).toBe(
      true,
    );
  });
});
