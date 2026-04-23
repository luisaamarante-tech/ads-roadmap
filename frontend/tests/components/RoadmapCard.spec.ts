/**
 * Unit tests for RoadmapCard component
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount } from '@vue/test-utils';
import RoadmapCard from '@/components/RoadmapCard.vue';
import { mockRoadmapItems } from '../../mocks/roadmapData';
import * as roadmapService from '@/services/roadmapService';

// Mock roadmap service
vi.mock('@/services/roadmapService', () => ({
  likeEpic: vi.fn(),
}));

describe('RoadmapCard', () => {
  const defaultItem = mockRoadmapItems[0];

  beforeEach(() => {
    vi.clearAllMocks();
    // Clear localStorage before each test
    localStorage.removeItem('weni-roadmap-liked-items');

    // Mock scrollIntoView (not available in jsdom)
    Element.prototype.scrollIntoView = vi.fn();
  });

  afterEach(() => {
    // Clear all timers to prevent leaks
    vi.clearAllTimers();
  });

  const createWrapper = (props = {}) => {
    return mount(RoadmapCard, {
      props: {
        item: defaultItem,
        ...props,
      },
    });
  };

  describe('rendering', () => {
    it('renders the card with item title', () => {
      const wrapper = createWrapper();
      expect(wrapper.text()).toContain(defaultItem.title);
    });

    it('renders the module badge', () => {
      const wrapper = createWrapper();
      expect(wrapper.text()).toContain(defaultItem.module);
    });

    it('renders release info with quarter and year', () => {
      const wrapper = createWrapper();
      expect(wrapper.text()).toContain(defaultItem.releaseQuarter);
      expect(wrapper.text()).toContain(String(defaultItem.releaseYear));
    });

    it('renders release info with month when available', () => {
      const itemWithMonth = { ...mockRoadmapItems[1] };
      const wrapper = createWrapper({ item: itemWithMonth });
      // April = month 4
      expect(wrapper.text()).toContain('Apr');
    });
  });

  describe('expansion behavior', () => {
    it('is collapsed by default', () => {
      const wrapper = createWrapper();
      expect(wrapper.find('.roadmap-card__content').exists()).toBe(false);
    });

    it('expands when clicked', async () => {
      const wrapper = createWrapper();
      await wrapper.trigger('click');
      expect(wrapper.find('.roadmap-card__content').exists()).toBe(true);
    });

    it('shows description when expanded', async () => {
      const wrapper = createWrapper();
      await wrapper.trigger('click');
      expect(wrapper.text()).toContain(defaultItem.description);
    });

    it('collapses when clicked again', async () => {
      const wrapper = createWrapper();
      await wrapper.trigger('click');
      await wrapper.trigger('click');
      expect(wrapper.find('.roadmap-card__content').exists()).toBe(false);
    });
  });

  describe('images', () => {
    it('shows images when item has images and is expanded', async () => {
      const itemWithImages = mockRoadmapItems[1];
      const wrapper = createWrapper({ item: itemWithImages });
      await wrapper.trigger('click');

      const images = wrapper.findAll('img');
      expect(images.length).toBe(itemWithImages.images.length);
    });

    it('does not show images section when no images', async () => {
      const wrapper = createWrapper();
      await wrapper.trigger('click');

      expect(wrapper.find('.roadmap-card__images').exists()).toBe(false);
    });
  });

  describe('documentation link', () => {
    it('shows documentation link when available and expanded', async () => {
      const itemWithDocs = mockRoadmapItems[1];
      const wrapper = createWrapper({ item: itemWithDocs });
      await wrapper.trigger('click');

      const link = wrapper.find('a[href]');
      expect(link.exists()).toBe(true);
      expect(link.attributes('href')).toBe(itemWithDocs.documentationUrl);
    });

    it('does not show documentation link when not available', async () => {
      const wrapper = createWrapper();
      await wrapper.trigger('click');

      expect(wrapper.find('.roadmap-card__link').exists()).toBe(false);
    });

    it('opens documentation in new tab', async () => {
      const itemWithDocs = mockRoadmapItems[1];
      const wrapper = createWrapper({ item: itemWithDocs });
      await wrapper.trigger('click');

      const link = wrapper.find('a[href]');
      expect(link.attributes('target')).toBe('_blank');
      expect(link.attributes('rel')).toContain('noopener');
    });
  });

  describe('expand button', () => {
    it('has correct aria-expanded attribute', async () => {
      const wrapper = createWrapper();
      const button = wrapper.find('.roadmap-card__expand-btn');

      expect(button.attributes('aria-expanded')).toBe('false');

      await wrapper.trigger('click');
      expect(button.attributes('aria-expanded')).toBe('true');
    });

    it('rotates chevron when expanded', async () => {
      const wrapper = createWrapper();
      await wrapper.trigger('click');

      const chevron = wrapper.find('.roadmap-card__chevron');
      expect(chevron.classes()).toContain('roadmap-card__chevron--rotated');
    });
  });

  describe('accessibility', () => {
    it('has clickable card element', () => {
      const wrapper = createWrapper();
      expect(wrapper.find('article.roadmap-card').exists()).toBe(true);
    });

    it('has aria-expanded on expand button', () => {
      const wrapper = createWrapper();
      const button = wrapper.find('.roadmap-card__expand-btn');
      expect(button.attributes('aria-expanded')).toBeDefined();
    });

    it('has aria-label on expand button', () => {
      const wrapper = createWrapper();
      const button = wrapper.find('.roadmap-card__expand-btn');
      expect(button.attributes('aria-label')).toBeDefined();
    });
  });

  describe('like count display', () => {
    it('displays like count when item has likes', () => {
      const itemWithLikes = { ...defaultItem, likes: 42 };
      const wrapper = createWrapper({ item: itemWithLikes });
      expect(wrapper.text()).toContain('42');
    });

    it('displays zero likes when item has no likes', () => {
      const itemWithNoLikes = { ...defaultItem, likes: 0 };
      const wrapper = createWrapper({ item: itemWithNoLikes });
      expect(wrapper.text()).toContain('0');
    });

    it('handles undefined likes gracefully', () => {
      const itemWithUndefinedLikes = { ...defaultItem, likes: undefined };
      const wrapper = createWrapper({ item: itemWithUndefinedLikes });
      // Should default to 0 or not crash
      expect(wrapper.find('.roadmap-card').exists()).toBe(true);
    });
  });

  describe('like functionality', () => {
    it('displays like button with correct aria-label', () => {
      const wrapper = createWrapper();
      const likeButton = wrapper.find('.roadmap-card__like-btn');
      expect(likeButton.exists()).toBe(true);
      expect(likeButton.attributes('aria-label')).toContain('Like this epic');
    });

    it('increments like count optimistically when clicked', async () => {
      vi.mocked(roadmapService.likeEpic).mockResolvedValue({
        success: true,
        likes: 1,
      });

      const wrapper = createWrapper({ item: { ...defaultItem, likes: 0 } });
      const likeButton = wrapper.find('.roadmap-card__like-btn');

      await likeButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(wrapper.text()).toContain('1');
    });

    it('prevents card expansion when like button clicked', async () => {
      vi.mocked(roadmapService.likeEpic).mockResolvedValue({
        success: true,
        likes: 1,
      });

      const wrapper = createWrapper();
      const likeButton = wrapper.find('.roadmap-card__like-btn');

      await likeButton.trigger('click');
      await wrapper.vm.$nextTick();

      // Card should not be expanded
      expect(wrapper.find('.roadmap-card__content').exists()).toBe(false);
    });

    it('disables button after liking', async () => {
      vi.mocked(roadmapService.likeEpic).mockResolvedValue({
        success: true,
        likes: 1,
      });

      const wrapper = createWrapper();
      const likeButton = wrapper.find('.roadmap-card__like-btn');

      await likeButton.trigger('click');
      await new Promise((resolve) => setTimeout(resolve, 600));
      await wrapper.vm.$nextTick();

      expect(likeButton.attributes('disabled')).toBeDefined();
    });

    it('stores liked item in localStorage on success', async () => {
      vi.mocked(roadmapService.likeEpic).mockResolvedValue({
        success: true,
        likes: 1,
      });

      const wrapper = createWrapper();
      const likeButton = wrapper.find('.roadmap-card__like-btn');

      await likeButton.trigger('click');
      await new Promise((resolve) => setTimeout(resolve, 600));
      await wrapper.vm.$nextTick();

      const likedItems = JSON.parse(
        localStorage.getItem('weni-roadmap-liked-items') || '[]',
      );
      expect(likedItems).toContain(defaultItem.id);
    });

    it('prevents liking if already liked (from localStorage)', () => {
      localStorage.setItem(
        'weni-roadmap-liked-items',
        JSON.stringify([defaultItem.id]),
      );

      const wrapper = createWrapper();
      const likeButton = wrapper.find('.roadmap-card__like-btn');

      expect(likeButton.attributes('disabled')).toBeDefined();
      expect(likeButton.classes()).toContain('roadmap-card__like-btn--liked');
    });

    it('rolls back like count on API error', async () => {
      vi.mocked(roadmapService.likeEpic).mockRejectedValue(
        new Error('Network error'),
      );

      const wrapper = createWrapper({ item: { ...defaultItem, likes: 5 } });
      const likeButton = wrapper.find('.roadmap-card__like-btn');

      await likeButton.trigger('click');
      await new Promise((resolve) => setTimeout(resolve, 600));
      await wrapper.vm.$nextTick();

      // Should rollback to original count
      expect(wrapper.text()).toContain('5');
      // Error message should be displayed
      expect(wrapper.find('.roadmap-card__error').exists()).toBe(true);
    });

    it('shows loading state while processing like', async () => {
      vi.mocked(roadmapService.likeEpic).mockImplementation(
        () => new Promise(() => {}),
      ); // Never resolves

      const wrapper = createWrapper();
      const likeButton = wrapper.find('.roadmap-card__like-btn');

      await likeButton.trigger('click');
      await wrapper.vm.$nextTick();

      expect(likeButton.classes()).toContain('roadmap-card__like-btn--loading');
    });
  });

  describe('formatted descriptions', () => {
    it('renders formatted HTML description correctly', async () => {
      const itemWithHtml = {
        ...defaultItem,
        description: '<p>This is <strong>bold</strong> text.</p>',
      };
      const wrapper = createWrapper({ item: itemWithHtml, autoExpand: true });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.html()).toContain('<strong>bold</strong>');
    });

    it('displays bold text with strong tag', async () => {
      const itemWithBold = {
        ...defaultItem,
        description: '<p>This is <strong>important</strong> information.</p>',
      };
      const wrapper = createWrapper({ item: itemWithBold, autoExpand: true });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.html()).toContain('<strong>important</strong>');
      expect(description.text()).toContain('important');
    });

    it('displays italic text with em tag', async () => {
      const itemWithItalic = {
        ...defaultItem,
        description: '<p>This is <em>emphasized</em> text.</p>',
      };
      const wrapper = createWrapper({ item: itemWithItalic, autoExpand: true });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.html()).toContain('<em>emphasized</em>');
    });

    it('renders links with security attributes', async () => {
      const itemWithLink = {
        ...defaultItem,
        description:
          '<p>Visit <a href="https://example.com" rel="noopener noreferrer" target="_blank">our docs</a></p>',
      };
      const wrapper = createWrapper({ item: itemWithLink, autoExpand: true });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      const link = description.find('a');

      expect(link.exists()).toBe(true);
      expect(link.attributes('href')).toBe('https://example.com');
      expect(link.attributes('rel')).toBe('noopener noreferrer');
      expect(link.attributes('target')).toBe('_blank');
    });

    it('renders lists with proper structure', async () => {
      const itemWithList = {
        ...defaultItem,
        description: '<ul><li>Item 1</li><li>Item 2</li></ul>',
      };
      const wrapper = createWrapper({ item: itemWithList, autoExpand: true });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.html()).toContain('<ul>');
      expect(description.html()).toContain('<li>Item 1</li>');
      expect(description.html()).toContain('<li>Item 2</li>');
    });

    it('handles plain text descriptions for backward compatibility', async () => {
      const itemWithPlainText = {
        ...defaultItem,
        description: 'This is plain text without any formatting.',
      };
      const wrapper = createWrapper({
        item: itemWithPlainText,
        autoExpand: true,
      });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.text()).toBe(
        'This is plain text without any formatting.',
      );
    });
  });

  describe('mixed formatting (User Story 3)', () => {
    it('displays combined formatting (bold + italic) correctly', async () => {
      const itemWithCombined = {
        ...defaultItem,
        description: '<p><strong><em>very important</em></strong></p>',
      };
      const wrapper = createWrapper({ item: itemWithCombined, autoExpand: true });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.html()).toContain('<strong><em>very important</em></strong>');
    });

    it('renders formatted list items (bold, links) correctly', async () => {
      const itemWithFormattedList = {
        ...defaultItem,
        description:
          '<ul><li><strong>Bold item</strong></li><li><a href="https://example.com" rel="noopener noreferrer" target="_blank">Link item</a></li></ul>',
      };
      const wrapper = createWrapper({
        item: itemWithFormattedList,
        autoExpand: true,
      });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.html()).toContain('<strong>Bold item</strong>');
      expect(description.find('a').attributes('href')).toBe('https://example.com');
    });

    it('displays nested lists with proper hierarchy', async () => {
      const itemWithNestedList = {
        ...defaultItem,
        description:
          '<ul><li>Level 1<ul><li>Level 2<ul><li>Level 3</li></ul></li></ul></li></ul>',
      };
      const wrapper = createWrapper({
        item: itemWithNestedList,
        autoExpand: true,
      });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      const html = description.html();

      // Check nested structure exists
      expect(html).toContain('Level 1');
      expect(html).toContain('Level 2');
      expect(html).toContain('Level 3');

      // Verify multiple ul tags (nested lists)
      const ulCount = (html.match(/<ul>/g) || []).length;
      expect(ulCount).toBeGreaterThanOrEqual(2);
    });
  });

  describe('code blocks and preformatted text (User Story 2)', () => {
    it('renders code block with monospace font', async () => {
      const itemWithCodeBlock = {
        ...defaultItem,
        description:
          '<pre><code class="language-python">def hello():\n    print("Hi")</code></pre>',
      };
      const wrapper = createWrapper({
        item: itemWithCodeBlock,
        autoExpand: true,
      });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.html()).toContain('<pre>');
      expect(description.html()).toContain('<code');
      expect(description.html()).toContain('class="language-python"');
    });

    it('displays inline code distinctly from text', async () => {
      const itemWithInlineCode = {
        ...defaultItem,
        description: '<p>Use <code>print()</code> function.</p>',
      };
      const wrapper = createWrapper({
        item: itemWithInlineCode,
        autoExpand: true,
      });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.html()).toContain('<code>print()</code>');
      expect(description.text()).toContain('print()');
    });

    it('renders blockquote with proper styling', async () => {
      const itemWithBlockquote = {
        ...defaultItem,
        description: '<blockquote><p>This is a quote.</p></blockquote>',
      };
      const wrapper = createWrapper({
        item: itemWithBlockquote,
        autoExpand: true,
      });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      expect(description.html()).toContain('<blockquote>');
      expect(description.text()).toContain('This is a quote.');
    });

    it('preserves whitespace in code blocks', async () => {
      const itemWithCode = {
        ...defaultItem,
        description:
          '<pre><code>def hello():\n    print("Hi")\n    return True</code></pre>',
      };
      const wrapper = createWrapper({ item: itemWithCode, autoExpand: true });
      await wrapper.vm.$nextTick();

      const description = wrapper.find('.roadmap-card__description');
      const codeElement = description.find('code');

      // Check whitespace preserved (newlines and indentation)
      expect(codeElement.text()).toContain('\n    print');
      expect(codeElement.text()).toContain('\n    return');
    });
  });
});
