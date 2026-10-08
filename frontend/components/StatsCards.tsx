'use client';

import React from 'react';
import { Layers, Clock, ArrowUpRight, CheckCircle2, AlertTriangle } from 'lucide-react';
import { TaskStatsResponse, TaskStatus, TaskPriority } from '../types/task';

interface StatsCardsProps {
  stats: TaskStatsResponse;
  activeStatus?: TaskStatus | 'ALL';
  activePriority?: TaskPriority | 'ALL';
  onFilterChange: (type: 'status' | 'priority', value: string) => void;
}

export const StatsCards: React.FC<StatsCardsProps> = ({
  stats,
  activeStatus = 'ALL',
  activePriority = 'ALL',
  onFilterChange,
}) => {
  const cards = [
    {
      id: 'total',
      label: 'Total Tasks',
      value: stats.total,
      icon: Layers,
      color: 'blue',
      active: activeStatus === 'ALL' && activePriority === 'ALL',
      onClick: () => {
        onFilterChange('status', 'ALL');
        onFilterChange('priority', 'ALL');
      },
    },
    {
      id: 'todo',
      label: 'To Do',
      value: stats.todo,
      icon: Clock,
      color: 'slate',
      active: activeStatus === 'TODO',
      onClick: () => onFilterChange('status', 'TODO'),
    },
    {
      id: 'in_progress',
      label: 'In Progress',
      value: stats.in_progress,
      icon: ArrowUpRight,
      color: 'indigo',
      active: activeStatus === 'IN_PROGRESS',
      onClick: () => onFilterChange('status', 'IN_PROGRESS'),
    },
    {
      id: 'done',
      label: 'Completed',
      value: stats.done,
      icon: CheckCircle2,
      color: 'emerald',
      active: activeStatus === 'DONE',
      onClick: () => onFilterChange('status', 'DONE'),
    },
    {
      id: 'high_priority',
      label: 'High Priority',
      value: stats.high_priority,
      icon: AlertTriangle,
      color: 'rose',
      active: activePriority === 'HIGH',
      onClick: () => onFilterChange('priority', 'HIGH'),
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 my-6">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <button
            key={card.id}
            type="button"
            onClick={card.onClick}
            data-testid={`stat-card-${card.id}`}
            className={`flex flex-col text-left p-4 rounded-xl border transition-all duration-150 ${
              card.active
                ? 'bg-white border-blue-500 shadow-md ring-2 ring-blue-500/20'
                : 'bg-white border-slate-200/80 hover:border-slate-300 shadow-xs hover:shadow-sm'
            }`}
          >
            <div className="flex items-center justify-between w-full mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {card.label}
              </span>
              <div
                className={`p-1.5 rounded-lg ${
                  card.color === 'blue'
                    ? 'bg-blue-50 text-blue-600'
                    : card.color === 'emerald'
                    ? 'bg-emerald-50 text-emerald-600'
                    : card.color === 'indigo'
                    ? 'bg-indigo-50 text-indigo-600'
                    : card.color === 'rose'
                    ? 'bg-rose-50 text-rose-600'
                    : 'bg-slate-100 text-slate-600'
                }`}
              >
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-900">{card.value}</div>
          </button>
        );
      })}
    </div>
  );
};
