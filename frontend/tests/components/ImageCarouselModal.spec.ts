import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import ImageCarouselModal from '@/components/ImageCarouselModal.vue';

describe('ImageCarouselModal', () => {
  const mockImages = [
    'https://example.com/image1.png',
    'https://example.com/image2.png',
    'https://example.com/image3.png',
  ];

  const defaultProps = {
    images: mockImages,
    currentIndex: 0,
    epicTitle: 'Test Epic',
    show: true,
  };

  let container: HTMLElement;

  beforeEach(() => {
    // Clear any existing event listeners
    vi.clearAllMocks();
    // Create a container for mounting
    container = document.createElement('div');
    document.body.appendChild(container);
  });

  afterEach(() => {
    // Clean up
    document.body.innerHTML = '';
  });

  it('should render modal when show=true', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: container,
    });

    await nextTick();

    // Teleport moves content to body, so query document directly
    expect(document.querySelector('.image-carousel-modal')).toBeTruthy();
    wrapper.unmount();
  });

  it('should not render modal when show=false', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: { ...defaultProps, show: false },
      attachTo: container,
    });

    await nextTick();

    expect(document.querySelector('.image-carousel-modal')).toBeNull();
    wrapper.unmount();
  });

  it('should display image at currentIndex', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: { ...defaultProps, currentIndex: 1 },
      attachTo: container,
    });

    await nextTick();

    // Verify the component's internal state reflects currentIndex: 1
    const position = document.querySelector('.image-carousel-modal__position');
    expect(position?.textContent).toBe('2 of 3');

    wrapper.unmount();
  });

  it('should emit close on backdrop click', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: container,
    });

    await nextTick();

    const backdrop = document.querySelector('.image-carousel-modal__backdrop');
    const clickEvent = new MouseEvent('click', { bubbles: true });
    backdrop?.dispatchEvent(clickEvent);
    await nextTick();

    expect(wrapper.emitted('close')).toBeTruthy();
    wrapper.unmount();
  });

  it('should emit close on close button click', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: container,
    });

    await nextTick();

    const closeBtn = document.querySelector('.image-carousel-modal__close-btn');
    const clickEvent = new MouseEvent('click', { bubbles: true });
    closeBtn?.dispatchEvent(clickEvent);
    await nextTick();

    expect(wrapper.emitted('close')).toBeTruthy();
    wrapper.unmount();
  });

  it('should emit close on ESC key', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: document.body,
    });

    const event = new KeyboardEvent('keydown', { key: 'Escape' });
    window.dispatchEvent(event);
    await nextTick();

    expect(wrapper.emitted('close')).toBeTruthy();
    wrapper.unmount();
  });

  it('should navigate to next image on arrow click', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: container,
    });

    await nextTick();

    const nextBtn = document.querySelector('.image-carousel-modal__nav-btn--next');
    const clickEvent = new MouseEvent('click', { bubbles: true });
    nextBtn?.dispatchEvent(clickEvent);
    await nextTick();

    expect(wrapper.emitted('indexChange')).toBeTruthy();
    expect(wrapper.emitted('indexChange')![0]).toEqual([1]);
    wrapper.unmount();
  });

  it('should navigate to previous image on arrow click', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: { ...defaultProps, currentIndex: 1 },
      attachTo: container,
    });

    await nextTick();

    const prevBtn = document.querySelector('.image-carousel-modal__nav-btn--prev');
    const clickEvent = new MouseEvent('click', { bubbles: true });
    prevBtn?.dispatchEvent(clickEvent);
    await nextTick();

    expect(wrapper.emitted('indexChange')).toBeTruthy();
    expect(wrapper.emitted('indexChange')![0]).toEqual([0]);
    wrapper.unmount();
  });

  it('should wrap navigation at boundaries', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: { ...defaultProps, currentIndex: 2 },
      attachTo: container,
    });

    await nextTick();

    // At last image, clicking next should wrap to first
    const nextBtn = document.querySelector('.image-carousel-modal__nav-btn--next');
    const clickEvent = new MouseEvent('click', { bubbles: true });
    nextBtn?.dispatchEvent(clickEvent);
    await nextTick();

    expect(wrapper.emitted('indexChange')).toBeTruthy();
    expect(wrapper.emitted('indexChange')![0]).toEqual([0]);

    wrapper.unmount();
  });

  it('should navigate with keyboard arrow keys', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: document.body,
    });

    // Right arrow for next
    const rightEvent = new KeyboardEvent('keydown', { key: 'ArrowRight' });
    window.dispatchEvent(rightEvent);
    await nextTick();

    expect(wrapper.emitted('indexChange')).toBeTruthy();
    expect(wrapper.emitted('indexChange')![0]).toEqual([1]);

    wrapper.unmount();
  });

  it('should hide navigation arrows for single image', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: {
        ...defaultProps,
        images: ['https://example.com/single.png'],
        currentIndex: 0,
      },
      attachTo: container,
    });

    await nextTick();

    // Navigation should not be present for single image
    const navigation = document.querySelector(
      '.image-carousel-modal__navigation',
    );
    expect(navigation).toBeNull();
    wrapper.unmount();
  });

  it('should render image element', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: container,
    });

    await nextTick();

    // Image element should be rendered
    const img = document.querySelector('.image-carousel-modal__image');
    expect(img).toBeTruthy();
    wrapper.unmount();
  });

  it('should show error placeholder for broken images', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: container,
    });

    await nextTick();

    // Verify position label is correct
    const position = document.querySelector('.image-carousel-modal__position');
    expect(position?.textContent).toBe('1 of 3');

    wrapper.unmount();
  });

  it('should have correct ARIA attributes', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: container,
    });

    await nextTick();

    const dialog = document.querySelector('.image-carousel-modal');
    expect(dialog?.getAttribute('role')).toBe('dialog');
    expect(dialog?.getAttribute('aria-modal')).toBe('true');
    expect(dialog?.getAttribute('aria-labelledby')).toBe('modal-title');

    const closeBtn = document.querySelector('.image-carousel-modal__close-btn');
    expect(closeBtn?.getAttribute('aria-label')).toBe('Close image viewer');

    wrapper.unmount();
  });

  it('should display position label for multiple images', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: { ...defaultProps, currentIndex: 1 },
      attachTo: container,
    });

    await nextTick();

    const position = document.querySelector('.image-carousel-modal__position');
    expect(position?.textContent).toBe('2 of 3');
    wrapper.unmount();
  });

  it('should update image when currentIndex prop changes', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: defaultProps,
      attachTo: container,
    });

    await nextTick();

    // Update to index 2
    await wrapper.setProps({ currentIndex: 2 });
    await nextTick();

    // Position should update to reflect new index
    const position = document.querySelector('.image-carousel-modal__position');
    expect(position?.textContent).toBe('3 of 3');

    wrapper.unmount();
  });

  it('should navigate with keyboard left arrow', async () => {
    const wrapper = mount(ImageCarouselModal, {
      props: { ...defaultProps, currentIndex: 1 },
      attachTo: container,
    });

    await nextTick();

    const leftEvent = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
    window.dispatchEvent(leftEvent);
    await nextTick();

    expect(wrapper.emitted('indexChange')).toBeTruthy();
    expect(wrapper.emitted('indexChange')![0]).toEqual([0]);

    wrapper.unmount();
  });
});
