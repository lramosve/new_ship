import { describe, expect, it } from 'vitest'
import { buildProjectManagementOverview, mergeProjectManagementOverview } from './projectManagement'
import type { Project, ProjectManagementOverview, Task, User } from './types'

const projects: Project[] = [
  { id: 1, name: 'Apollo', description: 'Core delivery stream' },
  { id: 2, name: 'Hermes', description: 'Integrations upgrade' },
]

const users: User[] = [
  {
    id: 1,
    name: 'Ada Lovelace',
    email: 'ada@example.com',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Grace Hopper',
    email: 'grace@example.com',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
]

const tasks: Task[] = [
  {
    id: 101,
    title: 'Design auth refresh',
    description: 'Refresh token UX work',
    status: 'todo',
    priority: 'high',
    progress: 0,
    start_date: '2024-01-10',
    due_date: '2024-01-12',
    project_id: 1,
    assignee_id: 1,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
    project: projects[0],
    assignee: users[0],
  },
  {
    id: 102,
    title: 'Ship kanban fallback',
    description: 'Client-side overview recovery',
    status: 'in_progress',
    priority: 'urgent',
    progress: 55,
    start_date: '2024-01-11',
    due_date: '2024-01-20',
    project_id: 1,
    assignee_id: 1,
    created_at: '2024-01-03T00:00:00Z',
    updated_at: '2024-01-04T00:00:00Z',
    project: projects[0],
    assignee: users[0],
  },
  {
    id: 103,
    title: 'QA delivery metrics',
    description: 'Validate insights',
    status: 'done',
    priority: 'medium',
    progress: 100,
    start_date: '2024-01-05',
    due_date: '2024-01-08',
    project_id: 2,
    assignee_id: null,
    created_at: '2024-01-04T00:00:00Z',
    updated_at: '2024-01-08T00:00:00Z',
    project: projects[1],
    assignee: null,
  },
  {
    id: 104,
    title: 'Backfill gantt dates',
    description: 'No schedule data yet',
    status: 'in_review',
    priority: 'low',
    progress: 80,
    start_date: null,
    due_date: null,
    project_id: null,
    assignee_id: 2,
    created_at: '2024-01-06T00:00:00Z',
    updated_at: '2024-01-07T00:00:00Z',
    project: null,
    assignee: users[1],
  },
]

describe('buildProjectManagementOverview', () => {
  it('derives kanban, gantt, workload, and summary data from local entities', () => {
    const overview = buildProjectManagementOverview(tasks, projects, users, '2024-01-15')

    expect(overview.summary).toEqual({
      total_projects: 2,
      total_tasks: 4,
      unassigned_tasks: 1,
      overdue_tasks: 1,
      completed_tasks: 1,
      completion_rate: 25,
    })

    expect(overview.kanban.map((column) => [column.status, column.count])).toEqual([
      ['todo', 1],
      ['in_progress', 1],
      ['in_review', 1],
      ['done', 1],
    ])

    expect(overview.gantt.map((item) => ({ id: item.task.id, offset: item.offset_days, duration: item.duration_days }))).toEqual([
      { id: 103, offset: 0, duration: 4 },
      { id: 101, offset: 5, duration: 3 },
      { id: 102, offset: 6, duration: 10 },
    ])

    expect(overview.timeline).toEqual({
      start_date: '2024-01-05',
      end_date: '2024-01-20',
      total_days: 16,
    })

    expect(overview.assignment_workload).toEqual([
      {
        assignee_id: 1,
        assignee_name: 'Ada Lovelace',
        total_tasks: 2,
        todo_tasks: 1,
        in_progress_tasks: 1,
        completed_tasks: 0,
        avg_progress: 28,
      },
      {
        assignee_id: 2,
        assignee_name: 'Grace Hopper',
        total_tasks: 1,
        todo_tasks: 0,
        in_progress_tasks: 1,
        completed_tasks: 0,
        avg_progress: 80,
      },
      {
        assignee_id: null,
        assignee_name: 'Unassigned',
        total_tasks: 1,
        todo_tasks: 0,
        in_progress_tasks: 0,
        completed_tasks: 1,
        avg_progress: 100,
      },
    ])
  })
})

describe('mergeProjectManagementOverview', () => {
  it('fills missing backend sections with locally derived fallback data', () => {
    const remoteOverview: ProjectManagementOverview = {
      summary: {
        total_projects: 2,
        total_tasks: 4,
        unassigned_tasks: 1,
        overdue_tasks: 0,
        completed_tasks: 1,
        completion_rate: 25,
      },
      kanban: [],
      gantt: [],
      assignment_workload: [],
      timeline: {
        start_date: null,
        end_date: null,
        total_days: 0,
      },
    }

    const merged = mergeProjectManagementOverview(remoteOverview, tasks, projects, users, '2024-01-15')

    expect(merged.summary).toEqual({
      total_projects: 2,
      total_tasks: 4,
      unassigned_tasks: 1,
      overdue_tasks: 1,
      completed_tasks: 1,
      completion_rate: 25,
    })
    expect(merged.kanban.map((column) => column.count)).toEqual([1, 1, 1, 1])
    expect(merged.gantt).toHaveLength(3)
    expect(merged.assignment_workload).toHaveLength(3)
    expect(merged.timeline).toEqual({
      start_date: '2024-01-05',
      end_date: '2024-01-20',
      total_days: 16,
    })
  })

  it('returns pure fallback output when overview is unavailable', () => {
    const merged = mergeProjectManagementOverview(null, tasks, projects, users, '2024-01-15')

    expect(merged.summary.total_tasks).toBe(4)
    expect(merged.kanban.find((column) => column.status === 'todo')?.tasks[0]?.title).toBe('Design auth refresh')
  })
})
