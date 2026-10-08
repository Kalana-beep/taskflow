'use client';

import React from 'react';
import { AlertTriangle, Loader2 } from 'lucide-react';
import { Task } from '../types/task';

interface DeleteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void>;
  task?: Task | null;
}

export const DeleteModal: React.FC<DeleteModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  task,
}) => {
  const [deleting, setDeleting] = React.useState(false);

  if (!isOpen || !task) return null;

  const handleConfirm = async () => {
    setDeleting(true);
    try {
      await onConfirm();
      onClose();
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
      <div
        className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 p-6 animate-in fade-in zoom-in-95 duration-150"
        role="alertdialog"
        aria-modal="true"
      >
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2.5 rounded-full bg-rose-50 text-rose-600 border border-rose-100">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-900">Delete Task</h2>
        </div>

        <p className="text-sm text-slate-600 mb-6">
          Are you sure you want to permanently delete{' '}
          <span className="font-semibold text-slate-900">&quot;{task.title}&quot;</span>?
          This action cannot be undone.
        </p>

        <div className="flex items-center justify-end space-x-3">
          <button
            type="button"
            onClick={onClose}
            disabled={deleting}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            data-testid="confirm-delete-btn"
            disabled={deleting}
            className="inline-flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-lg transition-colors shadow-sm shadow-rose-600/20 disabled:opacity-50"
          >
            {deleting && <Loader2 className="w-4 h-4 animate-spin" />}
            <span>Delete Permanently</span>
          </button>
        </div>
      </div>
    </div>
  );
};
