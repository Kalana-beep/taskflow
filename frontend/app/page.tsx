'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from '../components/Navbar';
import { StatsCards } from '../components/StatsCards';
import { TaskFilterBar } from '../components/TaskFilterBar';
import { TaskCard } from '../components/TaskCard';
import { TaskModal } from '../components/TaskModal';
import { DeleteModal } from '../components/DeleteModal';
import { taskApi } from '../lib/api';
import {
  Task,
  TaskCreateInput,
  TaskPriority,
  TaskStatsResponse,
  TaskStatus,
  TaskUpdateInput,
} from '../types/task';
import {
  AlertCircle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Loader2,
  RefreshCw,
} from 'lucide-react';

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [stats, setStats] = useState<TaskStatsResponse>({
    total: 0,
    todo: 0,
    in_progress: 0,
    done: 0,
    high_priority: 0,
  });

  const [loading, setLoading] = useState(true);
  const [statsLoading, setStatsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Filters & pagination
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'ALL'>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | 'ALL'>('ALL');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const pageSize = 9;

  // Modals state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deletingTask, setDeletingTask] = useState<Task | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      setStatsLoading(true);
      const data = await taskApi.getStats();
      setStats(data);
    } catch {
      // Degraded stats shouldn't block dashboard
    } finally {
      setStatsLoading(false);
    }
  }, []);

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await taskApi.getTasks({
        page,
        page_size: pageSize,
        search,
        status: statusFilter,
        priority: priorityFilter,
      });
      setTasks(res.items);
      setTotalPages(res.pages);
      setTotalCount(res.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to connect to TaskFlow API');
    } finally {
      setLoading(false);
    }
  }, [page, search, statusFilter, priorityFilter]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Clear toast feedback after 4s
  useEffect(() => {
    if (feedback) {
      const timer = setTimeout(() => setFeedback(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [feedback]);

  const handleFilterChange = (type: 'status' | 'priority', value: string) => {
    setPage(1);
    if (type === 'status') {
      setStatusFilter(value as TaskStatus | 'ALL');
    } else {
      setPriorityFilter(value as TaskPriority | 'ALL');
    }
  };

  const handleResetFilters = () => {
    setSearch('');
    setStatusFilter('ALL');
    setPriorityFilter('ALL');
    setPage(1);
  };

  const handleCreateOrUpdate = async (data: TaskCreateInput | TaskUpdateInput) => {
    if (editingTask) {
      await taskApi.updateTask(editingTask.id, data as TaskUpdateInput);
      setFeedback({ type: 'success', message: 'Task updated successfully' });
    } else {
      await taskApi.createTask(data as TaskCreateInput);
      setFeedback({ type: 'success', message: 'Task created successfully' });
    }
    fetchTasks();
    fetchStats();
  };

  const handleDelete = async () => {
    if (!deletingTask) return;
    await taskApi.deleteTask(deletingTask.id);
    setFeedback({ type: 'success', message: 'Task deleted successfully' });
    fetchTasks();
    fetchStats();
  };

  const handleStatusChange = async (task: Task, newStatus: TaskStatus) => {
    try {
      await taskApi.updateTask(task.id, { status: newStatus });
      setFeedback({ type: 'success', message: `Status changed to ${newStatus}` });
      fetchTasks();
      fetchStats();
    } catch {
      setFeedback({ type: 'error', message: 'Failed to update status' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar
        onNewTask={() => {
          setEditingTask(null);
          setIsModalOpen(true);
        }}
        systemHealthy={!error}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Feedback Alert */}
        {feedback && (
          <div
            data-testid="feedback-toast"
            className={`mb-6 p-4 rounded-xl border flex items-center justify-between text-sm transition-all animate-in fade-in slide-in-from-top-2 duration-200 ${
              feedback.type === 'success'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
                : 'bg-rose-50 border-rose-200 text-rose-800'
            }`}
          >
            <div className="flex items-center space-x-2">
              {feedback.type === 'success' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              ) : (
                <AlertCircle className="w-4 h-4 text-rose-600" />
              )}
              <span className="font-medium">{feedback.message}</span>
            </div>
            <button
              onClick={() => setFeedback(null)}
              className="text-xs font-semibold uppercase hover:underline"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Dashboard Title & Overview */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-2">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Task Dashboard
            </h1>
          </div>
          <button
            onClick={() => {
              fetchTasks();
              fetchStats();
            }}
            type="button"
            className="self-start md:self-auto inline-flex items-center space-x-2 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 rounded-lg shadow-xs transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading || statsLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* KPI Stats Overview */}
        <StatsCards
          stats={stats}
          activeStatus={statusFilter}
          activePriority={priorityFilter}
          onFilterChange={handleFilterChange}
        />

        {/* Search and Filters */}
        <TaskFilterBar
          search={search}
          onSearchChange={(val) => {
            setSearch(val);
            setPage(1);
          }}
          status={statusFilter}
          onStatusChange={(val) => {
            setStatusFilter(val);
            setPage(1);
          }}
          priority={priorityFilter}
          onPriorityChange={(val) => {
            setPriorityFilter(val);
            setPage(1);
          }}
          onReset={handleResetFilters}
        />

        {/* Content Section: Loading, Error, Empty, or Tasks Grid */}
        {loading ? (
          <div
            data-testid="loading-state"
            className="flex flex-col items-center justify-center py-20 text-slate-500"
          >
            <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-3" />
            <p className="text-sm font-medium">Loading tasks from TaskFlow API...</p>
          </div>
        ) : error ? (
          <div
            data-testid="error-state"
            className="bg-white rounded-2xl border border-rose-200 p-8 text-center max-w-lg mx-auto shadow-xs my-8"
          >
            <div className="w-12 h-12 bg-rose-50 text-rose-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-1">Failed to Load Tasks</h3>
            <p className="text-sm text-slate-600 mb-6">{error}</p>
            <button
              onClick={() => {
                fetchTasks();
                fetchStats();
              }}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry Connection</span>
            </button>
          </div>
        ) : tasks.length === 0 ? (
          <div
            data-testid="empty-state"
            className="bg-white rounded-2xl border border-dashed border-slate-300 p-12 text-center max-w-md mx-auto my-8"
          >
            <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <ClipboardList className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-1">No Tasks Found</h3>
            <p className="text-sm text-slate-500 mb-6">
              {search || statusFilter !== 'ALL' || priorityFilter !== 'ALL'
                ? 'No tasks matched your active filter criteria. Try adjusting your query.'
                : 'Get started by creating your first task in TaskFlow.'}
            </p>
            {search || statusFilter !== 'ALL' || priorityFilter !== 'ALL' ? (
              <button
                onClick={handleResetFilters}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
              >
                Clear Filters
              </button>
            ) : (
              <button
                onClick={() => {
                  setEditingTask(null);
                  setIsModalOpen(true);
                }}
                className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm"
              >
                <span>Create Task</span>
              </button>
            )}
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between text-xs text-slate-500 mb-4 px-1">
              <span>
                Showing {tasks.length} of {totalCount} task{totalCount === 1 ? '' : 's'}
              </span>
              <span>
                Page {page} of {totalPages || 1}
              </span>
            </div>

            <div
              data-testid="task-grid"
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              {tasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onEdit={(t) => {
                    setEditingTask(t);
                    setIsModalOpen(true);
                  }}
                  onDelete={(t) => {
                    setDeletingTask(t);
                    setIsDeleteModalOpen(true);
                  }}
                  onStatusChange={handleStatusChange}
                />
              ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center space-x-3 mt-8">
                <button
                  onClick={() => setPage((p) => Math.max(p - 1, 1))}
                  disabled={page <= 1}
                  data-testid="prev-page-btn"
                  className="inline-flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:pointer-events-none transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Previous</span>
                </button>
                <span className="text-xs text-slate-600 font-medium">
                  {page} / {totalPages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
                  disabled={page >= totalPages}
                  data-testid="next-page-btn"
                  className="inline-flex items-center space-x-1 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:pointer-events-none transition-colors"
                >
                  <span>Next</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Task Create / Edit Modal */}
      <TaskModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateOrUpdate}
        task={editingTask}
      />

      {/* Task Delete Confirmation Modal */}
      <DeleteModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDelete}
        task={deletingTask}
      />
    </div>
  );
}
