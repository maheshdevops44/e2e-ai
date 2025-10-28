"use server"

import { revalidatePath } from "next/cache"
import { prisma } from "@/lib/prisma"
import { TestStatus } from "@/generated/prisma"
import { z } from "zod"

// Schema for validating test data
const testActionSchema = z.object({
  testId: z.string().min(1, "Test ID is required"),
  description: z.string().min(1, "Description is required"),
  userStoryDescription: z.string().optional(),
  testSuiteId: z.string().optional().nullable(),
  acceptanceCriteria: z.array(z.string()).min(1, "At least one acceptance criterion is required"),
})

type _TestFormData = z.infer<typeof testActionSchema>

// Create a new test
export async function createTest(formData: FormData) {
  try {
    // Extract and parse acceptance criteria with error handling
    let acceptanceCriteria: string[];
    try {
      acceptanceCriteria = JSON.parse(formData.get("acceptanceCriteria") as string || "[]");
    } catch (parseError) {
      return {
        success: false,
        error: "Failed to parse acceptance criteria. Please ensure it is valid JSON.",
      }
    }

    // Extract data from FormData
    const data = {
      testId: formData.get("testId") as string,
      description: formData.get("description") as string,
      userStoryDescription: formData.get("userStoryDescription") as string || "",
      testSuiteId: formData.get("testSuiteId") as string || null,
      acceptanceCriteria,
    }

    // Clean up testSuiteId - if it's empty string, set to null
    if (!data.testSuiteId || data.testSuiteId.trim() === "") {
      data.testSuiteId = null
    } else {
      // Validate that the testSuiteId exists in the database
      const testSuiteExists = await prisma.testSuite.findUnique({
        where: { id: data.testSuiteId }
      })
      if (!testSuiteExists) {
        // If testSuite doesn't exist, set to null instead of failing
        data.testSuiteId = null
      }
    }

    // Validate the data
    const validatedData = testActionSchema.parse(data)

    // Prepare data for Prisma create - omit testSuiteId if null
    const createData: {
      testId: string
      description: string
      userStoryDescription?: string
      status: TestStatus
      testSuiteId?: string
      acceptanceCriteria: {
        create: Array<{
          content: string
        }>
      }
    } = {
      testId: validatedData.testId,
      description: validatedData.description,
      userStoryDescription: validatedData.userStoryDescription,
      status: TestStatus.DRAFT,
      acceptanceCriteria: {
        create: validatedData.acceptanceCriteria.map((content) => ({
          content,
        })),
      },
    }

    // Only include testSuiteId if it has a valid value
    if (validatedData.testSuiteId) {
      createData.testSuiteId = validatedData.testSuiteId
    }

    // Create the test
    const test = await prisma.test.create({
      data: createData,
      include: {
        acceptanceCriteria: true,
        testSuite: true,
      },
    })

    // Revalidate the drafts page to show the new test
    revalidatePath("/create-test")
    revalidatePath("/drafts")

    return {
      success: true,
      testId: test.id,
      testIdentifier: test.testId,
      message: "Test created successfully",
    }
  } catch (error) {
    console.error("Error creating test:", error)
    
    if (error instanceof z.ZodError) {
      console.error("Validation error details:", error.issues)
      return {
        success: false,
        error: `Validation failed: ${error.issues.map(issue => issue.message).join(', ')}`,
        details: error.issues,
      }
    }

    return {
      success: false,
      error: "Failed to create test",
    }
  }
}

