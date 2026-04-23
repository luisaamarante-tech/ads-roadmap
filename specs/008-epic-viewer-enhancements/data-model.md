# Phase 1: Data Models

**Feature**: Epic Viewer Enhancements
**Date**: January 21, 2026
**Purpose**: Define component state models, props, emits, and data flow

## Component State Models

### 1. ImageCarouselModal Component

**Purpose**: Display enlarged images in modal with navigation controls.

**Props** (Input):
```typescript
interface ImageCarouselModalProps {
  /**
   * Array of image URLs to display in the carousel.
   * Matches RoadmapItem.images structure.
   */
  images: string[];

  /**
   * Current image index to display when modal opens.
   * Zero-based index into images array.
   */
  currentIndex: number;

  /**
   * Epic title for context in alt text and ARIA labels.
   * Used for accessibility and error messages.
   */
  epicTitle: string;

  /**
   * Controls modal visibility.
   * Parent component manages this state.
   */
  show: boolean;
}
```

**Emits** (Output):
```typescript
interface ImageCarouselModalEmits {
  /**
   * Emitted when user closes the modal (click backdrop, ESC key, close button).
   * Parent should set show=false in response.
   */
  close: () => void;

  /**
   * Emitted when current image index changes (navigation).
   * Optional: for analytics or parent state sync.
   */
  indexChange: (newIndex: number) => void;
}
```

**Local State**:
```typescript
interface ImageCarouselModalState {
  /**
   * Tracks current image index during navigation.
   * Initialized from props.currentIndex, updates independently.
   */
  localIndex: Ref<number>;

  /**
   * Loading state for each image (by index).
   * Used to show spinner until image loads.
   */
  imageLoadingStates: Ref<Record<number, 'loading' | 'loaded' | 'error'>>;

  /**
   * Keyboard navigation handlers from useKeyboardNavigation composable.
   * Attached in onMounted, removed in onUnmounted.
   */
  keyboardHandlers: {
    onEscape: () => void;
    onArrowLeft: () => void;
    onArrowRight: () => void;
  };
}
```

**Computed Properties**:
```typescript
interface ImageCarouselModalComputed {
  /**
   * URL of currently displayed image.
   * images[localIndex.value]
   */
  currentImage: ComputedRef<string>;

  /**
   * Human-readable position indicator.
   * E.g., "2 of 5" or empty string if only 1 image.
   */
  positionLabel: ComputedRef<string>;

  /**
   * Whether to show previous/next arrows.
   * Hide if images.length <= 1.
   */
  showNavigation: ComputedRef<boolean>;

  /**
   * Current image loading state.
   * imageLoadingStates[localIndex.value]
   */
  currentImageState: ComputedRef<'loading' | 'loaded' | 'error'>;
}
```

**Validation Rules**:
- `images` array must not be empty (parent should not render modal if no images)
- `currentIndex` must be valid index (0 <= currentIndex < images.length)
- If invalid index provided, clamp to 0
- Image URLs should be valid HTTP(S) URLs (JIRA attachment format)

**State Transitions**:
```
[Initial: show=false, localIndex=0]
    ↓ (user clicks image)
[Modal Opens: show=true, localIndex=props.currentIndex]
    ↓ (user presses Right arrow)
[Navigate: localIndex++, wrap if needed]
    ↓ (user presses ESC or clicks backdrop)
[Modal Closes: emit('close'), parent sets show=false]
    ↓
[Reset: localIndex persists for next open]
```

---

### 2. ShareButton Component

**Purpose**: Generate and copy shareable link to clipboard with confirmation feedback.

**Props** (Input):
```typescript
interface ShareButtonProps {
  /**
   * Epic ID to include in shareable URL.
   * E.g., "WENI-123" from RoadmapItem.id
   */
  epicId: string;

  /**
   * Button size variant (matches Unnnic button sizes).
   * Allows different sizes for card vs expanded view.
   */
  size?: 'small' | 'medium' | 'large';

  /**
   * Button visual style variant.
   * Allows different prominence in different contexts.
   */
  variant?: 'primary' | 'secondary' | 'outlined' | 'ghost';

  /**
   * Optional additional CSS classes for positioning.
   */
  customClass?: string;
}
```

