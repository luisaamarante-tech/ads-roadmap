/**
 * Mock data for testing
 */

import type { RoadmapItem, Module, RoadmapStats } from '@/types/roadmap';

export const mockRoadmapItems: RoadmapItem[] = [
  {
    id: 'TEST-001',
    title: 'Test Feature One',
    description: 'Description for test feature one',
    status: 'DELIVERED',
    module: 'Test Module',
    moduleId: 'test-module',
    releaseYear: 2025,
    releaseQuarter: 'Q1',
    releaseMonth: null,
    images: [],
    documentationUrl: null,
    likes: 15,
    lastSyncedAt: '2025-01-01T00:00:00Z',
  },
  {
    id: 'TEST-002',
    title: 'Test Feature Two',
    description: 'Description for test feature two with more details',
    status: 'NOW',
    module: 'Another Module',
    moduleId: 'another-module',
    releaseYear: 2025,
    releaseQuarter: 'Q2',
    releaseMonth: 4,
    images: ['https://example.com/image1.png'],
    documentationUrl: 'https://docs.example.com/feature-two',
    likes: 42,
    lastSyncedAt: '2025-01-15T00:00:00Z',
  },
  {
    id: 'TEST-003',
    title: 'Test Feature Three',
    description: 'Description for test feature three',
    status: 'NEXT',
    module: 'Test Module',
    moduleId: 'test-module',
    releaseYear: 2025,
    releaseQuarter: 'Q3',
    releaseMonth: null,
    images: [],
    documentationUrl: null,
    likes: 8,
    lastSyncedAt: '2025-01-20T00:00:00Z',
  },
  {
    id: 'TEST-004',
    title: 'Test Feature Four',
    description: 'Description for test feature four',
    status: 'FUTURE',
    module: 'Future Module',
    moduleId: 'future-module',
    releaseYear: 2026,
    releaseQuarter: 'Q1',
    releaseMonth: null,
    images: [],
    documentationUrl: null,
    likes: 0,
    lastSyncedAt: '2025-01-25T00:00:00Z',
  },
];

export const mockModules: Module[] = [
  { id: 'test-module', name: 'Test Module', itemCount: 2 },
  { id: 'another-module', name: 'Another Module', itemCount: 1 },
  { id: 'future-module', name: 'Future Module', itemCount: 1 },
];

export const mockStats: RoadmapStats = {
  DELIVERED: 1,
  NOW: 1,
  NEXT: 1,
  FUTURE: 1,
};

export const mockEmptyStats: RoadmapStats = {
  DELIVERED: 0,
  NOW: 0,
  NEXT: 0,
  FUTURE: 0,
};

export function getMockItemsByStatus(status: string): RoadmapItem[] {
  return mockRoadmapItems.filter((item) => item.status === status);
}

export function getMockItemById(id: string): RoadmapItem | undefined {
  return mockRoadmapItems.find((item) => item.id === id);
}
