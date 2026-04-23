import { onMounted, onUnmounted, type Ref } from 'vue';

export interface UseKeyboardNavigationCallbacks {
  onEscape?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  onHome?: () => void;
  onEnd?: () => void;
}

export interface UseKeyboardNavigationOptions {
  isActive?: Ref<boolean>;
  preventDefault?: boolean;
}

/**
 * Composable for keyboard event handling in modals.
 */
export function useKeyboardNavigation(
  callbacks: UseKeyboardNavigationCallbacks,
  options: UseKeyboardNavigationOptions = {},
): void {
  const { isActive, preventDefault = true } = options;

  function handleKeydown(event: KeyboardEvent): void {
    // Check if navigation is active
    if (isActive && !isActive.value) {
      return;
    }

    const handlers: Record<string, (() => void) | undefined> = {
      Escape: callbacks.onEscape,
      ArrowLeft: callbacks.onArrowLeft,
      ArrowRight: callbacks.onArrowRight,
      Home: callbacks.onHome,
      End: callbacks.onEnd,
    };

    const handler = handlers[event.key];
    if (handler) {
      if (preventDefault) {
        event.preventDefault();
      }
      handler();
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown);
  });

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown);
  });
}
