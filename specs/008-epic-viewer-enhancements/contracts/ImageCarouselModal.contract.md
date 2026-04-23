# Component Contract: ImageCarouselModal

**Component**: `ImageCarouselModal.vue`
**Purpose**: Display epic images in an enlarged modal overlay with navigation controls
**Type**: Presentational Component
**Category**: UI Component

## Public API

### Props

```typescript
interface ImageCarouselModalProps {
  /**
   * Array of image URLs to display.
   * @required
   * @example ['https://jira.example.com/attachment/1.png', 'https://jira.example.com/attachment/2.png']
   */
  images: string[];

  /**
   * Initial image index to display (zero-based).
   * @required
   * @default 0
   * @constraints 0 <= currentIndex < images.length
   */
  currentIndex: number;

  /**
   * Epic title for accessibility and context.
   * @required
   * @example 'Add user authentication feature'
   */
  epicTitle: string;

  /**
   * Controls modal visibility.
   * @required
   * @default false
   */
  show: boolean;
}
```

### Emits

```typescript
interface ImageCarouselModalEmits {
  /**
   * Emitted when modal should close.
   * Triggers: Close button click, backdrop click, ESC key press.
   * @param void
   */
  (e: 'close'): void;

  /**
   * Emitted when current image index changes.
   * Triggers: Navigation arrow clicks, keyboard arrow keys.
   * @param newIndex - The new image index
   */
  (e: 'indexChange', newIndex: number): void;
}
```

### Slots

```typescript
// No slots - component is self-contained
```

### Exposed Methods

```typescript
// No exposed methods - component is purely reactive to props
```

## Usage Examples

### Basic Usage (Single Image)

```vue
<template>
  <ImageCarouselModal
    :images="['https://example.com/screenshot.png']"
    :current-index="0"
    :epic-title="epic.title"
    :show="showModal"
    @close="showModal = false"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ImageCarouselModal from '@/components/ImageCarouselModal.vue';

const showModal = ref(false);
const epic = {
  title: 'New Dashboard Feature',
  images: ['https://example.com/screenshot.png'],
};
</script>
```

### Multiple Images with Navigation

```vue
<template>
  <div>
    <!-- Thumbnail images that open modal -->
    <img
      v-for="(imageUrl, index) in epic.images"
      :key="index"
      :src="imageUrl"
      @click="openModal(index)"
      class="thumbnail"
    />

    <!-- Modal -->
    <ImageCarouselModal
      :images="epic.images"
      :current-index="selectedIndex"
      :epic-title="epic.title"
      :show="showModal"
      @close="showModal = false"
      @index-change="onIndexChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ImageCarouselModal from '@/components/ImageCarouselModal.vue';

const epic = {
  title: 'Payment Processing Update',
  images: [
    'https://example.com/flow-1.png',
    'https://example.com/flow-2.png',
    'https://example.com/flow-3.png',
  ],
};

const showModal = ref(false);
const selectedIndex = ref(0);

function openModal(index: number): void {
  selectedIndex.value = index;
  showModal.value = true;
}

function onIndexChange(newIndex: number): void {
  console.log('User navigated to image:', newIndex);
  // Optional: Track analytics
}
</script>
```

## Behavior Specification

### Opening Modal

**Trigger**: Parent sets `show=true`

**Actions**:
1. Render modal with dark backdrop overlay
2. Display image at `currentIndex` centered on screen
3. Attach keyboard event listeners (ESC, arrows)
4. Trap focus within modal for accessibility
5. Set `aria-hidden="true"` on main content
6. Show loading spinner while image loads

**Visual State**: Modal visible, image loading or displayed

### Navigation

**Triggers**:
- Click next arrow button
- Click previous arrow button
- Press Right Arrow key
- Press Left Arrow key

**Actions**:
1. Update `localIndex` (+1 for next, -1 for previous)
2. Wrap around boundaries (last→first, first→last)
3. Emit `indexChange` event with new index
4. Show loading spinner for new image
5. Update position label ("2 of 5")

**Visual State**: New image displayed, position updated

### Closing Modal

**Triggers**:
- Click close button (X icon)
- Click backdrop area
- Press ESC key

**Actions**:
1. Emit `close` event
2. Remove keyboard event listeners
3. Restore focus to element that opened modal
4. Remove `aria-hidden` from main content
5. Parent sets `show=false` (removes modal from DOM)

**Visual State**: Modal hidden

### Error Handling

**Scenario**: Image fails to load (404, network error, CORS)

**Actions**:
1. Show placeholder with error message
2. Display alt text: "[Epic Title] - Image [N]"
3. Log error to console
4. Keep navigation functional for other images

**Visual State**: Error placeholder visible, navigation still works

## Accessibility

### ARIA Attributes

