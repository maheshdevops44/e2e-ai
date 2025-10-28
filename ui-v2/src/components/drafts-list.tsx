import { getDraftTests } from "@/lib/actions/test"
import { TestStatus } from "@/generated/prisma"
import Link from "next/link"

interface DraftItemProps {
  id: string
  testId: string
  description: string
  status: TestStatus
  updatedAt: Date
  testSuite?: { id: string; name: string } | null
}

function DraftItem({ id, testId, description, status, updatedAt, testSuite }: DraftItemProps) {
  // Determine step based on status
  const getStepFromStatus = (status: TestStatus): number => {
    switch (status) {
      case TestStatus.DRAFT:
        return 1
      case TestStatus.IN_PROGRESS:
        return 2
      case TestStatus.PLAN_READY:
      case TestStatus.REVIEW_PENDING:
        return 3
      case TestStatus.SCRIPT_GENERATING:
      case TestStatus.SCRIPT_READY:
        return 4
      default:
        return 1
    }
  }

  const step = getStepFromStatus(status)
  const truncatedDescription = description.length > 50 ? description.substring(0, 50) + "..." : description

  return (
    <Link href={`/create-test/workflow/${id}?step=${step}`}>
      <div className="group p-3 hover:bg-gray-50 rounded-md cursor-pointer border-b border-gray-100 last:border-b-0">
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-gray-900 truncate">
                {testId || id.substring(0, 8)}
              </span>
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                Step {step}
              </span>
            </div>
            <p className="text-xs text-gray-500 truncate">
              {truncatedDescription}
            </p>
            {testSuite && (
              <p className="text-xs text-blue-600 mt-1">
                Suite: {testSuite.name}
              </p>
            )}
            <p className="text-xs text-gray-400 mt-1">
              {updatedAt.toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </Link>
  )
}

export async function DraftsList() {
  const drafts = await getDraftTests()

  if (drafts.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500 text-sm">
        No drafts found
      </div>
    )
  }

  return (
    <div className="space-y-0">
      {drafts.map((draft) => (
        <DraftItem
          key={draft.id}
          id={draft.id}
          testId={draft.testId}
          description={draft.description}
          status={draft.status}
          updatedAt={draft.updatedAt}
          testSuite={draft.testSuite}
        />
      ))}
    </div>
  )
}