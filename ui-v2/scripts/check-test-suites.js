const { PrismaClient } = require('../src/generated/prisma')

const prisma = new PrismaClient()

async function checkTestSuites() {
  try {
    const testSuites = await prisma.testSuite.findMany()
    console.log('Existing TestSuites:', testSuites)
    
    if (testSuites.length === 0) {
      console.log('No TestSuites found. Creating some default ones...')
      
      const defaultSuites = [
        { id: 'sprint-1-2', name: 'Sprint 1.2' },
        { id: 'sprint-1-3', name: 'Sprint 1.3' },
        { id: 'sprint-2-1', name: 'Sprint 2.1' },
        { id: 'regression-suite', name: 'Regression Suite' },
        { id: 'smoke-tests', name: 'Smoke Tests' },
      ]
      
      for (const suite of defaultSuites) {
        await prisma.testSuite.create({
          data: suite
        })
        console.log(`Created TestSuite: ${suite.name}`)
      }
    }
  } catch (error) {
    console.error('Error:', error)
  } finally {
    await prisma.$disconnect()
  }
}

checkTestSuites()