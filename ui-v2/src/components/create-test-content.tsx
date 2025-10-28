import { getDraftTests } from "@/lib/actions/test"
import { CreateTestContentClient } from "./create-test-content-client"

interface DraftTestData {
  id: string;
  testId: string;
  description: string;
  userStoryDescription: string | null;
  status: string;
  createdAt: Date;
  updatedAt: Date;
  testSuite: { id: string; name: string } | null;
  acceptanceCriteria: Array<{ id: string; content: string; testRecordId: string; createdAt: Date }>;
}

export async function CreateTestContent() {
  // Fetch drafts server-side
  const initialDrafts = await getDraftTests()

  // Transform to the format expected by the client component
  const formattedDrafts = initialDrafts.map((draft: DraftTestData) => ({
    id: draft.id,
    testName: draft.testId,
    testId: draft.testId,
    description: draft.description,
    userStoryDescription: draft.userStoryDescription || undefined,
    testSuite: draft.testSuite,
    currentStep: getStepFromStatus(draft.status),
    createdAt: draft.createdAt.toISOString(),
    updatedAt: draft.updatedAt.toISOString(),
  }))

  return <CreateTestContentClient initialDrafts={formattedDrafts} />
}

// Helper function to determine step from status
function getStepFromStatus(status: string): number {
  switch (status) {
    case 'DRAFT':
      return 1
    case 'IN_PROGRESS':
      return 2
    case 'PLAN_READY':
    case 'REVIEW_PENDING':
      return 3
    case 'SCRIPT_GENERATING':
    case 'SCRIPT_READY':
      return 4
    default:
      return 1
  }
}