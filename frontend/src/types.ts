export type HealthResponse = {
  status: string
}

export type AuthenticatedUser = {
  id: number
  name: string
  email: string
}

export type LoginPayload = {
  email: string
  password: string
}

export type TokenResponse = {
  access_token: string
  token_type: 'bearer'
}

export type ListResponse<T> = {
  items: T[]
  total: number
}

export type Project = {
  id: number
  name: string
  description: string
}

export type ProjectPayload = {
  name: string
  description: string
}

export type Document = {
  id: number
  title: string
  type: 'markdown' | 'spec' | 'note' | 'report'
  content: string | null
  created_at: string
  updated_at: string
}

export type DocumentPayload = {
  title: string
  type: Document['type']
  content: string | null
}

export type User = {
  id: number
  name: string
  email: string
  created_at: string
  updated_at: string
}

export type UserCreatePayload = {
  name: string
  email: string
  password: string
}

export type UserUpdatePayload = {
  name: string
  email: string
  password?: string
}

export type Issue = {
  id: number
  title: string
  description: string | null
  status: 'open' | 'in_progress' | 'blocked' | 'closed'
  created_at: string
  updated_at: string
}

export type IssuePayload = {
  title: string
  description: string | null
  status: Issue['status']
}

export type Plan = {
  id: number
  description: string
  week_number: number
  created_at: string
  updated_at: string
}

export type PlanPayload = {
  description: string
  week_number: number
}

export type TaskStatus = 'todo' | 'in_progress' | 'in_review' | 'done'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

export type Task = {
  id: number
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  progress: number
  start_date: string | null
  due_date: string | null
  project_id: number | null
  assignee_id: number | null
  created_at: string
  updated_at: string
  project: Project | null
  assignee: User | null
}

export type TaskPayload = {
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  progress: number
  start_date: string | null
  due_date: string | null
  project_id: number | null
  assignee_id: number | null
}

export type KanbanColumn = {
  status: TaskStatus
  label: string
  count: number
  tasks: Task[]
}

export type GanttTask = {
  task: Task
  start_date: string
  due_date: string
  duration_days: number
  offset_days: number
}

export type AssignmentSummary = {
  assignee_id: number | null
  assignee_name: string
  total_tasks: number
  todo_tasks: number
  in_progress_tasks: number
  completed_tasks: number
  avg_progress: number
}

export type TimelineBounds = {
  start_date: string | null
  end_date: string | null
  total_days: number
}

export type ProjectManagementSummary = {
  total_projects: number
  total_tasks: number
  unassigned_tasks: number
  overdue_tasks: number
  completed_tasks: number
  completion_rate: number
}

export type ProjectManagementOverview = {
  summary: ProjectManagementSummary
  kanban: KanbanColumn[]
  gantt: GanttTask[]
  assignment_workload: AssignmentSummary[]
  timeline: TimelineBounds
}

export type AnalyticsSummary = {
  total_tasks: number
  completed_tasks: number
  in_progress_tasks: number
  overdue_tasks: number
  completion_rate: number
  average_progress: number
}

export type TaskTrendPoint = {
  date: string
  created_tasks: number
  completed_tasks: number
}

export type TaskStatusDistribution = {
  status: TaskStatus
  label: string
  count: number
}

export type PriorityDistribution = {
  priority: TaskPriority
  label: string
  count: number
}

export type ProjectProgressSnapshot = {
  project_id: number | null
  project_name: string
  total_tasks: number
  completed_tasks: number
  average_progress: number
  completion_rate: number
}

export type AnalyticsOverview = {
  summary: AnalyticsSummary
  task_trends: TaskTrendPoint[]
  status_distribution: TaskStatusDistribution[]
  priority_distribution: PriorityDistribution[]
  project_progress: ProjectProgressSnapshot[]
}

export type AnalyticsQuery = {
  status?: TaskStatus
  priority?: TaskPriority
  project_id?: number
  q?: string
}
