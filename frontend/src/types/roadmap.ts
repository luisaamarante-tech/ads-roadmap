/**
 * TypeScript interfaces for the VTEX Ads Public Roadmap.
 */

export type DeliveryStatus = 'DELIVERED' | 'NOW' | 'NEXT' | 'FUTURE';

export type Quarter = 'Q1' | 'Q2' | 'Q3' | 'Q4';

export interface RoadmapItem {
  id: string;
  title: string;
  description: string;
  status: DeliveryStatus;
  module: string;
  moduleId: string;
  releaseYear: number;
  releaseQuarter: Quarter;
  releaseMonth?: number | null;
  images: string[];
  documentationUrl?: string | null;
  likes: number;
  lastSyncedAt: string;
  semesterGoals: string[];
  semesterGoalIds: string[];
}

export interface Module {
  id: string;
  name: string;
  itemCount: number;
}

export interface Goal {
  id: string;
  name: string;
  itemCount: number;
}

export interface RoadmapFilters {
  status?: DeliveryStatus;
  year?: number;
  quarter?: Quarter;
  module?: string | string[];
  goal?: string | string[];
}

export interface LikeResponse {
  id: string;
  likes: number;
  success: boolean;
  error?: string;
}

export interface RoadmapItemsResponse {
  items: RoadmapItem[];
  total: number;
  lastSyncedAt: string | null;
  isStale: boolean;
}

export interface ModulesResponse {
  modules: Module[];
}

export interface GoalsResponse {
  goals: Goal[];
}

export interface RoadmapStats {
  DELIVERED: number;
  NOW: number;
  NEXT: number;
  FUTURE: number;
}

export interface RoadmapStatsResponse {
  stats: RoadmapStats;
  total: number;
  lastSyncedAt: string | null;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  lastSyncAt: string | null;
  lastSyncStatus: 'SUCCESS' | 'PARTIAL' | 'FAILED' | null;
  itemCount: number;
  isStale: boolean;
  errorMessage?: string;
}

// Tab configuration
export interface StatusTab {
  value: DeliveryStatus;
  label: string;
  description: string;
}

export const STATUS_TABS: StatusTab[] = [
  {
    value: 'DELIVERED',
    label: 'Delivered',
    description: 'Features that have been released',
  },
  { value: 'NOW', label: 'Now', description: 'Features currently in progress' },
  {
    value: 'NEXT',
    label: 'Next',
    description: 'Features planned for near-term',
  },
  {
    value: 'FUTURE',
    label: 'Future',
    description: 'Features planned for longer-term',
  },
];

// Feature request types
export interface FeatureRequestPayload {
  moduleId: string;
  title: string;
  description: string;
  contactEmail: string;
  website?: string; // Honeypot field
}

export interface FeatureRequestResponse {
  success: boolean;
  issueKey: string;
  issueUrl?: string;
  leaderNotificationStatus?: string;
  message: string;
}

// Image carousel and share types
export type ImageLoadingState = 'loading' | 'loaded' | 'error';
export type ShareButtonSize = 'small' | 'medium' | 'large';
export type ShareButtonVariant = 'primary' | 'secondary' | 'outlined' | 'ghost';

export interface ClipboardCopyResult {
  success: boolean;
  error?: string;
}
