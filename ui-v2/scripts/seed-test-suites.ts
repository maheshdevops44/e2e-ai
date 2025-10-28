// Seed test suites for the application
import { PrismaClient } from '@/generated/prisma'

const prisma = new PrismaClient()

async function seedTestSuites() {
  console.log('Creating test suites...')
  
  const testSuites = [
    { name: "Sprint 1.2" },
    { name: "Sprint 1.3" },
    { name: "Sprint 2.1" },
    { name: "Regression Suite" },
    { name: "Smoke Tests" },
  ]

  for (const suite of testSuites) {
    const existing = await prisma.testSuite.findFirst({
      where: { name: suite.name }
    })
    
    if (!existing) {
      const created = await prisma.testSuite.create({
        data: suite
      })
      console.log(`Created test suite: ${created.name} (ID: ${created.id})`)
    } else {
      console.log(`Test suite already exists: ${existing.name} (ID: ${existing.id})`)
    }
  }
  
  console.log('Test suite seeding completed!')
}

async function main() {
  try {
    await seedTestSuites()
  } catch (error) {
    console.error('Error seeding test suites:', error)
  } finally {
    await prisma.$disconnect()
  }
}

main()