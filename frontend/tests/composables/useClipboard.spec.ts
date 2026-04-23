import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useClipboard } from '@/composables/useClipboard';

describe('useClipboard', () => {
  beforeEach(() => {
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should copy text successfully', async () => {
    const { copy, isCopied } = useClipboard();
    const result = await copy('test text');

    expect(result).toBe(true);
    expect(isCopied.value).toBe(true);
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('test text');
  });

  it('should handle clipboard API not supported', async () => {
    Object.assign(navigator, { clipboard: undefined });
    const { copy, error, isSupported } = useClipboard();

    expect(isSupported.value).toBe(false);
    const result = await copy('test');
    expect(result).toBe(false);
    expect(error.value).toBeTruthy();
  });

  it('should reset copied state after duration', async () => {
    vi.useFakeTimers();
    const { copy, isCopied } = useClipboard({ copiedStateDuration: 1000 });

    await copy('test');
    expect(isCopied.value).toBe(true);

    vi.advanceTimersByTime(1000);
    expect(isCopied.value).toBe(false);

    vi.useRealTimers();
  });

  it('should call onSuccess callback', async () => {
    const onSuccess = vi.fn();
    const { copy } = useClipboard({ onSuccess });

    await copy('test');
    expect(onSuccess).toHaveBeenCalledWith('test');
  });

  it('should call onError callback on failure', async () => {
    const onError = vi.fn();
    navigator.clipboard.writeText = vi
      .fn()
      .mockRejectedValue(new Error('Permission denied'));

    const { copy } = useClipboard({ onError });
    await copy('test');

    expect(onError).toHaveBeenCalled();
  });

  it('should handle empty text', async () => {
    const { copy, error } = useClipboard();
    const result = await copy('');

    expect(result).toBe(false);
    expect(error.value).toBe('No text provided');
  });

  it('should set isLoading during copy operation', async () => {
    const { copy, isLoading } = useClipboard();

    const copyPromise = copy('test');
    expect(isLoading.value).toBe(true);

    await copyPromise;
    expect(isLoading.value).toBe(false);
  });
});
