/**
 * API service for the Weni Public Roadmap.
 */

import axios from 'axios';
import type {
  RoadmapFilters,
  RoadmapItemsResponse,
  RoadmapItem,
  ModulesResponse,
  GoalsResponse,
  PillarsResponse,
  RoadmapStatsResponse,
  HealthResponse,
  LikeResponse,
} from '@/types/roadmap';

// API base URL from environment or default
import { env } from '@/utils/env';

const API_BASE = env.apiUrl;

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get roadmap items with optional filtering.
 */
export async function getRoadmapItems(
  filters: RoadmapFilters = {},
): Promise<RoadmapItemsResponse> {
  const params = new URLSearchParams();

  if (filters.status) params.append('status', filters.status);
  if (filters.year) params.append('year', String(filters.year));
  if (filters.quarter) params.append('quarter', filters.quarter);

  // Handle module: can be string or array
  if (filters.module) {
    if (Array.isArray(filters.module)) {
      filters.module.forEach((moduleId) => params.append('module', moduleId));
    } else {
      params.append('module', filters.module);
    }
  }

  // Handle goal: can be string or array
  if (filters.goal) {
    if (Array.isArray(filters.goal)) {
      filters.goal.forEach((goalId) => params.append('goal', goalId));
    } else {
      params.append('goal', filters.goal);
    }
  }

  // Handle pillar: can be string or array
  if (filters.pillar) {
    if (Array.isArray(filters.pillar)) {
      filters.pillar.forEach((pillarId) => params.append('pillar', pillarId));
    } else {
      params.append('pillar', filters.pillar);
    }
  }

  const response = await api.get<RoadmapItemsResponse>('/roadmap/items', {
    params,
  });
  return response.data;
}

/**
 * Get a single roadmap item by ID.
 */
export async function getRoadmapItem(itemId: string): Promise<RoadmapItem> {
  const response = await api.get<RoadmapItem>(`/roadmap/items/${itemId}`);
  return response.data;
}

/**
 * Like an epic by incrementing its like count.
 */
export async function likeEpic(itemId: string): Promise<LikeResponse> {
  const response = await api.post<LikeResponse>(
    `/roadmap/items/${itemId}/like`,
  );
  return response.data;
}

/**
 * Get all available modules for filtering.
 */
export async function getModules(): Promise<ModulesResponse> {
  const response = await api.get<ModulesResponse>('/roadmap/modules');
  return response.data;
}

/**
 * Get all available semester goals for filtering.
 */
export async function getGoals(): Promise<GoalsResponse> {
  const response = await api.get<GoalsResponse>('/roadmap/goals');
  return response.data;
}

/**
 * Get all available pillars for filtering.
 */
export async function getPillars(): Promise<PillarsResponse> {
  const response = await api.get<PillarsResponse>('/roadmap/pillars');
  return response.data;
}

/**
 * Get roadmap statistics (item counts by status).
 */
export async function getStats(
  filters: Omit<RoadmapFilters, 'status'> = {},
): Promise<RoadmapStatsResponse> {
  const params = new URLSearchParams();

  if (filters.year) params.append('year', String(filters.year));
  if (filters.quarter) params.append('quarter', filters.quarter);

  // Handle module: can be string or array
  if (filters.module) {
    if (Array.isArray(filters.module)) {
      filters.module.forEach((moduleId) => {
        params.append('module', moduleId);
      });
    } else {
      params.append('module', filters.module);
    }
  }

  const response = await api.get<RoadmapStatsResponse>('/roadmap/stats', {
    params,
  });
  return response.data;
}

/**
 * Check service health.
 */
export async function getHealth(): Promise<HealthResponse> {
  const response = await api.get<HealthResponse>('/health');
  return response.data;
}

/**
 * Get modules available for feature requests.
 */
export async function getFeatureRequestModules(): Promise<ModulesResponse> {
  const response = await api.get<ModulesResponse>(
    '/roadmap/feature-request/modules',
  );
  return response.data;
}

/**
 * Submit a feature request.
 */
export async function createFeatureRequest(
  payload: import('@/types/roadmap').FeatureRequestPayload,
  idempotencyKey: string,
): Promise<import('@/types/roadmap').FeatureRequestResponse> {
  const response = await api.post<
    import('@/types/roadmap').FeatureRequestResponse
  >('/roadmap/feature-requests', payload, {
    headers: {
      'Idempotency-Key': idempotencyKey,
    },
  });
  return response.data;
}
