-- CreateEnum
CREATE TYPE "public"."TestStatus" AS ENUM ('DRAFT', 'IN_PROGRESS', 'PLAN_READY', 'REVIEW_PENDING', 'SCRIPT_GENERATING', 'SCRIPT_READY', 'FAILED');

-- CreateTable
CREATE TABLE "public"."TestSuite" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,

    CONSTRAINT "TestSuite_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."Test" (
    "id" TEXT NOT NULL,
    "testId" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "userStoryDescription" TEXT,
    "status" "public"."TestStatus" NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "testSuiteId" TEXT,

    CONSTRAINT "Test_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."AcceptanceCriteria" (
    "id" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "testRecordId" TEXT NOT NULL,

    CONSTRAINT "AcceptanceCriteria_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."TestPlanVersion" (
    "id" TEXT NOT NULL,
    "versionNumber" INTEGER NOT NULL,
    "isFinalized" BOOLEAN NOT NULL DEFAULT false,
    "planContent" TEXT NOT NULL,
    "generatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "testRecordId" TEXT NOT NULL,

    CONSTRAINT "TestPlanVersion_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."TestScript" (
    "id" TEXT NOT NULL,
    "scriptContent" TEXT NOT NULL,
    "generatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "testRecordId" TEXT NOT NULL,

    CONSTRAINT "TestScript_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Test_testId_key" ON "public"."Test"("testId");

-- CreateIndex
CREATE UNIQUE INDEX "TestPlanVersion_testRecordId_versionNumber_key" ON "public"."TestPlanVersion"("testRecordId", "versionNumber");

-- CreateIndex
CREATE UNIQUE INDEX "TestScript_testRecordId_key" ON "public"."TestScript"("testRecordId");

-- AddForeignKey
ALTER TABLE "public"."Test" ADD CONSTRAINT "Test_testSuiteId_fkey" FOREIGN KEY ("testSuiteId") REFERENCES "public"."TestSuite"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."AcceptanceCriteria" ADD CONSTRAINT "AcceptanceCriteria_testRecordId_fkey" FOREIGN KEY ("testRecordId") REFERENCES "public"."Test"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."TestPlanVersion" ADD CONSTRAINT "TestPlanVersion_testRecordId_fkey" FOREIGN KEY ("testRecordId") REFERENCES "public"."Test"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "public"."TestScript" ADD CONSTRAINT "TestScript_testRecordId_fkey" FOREIGN KEY ("testRecordId") REFERENCES "public"."Test"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