**Emits** (Output):
```typescript
interface ShareButtonEmits {
  /**
   * Emitted when share link is successfully copied.
   * Useful for analytics or parent notifications.
   */
  copied: (url: string) => void;

  /**
   * Emitted when copy operation fails.
   * Parent can show error notification if desired.
   */
  copyError: (error: Error) => void;
}
```

**Local State**:
```typescript
interface ShareButtonState {
  /**
   * Whether copy operation is in progress.
   * Prevents duplicate clicks during async operation.
   */
  isLoading: Ref<boolean>;

  /**
   * Whether copy was successful (for visual feedback).
   * Resets after 2 seconds to restore default state.
   */
  showCopiedState: Ref<boolean>;

  /**
   * Fallback input ref for manual copy when Clipboard API unavailable.
   * Null when clipboard API works, InputElement when fallback shown.
   */
  fallbackInputRef: Ref<HTMLInputElement | null>;

  /**
   * Whether to show fallback input (clipboard API failed or unavailable).
   */
  showFallback: Ref<boolean>;

  /**
   * Error message if copy fails.
   * Cleared after 5 seconds or on retry.
   */
  errorMessage: Ref<string | null>;
}
```

**Computed Properties**:
```typescript
interface ShareButtonComputed {
  /**
   * Generated shareable URL.
   * Format: `${window.location.origin}/roadmap?epic=${epicId}`
   */
  shareUrl: ComputedRef<string>;

  /**
   * Button label based on current state.
   * "Share" | "Copied!" | "Copy failed, try again"
   */
  buttonLabel: ComputedRef<string>;

  /**
   * Button icon name (from Unnnic icon set).
   * "share-2" | "check" | "alert-circle"
   */
  buttonIcon: ComputedRef<string>;

  /**
   * Whether button should be disabled.
   * True during loading or if epicId is invalid.
   */
  isDisabled: ComputedRef<boolean>;
}
```

**Validation Rules**:
- `epicId` must be non-empty string
- `epicId` should match JIRA issue key format (PROJECT-NUMBER, e.g., "WENI-123")
- Generated URL must be valid absolute URL
- If validation fails, button is disabled and shows error state

**State Transitions**:
```
[Initial: isLoading=false, showCopiedState=false]
    ↓ (user clicks share button)
[Loading: isLoading=true]
    ↓ (clipboard API success)
[Copied: showCopiedState=true, emit('copied')]
    ↓ (after 2 seconds)
[Reset: showCopiedState=false]

OR

[Loading: isLoading=true]
    ↓ (clipboard API fails)
[Error: showFallback=true, errorMessage set]
    ↓ (user manually copies from input)
[User Action: no automatic state change]
    ↓ (user closes fallback)
[Reset: showFallback=false, errorMessage=null]
```

---

### 3. RoadmapCard Modifications

**Existing State** (No Changes):
```typescript
// Already exists
const isExpanded = ref(false);
const localLikeCount = ref<number>(props.item.likes ?? 0);
```

**New State**:
```typescript
interface RoadmapCardNewState {
  /**
   * Controls ImageCarouselModal visibility.
   * True when user clicks on an image.
   */
  showImageModal: Ref<boolean>;

  /**
   * Index of image clicked (to show in modal initially).
   * Updated when user clicks on a specific image.
   */
  clickedImageIndex: Ref<number>;
}
```

**New Event Handlers**:
```typescript
interface RoadmapCardNewHandlers {
  /**
   * Handle image click to open modal.
   * Stops event propagation to prevent card expansion.
   */
  onImageClick: (index: number) => void;

  /**
   * Handle modal close request.
   * Sets showImageModal to false.
   */
  onModalClose: () => void;
}
```

