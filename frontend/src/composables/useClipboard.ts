import { ref, readonly, type Ref } from 'vue';

export interface UseClipboardOptions {
  onSuccess?: (text: string) => void;
  onError?: (error: Error) => void;
  copiedStateDuration?: number;
}

export interface UseClipboardReturn {
  copy: (text: string) => Promise<boolean>;
  isLoading: Readonly<Ref<boolean>>;
  isCopied: Readonly<Ref<boolean>>;
  error: Readonly<Ref<string | null>>;
  isSupported: Readonly<Ref<boolean>>;
}

/**
 * Composable for clipboard operations with fallback support.
 */
export function useClipboard(
  options: UseClipboardOptions = {},
): UseClipboardReturn {
  const { onSuccess, onError, copiedStateDuration = 2000 } = options;

  const isLoading = ref(false);
  const isCopied = ref(false);
  const error = ref<string | null>(null);

  const isSupported = ref(
    typeof navigator !== 'undefined' &&
      'clipboard' in navigator &&
      navigator.clipboard !== undefined &&
      typeof navigator.clipboard.writeText === 'function',
  );

  let copiedTimeoutId: number | null = null;

  async function copy(text: string): Promise<boolean> {
    if (!text) {
      error.value = 'No text provided';
      return false;
    }

    isLoading.value = true;
    error.value = null;

    try {
      if (isSupported.value) {
        await navigator.clipboard.writeText(text);
      } else {
        throw new Error('Clipboard API not supported');
      }

      isCopied.value = true;
      onSuccess?.(text);

      // Reset copied state after duration
      if (copiedTimeoutId !== null) {
        clearTimeout(copiedTimeoutId);
      }
      copiedTimeoutId = window.setTimeout(() => {
        isCopied.value = false;
      }, copiedStateDuration);

      return true;
    } catch (err) {
      const errorObj = err instanceof Error ? err : new Error(String(err));
      error.value = errorObj.message;
      onError?.(errorObj);
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    copy,
    isLoading: readonly(isLoading),
    isCopied: readonly(isCopied),
    error: readonly(error),
    isSupported: readonly(isSupported),
  };
}