```html
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
  aria-describedby="modal-description"
>
  <h2 id="modal-title" class="sr-only">{{ epicTitle }} - Images</h2>
  <div id="modal-description" class="sr-only">
    Image {{ localIndex + 1 }} of {{ images.length }}. Use arrow keys to navigate, escape to close.
  </div>
  
  <img
    :src="currentImage"
    :alt="`${epicTitle} - Image ${localIndex + 1}`"
  />
  
  <button
    aria-label="Previous image"
    :aria-disabled="images.length <= 1"
  >
    ← Previous
  </button>
  
  <button
    aria-label="Next image"
    :aria-disabled="images.length <= 1"
  >
    Next →
  </button>
  
  <button
    aria-label="Close image viewer"
  >
    ✕ Close
  </button>
</div>
```

### Keyboard Navigation

| Key | Action | Condition |
|-----|--------|-----------|
| `ESC` | Close modal | Always |
| `Right Arrow` | Next image | Multiple images |
| `Left Arrow` | Previous image | Multiple images |
| `Home` | First image | Multiple images (optional) |
| `End` | Last image | Multiple images (optional) |
| `Tab` | Focus next control | Trapped within modal |
| `Shift+Tab` | Focus previous control | Trapped within modal |

### Focus Management

1. When modal opens: Focus on close button
2. Tab order: Close button → Previous button → Next button → Backdrop
3. Focus trap: Tab wraps within modal (cannot tab to background content)
4. When modal closes: Restore focus to trigger element (image that was clicked)

## Styling Contract

### CSS Classes (BEM)

```css
/* Block */
.image-carousel-modal { }

/* Elements */
.image-carousel-modal__backdrop { }
.image-carousel-modal__container { }
.image-carousel-modal__image { }
.image-carousel-modal__loading { }
.image-carousel-modal__error { }
.image-carousel-modal__navigation { }
.image-carousel-modal__nav-btn { }
.image-carousel-modal__nav-btn--prev { }
.image-carousel-modal__nav-btn--next { }
.image-carousel-modal__close-btn { }
.image-carousel-modal__position { }

/* Modifiers */
.image-carousel-modal--loading { }
.image-carousel-modal--error { }
.image-carousel-modal__nav-btn--disabled { }
```

### CSS Variables (Unnnic)

```css
--unnnic-color-background-black: rgba(0, 0, 0, 0.85); /* backdrop */
--unnnic-color-background-snow: #fff; /* close button background */
--unnnic-color-neutral-cloudy: #67738b; /* button text */
--unnnic-color-weni-600: #00a8a8; /* loading spinner */
--unnnic-border-radius-md: 12px; /* button corners */
--unnnic-spacing-inline-md: 16px; /* button padding */
--unnnic-font-size-body-md: 14px; /* position label */
```

### Animation

```css
/* Fade in/out */
.image-carousel-modal-enter-active,
.image-carousel-modal-leave-active {
  transition: opacity 0.3s ease;
}

.image-carousel-modal-enter-from,
.image-carousel-modal-leave-to {
  opacity: 0;
}

/* Image transition */
.image-carousel-modal__image {
  transition: opacity 0.2s ease;
}
```

## Testing Contract

### Unit Tests (Required)

```typescript
describe('ImageCarouselModal', () => {
  // Rendering
  it('should render modal when show=true', () => { });
  it('should not render modal when show=false', () => { });
  it('should display image at currentIndex', () => { });
  
  // Navigation
  it('should navigate to next image on arrow click', () => { });
  it('should navigate to previous image on arrow click', () => { });
  it('should wrap to first image when clicking next on last', () => { });
  it('should wrap to last image when clicking prev on first', () => { });
  it('should hide navigation arrows for single image', () => { });
  
  // Keyboard
  it('should close modal on ESC key', () => { });
  it('should navigate next on Right Arrow key', () => { });
  it('should navigate previous on Left Arrow key', () => { });
  
  // Events
  it('should emit close on backdrop click', () => { });
  it('should emit close on close button click', () => { });
  it('should emit indexChange on navigation', () => { });
  
  // Loading & Errors
  it('should show loading state while image loads', () => { });
  it('should show error placeholder for broken images', () => { });
  it('should handle empty images array gracefully', () => { });
  
  // Accessibility
  it('should have correct ARIA attributes', () => { });
  it('should trap focus within modal', () => { });
});
```

### Coverage Requirements

- Statements: ≥80%
- Branches: ≥80%
- Functions: ≥80%
- Lines: ≥80%

## Dependencies

- Vue 3.4+ (Composition API, Teleport)
- TypeScript 5.3+
- Unnnic Design System (CSS variables, icon patterns)
- Browser APIs: KeyboardEvent, Image.onload/onerror

## Performance Considerations

- Use `<Teleport>` to render modal at document root (avoid z-index issues)
- Lazy load images with `loading="lazy"` attribute
- Debounce rapid navigation clicks (300ms) to prevent animation conflicts
- Remove event listeners in `onUnmounted` to prevent memory leaks
- Limit image file size (recommendation: <2MB per image)

## Browser Compatibility

- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅

## Known Limitations

1. No image zoom/pan functionality (out of scope)
2. No swipe gestures for mobile (future enhancement)
3. No image download button (out of scope)
4. Maximum image size limited by browser memory (~10MB recommended)
