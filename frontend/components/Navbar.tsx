'use client';

import React from 'react';
import { CheckSquare, Plus, Activity } from 'lucide-react';

interface NavbarProps {
  onNewTask: () => void;
  systemHealthy?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onNewTask, systemHealthy = true }) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <CheckSquare className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-slate-900 tracking-tight">TaskFlow</span>
              <span className="px-2 py-0.5 text-xs font-medium bg-blue-50 text-blue-700 rounded-full border border-blue-200/60">
                v0.1.0
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">Modern Task Management & DevOps Pipeline</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="hidden md:flex items-center space-x-1.5 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium border border-emerald-200">
            <Activity className="w-3.5 h-3.5 text-emerald-600" />
            <span>API {systemHealthy ? 'Online' : 'Degraded'}</span>
          </div>

          <button
            onClick={onNewTask}
            data-testid="create-task-btn"
            className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm shadow-blue-600/20 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Task</span>
          </button>
        </div>
      </div>
    </header>
  );
};
