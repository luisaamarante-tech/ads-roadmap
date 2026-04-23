/**
 * Unit tests for CanvasExitButton component.
 */

import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import CanvasExitButton from '@/components/CanvasMode/CanvasExitButton.vue';

describe('CanvasExitButton', () => {
  it('renders correctly', () => {
    const wrapper = mount(CanvasExitButton);

    expect(wrapper.exists()).toBe(true);
    expect(wrapper.find('.canvas-exit-button').exists()).toBe(true);
  });

  it('displays exit text', () => {
    const wrapper = mount(CanvasExitButton);

    expect(wrapper.text()).toContain('Exit Search');
  });

  it('has accessible label', () => {
    const wrapper = mount(CanvasExitButton);

    expect(wrapper.find('button').attributes('aria-label')).toBe(
      'Exit canvas search mode',
    );
  });

  it('emits click event when clicked', async () => {
    const wrapper = mount(CanvasExitButton);

    await wrapper.find('button').trigger('click');

    expect(wrapper.emitted('click')).toBeTruthy();
    expect(wrapper.emitted('click')?.length).toBe(1);
  });

  it('has icon element', () => {
    const wrapper = mount(CanvasExitButton);

    expect(wrapper.find('.canvas-exit-button__icon').exists()).toBe(true);
  });

  it('has proper button type', () => {
    const wrapper = mount(CanvasExitButton);

    expect(wrapper.find('button').attributes('type')).toBe('button');
  });

  it('applies BEM classes correctly', () => {
    const wrapper = mount(CanvasExitButton);

    expect(wrapper.find('.canvas-exit-button__text').exists()).toBe(true);
    expect(wrapper.find('.canvas-exit-button__icon').exists()).toBe(true);
  });
});