// Update an existing test
export async function updateTest(testId: string, formData: FormData) {
  try {
    // Extract and parse acceptance criteria with error handling
    let acceptanceCriteria: string[];
    try {
      acceptanceCriteria = JSON.parse(formData.get("acceptanceCriteria") as string || "[]");
    } catch (parseError) {
      return {
        success: false,
        error: "Failed to parse acceptance criteria. Please ensure it is valid JSON.",
      }
    }

    // Extract data from FormData
    const data = {
      testId: formData.get("testId") as string,
      description: formData.get("description") as string,
      userStoryDescription: formData.get("userStoryDescription") as string || "",
      testSuiteId: formData.get("testSuiteId") as string || null,
      acceptanceCriteria,
    }

    // Clean up testSuiteId - if it's empty string, set to null
    if (!data.testSuiteId || data.testSuiteId.trim() === "") {
      data.testSuiteId = null
    } else {
      // Validate that the testSuiteId exists in the database
      const testSuiteExists = await prisma.testSuite.findUnique({
        where: { id: data.testSuiteId }
      })
      if (!testSuiteExists) {
        // If testSuite doesn't exist, set to null instead of failing
        data.testSuiteId = null
      }
    }

    // Validate the data
    const validatedData = testActionSchema.parse(data)

    // Update the test
    const test = await prisma.test.update({
      where: { id: testId },
      data: {
        testId: validatedData.testId,
        description: validatedData.description,
        userStoryDescription: validatedData.userStoryDescription,
        testSuiteId: validatedData.testSuiteId || null,
        acceptanceCriteria: {
          // Delete existing criteria and create new ones
          deleteMany: {},
          create: validatedData.acceptanceCriteria.map((content) => ({
            content,
          })),
        },
      },
      include: {
        acceptanceCriteria: true,
        testSuite: true,
      },
    })

    // Revalidate relevant pages
    revalidatePath("/create-test")
    revalidatePath("/drafts")
    revalidatePath(`/workflow/${testId}`)

    return {
      success: true,
      testId: test.id,
      message: "Test updated successfully",
    }
  } catch (error) {
    console.error("Error updating test:", error)
    
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: "Validation failed",
        details: error.issues,
      }
    }

    return {
      success: false,
      error: "Failed to update test",
    }
  }
}

// Get all draft tests
export async function getDraftTests() {
  try {
    const tests = await prisma.test.findMany({
      where: {
        status: {
          in: [TestStatus.DRAFT, TestStatus.IN_PROGRESS, TestStatus.PLAN_READY, TestStatus.REVIEW_PENDING],
        },
      },
      include: {
        acceptanceCriteria: true,
        testSuite: true,
      },
      orderBy: { updatedAt: "desc" },
    })

    return tests
  } catch (error) {
    console.error("Error fetching draft tests:", error)
    return []
  }
}

// Get a specific test by ID
export async function getTestById(id: string) {
  try {
    const test = await prisma.test.findUnique({
      where: { id },
      include: {
        acceptanceCriteria: true,
        testSuite: true,
        testPlanVersions: {
          orderBy: { versionNumber: "desc" },
        },
        testScript: true,
      },
    })

    return test
  } catch (error) {
    console.error("Error fetching test:", error)
    return null
  }
}

// Update test status
export async function updateTestStatus(testId: string, status: TestStatus) {
  try {
    const test = await prisma.test.update({
      where: { id: testId },
      data: { status },
    })

    // Revalidate relevant pages
    revalidatePath("/create-test")
    revalidatePath("/drafts")
    revalidatePath(`/workflow/${testId}`)

    return {
      success: true,
      testId: test.id,
      status: test.status,
      message: "Status updated successfully",
    }
  } catch (error) {
    console.error("Error updating test status:", error)
    return {
      success: false,
      error: "Failed to update status",
    }
  }
}

// Delete a test
export async function deleteTest(testId: string) {
  try {
    await prisma.test.delete({
      where: { id: testId },
    })

    // Revalidate relevant pages
    revalidatePath("/create-test")
    revalidatePath("/drafts")

    return {
      success: true,
      message: "Test deleted successfully",
    }
  } catch (error) {
    console.error("Error deleting test:", error)
    return {
      success: false,
      error: "Failed to delete test",
    }
  }
}

// Legacy function names for backward compatibility (will be removed later)
