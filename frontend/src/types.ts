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
