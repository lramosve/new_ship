import type {
  AnalyticsOverview,
  AuthenticatedUser,
  Document,
  DocumentPayload,
  HealthResponse,
  Issue,
  IssuePayload,
  ListResponse,
  LoginPayload,
  Plan,
  PlanPayload,
  Project,
  ProjectManagementOverview,
  ProjectPayload,
  Task,
  TaskPayload,
  TokenResponse,
  User,
  UserCreatePayload,
  UserUpdatePayload,
} from './types'

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '')
const API_BASE_URL = configuredBaseUrl && configuredBaseUrl.length > 0 ? configuredBaseUrl : '/api'
const TOKEN_STORAGE_KEY = 'shipyard-access-token'

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: unknown
  auth?: boolean
}

export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_STORAGE_KEY)
}

export function storeToken(token: string) {
  window.localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

export function clearStoredToken() {
  window.localStorage.removeItem(TOKEN_STORAGE_KEY)
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {}
  if (options.body) {
    headers['Content-Type'] = 'application/json'
  }
  if (options.auth) {
    const token = getStoredToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? 'GET',
    headers: Object.keys(headers).length > 0 ? headers : undefined,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  if (!response.ok) {
    let message = `Request failed: ${response.status} ${response.statusText}`

    try {
      const errorBody = (await response.json()) as { detail?: string | { msg?: string }[] }
      if (typeof errorBody.detail === 'string') {
        message = errorBody.detail
      } else if (Array.isArray(errorBody.detail)) {
        message = errorBody.detail.map((item) => item.msg ?? 'Validation error').join(', ')
      }
    } catch {
      // Ignore invalid JSON error bodies and preserve the default message.
    }

    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export const api = {
  health: () => request<HealthResponse>('/health'),
  login: (payload: LoginPayload) => request<TokenResponse>('/auth/login', { method: 'POST', body: payload }),
  me: () => request<AuthenticatedUser>('/users/me', { auth: true }),

  projects: () => request<ListResponse<Project>>('/projects/'),
  createProject: (payload: ProjectPayload) => request<Project>('/projects/', { method: 'POST', body: payload, auth: true }),
  updateProject: (id: number, payload: ProjectPayload) =>
    request<Project>(`/projects/${id}`, { method: 'PUT', body: payload, auth: true }),
  deleteProject: (id: number) => request<void>(`/projects/${id}`, { method: 'DELETE', auth: true }),

  documents: () => request<ListResponse<Document>>('/documents/'),
  createDocument: (payload: DocumentPayload) =>
    request<Document>('/documents/', { method: 'POST', body: payload, auth: true }),
  updateDocument: (id: number, payload: DocumentPayload) =>
    request<Document>(`/documents/${id}`, { method: 'PUT', body: payload, auth: true }),
  deleteDocument: (id: number) => request<void>(`/documents/${id}`, { method: 'DELETE', auth: true }),

  users: () => request<ListResponse<User>>('/users/'),
  createUser: (payload: UserCreatePayload) => request<User>('/users/', { method: 'POST', body: payload }),
  updateUser: (id: number, payload: UserUpdatePayload) =>
    request<User>(`/users/${id}`, { method: 'PUT', body: payload, auth: true }),
  deleteUser: (id: number) => request<void>(`/users/${id}`, { method: 'DELETE', auth: true }),

  issues: () => request<ListResponse<Issue>>('/issues/'),
  createIssue: (payload: IssuePayload) => request<Issue>('/issues/', { method: 'POST', body: payload, auth: true }),
  updateIssue: (id: number, payload: IssuePayload) =>
    request<Issue>(`/issues/${id}`, { method: 'PUT', body: payload, auth: true }),
  deleteIssue: (id: number) => request<void>(`/issues/${id}`, { method: 'DELETE', auth: true }),

  plans: () => request<ListResponse<Plan>>('/plans/'),
  createPlan: (payload: PlanPayload) => request<Plan>('/plans/', { method: 'POST', body: payload, auth: true }),
  updatePlan: (id: number, payload: PlanPayload) =>
    request<Plan>(`/plans/${id}`, { method: 'PUT', body: payload, auth: true }),
  deletePlan: (id: number) => request<void>(`/plans/${id}`, { method: 'DELETE', auth: true }),

  tasks: () => request<ListResponse<Task>>('/tasks/'),
  projectManagementOverview: () => request<ProjectManagementOverview>('/project-management/overview'),
  analyticsOverview: () => request<AnalyticsOverview>('/analytics/overview'),
  createTask: (payload: TaskPayload) => request<Task>('/tasks/', { method: 'POST', body: payload, auth: true }),
  updateTask: (id: number, payload: TaskPayload) => request<Task>(`/tasks/${id}`, { method: 'PUT', body: payload, auth: true }),
  deleteTask: (id: number) => request<void>(`/tasks/${id}`, { method: 'DELETE', auth: true }),
}
