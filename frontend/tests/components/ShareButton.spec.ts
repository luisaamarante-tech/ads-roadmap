import { describe, it, expect, beforeEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import ShareButton from '@/components/ShareButton.vue';

describe('ShareButton', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });

    Object.assign(window, {
      location: { origin: 'https://roadmap.weni.ai' },
    });
  });

  it('should render button with default props', () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123' },
    });

    expect(wrapper.find('.share-button').exists()).toBe(true);
    expect(wrapper.text()).toContain('Share');
  });

  it('should generate correct share URL', async () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-456' },
    });

    await wrapper.find('.share-button').trigger('click');
    await nextTick();

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      'https://roadmap.weni.ai/roadmap?epic=WENI-456',
    );
  });

  it('should emit copied event on success', async () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-789' },
    });

    await wrapper.find('.share-button').trigger('click');
    await nextTick();

    expect(wrapper.emitted('copied')).toBeTruthy();
    expect(wrapper.emitted('copied')![0]).toEqual([
      'https://roadmap.weni.ai/roadmap?epic=WENI-789',
    ]);
  });

  it('should show "Copied!" state after successful copy', async () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123' },
    });

    await wrapper.find('.share-button').trigger('click');
    await nextTick();

    expect(wrapper.text()).toContain('Copied!');
    expect(wrapper.find('.share-button--copied').exists()).toBe(true);
  });

  it('should disable button when epicId is empty', () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: '' },
    });

    const button = wrapper.find('.share-button');
    expect(button.attributes('disabled')).toBeDefined();
  });

  it('should apply size classes', () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123', size: 'large' },
    });

    expect(wrapper.find('.share-button--large').exists()).toBe(true);
  });

  it('should apply variant classes', () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123', variant: 'primary' },
    });

    expect(wrapper.find('.share-button--primary').exists()).toBe(true);
  });

  it('should show fallback when clipboard API fails', async () => {
    navigator.clipboard.writeText = vi
      .fn()
      .mockRejectedValue(new Error('Permission denied'));

    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123' },
    });

    await wrapper.find('.share-button').trigger('click');
    await nextTick();
    await nextTick();

    expect(wrapper.find('.share-button__fallback').exists()).toBe(true);
  });

  it('should emit copyError on failure', async () => {
    navigator.clipboard.writeText = vi
      .fn()
      .mockRejectedValue(new Error('Permission denied'));

    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123' },
    });

    await wrapper.find('.share-button').trigger('click');
    await nextTick();

    expect(wrapper.emitted('copyError')).toBeTruthy();
  });

  it('should have correct ARIA label', () => {
    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-999' },
    });

    const button = wrapper.find('.share-button');
    expect(button.attributes('aria-label')).toBe('Share link to epic WENI-999');
  });

  it('should close fallback when close button clicked', async () => {
    navigator.clipboard.writeText = vi
      .fn()
      .mockRejectedValue(new Error('Failed'));

    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123' },
    });

    // Trigger share to show fallback
    await wrapper.find('.share-button').trigger('click');
    await nextTick();
    await nextTick();

    expect(wrapper.find('.share-button__fallback').exists()).toBe(true);

    // Click close button
    await wrapper.find('.share-button__fallback-close').trigger('click');
    await nextTick();

    expect(wrapper.find('.share-button__fallback').exists()).toBe(false);
  });

  it('should select fallback input text on focus', async () => {
    navigator.clipboard.writeText = vi
      .fn()
      .mockRejectedValue(new Error('Failed'));

    const wrapper = mount(ShareButton, {
      props: { epicId: 'WENI-123' },
    });

    await wrapper.find('.share-button').trigger('click');
    await nextTick();
    await nextTick();

    const input = wrapper.find('.share-button__fallback-input');
    const selectSpy = vi.fn();
    (input.element as HTMLInputElement).select = selectSpy;

    await input.trigger('focus');

    expect(selectSpy).toHaveBeenCalled();
  });
});
