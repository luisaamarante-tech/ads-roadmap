# Component Contract: ShareButton

**Component**: `ShareButton.vue`
**Purpose**: Generate and copy shareable link to specific epic with visual feedback
**Type**: Presentational Component
**Category**: UI Component

## Public API

### Props

```typescript
interface ShareButtonProps {
  /**
   * Epic ID to include in shareable URL.
   * @required
   * @example 'WENI-123'
   * @format 'PROJECT-NUMBER' (JIRA issue key format)
   */
  epicId: string;

  /**
   * Button size variant.
   * @optional
   * @default 'medium'
   */
  size?: 'small' | 'medium' | 'large';

  /**
   * Button visual variant.
   * @optional
   * @default 'outlined'
   */
  variant?: 'primary' | 'secondary' | 'outlined' | 'ghost';

  /**
   * Additional CSS classes for custom styling.
   * @optional
   */
  customClass?: string;
}
```

### Emits

```typescript
interface ShareButtonEmits {
  /**
   * Emitted when link is successfully copied to clipboard.
   * @param url - The URL that was copied
   */
  (e: 'copied', url: string): void;

  /**
   * Emitted when copy operation fails.
   * @param error - Error object with details
   */
  (e: 'copyError', error: Error): void;
}
```

### Slots

```typescript
// No slots - component manages its own content
```

### Exposed Methods

```typescript
// No exposed methods - component is self-contained
```

## Usage Examples

### Basic Usage (Card View)

```vue
<template>
  <div class="roadmap-card__header">
    <h3>{{ epic.title }}</h3>
    
    <ShareButton
      :epic-id="epic.id"
      size="small"
      variant="ghost"
      @copied="onShareCopied"
    />
  </div>
</template>

<script setup lang="ts">
import ShareButton from '@/components/ShareButton.vue';

const epic = {
  id: 'WENI-456',
  title: 'Add OAuth2 Integration',
};

function onShareCopied(url: string): void {
  console.log('Share link copied:', url);
  // Optional: Show toast notification
}
</script>
```

### Expanded View with Error Handling

```vue
<template>
  <div class="roadmap-card__content">
    <p>{{ epic.description }}</p>
    
    <ShareButton
      :epic-id="epic.id"
      size="medium"
      variant="outlined"
      @copied="onShareCopied"
      @copy-error="onShareError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ShareButton from '@/components/ShareButton.vue';

const epic = {
  id: 'WENI-789',
  description: 'Implement two-factor authentication',
};

const errorMessage = ref<string | null>(null);

function onShareCopied(url: string): void {
  console.log('Link copied:', url);
  errorMessage.value = null;
}

function onShareError(error: Error): void {
  errorMessage.value = error.message;
  console.error('Share failed:', error);
}
</script>
```

### Custom Styling

```vue
<template>
  <ShareButton
    :epic-id="epic.id"
    size="large"
    variant="primary"
    custom-class="my-custom-share-btn"
    @copied="trackShareEvent"
  />
</template>

<style scoped>
.my-custom-share-btn {
  position: absolute;
  top: 16px;
  right: 16px;
}
</style>
```

## Behavior Specification

### Normal Copy Flow (Clipboard API Available)

**Trigger**: User clicks share button

**Actions**:
1. Set `isLoading=true`, disable button
2. Generate share URL: `${window.location.origin}/roadmap?epic=${epicId}`
3. Call `navigator.clipboard.writeText(url)`
4. On success:
   - Set `showCopiedState=true`
   - Emit `copied` event with URL
   - Change button text to "Copied!" with checkmark icon
   - After 2 seconds: Reset to default state
5. Set `isLoading=false`, re-enable button

**Visual State**: Button shows "Copied!" with checkmark for 2 seconds

### Fallback Copy Flow (Clipboard API Unavailable)

**Trigger**: Clipboard API fails or unsupported

**Actions**:
1. Set `showFallback=true`
2. Render text input with pre-filled URL
3. Automatically select input text
4. Show instruction: "Copy link manually (Ctrl+C / Cmd+C)"
5. User performs manual copy
6. User clicks "Done" or outside fallback
7. Set `showFallback=false`

