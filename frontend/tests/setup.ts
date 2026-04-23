/**
 * Vitest setup file
 * Configures test environment before tests run
 */

import { config } from '@vue/test-utils';

// Mock Unnnic components globally
config.global.stubs = {
  UnnnicButton: true,
  UnnnicInput: true,
  UnnnicTextArea: true,
  UnnnicSelectSmart: true,
  UnnnicTab: true,
  UnnnicSkeletonLoading: true,
  UnnnicIcon: true,
  UnnnicCard: true,
  UnnnicModal: true,
  UnnnicAlert: true,
};

// Mock IntersectionObserver
global.IntersectionObserver = class {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
} as unknown as typeof IntersectionObserver;

// Mock ResizeObserver
global.ResizeObserver = class {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
} as unknown as typeof ResizeObserver;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => {
      return store[key] || null;
    },
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});
