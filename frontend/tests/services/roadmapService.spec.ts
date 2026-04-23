/**
 * Unit tests for roadmapService
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import {
  mockRoadmapItems,
  mockModules,
  mockStats,
} from '../../mocks/roadmapData';

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
    })),
  },
}));

describe('roadmapService', () => {
  let mockAxiosGet: ReturnType<typeof vi.fn>;
  let mockAxiosPost: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    // Get the mocked axios instance
    mockAxiosGet = vi.fn();
    mockAxiosPost = vi.fn();
    (axios.create as ReturnType<typeof vi.fn>).mockReturnValue({
      get: mockAxiosGet,
      post: mockAxiosPost,
    });

    // Re-import to get fresh instance
    vi.resetModules();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('getRoadmapItems', () => {
    it('fetches items without filters', async () => {
      const mockResponse = {
        data: {
          items: mockRoadmapItems,
          total: mockRoadmapItems.length,
          lastSyncedAt: '2025-01-01T00:00:00Z',
          isStale: false,
        },
      };
      mockAxiosGet.mockResolvedValue(mockResponse);

      // Import fresh module
      const { getRoadmapItems: getItems } =
        await import('@/services/roadmapService');
      await getItems();

      expect(mockAxiosGet).toHaveBeenCalledWith('/roadmap/items', {
        params: expect.any(URLSearchParams),
      });
    });

    it('fetches items with status filter', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      mockAxiosGet.mockResolvedValue(mockResponse);

      const { getRoadmapItems: getItems } =
        await import('@/services/roadmapService');
      await getItems({ status: 'DELIVERED' });

      expect(mockAxiosGet).toHaveBeenCalled();
    });

    it('fetches items with all filters', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      mockAxiosGet.mockResolvedValue(mockResponse);

      const { getRoadmapItems: getItems } =
        await import('@/services/roadmapService');
      await getItems({
        status: 'NOW',
        year: 2025,
        quarter: 'Q1',
        module: 'test-module',
      });

      expect(mockAxiosGet).toHaveBeenCalled();
    });

    it('fetches items with multiple modules (array)', async () => {
      const mockResponse = { data: { items: [], total: 0 } };
      mockAxiosGet.mockResolvedValue(mockResponse);

      const { getRoadmapItems: getItems } =
        await import('@/services/roadmapService');
      await getItems({
        status: 'NOW',
        module: ['module-a', 'module-b', 'module-c'],
      });

      expect(mockAxiosGet).toHaveBeenCalled();
      // Verify the params include multiple module values
      const callArgs = mockAxiosGet.mock.calls[0];
      const params = callArgs[1].params as URLSearchParams;
      expect(params.getAll('module')).toEqual([
        'module-a',
        'module-b',
        'module-c',
      ]);
    });
  });

  describe('getRoadmapItem', () => {
    it('fetches single item by ID', async () => {
      const mockResponse = { data: mockRoadmapItems[0] };
      mockAxiosGet.mockResolvedValue(mockResponse);

      const { getRoadmapItem: getItem } =
        await import('@/services/roadmapService');
      await getItem('TEST-001');

      expect(mockAxiosGet).toHaveBeenCalledWith('/roadmap/items/TEST-001');
    });
  });

  describe('getModules', () => {
    it('fetches modules', async () => {
      const mockResponse = { data: { modules: mockModules } };
      mockAxiosGet.mockResolvedValue(mockResponse);

      const { getModules: fetchModules } =
        await import('@/services/roadmapService');
      await fetchModules();

      expect(mockAxiosGet).toHaveBeenCalledWith('/roadmap/modules');
    });
  });

  describe('getStats', () => {
    it('fetches stats without filters', async () => {
      const mockResponse = {
        data: {
          stats: mockStats,
          total: 4,
          lastSyncedAt: '2025-01-01T00:00:00Z',
        },
      };
      mockAxiosGet.mockResolvedValue(mockResponse);

      const { getStats: fetchStats } =
        await import('@/services/roadmapService');
      await fetchStats();

      expect(mockAxiosGet).toHaveBeenCalledWith('/roadmap/stats', {
        params: expect.any(URLSearchParams),
      });
    });

    it('fetches stats with filters', async () => {
      const mockResponse = { data: { stats: mockStats, total: 2 } };
      mockAxiosGet.mockResolvedValue(mockResponse);

      const { getStats: fetchStats } =
        await import('@/services/roadmapService');
      await fetchStats({ year: 2025, module: 'test-module' });

      expect(mockAxiosGet).toHaveBeenCalled();
    });

    it('fetches stats with multiple modules (array)', async () => {
      const mockResponse = { data: { stats: mockStats, total: 2 } };
      mockAxiosGet.mockResolvedValue(mockResponse);

      const { getStats: fetchStats } =
        await import('@/services/roadmapService');
      await fetchStats({ module: ['module-a', 'module-b'] });

      expect(mockAxiosGet).toHaveBeenCalled();
      // Verify the params include multiple module values
      const callArgs = mockAxiosGet.mock.calls[0];
      const params = callArgs[1].params as URLSearchParams;
      expect(params.getAll('module')).toEqual(['module-a', 'module-b']);
    });
  });

  describe('getHealth', () => {
    it('fetches health status', async () => {
      const mockResponse = {
        data: {
          status: 'healthy',
          lastSyncAt: '2025-01-01T00:00:00Z',
          lastSyncStatus: 'SUCCESS',
          itemCount: 10,
          isStale: false,
        },
      };
      mockAxiosGet.mockResolvedValue(mockResponse);

      const { getHealth: fetchHealth } =
        await import('@/services/roadmapService');
      await fetchHealth();

      expect(mockAxiosGet).toHaveBeenCalledWith('/health');
    });
  });

  describe('likeEpic', () => {
    it('successfully likes an epic', async () => {
      const mockResponse = {
        data: {
          success: true,
          likes: 43,
          id: 'TEST-001',
        },
      };
      mockAxiosPost.mockResolvedValue(mockResponse);

      const { likeEpic } = await import('@/services/roadmapService');
      const result = await likeEpic('TEST-001');

      expect(mockAxiosPost).toHaveBeenCalledWith('/roadmap/items/TEST-001/like');
      expect(result.success).toBe(true);
      expect(result.likes).toBe(43);
    });

    it('handles like error gracefully', async () => {
      mockAxiosPost.mockRejectedValue(new Error('JIRA API Error'));

      const { likeEpic } = await import('@/services/roadmapService');

      await expect(likeEpic('TEST-001')).rejects.toThrow('JIRA API Error');
    });
  });

  describe('error handling', () => {
    it('throws error when request fails', async () => {
      mockAxiosGet.mockRejectedValue(new Error('Network Error'));

      const { getRoadmapItems: getItems } =
        await import('@/services/roadmapService');

      await expect(getItems()).rejects.toThrow('Network Error');
    });
  });

  describe('Feature Request Operations', () => {
    it('should get feature request modules', async () => {
      const mockModulesResponse = {
        modules: [
          { id: 'nexus', name: 'Nexus', itemCount: 5 },
          { id: 'engage', name: 'Engage', itemCount: 3 },
        ],
      };

      mockAxiosGet.mockResolvedValue({ data: mockModulesResponse });

      const { getFeatureRequestModules } =
        await import('@/services/roadmapService');

      const result = await getFeatureRequestModules();

      expect(mockAxiosGet).toHaveBeenCalledWith(
        '/roadmap/feature-request/modules',
      );
      expect(result).toEqual(mockModulesResponse);
    });

    it('should create a feature request', async () => {
      const mockResponse = {
        success: true,
        issueKey: 'NEXUS-123',
        issueUrl: 'https://test.atlassian.net/browse/NEXUS-123',
        leaderNotificationStatus: 'SENT',
        message: 'Feature request submitted successfully',
      };

      mockAxiosPost.mockResolvedValue({ data: mockResponse });

      const { createFeatureRequest } = await import('@/services/roadmapService');

      const payload = {
        moduleId: 'nexus',
        title: 'Test Feature',
        description: 'This is a test feature request',
        contactEmail: 'user@example.com',
      };

      const idempotencyKey = 'test-key-123';

      const result = await createFeatureRequest(payload, idempotencyKey);

      expect(mockAxiosPost).toHaveBeenCalledWith(
        '/roadmap/feature-requests',
        payload,
        {
          headers: {
            'Idempotency-Key': idempotencyKey,
          },
        },
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle feature request creation error', async () => {
      mockAxiosPost.mockRejectedValue(new Error('Validation Error'));

      const { createFeatureRequest } = await import('@/services/roadmapService');

      const payload = {
        moduleId: 'nexus',
        title: 'Test',
        description: 'Test description',
        contactEmail: 'user@example.com',
      };

      await expect(
        createFeatureRequest(payload, 'test-key'),
      ).rejects.toThrow('Validation Error');
    });
  });
});