**Visual State**: Input field visible with pre-selected URL text

### Error Handling

**Scenario 1**: Permission Denied

```typescript
try {
  await navigator.clipboard.writeText(url);
} catch (error) {
  if (error.name === 'NotAllowedError') {
    // Show fallback input
    showFallback.value = true;
    errorMessage.value = 'Clipboard permission denied. Please copy manually.';
  }
}
```

**Scenario 2**: Invalid Epic ID

```typescript
if (!epicId || epicId.trim() === '') {
  isDisabled.value = true;
  errorMessage.value = 'Invalid epic ID';
  return;
}
```

**Scenario 3**: Network/Browser Error

```typescript
catch (error) {
  emit('copyError', error);
  errorMessage.value = 'Copy failed. Please try again.';
  showFallback.value = true; // Provide manual option
}
```

## Accessibility

### ARIA Attributes

```html
<button
  :aria-label="buttonAriaLabel"
  :aria-busy="isLoading"
  :disabled="isDisabled"
  role="button"
>
  <span aria-hidden="true">{{ buttonIcon }}</span>
  <span>{{ buttonLabel }}</span>
</button>

<!-- Fallback input -->
<div
  v-if="showFallback"
  role="dialog"
  aria-labelledby="fallback-title"
  aria-describedby="fallback-instructions"
>
  <h3 id="fallback-title">Copy Link Manually</h3>
  <p id="fallback-instructions">
    The link has been selected. Press Ctrl+C (Windows) or Cmd+C (Mac) to copy.
  </p>
  <input
    ref="fallbackInputRef"
    :value="shareUrl"
    readonly
    aria-label="Shareable link"
    @focus="$event.target.select()"
  />
</div>
```

### Computed ARIA Label

```typescript
const buttonAriaLabel = computed(() => {
  if (isLoading.value) return 'Copying link...';
  if (showCopiedState.value) return 'Link copied to clipboard';
  if (errorMessage.value) return `Share failed: ${errorMessage.value}`;
  return `Share link to ${props.epicId}`;
});
```

### Keyboard Navigation

| Key | Action | Condition |
|-----|--------|-----------|
| `Enter` | Trigger copy | Button focused |
| `Space` | Trigger copy | Button focused |
| `Tab` | Focus next element | Standard |
| `Shift+Tab` | Focus previous element | Standard |

## Styling Contract

### CSS Classes (BEM)

```css
/* Block */
.share-button { }

/* Elements */
.share-button__icon { }
.share-button__label { }
.share-button__fallback { }
.share-button__fallback-input { }
.share-button__fallback-close { }

/* Modifiers */
.share-button--loading { }
.share-button--copied { }
.share-button--error { }
.share-button--small { }
.share-button--medium { }
.share-button--large { }
.share-button--primary { }
.share-button--secondary { }
.share-button--outlined { }
.share-button--ghost { }
```

### CSS Variables (Unnnic)

```css
/* Button colors */
--unnnic-color-weni-600: #00a8a8; /* primary variant */
--unnnic-color-neutral-cloudy: #67738b; /* outlined/ghost text */
--unnnic-color-feedback-green: #52c41a; /* copied state */
--unnnic-color-feedback-red: #ff4d4f; /* error state */

/* Spacing */
--unnnic-spacing-inline-sm: 8px; /* small button padding */
--unnnic-spacing-inline-md: 12px; /* medium button padding */
--unnnic-spacing-inline-lg: 16px; /* large button padding */

/* Border radius */
--unnnic-border-radius-sm: 6px; /* button corners */
```

### Animation

```css
/* Copied state transition */
.share-button--copied {
  animation: copy-success 2s ease-in-out;
}

@keyframes copy-success {
  0% {
    transform: scale(1);
  }
  10% {
    transform: scale(1.05);
  }
  20% {
    transform: scale(1);
  }
  100% {
    transform: scale(1);
  }
}

/* Loading state */
.share-button--loading .share-button__icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
```

## Testing Contract

### Unit Tests (Required)