**Data Flow**:
```
[User clicks image]
    ↓
[onImageClick(index)]
    ↓
[Set clickedImageIndex=index, showImageModal=true]
    ↓
[ImageCarouselModal renders with images, currentIndex=clickedImageIndex]
    ↓
[User navigates/closes modal]
    ↓
[Modal emits('close')]
    ↓
[onModalClose() sets showImageModal=false]
```

---

### 4. RoadmapView Modifications

**Existing State** (Relevant):
```typescript
// Already exists - we'll extend this
const filters = ref<RoadmapFilters>({});
const items = ref<RoadmapItem[]>([]);
const activeStatus = ref<DeliveryStatus>('DELIVERED');
```

**New State**:
```typescript
interface RoadmapViewNewState {
  /**
   * Epic ID from URL query parameter.
   * Populated from route.query.epic on mount.
   */
  sharedEpicId: Ref<string | null>;

  /**
   * Whether we're currently processing a shared epic link.
   * Prevents filter changes during epic expansion.
   */
  isProcessingSharedEpic: Ref<boolean>;
}
```

**New Computed Properties**:
```typescript
interface RoadmapViewNewComputed {
  /**
   * Index of epic with matching sharedEpicId in items array.
   * -1 if not found.
   */
  sharedEpicIndex: ComputedRef<number>;

  /**
   * Whether a valid shared epic ID exists in URL.
   */
  hasSharedEpicParam: ComputedRef<boolean>;
}
```

**New Functions**:
```typescript
interface RoadmapViewNewFunctions {
  /**
   * Process shared epic link on mount.
   * Clears filters, fetches all items, finds and expands epic.
   */
  handleSharedEpicLink: () => Promise<void>;

  /**
   * Find epic in items array and programmatically expand it.
   * Returns true if found and expanded, false otherwise.
   */
  expandEpicById: (epicId: string) => boolean;

  /**
   * Clear shared epic state and remove parameter from URL.
   * Called after successful expansion or on error.
   */
  clearSharedEpicState: () => void;
}
```

**State Transitions** (Shared Epic Flow):
```
[Page Load: Check route.query.epic]
    ↓ (epic parameter exists)
[Set sharedEpicId=epicId, isProcessingSharedEpic=true]
    ↓
[Clear all filters: filters.value = {}]
    ↓
[Fetch all items without filters]
    ↓
[Find epic in items by ID]
    ↓ (epic found)
[Expand epic card (set card's isExpanded=true)]
    ↓
[Scroll to epic card]
    ↓
[Clear epic parameter from URL, isProcessingSharedEpic=false]

OR

    ↓ (epic not found)
[Show error toast: "Epic not found or no longer available"]
    ↓
[Clear epic parameter from URL, isProcessingSharedEpic=false]
```

---

## Composables

### useClipboard Composable

**Purpose**: Abstract clipboard operations with fallback support.

**Interface**:
```typescript
interface UseClipboardOptions {
  /**
   * Callback when copy succeeds.
   */
  onSuccess?: (text: string) => void;

  /**
   * Callback when copy fails.
   */
  onError?: (error: Error) => void;

  /**
   * Duration to maintain "copied" state (ms).
   * Default: 2000
   */
  copiedStateDuration?: number;
}

interface UseClipboardReturn {
  /**
   * Copy text to clipboard.
   * Returns true if successful, false otherwise.
   */
  copy: (text: string) => Promise<boolean>;

  /**
   * Whether a copy operation is in progress.
   */
  isLoading: Readonly<Ref<boolean>>;

  /**
   * Whether copy was successful (temporary state).
   */
  isCopied: Readonly<Ref<boolean>>;

  /**
   * Error message if copy failed.
   */
  error: Readonly<Ref<string | null>>;

  /**
   * Whether Clipboard API is supported.
   */
  isSupported: Readonly<Ref<boolean>>;
}

export function useClipboard(options?: UseClipboardOptions): UseClipboardReturn;
```

**Internal State**:
```typescript
const isLoading = ref(false);
const isCopied = ref(false);
const error = ref<string | null>(null);
const isSupported = ref(
  typeof navigator !== 'undefined' && 
  'clipboard' in navigator &&
  typeof navigator.clipboard.writeText === 'function'
);
```

