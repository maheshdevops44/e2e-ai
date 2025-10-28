import { redirect } from 'next/navigation'
import { getTestById } from '@/lib/actions/test'
import { WorkflowContent } from '../workflow-content'

interface WorkflowStepPageProps {
  params: { id: string; step: string }
}

// Define valid steps
const VALID_STEPS = ['user-story', 'processing', 'plan-output', 'test-script'] as const
type ValidStep = typeof VALID_STEPS[number]

function getStepNumber(step: string): number {
  const stepMap: Record<ValidStep, number> = {
    'user-story': 1,
    'processing': 2,
    'plan-output': 3,
    'test-script': 4
  }
  
  if (VALID_STEPS.includes(step as ValidStep)) {
    return stepMap[step as ValidStep]
  }
  
  // If invalid step, redirect to user-story
  return 1
}

export default async function WorkflowStepPage({ params }: WorkflowStepPageProps) {
  // Await params for Next.js 15 compatibility
  const { id, step } = await params
  
  const workflowId = id
  const stepName = step
  const stepNumber = getStepNumber(stepName)
  
  // Server-side debug
  console.log('🔍 Server Debug:', {
    workflowId,
    stepName,
    stepNumber,
    isValidStep: VALID_STEPS.includes(stepName as ValidStep)
  })
  
  // If invalid step, redirect to valid step
  if (!VALID_STEPS.includes(stepName as ValidStep)) {
    redirect(`/create-test/workflow/${workflowId}/user-story`)
  }

  // Fetch data server-side using server action
  const userStory = await getTestById(workflowId)
  
  if (!userStory) {
    redirect('/dashboard')
  }

  // Convert the user story data to the expected WorkflowData format
  const workflowData = {
    id: userStory.id,
    testName: userStory.testId,
    priority: 'Medium' as const,
    storyType: 'manual' as const,
    manualStory: userStory.description,
    criteriaList: userStory.acceptanceCriteria.map((ac: { content: string }) => ac.content),
    currentStep: stepNumber, // Use the step from URL
    testSuite: userStory.testSuite?.id || undefined,
  }

  // Debug what we're passing to the client
  console.log('🔍 Server workflowData:', {
    currentStep: workflowData.currentStep,
    stepNumber,
    stepName
  })

  return (
    <WorkflowContent 
      workflowId={workflowId}
      initialData={workflowData}
    />
  )
}