```typescript
describe('ShareButton', () => {
  // Rendering
  it('should render button with default props', () => { });
  it('should apply size and variant classes', () => { });
  it('should disable button when epicId is invalid', () => { });
  
  // Copy functionality
  it('should generate correct share URL', () => { });
  it('should copy URL to clipboard on click', () => { });
  it('should emit copied event on success', () => { });
  it('should show "Copied!" state for 2 seconds', () => { });
  
  // Fallback
  it('should show fallback input if clipboard API unavailable', () => { });
  it('should show fallback on permission denied error', () => { });
  it('should auto-select fallback input text', () => { });
  
  // Error handling
  it('should emit copyError on failure', () => { });
  it('should display error message to user', () => { });
  it('should handle empty epicId gracefully', () => { });
  
  // Accessibility
  it('should have correct ARIA label', () => { });
  it('should update aria-busy during loading', () => { });
  it('should be keyboard accessible', () => { });
});
```

### Mock Clipboard API

```typescript
// Test setup
beforeEach(() => {
  Object.assign(navigator, {
    clipboard: {
      writeText: vi.fn().mockResolvedValue(undefined),
    },
  });
});

// Test clipboard not supported
it('should handle missing clipboard API', () => {
  Object.assign(navigator, { clipboard: undefined });
  // ... test fallback behavior
});

// Test permission denied
it('should handle clipboard permission denied', () => {
  navigator.clipboard.writeText = vi.fn().mockRejectedValue(
    new DOMException('Permission denied', 'NotAllowedError')
  );
  // ... test fallback behavior
});
```

### Coverage Requirements

- Statements: ≥80%
- Branches: ≥80%
- Functions: ≥80%
- Lines: ≥80%

## Dependencies

- Vue 3.4+ (Composition API)
- TypeScript 5.3+
- Unnnic Design System (button styles, icons)
- Browser APIs: Clipboard API, window.location

## Performance Considerations

- Debounce rapid clicks (prevent multiple copy operations)
- Generate URL on-demand (not in computed property to avoid recalculation)
- Clear timeout on component unmount (prevent memory leaks)
- Minimal re-renders (use refs, avoid reactive objects)

## Browser Compatibility

### Clipboard API Support

| Browser | Clipboard API | Fallback Required |
|---------|---------------|-------------------|
| Chrome 90+ | ✅ Yes (since 66) | No |
| Firefox 88+ | ✅ Yes (since 63) | No |
| Safari 14+ | ✅ Yes (since 13.1) | No |
| Edge 90+ | ✅ Yes (since 79) | No |
| Older browsers | ❌ No | Yes |

### Fallback Strategy

For browsers without Clipboard API or when permissions denied:
1. Show text input with pre-filled URL
2. Auto-select text for easy Ctrl+C / Cmd+C copy
3. Provide clear instructions
4. Allow manual copy

## URL Format Specification

### Generated URL Structure

```
{origin}/roadmap?epic={epicId}

Examples:
- https://roadmap.weni.ai/roadmap?epic=WENI-123
- http://localhost:5173/roadmap?epic=FLOWS-456
```

### URL Components

- **Origin**: `window.location.origin` (automatically detects http/https, domain, port)
- **Path**: `/roadmap` (hardcoded, matches main roadmap route)
- **Query Parameter**: `epic={epicId}` (single parameter, no encoding needed for JIRA keys)

### URL Validation

```typescript
function isValidEpicId(epicId: string): boolean {
  // JIRA issue key format: PROJECT-NUMBER
  const jiraKeyPattern = /^[A-Z]+-\d+$/;
  return jiraKeyPattern.test(epicId);
}

function generateShareUrl(epicId: string): string {
  if (!isValidEpicId(epicId)) {
    throw new Error(`Invalid epic ID format: ${epicId}`);
  }
  
  const origin = window.location.origin;
  return `${origin}/roadmap?epic=${epicId}`;
}
```

## Known Limitations

1. No social media direct sharing (Twitter, LinkedIn) - out of scope
2. No URL shortening - uses full URL
3. No share analytics tracking - relies on parent component to track via `copied` event
4. No expiration/access control - public URL
5. Clipboard API requires HTTPS in production (browsers block on HTTP except localhost)
