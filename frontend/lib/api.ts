/**
 * TaskFlow API client
 */

import {
  Task,
  TaskCreateInput,
  TaskFilterOptions,
  TaskListResponse,
  TaskStatsResponse,
  TaskUpdateInput,
} from '../types/task';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  try {
    const res = await fetch(url, { ...options, headers });

    if (!res.ok) {
      let errorMessage = `HTTP error ${res.status}`;
      try {
        const errJson = await res.json();
        if (errJson.detail) {
          errorMessage = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
        }
      } catch {
        // Fallback to text
      }
      throw new ApiError(errorMessage, res.status);
    }

    if (res.status === 204) {
      return null as T;
    }

    return (await res.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(
      err instanceof Error ? err.message : 'Network request failed',
      0
    );
  }
}

export const taskApi = {
  /**
   * Fetch paginated tasks with optional filters
   */
  async getTasks(options: TaskFilterOptions = {}): Promise<TaskListResponse> {
    const params = new URLSearchParams();
    if (options.page) params.append('page', options.page.toString());
    if (options.page_size) params.append('page_size', options.page_size.toString());
    if (options.search?.trim()) params.append('search', options.search.trim());
    if (options.status && options.status !== 'ALL') params.append('status', options.status);
    if (options.priority && options.priority !== 'ALL') params.append('priority', options.priority);

    const query = params.toString() ? `?${params.toString()}` : '';
    return request<TaskListResponse>(`/api/tasks${query}`);
  },

  /**
   * Fetch task summary counts for dashboard
   */
  async getStats(): Promise<TaskStatsResponse> {
    return request<TaskStatsResponse>('/api/tasks/stats');
  },

  /**
   * Fetch single task by ID
   */
  async getTask(id: string): Promise<Task> {
    return request<Task>(`/api/tasks/${id}`);
  },

  /**
   * Create a new task
   */
  async createTask(data: TaskCreateInput): Promise<Task> {
    return request<Task>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Update task by ID
   */
  async updateTask(id: string, data: TaskUpdateInput): Promise<Task> {
    return request<Task>(`/api/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete task by ID
   */
  async deleteTask(id: string): Promise<void> {
    return request<void>(`/api/tasks/${id}`, {
      method: 'DELETE',
    });
  },
};
