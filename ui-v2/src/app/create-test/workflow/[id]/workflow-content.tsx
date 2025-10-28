'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { NewTestWorkflow } from '@/components/new-test-workflow'
import { WorkflowWithSidebar } from '@/components/workflow-with-sidebar'
import { updateTest } from '@/lib/actions/test'

interface WorkflowData {
  id: string
  testId?: string
  testDescription?: string
  storyType: string
  manualStory: string
  userStoryDescription?: string
  criteriaList: string[]
  currentStep: number
  testSuite?: string
}

interface StepData {
  testId?: string
  testDescription?: string
  userStoryDescription?: string
  storyType?: string
  manualStory?: string
  criteriaList?: string[]
  [key: string]: unknown
}

interface WorkflowContentProps {
  workflowId: string
  initialData: WorkflowData
}

export function WorkflowContent({ workflowId, initialData }: WorkflowContentProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [workflowData, setWorkflowData] = useState<WorkflowData>(initialData)

  const step = searchParams.get('step') ? parseInt(searchParams.get('step')!) : 1

  // Update workflowData when initialData or step changes
  useEffect(() => {
    setWorkflowData({
      ...initialData,
      currentStep: step
    })
  }, [initialData, step])

  const handleStepComplete = async (stepData: StepData) => {
    if (!workflowData) return

    try {
      const nextStep = workflowData.currentStep + 1
      const updatedData = {
        ...workflowData,
        ...stepData,
        currentStep: nextStep
      }

      // Create FormData for server action
      const formData = new FormData()
      formData.append("testId", updatedData.testId || "")
      formData.append("description", updatedData.testDescription || updatedData.manualStory || "")
      formData.append("userStoryDescription", updatedData.userStoryDescription || "")
      formData.append("testSuiteId", "")
      formData.append("acceptanceCriteria", JSON.stringify(updatedData.criteriaList || []))

      const result = await updateTest(workflowId, formData)

      if (result.success) {
        setWorkflowData(updatedData)
        
        // Navigate to next step
        if (nextStep <= 4) {
          router.push(`/create-test/workflow/${workflowId}?step=${nextStep}`)
        } else {
          // Workflow complete, go to dashboard
          router.push('/dashboard')
        }
      } else {
        console.error('Error updating workflow:', result.error)
      }
    } catch (error) {
      console.error('Error updating workflow:', error)
    }
  }

  return (
    <div className="flex-1 overflow-auto">
      <WorkflowWithSidebar>
        <NewTestWorkflow 
          workflowId={workflowId}
          initialData={{
            ...workflowData,
            storyType: workflowData.storyType as "manual" | "upload",
            currentStep: workflowData.currentStep
          }}
          onStepComplete={handleStepComplete}
        />
      </WorkflowWithSidebar>
    </div>
  )
}