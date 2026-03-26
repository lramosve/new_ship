import { useEffect, useMemo, useState } from 'react'
import { api, clearStoredToken, getStoredToken, storeToken } from './api'
import type {
  AuthenticatedUser,
  Document,
  DocumentPayload,
  HealthResponse,
  Issue,
  IssuePayload,
  LoginPayload,
  Plan,
  Project,
  ProjectPayload,
  User,
  UserCreatePayload,
  UserUpdatePayload,
} from './types'

type DashboardData = {
  health: HealthResponse | null
  projects: Project[]
  documents: Document[]
  users: User[]
  issues: Issue[]
  plans: Plan[]
}

type ResourceKey = 'projects' | 'documents' | 'users' | 'issues' | 'plans'

type EditingState = {
  projectId: number | null
  documentId: number | null
  userId: number | null
  issueId: number | null
  planId: number | null
}

type MutationState = {
  message: string | null
  error: string | null
  activeAction: string | null
}

type ValidationErrors = Record<string, string>

type TabOption = {
  key: ResourceKey
  label: string
}

const tabOptions: TabOption[] = [
  { key: 'projects', label: 'Projects' },
  { key: 'documents', label: 'Documents' },
  { key: 'users', label: 'Users' },
  { key: 'issues', label: 'Issues' },
  { key: 'plans', label: 'Plans' },
]

const initialData: DashboardData = {
  health: null,
  projects: [],
  documents: [],
  users: [],
  issues: [],
  plans: [],
}

const initialEditingState: EditingState = {
  projectId: null,
  documentId: null,
  userId: null,
  issueId: null,
  planId: null,
}

const initialLoginForm: LoginPayload = {
  email: '',
  password: '',
}

const initialProjectForm: ProjectPayload = {
  name: '',
  description: '',
}

const initialDocumentForm: DocumentPayload = {
  title: '',
  type: 'markdown',
  content: '',
}

const initialUserCreateForm: UserCreatePayload = {
  name: '',
  email: '',
  password: '',
}

const initialUserEditForm = {
  name: '',
  email: '',
  password: '',
}

const initialIssueForm: IssuePayload = {
  title: '',
  description: '',
  status: 'open',
}

