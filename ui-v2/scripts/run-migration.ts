import 'dotenv/config'

import { execFileSync } from 'node:child_process'
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

import { Migrate } from '@prisma/migrate'
import type { LoadedFile } from '@prisma/schema-files-loader';
import type { SchemaContext } from '@prisma/internals';
import { printFilesFromMigrationIds } from '@prisma/migrate/dist/utils/printFiles'

const projectRoot = process.cwd()
const schemaPath = join(projectRoot, 'prisma', 'schema.prisma')

// schemaFiles is an array of arrays, each containing a file path and its content
const schemaFiles = [[join(projectRoot, 'prisma', 'schema.prisma'), readFileSync(join(projectRoot, 'prisma', 'schema.prisma'), 'utf8')]]
console.log('schemaPath', schemaPath)

const exitWithError = (message: string) => {
  console.error(`⚠️  ${message}`)
  process.exit(1)
}

const runPrismaGenerate = () => {
  console.info('🔄 Generating Prisma client ...')
  try {
    execFileSync('npx', ['prisma', 'generate'], {
      cwd: projectRoot,
      stdio: 'inherit',
    })
  } catch (error) {
    exitWithError('Failed to run prisma generate')
  }
}

const main = async () => {
  if (!existsSync(schemaPath)) {
    exitWithError(`Missing Prisma schema at ${schemaPath}`)
  }

  const databaseUrl =
    process.env.DATABASE_URL ??
    process.env.LOCAL_DATABASE_URL ??
    'postgresql://postgres:postgres@localhost:5432/postgres'

  if (!process.env.DATABASE_URL) {
    console.info(`ℹ️  DATABASE_URL missing, defaulting to ${databaseUrl}`)
    process.env.DATABASE_URL = databaseUrl
  }

  console.info('🗄️  Checking database ...')
  process.env.DATABASE_URL = databaseUrl

  const migrate = await Migrate.setup({ 
    schemaContext: { 
        schemaRootDir: projectRoot, 
        primaryDatasourceDirectory: projectRoot, 
        loadedFromPathForLogMessages: projectRoot, schemaFiles: schemaFiles as LoadedFile[]
    } as SchemaContext,
    migrationsDirPath: join(projectRoot, 'prisma', 'migrations'),
  })
  
  // const wasDbCreated = await ensureDatabaseExists(schemaPath)
  // if (wasDbCreated) {
  //   console.info(wasDbCreated)
  // }

  try {
    const listResult = await migrate.listMigrationDirectories()
    if (listResult.migrations.length === 0) {
      exitWithError('No migrations found in prisma/migrations')
    }

    const diagnose = await migrate.diagnoseMigrationHistory({
      optInToShadowDatabase: false,
    })

    if (diagnose.editedMigrationNames.length > 0) {
      console.warn(
        `⚠️  The following migrations were modified after being applied:\n${diagnose.editedMigrationNames.join(
          '\n',
        )}`,
      )
    }

    console.info('🚀 Applying pending migrations ...')
    const { appliedMigrationNames } = await migrate.applyMigrations()

    if (appliedMigrationNames.length === 0) {
      console.info('✅ No pending migrations to apply.')
    } else {
      const files = printFilesFromMigrationIds('migrations', appliedMigrationNames, {
        'migration.sql': '',
      })
      console.info(
        `✅ Applied ${appliedMigrationNames.length} migration(s):\n${appliedMigrationNames.join(
          '\n',
        )}\n\n${files}`,
      )
    }
  } finally {
    await migrate.stop()
  }

  runPrismaGenerate()
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})

