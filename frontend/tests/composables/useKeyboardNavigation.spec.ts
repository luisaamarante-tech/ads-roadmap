import { describe, it, expect, vi } from 'vitest';
import { ref } from 'vue';
import { mount } from '@vue/test-utils';
import { useKeyboardNavigation } from '@/composables/useKeyboardNavigation';

describe('useKeyboardNavigation', () => {
  it('should call onEscape when Escape key pressed', () => {
    const onEscape = vi.fn();

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onEscape });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'Escape' });
    window.dispatchEvent(event);

    expect(onEscape).toHaveBeenCalled();
  });

  it('should call onArrowLeft when ArrowLeft key pressed', () => {
    const onArrowLeft = vi.fn();

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onArrowLeft });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
    window.dispatchEvent(event);

    expect(onArrowLeft).toHaveBeenCalled();
  });

  it('should call onArrowRight when ArrowRight key pressed', () => {
    const onArrowRight = vi.fn();

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onArrowRight });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'ArrowRight' });
    window.dispatchEvent(event);

    expect(onArrowRight).toHaveBeenCalled();
  });

  it('should not call handlers when isActive is false', () => {
    const onEscape = vi.fn();
    const isActive = ref(false);

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onEscape }, { isActive });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'Escape' });
    window.dispatchEvent(event);

    expect(onEscape).not.toHaveBeenCalled();
  });

  it('should call handlers when isActive becomes true', () => {
    const onEscape = vi.fn();
    const isActive = ref(false);

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onEscape }, { isActive });
        return () => null;
      },
    };

    mount(TestComponent);

    isActive.value = true;

    const event = new KeyboardEvent('keydown', { key: 'Escape' });
    window.dispatchEvent(event);

    expect(onEscape).toHaveBeenCalled();
  });

  it('should call onHome when Home key pressed', () => {
    const onHome = vi.fn();

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onHome });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'Home' });
    window.dispatchEvent(event);

    expect(onHome).toHaveBeenCalled();
  });

  it('should call onEnd when End key pressed', () => {
    const onEnd = vi.fn();

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onEnd });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'End' });
    window.dispatchEvent(event);

    expect(onEnd).toHaveBeenCalled();
  });

  it('should call handler when preventDefault is false', () => {
    const onArrowLeft = vi.fn();

    const TestComponent = {
      setup() {
        useKeyboardNavigation({ onArrowLeft }, { preventDefault: false });
        return () => null;
      },
    };

    mount(TestComponent);

    const event = new KeyboardEvent('keydown', { key: 'ArrowLeft' });
    window.dispatchEvent(event);

    // Handler should still be called even when preventDefault is false
    expect(onArrowLeft).toHaveBeenCalled();
  });
});