const initialPlanForm = {
  description: '',
  week_number: '1',
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

function normalizeText(value: string) {
  return value.trim()
}

function normalizeOptionalText(value: string | null | undefined) {
  const normalized = (value ?? '').trim()
  return normalized.length > 0 ? normalized : null
}

function validateLogin(payload: LoginPayload): ValidationErrors {
  const errors: ValidationErrors = {}
  if (!normalizeText(payload.email)) errors.loginEmail = 'Email is required.'
  if (!payload.password || payload.password.trim().length < 8) errors.loginPassword = 'Password must be at least 8 characters.'
  return errors
}

function validateProject(payload: ProjectPayload): ValidationErrors {
  const errors: ValidationErrors = {}
  if (!normalizeText(payload.name)) errors.projectName = 'Project name is required.'
  if (!normalizeText(payload.description)) errors.projectDescription = 'Project description is required.'
  return errors
}

function validateDocument(payload: DocumentPayload): ValidationErrors {
  const errors: ValidationErrors = {}
  if (!normalizeText(payload.title)) errors.documentTitle = 'Document title is required.'
  return errors
}

function validateUser(payload: { name: string; email: string; password?: string }, requirePassword: boolean): ValidationErrors {
  const errors: ValidationErrors = {}
  if (!normalizeText(payload.name)) errors.userName = 'User name is required.'
  if (!normalizeText(payload.email)) {
    errors.userEmail = 'Email is required.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizeText(payload.email))) {
    errors.userEmail = 'Email format is invalid.'
  }

  if (requirePassword) {
    if (!payload.password || payload.password.trim().length < 8) {
      errors.userPassword = 'Password must be at least 8 characters.'
    }
  } else if (payload.password && payload.password.trim().length > 0 && payload.password.trim().length < 8) {
    errors.userPassword = 'Replacement password must be at least 8 characters.'
  }

  return errors
}

function validateIssue(payload: IssuePayload): ValidationErrors {
  const errors: ValidationErrors = {}
  if (!normalizeText(payload.title)) errors.issueTitle = 'Issue title is required.'
  return errors
}

function validatePlan(payload: { description: string; week_number: string }): ValidationErrors {
  const errors: ValidationErrors = {}
  if (!normalizeText(payload.description)) errors.planDescription = 'Plan description is required.'
  const weekNumber = Number(payload.week_number)
  if (!Number.isInteger(weekNumber) || weekNumber < 1 || weekNumber > 53) {
    errors.planWeekNumber = 'Week number must be an integer between 1 and 53.'
  }
  return errors
}

function App() {
  const [data, setData] = useState<DashboardData>(initialData)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentUser, setCurrentUser] = useState<AuthenticatedUser | null>(null)
  const [loginForm, setLoginForm] = useState<LoginPayload>(initialLoginForm)
  const [mutation, setMutation] = useState<MutationState>({ message: null, error: null, activeAction: null })
  const [editing, setEditing] = useState<EditingState>(initialEditingState)
  const [activeTab, setActiveTab] = useState<ResourceKey>('projects')
  const [searchQuery, setSearchQuery] = useState('')
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({})

  const [projectCreateForm, setProjectCreateForm] = useState<ProjectPayload>(initialProjectForm)
  const [projectEditForm, setProjectEditForm] = useState<ProjectPayload>(initialProjectForm)
  const [documentCreateForm, setDocumentCreateForm] = useState<DocumentPayload>(initialDocumentForm)
  const [documentEditForm, setDocumentEditForm] = useState<DocumentPayload>(initialDocumentForm)
  const [userCreateForm, setUserCreateForm] = useState<UserCreatePayload>(initialUserCreateForm)
  const [userEditForm, setUserEditForm] = useState(initialUserEditForm)
  const [issueCreateForm, setIssueCreateForm] = useState<IssuePayload>(initialIssueForm)
  const [issueEditForm, setIssueEditForm] = useState<IssuePayload>(initialIssueForm)
  const [planCreateForm, setPlanCreateForm] = useState(initialPlanForm)
  const [planEditForm, setPlanEditForm] = useState(initialPlanForm)

  const loadDashboard = async () => {
    try {
      setLoading(true)
      setError(null)

      const [health, projects, documents, users, issues, plans] = await Promise.all([
        api.health(),
        api.projects(),
        api.documents(),
        api.users(),
        api.issues(),
        api.plans(),
      ])

      setData({
        health,
        projects: projects.items,
        documents: documents.items,
        users: users.items,
        issues: issues.items,
        plans: plans.items,
      })
    } catch (loadError) {
      const message = loadError instanceof Error ? loadError.message : 'Unknown error while loading dashboard'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const loadCurrentUser = async () => {
    if (!getStoredToken()) {
      setCurrentUser(null)
      return
    }

    try {
      const user = await api.me()
      setCurrentUser(user)
    } catch {
      clearStoredToken()
      setCurrentUser(null)
    }
  }

  useEffect(() => {
    void Promise.all([loadDashboard(), loadCurrentUser()])
  }, [])

  const totals = useMemo(
    () => [
      { label: 'Projects', value: data.projects.length },
      { label: 'Documents', value: data.documents.length },
      { label: 'Users', value: data.users.length },
      { label: 'Issues', value: data.issues.length },
      { label: 'Plans', value: data.plans.length },
    ],
    [data],
  )

  const filteredProjects = useMemo(() => {
    const query = searchQuery.trim().toLowerCase()
    return data.projects.filter((project) => !query || `${project.name} ${project.description}`.toLowerCase().includes(query))
  }, [data.projects, searchQuery])

  const filteredDocuments = useMemo(() => {
    const query = searchQuery.trim().toLowerCase()
    return data.documents.filter((document) => !query || `${document.title} ${document.type} ${document.content ?? ''}`.toLowerCase().includes(query))
  }, [data.documents, searchQuery])

  const filteredUsers = useMemo(() => {
    const query = searchQuery.trim().toLowerCase()
    return data.users.filter((user) => !query || `${user.name} ${user.email}`.toLowerCase().includes(query))
  }, [data.users, searchQuery])

  const filteredIssues = useMemo(() => {
    const query = searchQuery.trim().toLowerCase()
    return data.issues.filter((issue) => !query || `${issue.title} ${issue.status} ${issue.description ?? ''}`.toLowerCase().includes(query))
  }, [data.issues, searchQuery])

  const filteredPlans = useMemo(() => {
    const query = searchQuery.trim().toLowerCase()
    return data.plans.filter((plan) => !query || `week ${plan.week_number} ${plan.description}`.toLowerCase().includes(query))
  }, [data.plans, searchQuery])

  const isBusy = (action: string) => mutation.activeAction === action

  const beginMutation = (action: string) => {
    setMutation({ message: null, error: null, activeAction: action })
    setValidationErrors({})
  }

  const completeMutation = (message: string) => {
    setMutation({ message, error: null, activeAction: null })
  }

  const failMutation = (mutationError: unknown) => {
    const message = mutationError instanceof Error ? mutationError.message : 'The request failed.'
    setMutation({ message: null, error: message, activeAction: null })
  }

  const applyValidation = (errors: ValidationErrors) => {
    setValidationErrors(errors)
    setMutation({ message: null, error: 'Please fix the highlighted form errors.', activeAction: null })
  }

  const handleLogin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const payload = { email: normalizeText(loginForm.email), password: loginForm.password.trim() }
    const errors = validateLogin(payload)
    if (Object.keys(errors).length > 0) {
      applyValidation(errors)
      return
    }

    beginMutation('login')
    try {
      const token = await api.login(payload)
      storeToken(token.access_token)
      const user = await api.me()
      setCurrentUser(user)
      setLoginForm(initialLoginForm)
      completeMutation('Signed in successfully.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleLogout = () => {
    clearStoredToken()
    setCurrentUser(null)
    setMutation({ message: 'Signed out.', error: null, activeAction: null })
  }

  const startProjectEdit = (project: Project) => {
    setEditing((current) => ({ ...current, projectId: project.id }))
    setProjectEditForm({ name: project.name, description: project.description })
    setValidationErrors({})
  }

  const handleCreateProject = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const payload = { name: normalizeText(projectCreateForm.name), description: normalizeText(projectCreateForm.description) }
    const errors = validateProject(payload)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation('create-project')
    try {
      const created = await api.createProject(payload)
      setData((current) => ({ ...current, projects: [...current.projects, created] }))
      setProjectCreateForm(initialProjectForm)
      completeMutation('Project created.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleUpdateProject = async (projectId: number) => {
    const payload = { name: normalizeText(projectEditForm.name), description: normalizeText(projectEditForm.description) }
    const errors = validateProject(payload)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation(`update-project-${projectId}`)
    try {
      const updated = await api.updateProject(projectId, payload)
      setData((current) => ({ ...current, projects: current.projects.map((project) => (project.id === projectId ? updated : project)) }))
      setEditing((current) => ({ ...current, projectId: null }))
      completeMutation('Project updated.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleDeleteProject = async (projectId: number) => {
    beginMutation(`delete-project-${projectId}`)
    try {
      await api.deleteProject(projectId)
      setData((current) => ({ ...current, projects: current.projects.filter((project) => project.id !== projectId) }))
      completeMutation('Project deleted.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleCreateDocument = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const payload: DocumentPayload = {
      title: normalizeText(documentCreateForm.title),
      type: documentCreateForm.type,
      content: normalizeOptionalText(documentCreateForm.content),
    }
    const errors = validateDocument(payload)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation('create-document')
    try {
      const created = await api.createDocument(payload)
      setData((current) => ({ ...current, documents: [created, ...current.documents] }))
      setDocumentCreateForm(initialDocumentForm)
      completeMutation('Document created.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleUpdateDocument = async (documentId: number) => {
    const payload: DocumentPayload = {
      title: normalizeText(documentEditForm.title),
      type: documentEditForm.type,
      content: normalizeOptionalText(documentEditForm.content),
    }
    const errors = validateDocument(payload)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation(`update-document-${documentId}`)
    try {
      const updated = await api.updateDocument(documentId, payload)
      setData((current) => ({ ...current, documents: current.documents.map((document) => (document.id === documentId ? updated : document)) }))
      setEditing((current) => ({ ...current, documentId: null }))
      completeMutation('Document updated.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleDeleteDocument = async (documentId: number) => {
    beginMutation(`delete-document-${documentId}`)
    try {
      await api.deleteDocument(documentId)
      setData((current) => ({ ...current, documents: current.documents.filter((document) => document.id !== documentId) }))
      completeMutation('Document deleted.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleCreateUser = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const payload = { name: normalizeText(userCreateForm.name), email: normalizeText(userCreateForm.email), password: userCreateForm.password.trim() }
    const errors = validateUser(payload, true)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation('create-user')
    try {
      const created = await api.createUser(payload)
      setData((current) => ({ ...current, users: [...current.users, created] }))
      setUserCreateForm(initialUserCreateForm)
      completeMutation('User created.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleUpdateUser = async (userId: number) => {
    const payload: UserUpdatePayload = { name: normalizeText(userEditForm.name), email: normalizeText(userEditForm.email) }
    if (userEditForm.password.trim()) payload.password = userEditForm.password.trim()
    const errors = validateUser({ ...payload, password: payload.password }, false)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation(`update-user-${userId}`)
    try {
      const updated = await api.updateUser(userId, payload)
      setData((current) => ({ ...current, users: current.users.map((user) => (user.id === userId ? updated : user)) }))
      setEditing((current) => ({ ...current, userId: null }))
      completeMutation('User updated.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleDeleteUser = async (userId: number) => {
    beginMutation(`delete-user-${userId}`)
    try {
      await api.deleteUser(userId)
      setData((current) => ({ ...current, users: current.users.filter((user) => user.id !== userId) }))
      completeMutation('User deleted.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleCreateIssue = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const payload: IssuePayload = {
      title: normalizeText(issueCreateForm.title),
      description: normalizeOptionalText(issueCreateForm.description),
      status: issueCreateForm.status,
    }
    const errors = validateIssue(payload)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation('create-issue')
    try {
      const created = await api.createIssue(payload)
      setData((current) => ({ ...current, issues: [created, ...current.issues] }))
      setIssueCreateForm(initialIssueForm)
      completeMutation('Issue created.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleUpdateIssue = async (issueId: number) => {
    const payload: IssuePayload = {
      title: normalizeText(issueEditForm.title),
      description: normalizeOptionalText(issueEditForm.description),
      status: issueEditForm.status,
    }
    const errors = validateIssue(payload)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation(`update-issue-${issueId}`)
    try {
      const updated = await api.updateIssue(issueId, payload)
      setData((current) => ({ ...current, issues: current.issues.map((issue) => (issue.id === issueId ? updated : issue)) }))
      setEditing((current) => ({ ...current, issueId: null }))
      completeMutation('Issue updated.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleDeleteIssue = async (issueId: number) => {
    beginMutation(`delete-issue-${issueId}`)
    try {
      await api.deleteIssue(issueId)
      setData((current) => ({ ...current, issues: current.issues.filter((issue) => issue.id !== issueId) }))
      completeMutation('Issue deleted.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleCreatePlan = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const errors = validatePlan(planCreateForm)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation('create-plan')
    try {
      const created = await api.createPlan({ description: normalizeText(planCreateForm.description), week_number: Number(planCreateForm.week_number) })
      setData((current) => ({ ...current, plans: [...current.plans, created] }))
      setPlanCreateForm(initialPlanForm)
      completeMutation('Plan created.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleUpdatePlan = async (planId: number) => {
    const errors = validatePlan(planEditForm)
    if (Object.keys(errors).length > 0) return applyValidation(errors)
    beginMutation(`update-plan-${planId}`)
    try {
      const updated = await api.updatePlan(planId, { description: normalizeText(planEditForm.description), week_number: Number(planEditForm.week_number) })
      setData((current) => ({ ...current, plans: current.plans.map((plan) => (plan.id === planId ? updated : plan)) }))
      setEditing((current) => ({ ...current, planId: null }))
      completeMutation('Plan updated.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  const handleDeletePlan = async (planId: number) => {
    beginMutation(`delete-plan-${planId}`)
    try {
      await api.deletePlan(planId)
      setData((current) => ({ ...current, plans: current.plans.filter((plan) => plan.id !== planId) }))
      completeMutation('Plan deleted.')
    } catch (mutationError) {
      failMutation(mutationError)
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">React frontend</p>
          <h1>Ship Dashboard</h1>
          <p className="hero-copy">Authenticated, validated CRUD workflows against the FastAPI backend with list metadata and protected mutations.</p>
        </div>
        <div className="status-card">
          <span className={`status-dot ${data.health ? 'online' : 'offline'}`} />
          <div>
            <p className="status-label">Backend health</p>
            <strong>{data.health?.status ?? 'Unavailable'}</strong>
            <p className="status-label">{currentUser ? `Signed in as ${currentUser.email}` : 'Read-only until login'}</p>
          </div>
        </div>
      </header>

      {!currentUser && (
        <section className="resource-card auth-card">
          <div className="section-heading">
            <div>
              <h2>Sign in</h2>
              <p>Protected create, edit, and delete actions require a valid account session.</p>
            </div>
          </div>
          <form className="crud-form" onSubmit={handleLogin}>
            <div className="form-grid">
              <label>
                <span>Email</span>
                <input type="email" value={loginForm.email} onChange={(event) => setLoginForm((current) => ({ ...current, email: event.target.value }))} />
                {validationErrors.loginEmail && <small className="field-error">{validationErrors.loginEmail}</small>}
              </label>
              <label>
                <span>Password</span>
                <input type="password" value={loginForm.password} onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))} />
                {validationErrors.loginPassword && <small className="field-error">{validationErrors.loginPassword}</small>}
              </label>
            </div>
            <div className="form-actions">
              <button type="submit" disabled={isBusy('login')}>{isBusy('login') ? 'Signing in…' : 'Sign in'}</button>
            </div>
          </form>
        </section>
      )}

      {loading && <section className="banner info">Loading dashboard data…</section>}
      {error && <section className="banner error">{error}</section>}
      {mutation.message && <section className="banner success">{mutation.message}</section>}
      {mutation.error && <section className="banner error">{mutation.error}</section>}

      <section className="stats-grid">
        {totals.map((item) => (
          <article className="stat-card" key={item.label}>
            <span>{item.label}</span>
            <strong>{item.value}</strong>
          </article>
        ))}
      </section>

      <section className="toolbar-card">
        <div className="tab-bar" role="tablist" aria-label="Resources">
          {tabOptions.map((tab) => (
            <button key={tab.key} type="button" role="tab" className={`tab-button ${activeTab === tab.key ? 'active' : ''}`} onClick={() => setActiveTab(tab.key)}>
              {tab.label}
            </button>
          ))}
          {currentUser && <button type="button" className="secondary" onClick={handleLogout}>Sign out</button>}
        </div>
        <div className="search-row">
          <input value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder={`Search ${activeTab}...`} />
        </div>
      </section>

      <section className="content-grid single-column">
        {activeTab === 'projects' && <ResourceSection title="Projects" items={filteredProjects.length} createEnabled={Boolean(currentUser)}>
          {currentUser && <ProjectCreateForm form={projectCreateForm} setForm={setProjectCreateForm} onSubmit={handleCreateProject} busy={isBusy('create-project')} errors={validationErrors} />}
          {filteredProjects.map((project) => (
            <article className="item-card" key={project.id}>
              <div className="item-header"><h3>{project.name}</h3><span className="badge">#{project.id}</span></div>
              <p>{project.description}</p>
              {currentUser && <div className="item-actions"><button type="button" className="secondary" onClick={() => startProjectEdit(project)}>Edit</button><button type="button" className="danger" onClick={() => void handleDeleteProject(project.id)}>Delete</button></div>}
              {editing.projectId === project.id && currentUser && <InlineProjectEdit form={projectEditForm} setForm={setProjectEditForm} onSave={() => void handleUpdateProject(project.id)} onCancel={() => setEditing((current) => ({ ...current, projectId: null }))} busy={isBusy(`update-project-${project.id}`)} />}
            </article>
          ))}
          {filteredProjects.length === 0 && <EmptyState message="No projects match the current filter." />}
        </ResourceSection>}

        {activeTab === 'documents' && <ResourceSection title="Documents" items={filteredDocuments.length} createEnabled={Boolean(currentUser)}>
          {currentUser && <DocumentCreateForm form={documentCreateForm} setForm={setDocumentCreateForm} onSubmit={handleCreateDocument} busy={isBusy('create-document')} errors={validationErrors} />}
          {filteredDocuments.map((document) => (
            <article className="item-card" key={document.id}>
              <div className="item-header"><h3>{document.title}</h3><span className="badge">{document.type}</span></div>
              <p>{document.content || 'No content body saved.'}</p><small>Updated {formatDate(document.updated_at)}</small>
              {currentUser && <div className="item-actions"><button type="button" className="secondary" onClick={() => { setEditing((current) => ({ ...current, documentId: document.id })); setDocumentEditForm({ title: document.title, type: document.type, content: document.content }) }}>Edit</button><button type="button" className="danger" onClick={() => void handleDeleteDocument(document.id)}>Delete</button></div>}
              {editing.documentId === document.id && currentUser && <InlineDocumentEdit form={documentEditForm} setForm={setDocumentEditForm} onSave={() => void handleUpdateDocument(document.id)} onCancel={() => setEditing((current) => ({ ...current, documentId: null }))} busy={isBusy(`update-document-${document.id}`)} />}
            </article>
          ))}
          {filteredDocuments.length === 0 && <EmptyState message="No documents match the current filter." />}
        </ResourceSection>}

        {activeTab === 'users' && <ResourceSection title="Users" items={filteredUsers.length} createEnabled>
          <UserCreateForm form={userCreateForm} setForm={setUserCreateForm} onSubmit={handleCreateUser} busy={isBusy('create-user')} errors={validationErrors} />
          {filteredUsers.map((user) => (
            <article className="item-card" key={user.id}>
              <div className="item-header"><h3>{user.name}</h3><span className="badge">#{user.id}</span></div>
              <p>{user.email}</p><small>Created {formatDate(user.created_at)}</small>
              {currentUser && <div className="item-actions"><button type="button" className="secondary" onClick={() => { setEditing((current) => ({ ...current, userId: user.id })); setUserEditForm({ name: user.name, email: user.email, password: '' }) }}>Edit</button><button type="button" className="danger" onClick={() => void handleDeleteUser(user.id)}>Delete</button></div>}
              {editing.userId === user.id && currentUser && <InlineUserEdit form={userEditForm} setForm={setUserEditForm} onSave={() => void handleUpdateUser(user.id)} onCancel={() => setEditing((current) => ({ ...current, userId: null }))} busy={isBusy(`update-user-${user.id}`)} />}
            </article>
          ))}
          {filteredUsers.length === 0 && <EmptyState message="No users match the current filter." />}
        </ResourceSection>}

        {activeTab === 'issues' && <ResourceSection title="Issues" items={filteredIssues.length} createEnabled={Boolean(currentUser)}>
          {currentUser && <IssueCreateForm form={issueCreateForm} setForm={setIssueCreateForm} onSubmit={handleCreateIssue} busy={isBusy('create-issue')} errors={validationErrors} />}
          {filteredIssues.map((issue) => (
            <article className="item-card" key={issue.id}>
              <div className="item-header"><h3>{issue.title}</h3><span className="badge accent">{issue.status}</span></div>
              <p>{issue.description || 'No description provided.'}</p><small>Updated {formatDate(issue.updated_at)}</small>
              {currentUser && <div className="item-actions"><button type="button" className="secondary" onClick={() => { setEditing((current) => ({ ...current, issueId: issue.id })); setIssueEditForm({ title: issue.title, description: issue.description, status: issue.status }) }}>Edit</button><button type="button" className="danger" onClick={() => void handleDeleteIssue(issue.id)}>Delete</button></div>}
              {editing.issueId === issue.id && currentUser && <InlineIssueEdit form={issueEditForm} setForm={setIssueEditForm} onSave={() => void handleUpdateIssue(issue.id)} onCancel={() => setEditing((current) => ({ ...current, issueId: null }))} busy={isBusy(`update-issue-${issue.id}`)} />}
            </article>
          ))}
          {filteredIssues.length === 0 && <EmptyState message="No issues match the current filter." />}
        </ResourceSection>}

        {activeTab === 'plans' && <ResourceSection title="Plans" items={filteredPlans.length} createEnabled={Boolean(currentUser)}>
          {currentUser && <PlanCreateForm form={planCreateForm} setForm={setPlanCreateForm} onSubmit={handleCreatePlan} busy={isBusy('create-plan')} errors={validationErrors} />}
          {filteredPlans.map((plan) => (
            <article className="item-card" key={plan.id}>
              <div className="item-header"><h3>Week {plan.week_number}</h3><span className="badge">#{plan.id}</span></div>
              <p>{plan.description}</p><small>Updated {formatDate(plan.updated_at)}</small>
              {currentUser && <div className="item-actions"><button type="button" className="secondary" onClick={() => { setEditing((current) => ({ ...current, planId: plan.id })); setPlanEditForm({ description: plan.description, week_number: String(plan.week_number) }) }}>Edit</button><button type="button" className="danger" onClick={() => void handleDeletePlan(plan.id)}>Delete</button></div>}
              {editing.planId === plan.id && currentUser && <InlinePlanEdit form={planEditForm} setForm={setPlanEditForm} onSave={() => void handleUpdatePlan(plan.id)} onCancel={() => setEditing((current) => ({ ...current, planId: null }))} busy={isBusy(`update-plan-${plan.id}`)} />}
            </article>
          ))}
          {filteredPlans.length === 0 && <EmptyState message="No plans match the current filter." />}
        </ResourceSection>}
      </section>
    </div>
  )
}

type ResourceSectionProps = { title: string; items: number; createEnabled?: boolean; children: React.ReactNode }
function ResourceSection({ title, items, createEnabled, children }: ResourceSectionProps) {
  return <section className="resource-card"><div className="section-heading"><div><h2>{title}</h2><p>{items} visible item(s){createEnabled === false ? ' · sign in to mutate' : ''}</p></div></div><div className="resource-list">{children}</div></section>
}

function ProjectCreateForm({ form, setForm, onSubmit, busy, errors }: { form: ProjectPayload; setForm: React.Dispatch<React.SetStateAction<ProjectPayload>>; onSubmit: (event: React.FormEvent<HTMLFormElement>) => Promise<void>; busy: boolean; errors: ValidationErrors }) { return <form className="crud-form" onSubmit={(event) => void onSubmit(event)}><div className="form-grid"><label><span>Name</span><input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} />{errors.projectName && <small className="field-error">{errors.projectName}</small>}</label><label className="full-width"><span>Description</span><textarea value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} />{errors.projectDescription && <small className="field-error">{errors.projectDescription}</small>}</label></div><div className="form-actions"><button type="submit" disabled={busy}>{busy ? 'Creating…' : 'Create project'}</button></div></form> }
function InlineProjectEdit({ form, setForm, onSave, onCancel, busy }: { form: ProjectPayload; setForm: React.Dispatch<React.SetStateAction<ProjectPayload>>; onSave: () => void; onCancel: () => void; busy: boolean }) { return <div className="editable-card"><div className="form-grid compact"><label><span>Name</span><input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} /></label><label className="full-width"><span>Description</span><textarea value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} /></label></div><div className="item-actions"><button type="button" onClick={onSave} disabled={busy}>{busy ? 'Saving…' : 'Save'}</button><button type="button" className="secondary" onClick={onCancel}>Cancel</button></div></div> }
function DocumentCreateForm({ form, setForm, onSubmit, busy, errors }: { form: DocumentPayload; setForm: React.Dispatch<React.SetStateAction<DocumentPayload>>; onSubmit: (event: React.FormEvent<HTMLFormElement>) => Promise<void>; busy: boolean; errors: ValidationErrors }) { return <form className="crud-form" onSubmit={(event) => void onSubmit(event)}><div className="form-grid"><label><span>Title</span><input value={form.title} onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))} />{errors.documentTitle && <small className="field-error">{errors.documentTitle}</small>}</label><label><span>Type</span><select value={form.type} onChange={(event) => setForm((current) => ({ ...current, type: event.target.value as Document['type'] }))}><option value="markdown">markdown</option><option value="spec">spec</option><option value="note">note</option><option value="report">report</option></select></label><label className="full-width"><span>Content</span><textarea value={form.content ?? ''} onChange={(event) => setForm((current) => ({ ...current, content: event.target.value }))} /></label></div><div className="form-actions"><button type="submit" disabled={busy}>{busy ? 'Creating…' : 'Create document'}</button></div></form> }
function InlineDocumentEdit({ form, setForm, onSave, onCancel, busy }: { form: DocumentPayload; setForm: React.Dispatch<React.SetStateAction<DocumentPayload>>; onSave: () => void; onCancel: () => void; busy: boolean }) { return <div className="editable-card"><div className="form-grid compact"><label><span>Title</span><input value={form.title} onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))} /></label><label><span>Type</span><select value={form.type} onChange={(event) => setForm((current) => ({ ...current, type: event.target.value as Document['type'] }))}><option value="markdown">markdown</option><option value="spec">spec</option><option value="note">note</option><option value="report">report</option></select></label><label className="full-width"><span>Content</span><textarea value={form.content ?? ''} onChange={(event) => setForm((current) => ({ ...current, content: event.target.value }))} /></label></div><div className="item-actions"><button type="button" onClick={onSave} disabled={busy}>{busy ? 'Saving…' : 'Save'}</button><button type="button" className="secondary" onClick={onCancel}>Cancel</button></div></div> }
function UserCreateForm({ form, setForm, onSubmit, busy, errors }: { form: UserCreatePayload; setForm: React.Dispatch<React.SetStateAction<UserCreatePayload>>; onSubmit: (event: React.FormEvent<HTMLFormElement>) => Promise<void>; busy: boolean; errors: ValidationErrors }) { return <form className="crud-form" onSubmit={(event) => void onSubmit(event)}><div className="form-grid"><label><span>Name</span><input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} />{errors.userName && <small className="field-error">{errors.userName}</small>}</label><label><span>Email</span><input type="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} />{errors.userEmail && <small className="field-error">{errors.userEmail}</small>}</label><label className="full-width"><span>Password</span><input type="password" value={form.password} onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} />{errors.userPassword && <small className="field-error">{errors.userPassword}</small>}</label></div><div className="form-actions"><button type="submit" disabled={busy}>{busy ? 'Creating…' : 'Create user'}</button></div></form> }
function InlineUserEdit({ form, setForm, onSave, onCancel, busy }: { form: { name: string; email: string; password: string }; setForm: React.Dispatch<React.SetStateAction<{ name: string; email: string; password: string }>>; onSave: () => void; onCancel: () => void; busy: boolean }) { return <div className="editable-card"><div className="form-grid compact"><label><span>Name</span><input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} /></label><label><span>Email</span><input type="email" value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} /></label><label className="full-width"><span>Replacement password</span><input type="password" value={form.password} onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))} placeholder="Leave blank to preserve existing password" /></label></div><div className="item-actions"><button type="button" onClick={onSave} disabled={busy}>{busy ? 'Saving…' : 'Save'}</button><button type="button" className="secondary" onClick={onCancel}>Cancel</button></div></div> }
function IssueCreateForm({ form, setForm, onSubmit, busy, errors }: { form: IssuePayload; setForm: React.Dispatch<React.SetStateAction<IssuePayload>>; onSubmit: (event: React.FormEvent<HTMLFormElement>) => Promise<void>; busy: boolean; errors: ValidationErrors }) { return <form className="crud-form" onSubmit={(event) => void onSubmit(event)}><div className="form-grid"><label><span>Title</span><input value={form.title} onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))} />{errors.issueTitle && <small className="field-error">{errors.issueTitle}</small>}</label><label><span>Status</span><select value={form.status} onChange={(event) => setForm((current) => ({ ...current, status: event.target.value as Issue['status'] }))}><option value="open">open</option><option value="in_progress">in_progress</option><option value="blocked">blocked</option><option value="closed">closed</option></select></label><label className="full-width"><span>Description</span><textarea value={form.description ?? ''} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} /></label></div><div className="form-actions"><button type="submit" disabled={busy}>{busy ? 'Creating…' : 'Create issue'}</button></div></form> }
function InlineIssueEdit({ form, setForm, onSave, onCancel, busy }: { form: IssuePayload; setForm: React.Dispatch<React.SetStateAction<IssuePayload>>; onSave: () => void; onCancel: () => void; busy: boolean }) { return <div className="editable-card"><div className="form-grid compact"><label><span>Title</span><input value={form.title} onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))} /></label><label><span>Status</span><select value={form.status} onChange={(event) => setForm((current) => ({ ...current, status: event.target.value as Issue['status'] }))}><option value="open">open</option><option value="in_progress">in_progress</option><option value="blocked">blocked</option><option value="closed">closed</option></select></label><label className="full-width"><span>Description</span><textarea value={form.description ?? ''} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} /></label></div><div className="item-actions"><button type="button" onClick={onSave} disabled={busy}>{busy ? 'Saving…' : 'Save'}</button><button type="button" className="secondary" onClick={onCancel}>Cancel</button></div></div> }
function PlanCreateForm({ form, setForm, onSubmit, busy, errors }: { form: { description: string; week_number: string }; setForm: React.Dispatch<React.SetStateAction<{ description: string; week_number: string }>>; onSubmit: (event: React.FormEvent<HTMLFormElement>) => Promise<void>; busy: boolean; errors: ValidationErrors }) { return <form className="crud-form" onSubmit={(event) => void onSubmit(event)}><div className="form-grid"><label><span>Week number</span><input type="number" min="1" max="53" value={form.week_number} onChange={(event) => setForm((current) => ({ ...current, week_number: event.target.value }))} />{errors.planWeekNumber && <small className="field-error">{errors.planWeekNumber}</small>}</label><label className="full-width"><span>Description</span><textarea value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} />{errors.planDescription && <small className="field-error">{errors.planDescription}</small>}</label></div><div className="form-actions"><button type="submit" disabled={busy}>{busy ? 'Creating…' : 'Create plan'}</button></div></form> }
function InlinePlanEdit({ form, setForm, onSave, onCancel, busy }: { form: { description: string; week_number: string }; setForm: React.Dispatch<React.SetStateAction<{ description: string; week_number: string }>>; onSave: () => void; onCancel: () => void; busy: boolean }) { return <div className="editable-card"><div className="form-grid compact"><label><span>Week number</span><input type="number" min="1" max="53" value={form.week_number} onChange={(event) => setForm((current) => ({ ...current, week_number: event.target.value }))} /></label><label className="full-width"><span>Description</span><textarea value={form.description} onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))} /></label></div><div className="item-actions"><button type="button" onClick={onSave} disabled={busy}>{busy ? 'Saving…' : 'Save'}</button><button type="button" className="secondary" onClick={onCancel}>Cancel</button></div></div> }
function EmptyState({ message }: { message: string }) { return <div className="empty-state">{message}</div> }

export default App
