"use server"

import { revalidatePath } from "next/cache"
import { prisma } from "@/lib/prisma"
import { z } from "zod"

// Schema for validating test suite data
const testSuiteActionSchema = z.object({
  name: z.string().min(1, "Test suite name is required"),
})

type _TestSuiteFormData = z.infer<typeof testSuiteActionSchema>

// Create a new test suite
export async function createTestSuite(formData: FormData) {
  try {
    // Extract data from FormData
    const data = {
      name: formData.get("name") as string,
    }

    // Validate the data
    const validatedData = testSuiteActionSchema.parse(data)

    // Create the test suite
    const testSuite = await prisma.testSuite.create({
      data: {
        name: validatedData.name,
      },
      include: {
        stories: true,
      },
    })

    // Revalidate relevant pages
    revalidatePath("/create-test")
    revalidatePath("/test-suites")

    return {
      success: true,
      testSuiteId: testSuite.id,
      name: testSuite.name,
      message: "Test suite created successfully",
    }
  } catch (error) {
    console.error("Error creating test suite:", error)
    
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: "Validation failed",
        details: error.issues,
      }
    }

    return {
      success: false,
      error: "Failed to create test suite",
    }
  }
}

// Get all test suites
export async function getTestSuites() {
  try {
    const testSuites = await prisma.testSuite.findMany({
      include: {
        stories: true,
      },
      orderBy: { name: "asc" },
    })

    return testSuites
  } catch (error) {
    console.error("Error fetching test suites:", error)
    return []
  }
}

// Get a specific test suite by ID
export async function getTestSuiteById(id: string) {
  try {
    const testSuite = await prisma.testSuite.findUnique({
      where: { id },
      include: {
        stories: {
          include: {
            acceptanceCriteria: true,
          },
          orderBy: { updatedAt: "desc" },
        },
      },
    })

    return testSuite
  } catch (error) {
    console.error("Error fetching test suite:", error)
    return null
  }
}

// Update a test suite
export async function updateTestSuite(testSuiteId: string, formData: FormData) {
  try {
    // Extract data from FormData
    const data = {
      name: formData.get("name") as string,
    }

    // Validate the data
    const validatedData = testSuiteActionSchema.parse(data)

    // Update the test suite
    const testSuite = await prisma.testSuite.update({
      where: { id: testSuiteId },
      data: {
        name: validatedData.name,
      },
      include: {
        stories: true,
      },
    })

    // Revalidate relevant pages
    revalidatePath("/create-test")
    revalidatePath("/test-suites")
    revalidatePath(`/test-suites/${testSuiteId}`)

    return {
      success: true,
      testSuiteId: testSuite.id,
      message: "Test suite updated successfully",
    }
  } catch (error) {
    console.error("Error updating test suite:", error)
    
    if (error instanceof z.ZodError) {
      return {
        success: false,
        error: "Validation failed",
        details: error.issues,
      }
    }

    return {
      success: false,
      error: "Failed to update test suite",
    }
  }
}

// Delete a test suite
export async function deleteTestSuite(testSuiteId: string) {
  try {
    await prisma.testSuite.delete({
      where: { id: testSuiteId },
    })

    // Revalidate relevant pages
    revalidatePath("/create-test")
    revalidatePath("/test-suites")

    return {
      success: true,
      message: "Test suite deleted successfully",
    }
  } catch (error) {
    console.error("Error deleting test suite:", error)
    return {
      success: false,
      error: "Failed to delete test suite",
    }
  }
}