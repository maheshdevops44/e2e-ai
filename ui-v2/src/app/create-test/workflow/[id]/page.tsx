import { redirect } from 'next/navigation'
import { getTestById } from '@/lib/actions/test'
import { WorkflowContent } from './workflow-content'

interface WorkflowPageProps {
  params: { id: string }
  searchParams: { step?: string }
}

export default async function WorkflowPage({ params, searchParams }: WorkflowPageProps) {
  // Await params and searchParams for Next.js 15 compatibility
  const { id } = await params
  const { step } = await searchParams
  
  const workflowId = id
  const stepNumber = step ? parseInt(step) : 1

  // Fetch data server-side using server action
  const test = await getTestById(workflowId)
  
  if (!test) {
    redirect('/dashboard')
  }

  // Convert the test data to the expected WorkflowData format
  const workflowData = {
    id: test.id,
    testId: test.testId,  // Include the testId
    testDescription: test.description,  // Include the test description
    storyType: 'manual' as const,
    manualStory: test.userStoryDescription || "",  // Use userStoryDescription for manualStory
    userStoryDescription: test.userStoryDescription || "",  // Don't fallback to description
    criteriaList: test.acceptanceCriteria.map((ac: { content: string }) => ac.content),
    currentStep: stepNumber,
    testSuite: test.testSuite?.id || undefined,
  }

  return (
    <WorkflowContent 
      workflowId={workflowId}
      initialData={workflowData}
    />
  )
}