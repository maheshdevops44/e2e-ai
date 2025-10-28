'use client'

import { useEffect, useState } from 'react'
import { ChangeRequest } from '@/lib/actions/test-plan-version'
import { getTestPlanVersionV1, upsertTestPlanVersionV1 } from '@/lib/actions/test-plan-version'
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import VersionCard, { TestPlan } from '@/components/workflow/version-card'

interface PlanOutputStepProps {
  workflowData?: {
    id?: string
    storyType?: string
    manualStory?: string
    criteriaList?: string[]
    currentStep?: number
  }
  onProceed: () => void
}

function toTestPlan(json: Record<string, unknown>): TestPlan {
  return {
    objective: (json?.objective as string) ?? '',
    applicationsInvolved: Array.isArray(json?.applicationsInvolved)
      ? json.applicationsInvolved
      : [],
    summary: Array.isArray(json?.summary) ? json.summary : [],
    testFlow: Array.isArray(json?.testFlow) ? json.testFlow : [],
  }
}

export function PlanOutputStep({ workflowData, onProceed }: PlanOutputStepProps) {
  const [versions, setVersions] = useState<TestPlan[]>([])

  useEffect(() => {
    async function load() {
      try {
        if (!workflowData?.id) return

        const v1 = await getTestPlanVersionV1(workflowData.id)

        if (v1?.planContent) {
          setVersions([toTestPlan(JSON.parse(v1.planContent))])
        } else {
          setVersions([
            {
              objective:
                'To validate the end-to-end Trend Biosimilar workflow for a Direct Patient Fax Referral, ensuring the journey from fax ingestion through Intake, Clearance, RxProcessing, and CRM Order Scheduling.',
              applicationsInvolved: ['TDM', 'Intake', 'Clearance', 'RXP', 'CRM'],
              summary: [
                { label: 'Channel', value: 'FAX' },
                { label: 'Therapy Type', value: 'HUMA' },
                { label: 'Order', value: 'New Referral' },
                { label: 'Patient Type', value: 'Direct' },
              ],
              testFlow: [
                'Verify Intake Application:',
                'Ensure a new referral is created using the Common Intake ID from the file',
                'Therapy Type: HUMA',
                "Drug: HUMA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402)",
                'Place Of Service: Clinic (Optional)',
                'Service Branch OSB Code: 556',
              ],
            },
          ])
        }
      } catch (e) {
        console.error('Failed to load Version 1:', e)
      }
    }

    load()
  }, [workflowData?.id])

  const handleMakeChanges = async (newRequests: ChangeRequest[]) => {
    try {
      if (!workflowData?.id) {
        console.error('Missing workflowData.id (testPlanId)')
        return
      }

      const latest = versions[versions.length - 1]
      const updated = { ...latest }

      newRequests.forEach((r) => {
        switch (r.section) {
          case 'Objective':
            updated.objective = r.message
            break
          case 'Applications':
            updated.applicationsInvolved = r.message.split(',').map((s: string) => s.trim())
            break
          case 'Summary':
            updated.summary = r.message.split('\n').map((line: string) => {
              const [label, ...rest] = line.split(':')
              return { label: label.trim(), value: rest.join(':').trim() }
            })
            break
          case 'Test Flow':
            updated.testFlow = r.message
              .split('\n')
              .map((line: string) => line.replace(/^\d+\.\s*/, '').trim())
            break
        }
      })

      const saved = await upsertTestPlanVersionV1({
        testRecordId: workflowData.id,
        planContent: JSON.stringify(updated),
        finalize: false,
      })

      console.log('Version 1 saved to DB:', saved)
      setVersions((prev) => [...prev, updated])
    } catch (err) {
      console.error('Failed to save Version 1:', err)
    }
  }

  return (
    <div className="space-y-4">
      <Card className="rounded-[10px] border border-muted/100 font-sans shadow-sm">
        <CardHeader>
          <CardTitle className="text-base font-semibold">
            Step 3: Your test case plan is ready
          </CardTitle>
          <CardDescription className="text-sm">
            Review the output below and make any changes before generating the test script
          </CardDescription>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 gap-4 text-sm lg:grid-cols-12">
        <div className={'lg:col-span-12'}>
          {versions.map((plan, idx) =>
            idx === 0 ? (
              <VersionCard
                key={idx}
                title={`Version ${idx + 1}`}
                plan={plan}
                onModify={() => {}}
                onProceed={() => {
                  handleMakeChanges([])
                  onProceed()
                }}
              />
            ) : null
          )}
        </div>
      </div>
    </div>
  )
}
