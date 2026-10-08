'use client';

import React from 'react';
import { Search, Filter, RotateCcw } from 'lucide-react';
import { TaskStatus, TaskPriority } from '../types/task';

interface TaskFilterBarProps {
  search: string;
  onSearchChange: (value: string) => void;
  status: TaskStatus | 'ALL';
  onStatusChange: (value: TaskStatus | 'ALL') => void;
  priority: TaskPriority | 'ALL';
  onPriorityChange: (value: TaskPriority | 'ALL') => void;
  onReset: () => void;
}

export const TaskFilterBar: React.FC<TaskFilterBarProps> = ({
  search,
  onSearchChange,
  status,
  onStatusChange,
  priority,
  onPriorityChange,
  onReset,
}) => {
  const hasActiveFilters = search.trim() !== '' || status !== 'ALL' || priority !== 'ALL';

  return (
    <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs mb-6">
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            type="text"
            data-testid="search-input"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search tasks by title or description..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 hover:bg-slate-100/70 focus:bg-white text-sm rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all placeholder:text-slate-400"
          />
        </div>

        {/* Filter dropdowns */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center space-x-1.5 text-xs font-medium text-slate-500 mr-1">
            <Filter className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Filters:</span>
          </div>

          {/* Status select */}
          <select
            data-testid="status-filter"
            value={status}
            onChange={(e) => onStatusChange(e.target.value as TaskStatus | 'ALL')}
            className="px-3 py-2 text-xs font-medium bg-slate-50 hover:bg-slate-100 focus:bg-white rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all text-slate-700"
          >
            <option value="ALL">All Statuses</option>
            <option value="TODO">To Do</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="DONE">Completed</option>
          </select>

          {/* Priority select */}
          <select
            data-testid="priority-filter"
            value={priority}
            onChange={(e) => onPriorityChange(e.target.value as TaskPriority | 'ALL')}
            className="px-3 py-2 text-xs font-medium bg-slate-50 hover:bg-slate-100 focus:bg-white rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none transition-all text-slate-700"
          >
            <option value="ALL">All Priorities</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
          </select>

          {/* Clear filters button */}
          {hasActiveFilters && (
            <button
              onClick={onReset}
              data-testid="reset-filters-btn"
              type="button"
              className="inline-flex items-center space-x-1 px-2.5 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
