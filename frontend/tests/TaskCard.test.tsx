import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { screen, fireEvent } from '@testing-library/dom';
import { TaskCard } from '../components/TaskCard';
import { Task } from '../types/task';

describe('TaskCard Component Suite', () => {
  const mockTask: Task = {
    id: 'task-100',
    title: 'Deploy to Staging',
    description: 'Verify smoke test and health endpoints',
    status: 'TODO',
    priority: 'HIGH',
    created_at: '2026-10-07T10:00:00Z',
    updated_at: '2026-10-07T10:00:00Z',
    completed_at: null,
  };

  it('renders task details correctly', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    const onStatusChange = vi.fn();

    render(
      <TaskCard
        task={mockTask}
        onEdit={onEdit}
        onDelete={onDelete}
        onStatusChange={onStatusChange}
      />
    );

    expect(screen.getByText('Deploy to Staging')).toBeInTheDocument();
    expect(screen.getByText('Verify smoke test and health endpoints')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
  });

  it('calls onStatusChange when status is changed via dropdown', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    const onStatusChange = vi.fn();

    render(
      <TaskCard
        task={mockTask}
        onEdit={onEdit}
        onDelete={onDelete}
        onStatusChange={onStatusChange}
      />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'DONE' } });

    expect(onStatusChange).toHaveBeenCalledWith(mockTask, 'DONE');
  });

  it('triggers onEdit and onDelete handlers', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    const onStatusChange = vi.fn();

    render(
      <TaskCard
        task={mockTask}
        onEdit={onEdit}
        onDelete={onDelete}
        onStatusChange={onStatusChange}
      />
    );

    // Open dropdown menu
    const menuBtn = screen.getByTestId('task-menu-btn-task-100');
    fireEvent.click(menuBtn);

    // Click Edit
    const editBtn = screen.getByText('Edit');
    fireEvent.click(editBtn);
    expect(onEdit).toHaveBeenCalledWith(mockTask);

    // Open menu again
    fireEvent.click(menuBtn);

    // Click Delete
    const deleteBtn = screen.getByText('Delete');
    fireEvent.click(deleteBtn);
    expect(onDelete).toHaveBeenCalledWith(mockTask);
  });
});
