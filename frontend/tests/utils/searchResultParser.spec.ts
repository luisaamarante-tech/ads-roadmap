/**
 * Unit tests for searchResultParser utility.
 */

import { describe, it, expect } from 'vitest';
import {
  parseSearchResults,
  extractIds,
  isValidId,
  hasSearchResultBlock,
  cleanMessageText,
} from '@/utils/searchResultParser';

describe('searchResultParser', () => {
  describe('parseSearchResults', () => {
    it('parses valid [[SEARCH_RESULT]] block with multiple IDs', () => {
      const text = `Here are some features for you!
[[SEARCH_RESULT]]
- EXPERI-2434
- ENGAGE-4388
- ENGAGE-4047
[[/SEARCH_RESULT]]`;

      const result = parseSearchResults(text);

      expect(result.found).toBe(true);
      expect(result.result).not.toBeNull();
      expect(result.result?.ids).toEqual([
        'EXPERI-2434',
        'ENGAGE-4388',
        'ENGAGE-4047',
      ]);
      expect(result.result?.hasResults).toBe(true);
      expect(result.cleanText).toBe('Here are some features for you!');
    });

    it('returns found=false when no block present', () => {
      const text = 'Just a normal message without any search results';

      const result = parseSearchResults(text);

      expect(result.found).toBe(false);
      expect(result.result).toBeNull();
      expect(result.cleanText).toBe(text);
    });

    it('handles empty text', () => {
      const result = parseSearchResults('');

      expect(result.found).toBe(false);
      expect(result.result).toBeNull();
      expect(result.cleanText).toBe('');
    });

    it('handles null/undefined text gracefully', () => {
      const result = parseSearchResults(null as unknown as string);

      expect(result.found).toBe(false);
      expect(result.result).toBeNull();
    });

    it('handles block with no valid IDs', () => {
      const text = `Message
[[SEARCH_RESULT]]
- invalid
- also-invalid
[[/SEARCH_RESULT]]`;

      const result = parseSearchResults(text);

      expect(result.found).toBe(true);
      expect(result.result?.ids).toEqual([]);
      expect(result.result?.hasResults).toBe(false);
    });

    it('removes duplicate IDs', () => {
      const text = `[[SEARCH_RESULT]]
- EXPERI-2434
- ENGAGE-4388
- EXPERI-2434
[[/SEARCH_RESULT]]`;

      const result = parseSearchResults(text);

      expect(result.result?.ids).toEqual(['EXPERI-2434', 'ENGAGE-4388']);
    });

    it('filters out invalid IDs but keeps valid ones', () => {
      const text = `[[SEARCH_RESULT]]
- EXPERI-2434
- invalid-id
- ENGAGE-4388
- lowercase-123
[[/SEARCH_RESULT]]`;

      const result = parseSearchResults(text);

      expect(result.result?.ids).toEqual(['EXPERI-2434', 'ENGAGE-4388']);
    });

    it('handles block at end of message', () => {
      const text = `Check these out: [[SEARCH_RESULT]]
- TEST-123
[[/SEARCH_RESULT]]`;

      const result = parseSearchResults(text);

      expect(result.found).toBe(true);
      expect(result.result?.ids).toEqual(['TEST-123']);
      expect(result.cleanText).toBe('Check these out:');
    });

    it('includes timestamp in result', () => {
      const before = Date.now();
      const result = parseSearchResults(`[[SEARCH_RESULT]]
- TEST-123
[[/SEARCH_RESULT]]`);
      const after = Date.now();

      expect(result.result?.timestamp).toBeGreaterThanOrEqual(before);
      expect(result.result?.timestamp).toBeLessThanOrEqual(after);
    });
  });

  describe('extractIds', () => {
    it('extracts IDs from dash-prefixed lines', () => {
      const content = `
- EXPERI-2434
- ENGAGE-4388
`;
      const ids = extractIds(content);

      expect(ids).toEqual(['EXPERI-2434', 'ENGAGE-4388']);
    });

    it('handles lines without dash prefix', () => {
      const content = `
EXPERI-2434
ENGAGE-4388
`;
      const ids = extractIds(content);

      // Lines without dash should still be parsed if they match ID pattern
      expect(ids).toEqual(['EXPERI-2434', 'ENGAGE-4388']);
    });

    it('skips empty lines', () => {
      const content = `
- EXPERI-2434

- ENGAGE-4388
`;
      const ids = extractIds(content);

      expect(ids).toEqual(['EXPERI-2434', 'ENGAGE-4388']);
    });

    it('returns empty array for empty content', () => {
      expect(extractIds('')).toEqual([]);
      expect(extractIds(null as unknown as string)).toEqual([]);
    });
  });

  describe('isValidId', () => {
    it('accepts valid ID formats', () => {
      expect(isValidId('EXPERI-2434')).toBe(true);
      expect(isValidId('ENGAGE-4388')).toBe(true);
      expect(isValidId('TEST-1')).toBe(true);
      expect(isValidId('ABC-123456')).toBe(true);
    });

    it('rejects invalid ID formats', () => {
      expect(isValidId('invalid')).toBe(false);
      expect(isValidId('lowercase-123')).toBe(false);
      expect(isValidId('EXPERI2434')).toBe(false);
      expect(isValidId('123-ABC')).toBe(false);
      expect(isValidId('')).toBe(false);
      expect(isValidId('EXPERI-')).toBe(false);
      expect(isValidId('-123')).toBe(false);
    });
  });

  describe('hasSearchResultBlock', () => {
    it('returns true when block is present', () => {
      const text = `Message [[SEARCH_RESULT]]
- TEST-123
[[/SEARCH_RESULT]]`;

      expect(hasSearchResultBlock(text)).toBe(true);
    });

    it('returns false when block is not present', () => {
      expect(hasSearchResultBlock('Normal message')).toBe(false);
      expect(hasSearchResultBlock('[[SEARCH_RESULT]] incomplete')).toBe(false);
    });
  });

  describe('cleanMessageText', () => {
    it('removes [[SEARCH_RESULT]] block from text', () => {
      const text = `Hello! [[SEARCH_RESULT]]
- TEST-123
[[/SEARCH_RESULT]] Goodbye!`;

      expect(cleanMessageText(text)).toBe('Hello!  Goodbye!');
    });

    it('returns original text if no block', () => {
      const text = 'Just a normal message';
      expect(cleanMessageText(text)).toBe(text);
    });

    it('handles empty text', () => {
      expect(cleanMessageText('')).toBe('');
      expect(cleanMessageText(null as unknown as string)).toBe('');
    });
  });
});