---

### useKeyboardNavigation Composable

**Purpose**: Handle keyboard events for modal navigation.

**Interface**:
```typescript
interface UseKeyboardNavigationCallbacks {
  /**
   * Called when ESC key pressed.
   */
  onEscape?: () => void;

  /**
   * Called when Left Arrow pressed.
   */
  onArrowLeft?: () => void;

  /**
   * Called when Right Arrow pressed.
   */
  onArrowRight?: () => void;

  /**
   * Called when Home key pressed (optional).
   * Navigate to first image.
   */
  onHome?: () => void;

  /**
   * Called when End key pressed (optional).
   * Navigate to last image.
   */
  onEnd?: () => void;
}

interface UseKeyboardNavigationOptions {
  /**
   * Whether keyboard navigation is currently active.
   * Useful for disabling when modal is closed.
   */
  isActive?: Ref<boolean>;

  /**
   * Whether to prevent default behavior for navigation keys.
   * Default: true (prevents page scroll on arrow keys)
   */
  preventDefault?: boolean;
}

export function useKeyboardNavigation(
  callbacks: UseKeyboardNavigationCallbacks,
  options?: UseKeyboardNavigationOptions
): void;
```

**Internal Logic**:
```typescript
function handleKeydown(event: KeyboardEvent): void {
  // Check if navigation is active (if option provided)
  if (options?.isActive && !options.isActive.value) {
    return;
  }

  // Handle each key
  const handlers: Record<string, (() => void) | undefined> = {
    Escape: callbacks.onEscape,
    ArrowLeft: callbacks.onArrowLeft,
    ArrowRight: callbacks.onArrowRight,
    Home: callbacks.onHome,
    End: callbacks.onEnd,
  };

  const handler = handlers[event.key];
  if (handler) {
    if (options?.preventDefault !== false) {
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
```

---

## Data Relationships

### Epic → Images → Carousel

```
RoadmapItem
├── id: string (for sharing)
├── title: string (for alt text)
├── images: string[] (URLs)
└── [other fields...]
        ↓
RoadmapCard
├── item.images → ImageCarouselModal.images
├── item.title → ImageCarouselModal.epicTitle
└── item.id → ShareButton.epicId
        ↓
ImageCarouselModal
└── Display images[currentIndex]
    Navigate: currentIndex ± 1
```

### Share Flow → URL → Epic Expansion

```
User clicks ShareButton
        ↓
ShareButton generates URL: `/roadmap?epic=${epicId}`
        ↓
Clipboard API copies URL
        ↓
User shares link → Someone opens link
        ↓
RoadmapView detects route.query.epic
        ↓
Clear filters → Fetch all items → Find epic → Expand
```

---

## Type Definitions (TypeScript)

**Additions to `frontend/src/types/roadmap.ts`**:

```typescript
/**
 * State for image loading in carousel modal.
 */
export type ImageLoadingState = 'loading' | 'loaded' | 'error';

/**
 * Share button size variants (matches Unnnic).
 */
export type ShareButtonSize = 'small' | 'medium' | 'large';

/**
 * Share button visual variants (matches Unnnic).
 */
export type ShareButtonVariant = 'primary' | 'secondary' | 'outlined' | 'ghost';

/**
 * Result of clipboard copy operation.
 */
export interface ClipboardCopyResult {
  success: boolean;
  error?: string;
}
```

---

## Validation Summary

All state models follow Vue 3 composition API patterns:
- ✅ Props typed with TypeScript interfaces
- ✅ Emits documented with event signatures
- ✅ Local state uses `ref()` for primitives, `reactive()` for objects
- ✅ Computed properties derive from refs (no duplicate state)
- ✅ Event handlers follow naming convention (`onXxx`)
- ✅ State transitions clearly defined
- ✅ Composables follow VueUse patterns (return objects with refs)
- ✅ All models testable in isolation with mocks
