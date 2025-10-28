const { PrismaClient } = require('../src/generated/prisma')

const prisma = new PrismaClient()

async function main() {
  console.log('Seeding test suites...')
  
  const testSuites = [
    { id: 'sprint-1-2', name: 'Sprint 1.2' },
    { id: 'sprint-1-3', name: 'Sprint 1.3' },
    { id: 'sprint-2-1', name: 'Sprint 2.1' },
    { id: 'regression-suite', name: 'Regression Suite' },
    { id: 'smoke-tests', name: 'Smoke Tests' },
  ]

  for (const suite of testSuites) {
    try {
      await prisma.testSuite.upsert({
        where: { id: suite.id },
        update: { name: suite.name },
        create: { id: suite.id, name: suite.name },
      })
      console.log(`✓ Created/updated test suite: ${suite.name}`)
    } catch (error) {
      console.error(`✗ Failed to create test suite ${suite.name}:`, error)
    }
  }
  
  console.log('Seeding completed!')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })