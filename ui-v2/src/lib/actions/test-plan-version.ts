'use server'

import { prisma } from '@/lib/prisma'
import type { Prisma } from '@/generated/prisma';

export type ChangeRequest = { id?: string; message: string; section?: string }

export async function upsertTestPlanVersionV1(params: {
  testRecordId: string
  planContent: string
  finalize?: boolean
}) {
  const { testRecordId, planContent, finalize } = params

  const parent = await prisma.test.findUnique({ where: { id: testRecordId } })
  if (!parent) throw new Error('Test not found')

  const existing = await prisma.testPlanVersion.findFirst({
    where: { testRecordId, versionNumber: 1 },
    select: { id: true },
  })

  if (existing) {
    const updateData: Prisma.TestPlanVersionUpdateInput = {
      isFinalized: !!finalize,
      planContent,
    }

    const version = await prisma.testPlanVersion.update({
      where: { id: existing.id },
      data: updateData,
    })

    await prisma.test.update({
      where: { id: testRecordId },
      data: { status: 'PLAN_READY' },
    })

    return version
  } else {
    const createData: Prisma.TestPlanVersionCreateInput = {
      test: { connect: { id: testRecordId } },
      versionNumber: 1,
      isFinalized: !!finalize,
      planContent,
    }

    const version = await prisma.testPlanVersion.create({ data: createData })

    await prisma.test.update({
      where: { id: testRecordId },
      data: { status: 'PLAN_READY' },
    })

    return version
  }
}

export async function getTestPlanVersionV1(testRecordId: string) {
  return prisma.testPlanVersion.findFirst({
    where: { testRecordId, versionNumber: 1 },
  })
}
