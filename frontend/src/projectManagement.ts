import type {
  AssignmentSummary,
  GanttTask,
  KanbanColumn,
  Project,
  ProjectManagementOverview,
  Task,
  TaskStatus,
  TimelineBounds,
  User,
} from './types'

const taskStatuses: Array<{ status: TaskStatus; label: string }> = [
  { status: 'todo', label: 'To do' },
  { status: 'in_progress', label: 'In progress' },
  { status: 'in_review', label: 'In review' },
  { status: 'done', label: 'Done' },
]

function startOfToday(todayOverride?: string) {
  const today = todayOverride ? parseDateOnly(todayOverride) ?? new Date(todayOverride) : new Date()
  today.setHours(0, 0, 0, 0)
  return today
}

function parseDateOnly(value: string | null) {
  if (!value) return null
  const parsed = new Date(`${value}T00:00:00`)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function differenceInDays(start: Date, end: Date) {
  const millisecondsPerDay = 1000 * 60 * 60 * 24
  return Math.round((end.getTime() - start.getTime()) / millisecondsPerDay)
}

function enrichTask(task: Task, projects: Project[], users: User[]): Task {
  const project = task.project ?? projects.find((item) => item.id === task.project_id) ?? null
  const assignee = task.assignee ?? users.find((item) => item.id === task.assignee_id) ?? null
  return {
    ...task,
    project,
    assignee,
  }
}

function buildKanban(tasks: Task[]): KanbanColumn[] {
  return taskStatuses.map(({ status, label }) => {
    const columnTasks = tasks.filter((task) => task.status === status)
    return {
      status,
      label,
      count: columnTasks.length,
      tasks: columnTasks,
    }
  })
}

function buildTimelineBounds(tasks: Task[]): TimelineBounds {
  const timelineDates = tasks.flatMap((task) => [parseDateOnly(task.start_date), parseDateOnly(task.due_date)]).filter((value): value is Date => value !== null)
  if (timelineDates.length === 0) {
    return { start_date: null, end_date: null, total_days: 0 }
  }

  const start = new Date(Math.min(...timelineDates.map((value) => value.getTime())))
  const end = new Date(Math.max(...timelineDates.map((value) => value.getTime())))
  return {
    start_date: start.toISOString().slice(0, 10),
    end_date: end.toISOString().slice(0, 10),
    total_days: Math.max(differenceInDays(start, end) + 1, 1),
  }
}

function buildGantt(tasks: Task[], timeline: TimelineBounds): GanttTask[] {
  const timelineStart = parseDateOnly(timeline.start_date)
  if (!timelineStart) return []

  return tasks
    .filter((task) => task.start_date && task.due_date)
    .map((task) => {
      const start = parseDateOnly(task.start_date)
      const due = parseDateOnly(task.due_date)
      if (!start || !due) return null
      return {
        task,
        start_date: task.start_date as string,
        due_date: task.due_date as string,
        duration_days: Math.max(differenceInDays(start, due) + 1, 1),
        offset_days: Math.max(differenceInDays(timelineStart, start), 0),
      }
    })
    .filter((entry): entry is GanttTask => entry !== null)
    .sort((left, right) => left.offset_days - right.offset_days || left.task.title.localeCompare(right.task.title))
}

function buildAssignmentWorkload(tasks: Task[], users: User[]): AssignmentSummary[] {
  const workload = new Map<number | null, AssignmentSummary>()

  users.forEach((user) => {
    workload.set(user.id, {
      assignee_id: user.id,
      assignee_name: user.name,
      total_tasks: 0,
      todo_tasks: 0,
      in_progress_tasks: 0,
      completed_tasks: 0,
      avg_progress: 0,
    })
  })

  tasks.forEach((task) => {
    const key = task.assignee_id ?? null
    const current = workload.get(key) ?? {
      assignee_id: null,
      assignee_name: 'Unassigned',
      total_tasks: 0,
      todo_tasks: 0,
      in_progress_tasks: 0,
      completed_tasks: 0,
      avg_progress: 0,
    }

    current.total_tasks += 1
    current.avg_progress += task.progress
    if (task.status === 'todo') current.todo_tasks += 1
    if (task.status === 'in_progress' || task.status === 'in_review') current.in_progress_tasks += 1
    if (task.status === 'done') current.completed_tasks += 1
    workload.set(key, current)
  })

  return Array.from(workload.values())
    .map((entry) => ({
      ...entry,
      avg_progress: entry.total_tasks > 0 ? Math.round(entry.avg_progress / entry.total_tasks) : 0,
    }))
    .sort((left, right) => right.total_tasks - left.total_tasks || left.assignee_name.localeCompare(right.assignee_name))
}

export function buildProjectManagementOverview(
  tasks: Task[],
  projects: Project[],
  users: User[],
  todayOverride?: string,
): ProjectManagementOverview {
  const enrichedTasks = tasks.map((task) => enrichTask(task, projects, users))
  const today = startOfToday(todayOverride)
  const completedTasks = enrichedTasks.filter((task) => task.status === 'done').length
  const overdueTasks = enrichedTasks.filter((task) => {
    if (task.status === 'done' || !task.due_date) return false
    const dueDate = parseDateOnly(task.due_date)
    return dueDate !== null && dueDate < today
  }).length
  const unassignedTasks = enrichedTasks.filter((task) => task.assignee_id === null).length
  const timeline = buildTimelineBounds(enrichedTasks)

  return {
    summary: {
      total_projects: projects.length,
      total_tasks: enrichedTasks.length,
      unassigned_tasks: unassignedTasks,
      overdue_tasks: overdueTasks,
      completed_tasks: completedTasks,
      completion_rate: enrichedTasks.length > 0 ? Math.round((completedTasks / enrichedTasks.length) * 100) : 0,
    },
    kanban: buildKanban(enrichedTasks),
    gantt: buildGantt(enrichedTasks, timeline),
    assignment_workload: buildAssignmentWorkload(enrichedTasks, users),
    timeline,
  }
}

export function mergeProjectManagementOverview(
  apiOverview: ProjectManagementOverview | null,
  tasks: Task[],
  projects: Project[],
  users: User[],
  todayOverride?: string,
) {
  const fallbackOverview = buildProjectManagementOverview(tasks, projects, users, todayOverride)
  if (!apiOverview) return fallbackOverview

  return {
    summary: fallbackOverview.summary,
    kanban: apiOverview.kanban?.length ? apiOverview.kanban : fallbackOverview.kanban,
    gantt: apiOverview.gantt?.length ? apiOverview.gantt : fallbackOverview.gantt,
    assignment_workload: apiOverview.assignment_workload?.length
      ? apiOverview.assignment_workload
      : fallbackOverview.assignment_workload,
    timeline:
      apiOverview.timeline?.start_date || apiOverview.timeline?.end_date || apiOverview.timeline?.total_days
        ? apiOverview.timeline
        : fallbackOverview.timeline,
  }
}
