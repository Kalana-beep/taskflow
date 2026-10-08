import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { screen, waitFor, fireEvent } from '@testing-library/dom';
import Dashboard from '../app/page';
import { taskApi } from '../lib/api';
import { TaskListResponse, TaskStatsResponse } from '../types/task';

vi.mock('../lib/api', () => ({
  taskApi: {
    getTasks: vi.fn(),
    getStats: vi.fn(),
    createTask: vi.fn(),
    updateTask: vi.fn(),
    deleteTask: vi.fn(),
  },
}));

describe('Dashboard Component Suite', () => {
  const mockStats: TaskStatsResponse = {
    total: 3,
    todo: 1,
    in_progress: 1,
    done: 1,
    high_priority: 1,
  };

  const mockTasks: TaskListResponse = {
    items: [
      {
        id: 'task-1',
        title: 'Configure Docker Compose',
        description: 'Multi-container orchestration',
        status: 'TODO',
        priority: 'HIGH',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        completed_at: null,
      },
      {
        id: 'task-2',
        title: 'Run Trivy Vulnerability Scan',
        description: 'Scan images for CVEs',
        status: 'IN_PROGRESS',
        priority: 'MEDIUM',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        completed_at: null,
      },
    ],
    page: 1,
    page_size: 9,
    total: 2,
    pages: 1,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard with stats cards and task items', async () => {
    vi.mocked(taskApi.getStats).mockResolvedValue(mockStats);
    vi.mocked(taskApi.getTasks).mockResolvedValue(mockTasks);

    render(<Dashboard />);

    // Shows loading initially
    expect(screen.getByTestId('loading-state')).toBeInTheDocument();

    // Await tasks rendered
    await waitFor(() => {
      expect(screen.getByText('Configure Docker Compose')).toBeInTheDocument();
      expect(screen.getByText('Run Trivy Vulnerability Scan')).toBeInTheDocument();
    });

    // Verify stats counters
    expect(screen.getByTestId('stat-card-total')).toHaveTextContent('3');
    expect(screen.getByTestId('stat-card-todo')).toHaveTextContent('1');
    expect(screen.getByTestId('stat-card-in_progress')).toHaveTextContent('1');
  });

  it('renders empty state when no tasks exist', async () => {
    vi.mocked(taskApi.getStats).mockResolvedValue({
      total: 0,
      todo: 0,
      in_progress: 0,
      done: 0,
      high_priority: 0,
    });
    vi.mocked(taskApi.getTasks).mockResolvedValue({
      items: [],
      page: 1,
      page_size: 9,
      total: 0,
      pages: 0,
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
      expect(screen.getByText('No Tasks Found')).toBeInTheDocument();
    });
  });

  it('renders error state when API call fails', async () => {
    vi.mocked(taskApi.getStats).mockResolvedValue(mockStats);
    vi.mocked(taskApi.getTasks).mockRejectedValue(new Error('Connection refused'));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByTestId('error-state')).toBeInTheDocument();
      expect(screen.getByText('Connection refused')).toBeInTheDocument();
    });
  });

  it('opens create modal when clicking New Task button and submits successfully', async () => {
    vi.mocked(taskApi.getStats).mockResolvedValue(mockStats);
    vi.mocked(taskApi.getTasks).mockResolvedValue(mockTasks);
    vi.mocked(taskApi.createTask).mockResolvedValue({
      id: 'task-3',
      title: 'New Integration Test',
      description: 'Test end-to-end flow',
      status: 'TODO',
      priority: 'MEDIUM',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      completed_at: null,
    });

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Configure Docker Compose')).toBeInTheDocument();
    });

    // Click New Task button
    const createBtn = screen.getByTestId('create-task-btn');
    fireEvent.click(createBtn);

    // Modal opens
    expect(screen.getByText('Create New Task')).toBeInTheDocument();

    // Fill title
    const titleInput = screen.getByTestId('modal-title-input');
    fireEvent.change(titleInput, { target: { value: 'New Integration Test' } });

    // Submit
    const submitBtn = screen.getByTestId('modal-submit-btn');
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(taskApi.createTask).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'New Integration Test',
        })
      );
    });
  });

  it('filters tasks when searching keyword', async () => {
    vi.mocked(taskApi.getStats).mockResolvedValue(mockStats);
    vi.mocked(taskApi.getTasks).mockResolvedValue(mockTasks);

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByText('Configure Docker Compose')).toBeInTheDocument();
    });

    const searchInput = screen.getByTestId('search-input');
    fireEvent.change(searchInput, { target: { value: 'Docker' } });

    await waitFor(() => {
      expect(taskApi.getTasks).toHaveBeenCalledWith(
        expect.objectContaining({
          search: 'Docker',
        })
      );
    });
  });
});
