/**
 * Parser for [[SEARCH_RESULT]] blocks in WebChat messages.
 *
 * Extract roadmap item IDs from agent messages that contain hidden
 * [[SEARCH_RESULT]] blocks for filtering the roadmap display.
 */

import type { SearchResult, ParseResult } from '@/types/canvas';

/** Regex pattern for matching [[SEARCH_RESULT]] blocks */
const SEARCH_RESULT_REGEX =
  /\[\[SEARCH_RESULT\]\]([\s\S]*?)\[\[\/SEARCH_RESULT\]\]/;

/** Pattern for validating roadmap item IDs (e.g., EXPERI-2434, ENGAGE-4388) */
const VALID_ID_PATTERN = /^[A-Z]+-\d+$/;

/**
 * Parse a message text to extract [[SEARCH_RESULT]] block.
 *
 * @param text - The message text to parse
 * @returns ParseResult with extracted IDs and cleaned text
 *
 * @example
 * const result = parseSearchResults(`Hello! [[SEARCH_RESULT]]
 * - EXPERI-2434
 * - ENGAGE-4388
 * [[/SEARCH_RESULT]]`);
 * // result.found === true
 * // result.result.ids === ['EXPERI-2434', 'ENGAGE-4388']
 * // result.cleanText === 'Hello! '
 */
export function parseSearchResults(text: string): ParseResult {
  if (!text || typeof text !== 'string') {
    return {
      found: false,
      result: null,
      cleanText: text || '',
    };
  }

  const match = text.match(SEARCH_RESULT_REGEX);

  if (!match) {
    return {
      found: false,
      result: null,
      cleanText: text,
    };
  }

  const rawMatch = match[0];
  const content = match[1];

  // Extract IDs from the content
  const ids = extractIds(content);

  // Remove the [[SEARCH_RESULT]] block from text
  const cleanText = text.replace(SEARCH_RESULT_REGEX, '').trim();

  const result: SearchResult = {
    ids,
    hasResults: ids.length > 0,
    rawMatch,
    timestamp: Date.now(),
  };

  return {
    found: true,
    result,
    cleanText,
  };
}

/**
 * Extract valid roadmap item IDs from content.
 *
 * @param content - Content inside [[SEARCH_RESULT]] block
 * @returns Array of valid, unique IDs
 */
export function extractIds(content: string): string[] {
  if (!content) {
    return [];
  }

  const lines = content.split('\n');
  const ids: string[] = [];
  const seen = new Set<string>();

  for (const line of lines) {
    // Remove leading dash and whitespace
    const trimmed = line.replace(/^-\s*/, '').trim();

    // Skip empty lines
    if (!trimmed) {
      continue;
    }

    // Validate ID format
    if (!isValidId(trimmed)) {
      continue;
    }

    // Skip duplicates
    if (seen.has(trimmed)) {
      continue;
    }

    seen.add(trimmed);
    ids.push(trimmed);
  }

  return ids;
}

/**
 * Check if a string is a valid roadmap item ID.
 *
 * @param id - String to validate
 * @returns True if valid ID format (e.g., EXPERI-2434)
 */
export function isValidId(id: string): boolean {
  return VALID_ID_PATTERN.test(id);
}

/**
 * Check if text contains a [[SEARCH_RESULT]] block.
 *
 * @param text - Text to check
 * @returns True if block is present
 */
export function hasSearchResultBlock(text: string): boolean {
  return SEARCH_RESULT_REGEX.test(text);
}

/**
 * Remove [[SEARCH_RESULT]] block from text without parsing.
 *
 * @param text - Text to clean
 * @returns Text with [[SEARCH_RESULT]] block removed
 */
export function cleanMessageText(text: string): string {
  if (!text) {
    return '';
  }
  return text.replace(SEARCH_RESULT_REGEX, '').trim();
}
