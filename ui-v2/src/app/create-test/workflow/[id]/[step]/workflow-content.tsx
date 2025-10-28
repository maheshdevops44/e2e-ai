'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { NewTestWorkflow } from '@/components/new-test-workflow'
import { WorkflowWithSidebar } from '@/components/workflow-with-sidebar'
import { updateTest } from '@/lib/actions/test'

interface WorkflowData {
  id: string
  testName: string
  priority: string
  storyType: string
  manualStory: string
  criteriaList: string[]
  currentStep: number
  testSuite?: string
}

interface StepData {
  testName?: string
  priority?: string
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
  const pathname = usePathname()
  const [workflowData, setWorkflowData] = useState<WorkflowData>(initialData)

  // Extract step directly from URL as fallback
  const currentStepName = pathname.split('/').pop() || 'user-story'
  const getStepNumber = (stepName: string): number => {
    const stepMap: Record<string, number> = {
      'user-story': 1,
      'processing': 2,
      'plan-output': 3,
      'test-script': 4
    }
    return stepMap[stepName] || 1
  }
  
  const urlBasedStep = getStepNumber(currentStepName)

  // Debug both server data and URL-based step
  console.log('🔍 WorkflowContent Debug:', {
    initialDataCurrentStep: initialData.currentStep,
    pathname,
    currentStepName,
    urlBasedStep,
    'using step': urlBasedStep
  })

  // Override initialData with URL-based step to ensure consistency
  const correctedInitialData = {
    ...initialData,
    currentStep: urlBasedStep
  }
  
  // Map step numbers to names
  const getStepName = (stepNumber: number): string => {
    const nameMap: Record<number, string> = {
      1: 'user-story',
      2: 'processing',
      3: 'plan-output',
      4: 'test-script'
    }
    return nameMap[stepNumber] || 'user-story'
  }

  // Update workflowData when correctedInitialData changes  
  useEffect(() => {
    setWorkflowData(correctedInitialData)
  }, [correctedInitialData])

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
      formData.append("testId", updatedData.testName || "")
      formData.append("description", updatedData.manualStory || "")
      formData.append("testSuiteId", "")
      formData.append("acceptanceCriteria", JSON.stringify(updatedData.criteriaList || []))

      const result = await updateTest(workflowId, formData)

      if (result.success) {
        setWorkflowData(updatedData)
        
        // Navigate to next step using new URL structure
        const nextStepName = getStepName(nextStep)
        if (nextStep <= 4) {
          router.push(`/create-test/workflow/${workflowId}/${nextStepName}`)
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
        <div className="p-4">
          <NewTestWorkflow 
            workflowId={workflowId}
            initialData={{
              ...workflowData,
              storyType: workflowData.storyType as "manual" | "upload",
              currentStep: workflowData.currentStep
            }}
            onStepComplete={handleStepComplete}
          />
        </div>
      </WorkflowWithSidebar>
    </div>
  )
}