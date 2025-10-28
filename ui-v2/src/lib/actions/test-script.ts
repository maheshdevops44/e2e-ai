'use server'

import { prisma } from '@/lib/prisma'
import type { Prisma } from '@/generated/prisma'

function dummyPythonPlaywright(name: string = 'e2e_flow') {
  return [
    'from playwright.sync_api import sync_playwright',
    '',
    `def test_${name}():`,
    ' with sync_playwright() as p:',
    ' browser = p.chromium.launch(headless=True)',
    ' context = browser.new_context()',
    ' page = context.new_page()',
    '',
    ' # TODO: replace with real URLs/selectors',
    " page.goto('https://example.com/login')",
    " page.fill('#username', 'demo')",
    " page.fill('#password', 'demo')",
    ' page.click(\'button:has-text("Sign in")\')',
    " page.wait_for_url('**/dashboard')",
    '',
    ' # assertion example',
    " assert page.is_visible('text=Dashboard')",
    '',
    ' context.close()',
    ' browser.close()',
    '',
  ].join('\n')
}

export async function generateDummyTestScript(params: {
  testRecordId?: string
  testId?: string
  overwrite?: boolean
}) {
  const { testRecordId, testId, overwrite = true } = params

  const test = testRecordId
    ? await prisma.test.findUnique({ where: { id: testRecordId } })
    : testId
      ? await prisma.test.findUnique({ where: { testId } })
      : null

  if (!test) throw new Error('test not found (need testRecordId or testId)')

  const existing = await prisma.testScript.findUnique({
    where: { testRecordId: test.id },
  })
  if (existing && !overwrite) return existing

  const scriptContent = dummyPythonPlaywright(test.testId ?? 'e2e_flow')

  if (existing) {
    // update existing
    return prisma.testScript.update({
      where: { testRecordId: test.id },
      data: {
        scriptContent,
      },
    })
  }

  // create new
  return prisma.testScript.create({
    data: {
      test: { connect: { id: test.id } },
      scriptContent,
    },
  })
}
