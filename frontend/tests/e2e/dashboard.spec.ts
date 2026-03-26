import { expect, test } from '@playwright/test'

const apiBaseUrl = (process.env.PLAYWRIGHT_API_BASE_URL ?? 'http://127.0.0.1:8000').trim().replace(/\s+/g, '')

async function ensureUser() {
  const email = `e2e-${Date.now()}@example.com`
  const password = 'password123'
  const response = await fetch(`${apiBaseUrl}/users/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: 'E2E User',
      email,
      password,
    }),
  })

  expect(response.ok).toBeTruthy()
  return { email, password }
}

test('sign in, create task, move workflow, and view delivery insights', async ({ page }) => {
  const credentials = await ensureUser()

  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Ship Dashboard' })).toBeVisible()
  await page.getByLabel('Email').fill(credentials.email)
  await page.getByLabel('Password').fill(credentials.password)
  await page.getByRole('button', { name: 'Sign in' }).click()

  await expect(page.getByText('Signed in successfully.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Sign out' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Sign in' })).toHaveCount(0)
  await expect(page.getByText(`Signed in as ${credentials.email}`)).toBeVisible()

  await page.getByRole('tab', { name: 'Tasks' }).click()
  await expect(page.getByRole('heading', { name: 'Tasks' })).toBeVisible()

  const taskTitle = `E2E Workflow Task ${Date.now()}`

  await page.getByLabel('Title').first().fill(taskTitle)
  await page.getByLabel('Description').first().fill('Created by Playwright smoke coverage.')
  await page.getByLabel('Priority').first().selectOption('high')
  await page.getByLabel('Progress %').first().fill('25')
  await page.getByLabel('Start date').first().fill('2026-03-26')
  await page.getByLabel('Due date').first().fill('2026-03-30')
  await page.getByRole('button', { name: 'Create task' }).click()

  await expect(page.getByText('Please fix the highlighted form errors.')).toHaveCount(0)
  await expect(page.getByText('Task created.')).toBeVisible()
  await expect(page.getByText(taskTitle)).toBeVisible()

  await expect(page.getByRole('heading', { name: 'Kanban board' })).toBeVisible()
  const kanbanTaskCard = page.locator('.kanban-card', { hasText: taskTitle }).first()
  await expect(kanbanTaskCard).toBeVisible()
  await kanbanTaskCard.getByRole('button', { name: 'in progress' }).click()
  await expect(page.getByText('Task moved to in progress.')).toBeVisible()

  await page.getByRole('tab', { name: 'Analytics' }).click()
  await expect(page.getByRole('heading', { name: 'Analytics' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Filtered analytics summary' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Status distribution' })).toBeVisible()

  await page.getByRole('tab', { name: 'Tasks' }).click()
  await expect(page.getByRole('heading', { name: 'Gantt timeline' })).toBeVisible()
  await expect(page.getByText('E2E Workflow Task')).toBeVisible()
})
