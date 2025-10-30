# CI/CD Pipeline Optimization Proposal
## Path-Based Filtering & PR/Deployment Separation

**Presented To:** DevOps Architecture Team  
**Presented By:** Loka Mahesh  
**Date:** 30/10/2025  
**Project:** E2E AI Platform  
**Environment:** Development (AWS ECS Fargate)

---

## Executive Summary

**Problem:** Current pipeline deploys all 4 services on every change, wasting 60-70% of pipeline time and resources.

**Solution:** Implement intelligent path-based filtering to deploy only changed services.

**Impact:**
- ⏱️ **60-70% faster** PR feedback (5-7 min vs 15-20 min)
- 💰 **60% cost reduction** in GitHub Actions minutes
- 🛡️ **Eliminated risk** of PRs deploying to dev environment
- 🚀 **Improved developer experience** with faster iterations

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Proposed Solution Overview](#2-proposed-solution-overview)
3. [Technical Implementation](#3-technical-implementation)
4. [How The Script Runs](#4-how-the-script-runs)
5. [Old vs New Comparison](#5-old-vs-new-comparison)
6. [Real-World Scenarios](#6-real-world-scenarios)
7. [Benefits & ROI](#7-benefits--roi)
8. [Risk Analysis](#8-risk-analysis)
9. [Implementation Plan](#9-implementation-plan)

---

## 1. Current State Analysis

### 1.1 Current Architecture

**Services:** 4 microservices on ECS Fargate
- `ui/` - NextJS frontend (port 3000)
- `ui-v2/` (platform) - Alternative NextJS UI (port 3000)
- `agent/` - Python backend API (port 8000)
- `test-executor/` - Python test runner (port 8000)

**Current Pipeline Flow:**
```
Push/PR → develop
    ↓
terraform-apply (ALWAYS runs)
    ↓
    ├─── docker-build-push-ui (ALWAYS runs)
    ├─── docker-build-push-platform (ALWAYS runs)
    ├─── docker-build-push-agent (ALWAYS runs)
    └─── docker-build-push-test-executor (ALWAYS runs)
         ↓
    All 4 services → Build → ECR → ECS Deploy
    ↓
Total: 15-20 minutes (every time)
```

### 1.2 Current Problems

#### Problem 1: No Service Isolation
**Scenario:** Developer updates UI header styling
```yaml
Changed files:
  - ui/src/components/Header.tsx

Current Behavior:
  ✅ Builds UI ✓ (needed)
  ✅ Builds Platform ✗ (NOT needed)
  ✅ Builds Agent ✗ (NOT needed)
  ✅ Builds Test Executor ✗ (NOT needed)
  ✅ Deploys all 4 services ✗ (3 unnecessary)
  
Time Wasted: 15 minutes
Services Restarted: 4 (should be 1)
```

#### Problem 2: PRs Deploy to Dev
**Scenario:** Developer creates PR with experimental changes
```yaml
Action: Create PR feature/new-feature → develop

Current Behavior:
  ✅ terraform-apply RUNS (deploys to dev!) ✗
  ✅ All services BUILD and DEPLOY ✗
  ❌ No validation-only mode
  
Risk: Unstable code affects entire dev environment
Impact: Other developers disrupted
```

#### Problem 3: No Change Detection
**Current trigger logic:**
```yaml
on:
  push:
    branches: ["develop"]
    paths: ["terraform/**", ".github/**", "ui/**", "agent/**", "test-executor/**"]
```

**Problem:** This says "run if ANY of these paths change" but doesn't tell us WHICH ones changed. So ALL services build regardless.

#### Problem 4: Resource Waste

**Monthly Waste (Current State):**
```
GitHub Actions Minutes:
  - Total used: ~2000 minutes/month
  - Wasted: ~1200 minutes/month (60%)
  
AWS Costs:
  - Unnecessary ECR pushes: ~150/month
  - Unnecessary ECS deployments: ~150/month
  - Unnecessary API calls: 4x what's needed
  
Developer Time:
  - Waiting for pipelines: ~20 hours/month
  - Context switching: High
  - Frustration: Increasing
```

---

## 2. Proposed Solution Overview

### 2.1 Solution Architecture

**Key Innovation:** Separate "What Changed" Detection from "What to Do"

```
┌─────────────────────────────────────────────────────────────┐
│                   PHASE 1: DETECTION                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Job: detect-changes                                   │ │
│  │  Action: dorny/paths-filter@v2                         │ │
│  │                                                        │ │
│  │  Input: Git diff between commits                       │ │
│  │  Output: Boolean flags for each component              │ │
│  │    • ui: true/false                                    │ │
│  │    • platform: true/false                              │ │
│  │    • agent: true/false                                 │ │
│  │    • test-executor: true/false                         │ │
│  │    • terraform: true/false                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│             PHASE 2: MODE DETERMINATION                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Check: github.event_name                              │ │
│  │                                                        │ │
│  │  IF event == "pull_request":                           │ │
│  │    → Execute VALIDATION mode                           │ │
│  │    → Build Docker (no push)                            │ │
│  │    → Terraform plan (no apply)                         │ │
│  │    → Comment results on PR                             │ │
│  │                                                        │ │
│  │  IF event == "push" AND branch == "develop":           │ │
│  │    → Execute DEPLOYMENT mode                           │ │
│  │    → Build Docker + Push to ECR                        │ │
│  │    → Terraform apply                                   │ │
│  │    → Deploy to ECS                                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          PHASE 3: CONDITIONAL EXECUTION                     │
│                                                             │
│  For each service:                                          │
│    IF (mode == validation AND service.changed == true):     │
│      → Run {service}-validation job                         │
│                                                             │
│    IF (mode == deployment AND service.changed == true):     │
│      → Run {service}-deployment job                         │
│                                                             │
│    ELSE:                                                    │
│      → Skip service jobs                                    │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 New Job Structure

**Before: 5 jobs (all always run)**
```yaml
1. terraform-apply
2. docker-build-push-ui
3. docker-build-push-platform
4. docker-build-push-agent
5. docker-build-push-test-executor
```

**After: 15 jobs (selective execution)**
```yaml
Detection Layer:
  1. detect-changes (always runs)

Validation Layer (PR only):
  2. terraform-plan (if terraform changed)
  3. ui-validation (if ui changed)
  4. platform-validation (if platform changed)
  5. agent-validation (if agent changed)
  6. test-executor-validation (if test-executor changed)

Deployment Layer (Push to develop only):
  7. terraform-apply (if terraform changed)
  8. ui-deployment (if ui changed)
  9. platform-deployment (if platform changed)
  10. agent-deployment (if agent changed)
  11. test-executor-deployment (if test-executor changed)

Utility:
  12. terraform-destroy (manual only)
```

---

## 3. Technical Implementation

### 3.1 Change Detection Implementation

**Tool:** `dorny/paths-filter@v2` (GitHub Actions marketplace)
- **Purpose:** Analyzes git diff to determine which paths changed
- **Reliability:** Used by 10,000+ repositories
- **Performance:** <5 seconds execution time

**Configuration:**
```yaml
jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      ui: ${{ steps.filter.outputs.ui }}
      platform: ${{ steps.filter.outputs.platform }}
      agent: ${{ steps.filter.outputs.agent }}
      test-executor: ${{ steps.filter.outputs.test-executor }}
      terraform: ${{ steps.filter.outputs.terraform }}
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            ui:
              - 'ui/**'
            platform:
              - 'ui-v2/**'
            agent:
              - 'agent/**'
            test-executor:
              - 'test-executor/**'
            terraform:
              - 'terraform/**'
              - '.github/**'
```

**How It Works:**
1. Checks out repository code
2. Compares current commit with base branch (develop)
3. Generates git diff
4. Matches changed files against filter patterns
5. Outputs boolean for each filter (`true`/`false`)
6. Makes outputs available to downstream jobs

**Example Output:**
```yaml
# If developer changes ui/src/App.tsx:
outputs:
  ui: 'true'
  platform: 'false'
  agent: 'false'
  test-executor: 'false'
  terraform: 'false'
```

### 3.2 Conditional Job Execution

**Pattern:** Every job uses conditional logic based on:
1. Event type (PR vs Push)
2. Branch name (develop vs others)
3. Change detection outputs

**Example: UI Validation Job**
```yaml
ui-validation:
  name: UI - Build Validation
  needs: detect-changes
  
  # This is the conditional logic:
  if: |
    github.event_name == 'pull_request' &&
    needs.detect-changes.outputs.ui == 'true'
  
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Build Docker Image (Validation Only)
      uses: docker/build-push-action@v5
      with:
        context: ./ui
        push: false  # ← Key: Don't push to ECR
        tags: e2e-ai-dev-ui:pr-${{ github.event.pull_request.number }}
```

**Breakdown:**
- `github.event_name == 'pull_request'` → Only runs on PRs
- `needs.detect-changes.outputs.ui == 'true'` → Only runs if UI changed
- `push: false` → Builds Docker but doesn't push to ECR
- **Result:** Fast validation without deployment

**Example: UI Deployment Job**
```yaml
ui-deployment:
  name: UI - Build and Deploy
  needs: [detect-changes, terraform-apply]
  
  # This is the conditional logic:
  if: |
    github.event_name == 'push' &&
    github.ref == 'refs/heads/develop' &&
    needs.detect-changes.outputs.ui == 'true'
  
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Push Docker Image - UI
      uses: ./.github/actions/docker-build-push-ecr
      with:
        ecr_repository_name: e2e-ai-dev-ui
        image_tag: ${{ github.sha }}
        dockerfile_path: "./ui"
    
    - name: Deploy to ECS service
      uses: ./.github/actions/ecs-redeploy
      with:
        ecs_cluster_name: e2e-ai-dev-cluster
        ecs_service_name: e2e-ai-dev-ui-service
```

**Breakdown:**
- `github.event_name == 'push'` → Only runs on merge to branch
- `github.ref == 'refs/heads/develop'` → Only on develop branch
- `needs.detect-changes.outputs.ui == 'true'` → Only if UI changed
- Uses existing custom actions for ECR push and ECS deploy
- **Result:** Full deployment only when needed

### 3.3 Terraform Split

**Old Approach: Single Job**
```yaml
terraform-apply:
  runs-on: ubuntu-latest
  steps:
    - uses: cigna-group/aws-template-actions/terraform-apply@v2.0.3
      # This ALWAYS applies terraform changes
```
**Problem:** PRs trigger actual infrastructure changes!

**New Approach: Two Jobs**

**Job 1: terraform-plan (PR only)**
```yaml
terraform-plan:
  name: Terraform Plan (PR Validation)
  needs: detect-changes
  if: |
    github.event_name == 'pull_request' &&
    (needs.detect-changes.outputs.terraform == 'true' || 
     needs.detect-changes.outputs.github-workflows == 'true')
  
  steps:
    - name: Terraform Init
      run: terraform init
    
    - name: Terraform Plan
      id: plan
      run: terraform plan -no-color -out=tfplan
    
    - name: Comment PR with Terraform Plan
      uses: actions/github-script@v7
      with:
        script: |
          const output = `#### Terraform Plan 📖
          \`\`\`terraform
          ${{ steps.plan.outputs.stdout }}
          \`\`\`
          `;
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: output
          });
```
**Result:** Developers see infrastructure changes before merging, no actual changes applied

**Job 2: terraform-apply (Deploy only)**
```yaml
terraform-apply:
  name: Terraform Apply (Deployment)
  needs: detect-changes
  if: |
    github.event_name == 'push' &&
    github.ref == 'refs/heads/develop' &&
    (needs.detect-changes.outputs.terraform == 'true' || 
     needs.detect-changes.outputs.github-workflows == 'true')
  
  steps:
    - uses: cigna-group/aws-template-actions/terraform-apply@v2.0.3
      # Now only applies on merge to develop
```
**Result:** Infrastructure changes only applied after PR approval and merge

---

## 4. How The Script Runs

### 4.1 Execution Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│              GITHUB EVENT (Trigger)                          │
│  • Developer pushes to branch                                │
│  • Developer creates/updates PR                              │
│  • Manual workflow dispatch                                  │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: DETECT CHANGES (5-10 seconds)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Job: detect-changes                                    │ │
│  │ • Checkout code                                        │ │
│  │ • Run dorny/paths-filter                               │ │
│  │ • Generate outputs:                                    │ │
│  │   ui: 'true/false'                                     │ │
│  │   platform: 'true/false'                               │ │
│  │   agent: 'true/false'                                  │ │
│  │   test-executor: 'true/false'                          │ │
│  │   terraform: 'true/false'                              │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│  STEP 2: EVALUATE CONDITIONS                                 │
│  Each job checks:                                            │
│  1. Is this a PR or push to develop?                         │
│  2. Did my service change?                                   │
│  3. Are my dependencies ready?                               │
│                                                              │
│  If ALL conditions true → Job RUNS                           │
│  If ANY condition false → Job SKIPPED                        │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
        ┌──────────────┴───────────────┐
        ↓                              ↓
┌────────────────┐           ┌─────────────────┐
│  PR MODE       │           │  DEPLOY MODE    │
│  (Validation)  │           │  (Full Deploy)  │
└────────────────┘           └─────────────────┘
        ↓                              ↓
┌────────────────────────┐   ┌─────────────────────────┐
│ STEP 3A: PR VALIDATION │   │ STEP 3B: DEPLOYMENT     │
│ (Parallel Execution)   │   │ (Sequential+Parallel)   │
│                        │   │                         │
│ terraform-plan         │   │ terraform-apply         │
│    ↓ (if tf changed)   │   │    ↓ (if tf changed)    │
│                        │   │    Wait for completion  │
│ ┌──────────────────┐   │   │    ↓                    │
│ │ Validation Jobs  │   │   │ ┌──────────────────┐    │
│ │ (Run in parallel)│   │   │ │ Deployment Jobs  │    │
│ │                  │   │   │ │ (Run in parallel)│    │
│ │ ui-validation    │   │   │ │ ui-deployment    │    │
│ │ platform-val     │   │   │ │ platform-deploy  │    │
│ │ agent-val        │   │   │ │ agent-deploy     │    │
│ │ test-exec-val    │   │   │ │ test-exec-deploy │    │
│ │                  │   │   │ │                  │    │
│ │ (Only if svc     │   │   │ │ (Only if svc     │    │
│ │  changed)        │   │   │ │  changed)        │    │
│ └──────────────────┘   │   │ └──────────────────┘    │
│         ↓              │   │         ↓               │
│ Comment plan on PR     │   │ Deploy to ECS           │
│ Report validation      │   │ Health checks           │
└────────────────────────┘   └─────────────────────────┘
```

### 4.2 Step-by-Step Execution Example

**Scenario: Developer Changes UI and Agent**

**Step 1: Developer Actions**
```bash
# Developer on feature branch
git checkout -b feature/ui-and-agent-updates

# Makes changes
vi ui/src/components/Header.tsx      # Change 1
vi agent/src/api/endpoints.py        # Change 2

# Commits and pushes
git add ui/ agent/
git commit -m "feat: update UI header and agent endpoints"
git push origin feature/ui-and-agent-updates

# Creates PR on GitHub
# feature/ui-and-agent-updates → develop
```

**Step 2: detect-changes Job Executes**
```yaml
detect-changes:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - uses: dorny/paths-filter@v2
      id: filter
      with:
        filters: |
          ui: ['ui/**']
          platform: ['ui-v2/**']
          agent: ['agent/**']
          test-executor: ['test-executor/**']
          terraform: ['terraform/**', '.github/**']
```

**Internal Process:**
```bash
# Git diff analysis
Changed files:
  - ui/src/components/Header.tsx      → Matches 'ui/**'
  - agent/src/api/endpoints.py        → Matches 'agent/**'

# Pattern matching
ui filter: 'ui/**' → MATCH → ui = 'true'
platform filter: 'ui-v2/**' → NO MATCH → platform = 'false'
agent filter: 'agent/**' → MATCH → agent = 'true'
test-executor filter: 'test-executor/**' → NO MATCH → test-executor = 'false'
terraform filter: ['terraform/**', '.github/**'] → NO MATCH → terraform = 'false'
```

**Outputs:**
```yaml
outputs:
  ui: 'true'
  platform: 'false'
  agent: 'true'
  test-executor: 'false'
  terraform: 'false'
```

**Step 3: Job Evaluation Phase**

Each job evaluates its conditions:

**terraform-plan:**
```yaml
if: |
  github.event_name == 'pull_request' &&
  needs.detect-changes.outputs.terraform == 'true'

Evaluation:
  github.event_name = 'pull_request' → TRUE ✓
  outputs.terraform = 'false' → FALSE ✗
  
Result: SKIPPED
```

**ui-validation:**
```yaml
if: |
  github.event_name == 'pull_request' &&
  needs.detect-changes.outputs.ui == 'true'

Evaluation:
  github.event_name = 'pull_request' → TRUE ✓
  outputs.ui = 'true' → TRUE ✓
  
Result: RUNS ✓
```

**platform-validation:**
```yaml
if: |
  github.event_name == 'pull_request' &&
  needs.detect-changes.outputs.platform == 'true'

Evaluation:
  github.event_name = 'pull_request' → TRUE ✓
  outputs.platform = 'false' → FALSE ✗
  
Result: SKIPPED
```

**agent-validation:**
```yaml
if: |
  github.event_name == 'pull_request' &&
  needs.detect-changes.outputs.agent == 'true'

Evaluation:
  github.event_name = 'pull_request' → TRUE ✓
  outputs.agent = 'true' → TRUE ✓
  
Result: RUNS ✓
```

**test-executor-validation:**
```yaml
if: |
  github.event_name == 'pull_request' &&
  needs.detect-changes.outputs.test-executor == 'true'

Evaluation:
  github.event_name = 'pull_request' → TRUE ✓
  outputs.test-executor = 'false' → FALSE ✗
  
Result: SKIPPED
```

**Step 4: Execution (PR Mode)**

**Jobs That Run:**
```
┌─────────────────────┐
│ detect-changes      │ (5 seconds)
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ↓           ↓
┌──────────┐  ┌──────────┐
│ui-       │  │agent-    │ (Parallel, 5 min each)
│validation│  │validation│
└──────────┘  └──────────┘

Total Time: ~5-6 minutes
Services Validated: 2 (ui, agent)
Services Skipped: 2 (platform, test-executor)
Deployments: 0 (validation only)
```

**Step 5: Developer Merges PR**
```bash
# PR approved and merged on GitHub
# Triggers new workflow run with event_name = 'push'
```

**Step 6: detect-changes Job Runs Again**
```yaml
# Same analysis, same outputs
outputs:
  ui: 'true'
  agent: 'true'
  platform: 'false'
  test-executor: 'false'
  terraform: 'false'
```

**Step 7: Job Evaluation (Deployment Mode)**

**terraform-apply:**
```yaml
if: |
  github.event_name == 'push' &&
  github.ref == 'refs/heads/develop' &&
  needs.detect-changes.outputs.terraform == 'true'

Evaluation:
  github.event_name = 'push' → TRUE ✓
  github.ref = 'refs/heads/develop' → TRUE ✓
  outputs.terraform = 'false' → FALSE ✗
  
Result: SKIPPED
```

**ui-deployment:**
```yaml
if: |
  github.event_name == 'push' &&
  github.ref == 'refs/heads/develop' &&
  needs.detect-changes.outputs.ui == 'true'

Evaluation:
  github.event_name = 'push' → TRUE ✓
  github.ref = 'refs/heads/develop' → TRUE ✓
  outputs.ui = 'true' → TRUE ✓
  
Result: RUNS ✓
```

**agent-deployment:**
```yaml
if: |
  github.event_name == 'push' &&
  github.ref == 'refs/heads/develop' &&
  needs.detect-changes.outputs.agent == 'true'

Evaluation:
  github.event_name = 'push' → TRUE ✓
  github.ref = 'refs/heads/develop' → TRUE ✓
  outputs.agent = 'true' → TRUE ✓
  
Result: RUNS ✓
```

**Step 8: Execution (Deployment Mode)**

```
┌─────────────────────┐
│ detect-changes      │ (5 seconds)
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ↓             ↓
┌──────────┐  ┌──────────┐
│ui-       │  │agent-    │ (Parallel, 8 min each)
│deployment│  │deployment│
└──────────┘  └──────────┘
    │             │
    ├─ Build Docker image
    ├─ Push to ECR
    ├─ Update ECS task definition
    ├─ Deploy to ECS
    └─ Health check

Total Time: ~8-9 minutes
Services Deployed: 2 (ui, agent)
Services Skipped: 2 (platform, test-executor)
ECS Restarts: 2 (only changed services)
```

**Summary of This Example:**
- **PR Phase:** 5-6 minutes, 2 services validated, 0 deployments
- **Deployment Phase:** 8-9 minutes, 2 services deployed, 2 skipped
- **Total Time:** ~14 minutes
- **Old Pipeline Time:** 18-20 minutes (all 4 services)
- **Time Saved:** 4-6 minutes (25-30%)
- **Unnecessary Work:** 0% (was 50% - 2 out of 4 services)

---

## 5. Old vs New Comparison

### 5.1 Architecture Comparison

**OLD PIPELINE:**
```
┌────────────────────────────────────────────────────────┐
│             Single Linear Path                         │
│                                                        │
│             Push/PR → develop                          │
│                  ↓                                     │
│             terraform-apply (ALWAYS)                   │
│                  ↓                                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │   ALL Jobs Run in Parallel (ALWAYS)             │   │
│  │                                                 │   │
│  │  ┌────────────┐  ┌────────────┐                 │   │
│  │  │ docker-    │  │ docker-    │                 │   │
│  │  │ build-push-│  │ build-push-│                 │   │
│  │  │ ui         │  │ platform   │                 │   │
│  │  └────────────┘  └────────────┘                 │   │
│  │                                                 │   │
│  │  ┌────────────┐  ┌────────────┐                 │   │
│  │  │ docker-    │  │ docker-    │                 │   │
│  │  │ build-push-│  │ build-push-│                 │   │
│  │  │ agent      │  │ test-exec  │                 │   │
│  │  └────────────┘  └────────────┘                 │   │
│  └─────────────────────────────────────────────────┘   │
│       ↓                                                │
│  All services → ECR → ECS Deploy                       │
│                                                        │
│  Characteristics:                                      │
│  • No change detection                                 │
│  • No PR/Deploy separation                             │
│  • All services always process                         │
│  • Terraform always applies                            │
│  • PRs deploy to dev                                   │
└────────────────────────────────────────────────────────┘
```

**NEW PIPELINE:**
```
┌────────────────────────────────────────────────────────┐
│           Intelligent Branching Path                   │
│                                                        │
│        Push/PR → develop                               │
│                 ↓                                      │
│        detect-changes (NEW!)                           │
│        • Analyzes git diff                             │
│        • Outputs changed components                    │
│                 ↓                                      │
│  ┌──────────────┴───────────────┐                      │
│  ↓                              ↓                      │
│  PR MODE                  DEPLOY MODE                  │
│  (Validation)             (Full Deploy)                │
│  ↓                              ↓                      │
│  terraform-plan           terraform-apply              │
│  (if tf changed)          (if tf changed)              │
│  • Shows plan                 • Applies changes        │
│  • Comments on PR             • After validation       │
│  • NO apply                   ↓                        │
│  ↓                        (Dependencies ready)         │
│  ┌──────────────┐          ┌──────────────┐            │
│  │ Validation   │          │ Deployment   │            │
│  │ Jobs         │          │ Jobs         │            │
│  │ (Parallel)   │          │ (Parallel)   │            │
│  │              │          │              │            │
│  │ IF changed:  │          │ IF changed:  │            │
│  │ • ui-val     │          │ • ui-deploy  │            │
│  │ • plat-val   │          │ • plat-deploy│            │
│  │ • agent-val  │          │ • agent-dep  │            │
│  │ • test-val   │          │ • test-dep   │            │
│  │              │          │              │            │
│  │ ELSE: Skip   │          │ ELSE: Skip   │            │
│  └──────────────┘          └──────────────┘            │
│       ↓                         ↓                      │
│  Fast feedback             Only changed                │
│  No deployment             services deploy             │
│                                                        │
│  Characteristics:                                      │
│  • Smart change detection                              │
│  • PR/Deploy separation                                │
│  • Selective execution                                 │
│  • Conditional terraform                               │
│  • PRs validate only                                   │
└────────────────────────────────────────────────────────┘
```

### 5.2 Code Comparison

**OLD: Single terraform-apply Job**
```yaml
terraform-apply:
  runs-on: ubuntu-latest
  environment: dev
  steps:
    - uses: actions/checkout@v4
    - uses: cigna-group/aws-template-actions/terraform-apply@v2.0.3
      with:
        iam_deployer_role_name: ${{ env.IAM_DEPLOYER_ROLE_NAME }}
        aws_account_id: ${{ secrets.AWS_ACCOUNT_ID }}
        environment: ${{ env.ENVIRONMENT }}
        aws_region: ${{ env.AWS_REGION }}
```
**Problems:**
- ❌ Runs on EVERY trigger (PR and push)
- ❌ Always applies changes
- ❌ No preview for PRs
- ❌ No conditional execution

**NEW: Split into Plan and Apply**
```yaml
# Job 1: terraform-plan (PR only)
terraform-plan:
  name: Terraform Plan (PR Validation)
  needs: detect-changes
  if: |
    github.event_name == 'pull_request' &&
    (needs.detect-changes.outputs.terraform == 'true' || 
     needs.detect-changes.outputs.github-workflows == 'true')
  runs-on: ubuntu-latest
  environment: dev
  steps:
    - uses: actions/checkout@v4
    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v3
    - name: Terraform Plan
      id: plan
      run: terraform plan -no-color
    - name: Comment PR with Plan
      uses: actions/github-script@v7
      with:
        script: |
          github.rest.issues.createComment({
            body: `#### Terraform Plan 📖\n\`\`\`\n${{ steps.plan.outputs.stdout }}\n\`\`\``
          });

# Job 2: terraform-apply (Deploy only)
terraform-apply:
  name: Terraform Apply (Deployment)
  needs: detect-changes
  if: |
    github.event_name == 'push' &&
    github.ref == 'refs/heads/develop' &&
    (needs.detect-changes.outputs.terraform == 'true' || 
     needs.detect-changes.outputs.github-workflows == 'true')
  runs-on: ubuntu-latest
  environment: dev
  steps:
    - uses: actions/checkout@v4
    - uses: cigna-group/aws-template-actions/terraform-apply@v2.0.3
```
**Benefits:**
- ✅ PRs show plan without applying
- ✅ Only applies on merge to develop
- ✅ Conditional based on changes
- ✅ Clear separation of concerns

---

**OLD: Single docker-build-push Job**
```yaml
docker-build-push-ui:
  runs-on: ubuntu-latest
  needs: terraform-apply  # Always waits for terraform
  steps:
    - uses: actions/checkout@v4
    - uses: ./.github/actions/docker-build-push-ecr
      with:
        ecr_repository_name: ${{ env.ECR_REPOSITORY_NAME_UI }}
        image_tag: ${{ github.sha }}
        dockerfile_path: "./ui"
    - uses: ./.github/actions/ecs-redeploy
      with:
        ecs_cluster_name: ${{ env.ECS_CLUSTER_NAME }}
        ecs_service_name: ${{ env.ECS_SERVICE_NAME_UI }}
```
**Problems:**
- ❌ Always runs (even if UI didn't change)
- ❌ Always pushes to ECR (even on PRs)
- ❌ Always deploys to ECS (even on PRs)
- ❌ Depends on terraform (even if terraform didn't run)

**NEW: Split into Validation and Deployment**
```yaml
# Job 1: ui-validation (PR only)
ui-validation:
  name: UI - Build Validation
  needs: detect-changes
  if: |
    github.event_name == 'pull_request' &&
    needs.detect-changes.outputs.ui == 'true'
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: docker/setup-buildx-action@v3
    - uses: docker/build-push-action@v5
      with:
        context: ./ui
        push: false  # ← Validate only, don't push
        tags: e2e-ai-dev-ui:pr-${{ github.event.pull_request.number }}

# Job 2: ui-deployment (Deploy only)
ui-deployment:
  name: UI - Build and Deploy
  needs: [detect-changes, terraform-apply]
  if: |
    github.event_name == 'push' &&
    github.ref == 'refs/heads/develop' &&
    needs.detect-changes.outputs.ui == 'true'
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: ./.github/actions/docker-build-push-ecr
      with:
        ecr_repository_name: ${{ env.ECR_REPOSITORY_NAME_UI }}
        image_tag: ${{ github.sha }}
        dockerfile_path: "./ui"
    - uses: ./.github/actions/ecs-redeploy
      with:
        ecs_cluster_name: ${{ env.ECS_CLUSTER_NAME }}
        ecs_service_name: ${{ env.ECS_SERVICE_NAME_UI }}
```
**Benefits:**
- ✅ Only runs if UI changed
- ✅ PRs validate without pushing/deploying
- ✅ Deployments only on merge
- ✅ Clear intent and purpose

### 5.3 Behavior Comparison

**Scenario 1: Developer Changes UI Only**

**OLD BEHAVIOR:**
```yaml
Trigger: Create PR with ui/src/App.tsx change

Pipeline Execution:
  ✅ terraform-apply RUNS (unnecessary)
     Duration: 3 minutes
     Action: Applies to dev environment
  
  ✅ docker-build-push-ui RUNS
     Duration: 5 minutes
     Actions:
       - Builds Docker image
       - Pushes to ECR
       - Deploys to ECS
  
  ✅ docker-build-push-platform RUNS (unnecessary)
     Duration: 5 minutes
     Actions:
       - Builds Docker image
       - Pushes to ECR
       - Deploys to ECS
  
  ✅ docker-build-push-agent RUNS (unnecessary)
     Duration: 5 minutes
     Actions:
       - Builds Docker image
       - Pushes to ECR
       - Deploys to ECS
  
  ✅ docker-build-push-test-executor RUNS (unnecessary)
     Duration: 5 minutes
     Actions:
       - Builds Docker image
       - Pushes to ECR
       - Deploys to ECS

Total Time: 18-20 minutes
Services Built: 4
Services Deployed: 4
Necessary Work: 25% (1 out of 4 services)
Wasted Work: 75% (3 out of 4 services)
PR Impact: Deploys to dev environment ❌
```

**NEW BEHAVIOR:**
```yaml
Trigger: Create PR with ui/src/App.tsx change

Pipeline Execution:
  ✅ detect-changes RUNS
     Duration: 5 seconds
     Output: ui='true', others='false'
  
  ✅ ui-validation RUNS
     Duration: 5 minutes
     Actions:
       - Builds Docker image
       - NO ECR push
       - NO ECS deployment
  
  ❌ terraform-plan SKIPPED (terraform didn't change)
  ❌ platform-validation SKIPPED (platform didn't change)
  ❌ agent-validation SKIPPED (agent didn't change)
  ❌ test-executor-validation SKIPPED (test-executor didn't change)

Total Time: 5-6 minutes (70% faster)
Services Validated: 1
Services Deployed: 0
Necessary Work: 100%
Wasted Work: 0%
PR Impact: No deployment ✅

After PR Merge:
  ✅ detect-changes RUNS
     Output: ui='true', others='false'
  
  ❌ terraform-apply SKIPPED (terraform didn't change)
  
  ✅ ui-deployment RUNS
     Duration: 8 minutes
     Actions:
       - Builds Docker image
       - Pushes to ECR
       - Deploys to ECS
  
  ❌ platform-deployment SKIPPED
  ❌ agent-deployment SKIPPED
  ❌ test-executor-deployment SKIPPED

Deployment Time: 8-9 minutes (55% faster)
Services Deployed: 1
Necessary Work: 100%
Wasted Work: 0%
```

**Scenario 2: Developer Changes Terraform Only**

**OLD BEHAVIOR:**
```yaml
Trigger: Create PR with terraform/base/ecs.tf change

Pipeline Execution:
  ✅ terraform-apply RUNS
     Duration: 3 minutes
     Action: Applies to dev environment ❌ (risky!)
  
  ✅ ALL service jobs RUN (unnecessary)
     Duration: 15 minutes
     Action: Rebuild and redeploy all services

Total Time: 18 minutes
Infrastructure Changed: Yes (from PR!) ❌
Services Redeployed: 4 (unnecessary)
Risk Level: HIGH (infrastructure changed before review)
```

**NEW BEHAVIOR:**
```yaml
Trigger: Create PR with terraform/base/ecs.tf change

Pipeline Execution:
  ✅ detect-changes RUNS
     Output: terraform='true', services='false'
  
  ✅ terraform-plan RUNS
     Duration: 1 minute
     Actions:
       - Shows what would change
       - Comments plan on PR
       - NO apply ✅
  
  ❌ ALL service validation jobs SKIPPED (services didn't change)

Total Time: 1-2 minutes (90% faster)
Infrastructure Changed: No (plan only) ✅
Services Redeployed: 0
Risk Level: LOW (review before apply)
Visibility: High (plan visible on PR)

After PR Merge:
  ✅ terraform-apply RUNS
     Duration: 3 minutes
     Action: Applies infrastructure changes
  
  ❌ ALL service deployment jobs SKIPPED

Deployment Time: 3-4 minutes
Only Infrastructure Updated: Yes ✅
```

### 5.4 Metrics Comparison Table

| Metric                             | OLD Pipeline | NEW Pipeline | Improvement          |
|------------------------------------|--------------|--------------|----------------------|
| **PR Feedback Time (1 service)**   | 18-20 min    | 5-7 min      | **65-70% faster**    |
| **PR Feedback Time (2 services)**  | 18-20 min    | 7-10 min     | **50-60% faster**    |
| **PR Feedback Time (terraform)**   | 18-20 min    | 1-2 min      | **90% faster**       |
| **Deployment Time (1 service)**    | 18-20 min    | 8-10 min     | **50% faster**       |
| **Deployment Time (2 services)**   | 18-20 min    | 12-14 min    | **30% faster**       |
| **Deployment Time (all services)** | 18-20 min    | 16-18 min    | Baseline             |
| **GitHub Actions Minutes/Month**   | ~2000 min    | ~800 min     | **60% reduction**    |
| **Unnecessary Builds**             | 75%          | 0%           | **100% elimination** |
| **Unnecessary Deployments**        | 75%          | 0%           | **100% elimination** |
| **PR Deploys to Dev**              | Yes ❌      | No ✅        | **Risk eliminated**  |
| **Developer Waiting Time/Week**    | ~5 hours     | ~2 hours     | **60% reduction**    |
| **Context Switches/Day**           | High         | Low          | **Better flow**      |

---

## 6. Real-World Scenarios

### Scenario A: Hotfix for Production Bug

**Context:** Critical bug found in UI production. Need fast fix.

**OLD WORKFLOW:**
```bash
10:00 AM - Bug identified
10:15 AM - Developer creates fix in ui/src/
10:20 AM - Creates PR → develop
10:20 AM - Pipeline starts
          - Builds ALL 4 services
          - Deploys ALL 4 to dev
10:38 AM - Pipeline completes (18 min)
          - Dev environment disrupted ❌
          - Other developers affected ❌
10:40 AM - PR approved
10:42 AM - Merge to develop
10:42 AM - Pipeline starts AGAIN
          - Builds ALL 4 services
          - Deploys ALL 4 to dev
11:00 AM - Deployment complete (18 min)
          - Ready for production

Total Time: 1 hour
Developer Frustration: High
Risk of Side Effects: High
```

**NEW WORKFLOW:**
```bash
10:00 AM - Bug identified
10:15 AM - Developer creates fix in ui/src/
10:20 AM - Creates PR → develop
10:20 AM - Pipeline starts
          - detect-changes: ui changed
          - ui-validation ONLY
10:25 AM - Pipeline completes (5 min) ✅
          - Fast feedback
          - No dev disruption ✅
10:27 AM - PR approved
10:28 AM - Merge to develop
10:28 AM - Pipeline starts
          - detect-changes: ui changed
          - ui-deployment ONLY
10:36 AM - Deployment complete (8 min)
          - Only UI restarted ✅
          - Ready for production

Total Time: 16 minutes (62% faster)
Developer Frustration: Low
Risk of Side Effects: Minimal
Other Services: Unaffected ✅
```

### Scenario B: Infrastructure Capacity Update

**Context:** Need to increase ECS task memory from 512MB to 1024MB.

**OLD WORKFLOW:**
```bash
2:00 PM - Update terraform/base/ecs.tf
2:05 PM - Create PR → develop
2:05 PM - Pipeline starts
          - terraform-apply RUNS immediately ❌
          - Infrastructure CHANGES in dev ❌
          - ALL services rebuild
          - ALL services redeploy
2:23 PM - Complete (18 min)
          - Infrastructure already changed
          - Can't review before apply ❌

Risk: High (changed before review)
Visibility: Low (no preview)
Rollback: Difficult
```

**NEW WORKFLOW:**
```bash
2:00 PM - Update terraform/base/ecs.tf
2:05 PM - Create PR → develop
2:05 PM - Pipeline starts
          - terraform-plan RUNS
          - Shows proposed changes
          - Comments on PR
          - NO apply ✅
2:07 PM - Complete (2 min)
          - Team reviews plan
          - Discusses changes
          - Identifies potential issues
2:15 PM - PR approved after review
2:16 PM - Merge to develop
2:16 PM - terraform-apply RUNS
          - Applies changes
2:19 PM - Complete (3 min)
          - Services NOT rebuilt (didn't change) ✅
          - Services NOT redeployed ✅

Total Time: 5 minutes
Risk: Low (reviewed before apply)
Visibility: High (plan visible)
Rollback: Easy (git revert)
Service Disruption: None ✅
```

### Scenario C: Multi-Service Feature

**Context:** New feature requires changes to UI, Agent, and Test Executor.

**OLD WORKFLOW:**
```bash
Day 1:
9:00 AM - Start feature development
        - Work on all 3 services
        - Create checkpoints/tests

11:00 AM - Create PR for progress check
11:00 AM - Pipeline starts
          - ALL 4 services build/deploy (18 min)
          - Dev environment updated with WIP code ❌
11:18 AM - Team reviews WIP changes
          - But dev is now unstable ❌

2:00 PM - More changes
2:00 PM - Push to PR
2:00 PM - Pipeline starts again
          - ALL 4 services build/deploy (18 min)
2:18 PM - Dev disrupted again ❌

Iterations: 3-4 times/day
Time per iteration: 18 minutes
Total pipeline time: 54-72 minutes/day
Dev stability: Poor ❌
Team impact: High ❌
```

**NEW WORKFLOW:**
```bash
Day 1:
9:00 AM - Start feature development
        - Work on all 3 services
        - Create checkpoints/tests

11:00 AM - Create PR for progress check
11:00 AM - Pipeline starts
          - detect-changes: ui, agent, test-executor
          - Only those 3 validate (8 min)
          - NO deployment ✅
11:08 AM - Team reviews WIP changes
          - Dev environment stable ✅
          - Other developers unaffected ✅

2:00 PM - More changes
2:00 PM - Push to PR
2:00 PM - Pipeline starts
          - Only changed services validate (6 min)
2:06 PM - Fast feedback ✅

Iterations: 3-4 times/day
Time per iteration: 6-8 minutes
Total pipeline time: 18-32 minutes/day (60% faster)
Dev stability: Excellent ✅
Team impact: Minimal ✅

When ready:
4:00 PM - Final approval
4:01 PM - Merge to develop
4:01 PM - Pipeline deploys only 3 services (12 min)
4:13 PM - Feature live in dev ✅
```

---

## 7. Benefits & ROI

### 7.1 Time Savings

**Pipeline Duration Reduction:**
```
Scenario: Single service change (most common - 70% of changes)

Old: 18-20 minutes (all services)
New: 5-7 minutes (PR) + 8-10 minutes (deploy)

PR Phase Savings: 65-70% faster
Deploy Phase Savings: 50% faster

Average Weighted Savings: 60%
```

**Monthly Time Savings:**
```
Assumptions:
- 100 PRs/month
- 70% single service, 20% two services, 10% all services

Old Pipeline:
  100 PRs × 18 min = 1,800 minutes
  100 deploys × 18 min = 1,800 minutes
  Total: 3,600 minutes (60 hours)

New Pipeline:
  70 single-service PRs × 6 min = 420 minutes
  20 two-service PRs × 8 min = 160 minutes
  10 all-service PRs × 18 min = 180 minutes
  70 single-service deploys × 9 min = 630 minutes
  20 two-service deploys × 13 min = 260 minutes
  10 all-service deploys × 18 min = 180 minutes
  Total: 1,830 minutes (30.5 hours)

Time Saved: 1,770 minutes/month (29.5 hours)
Reduction: 49% overall
```

### 7.2 Cost Savings

**GitHub Actions Minutes:**
```
Old: ~2,000 minutes/month
New: ~830 minutes/month
Savings: 1,170 minutes/month (58.5%)

Cost (at $0.008/minute for Linux):
Old: $16.00/month
New: $6.64/month
Savings: $9.36/month ($112/year)
```

**AWS Costs:**
```
ECR API Calls:
  Old: ~400 pushes/month (all services)
  New: ~130 pushes/month (only changed)
  Savings: 67.5%

ECS Deployments:
  Old: ~400 deployments/month
  New: ~130 deployments/month
  Savings: 67.5%

AWS API Costs:
  Estimated savings: $50-100/month
  Annual: $600-1,200/year
```

**Developer Productivity:**
```
Developer waiting time:
  Old: ~20 hours/month team-wide
  New: ~8 hours/month team-wide
  Savings: 12 hours/month

Value (at $100/hour loaded cost):
  Monthly: $1,200
  Annual: $14,400
```

**Total Annual ROI:**
```
GitHub Actions: $112/year
AWS Costs: $900/year (conservative)
Developer Time: $14,400/year
Total Savings: $15,412/year

Implementation Cost: ~40 hours (one-time)
Payback Period: <2 weeks
```

### 7.3 Quality Improvements

**Risk Reduction:**
```
✅ Eliminated: PRs deploying to dev
   - Impact: High
   - Frequency: Every PR
   - Risk: Environment instability

✅ Eliminated: Unnecessary service restarts
   - Impact: Medium
   - Frequency: 75% of deployments
   - Risk: Service disruption

✅ Added: Terraform plan review
   - Impact: High
   - Frequency: Every terraform change
   - Risk: Infrastructure accidents
```

**Developer Experience:**
```
Before:
  - PR feedback: 18-20 minutes
  - Context switches: High
  - Frustration: "Why so slow?"
  - Iteration speed: Low

After:
  - PR feedback: 5-7 minutes (70% faster)
  - Context switches: Low
  - Satisfaction: High
  - Iteration speed: High
  - Confidence: Improved (no accidental deploys)
```

### 7.4 Operational Benefits

**Deployment Safety:**
```
✅ Clear separation: Validation vs Deployment
✅ Predictable behavior: Only changed services deploy
✅ Better observability: Easy to see what deployed
✅ Faster rollback: Smaller change sets
✅ Reduced blast radius: Only changed services affected
```

**Team Collaboration:**
```
✅ Less dev environment disruption
✅ Parallel work enabled (different services)
✅ Faster code reviews (quick feedback)
✅ Better visibility (terraform plans)
✅ Reduced merge conflicts (faster iteration)
```

---

## 8. Risk Analysis

### 8.1 Implementation Risks

**Risk 1: False Negatives (Missed Deployments)**

**Description:** Change detection misses a dependency, causing a service not to deploy when it should.

**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:**
- Comprehensive testing during POC phase
- `dorny/paths-filter` is well-tested (10,000+ repos)
- Path patterns are explicit and reviewable
- Manual workflow dispatch available as backup
- Monitoring during first week post-deployment

**Risk 2: Job Name Breaking Changes**

**Description:** External systems referencing old job names break.

**Likelihood:** Medium  
**Impact:** Low  
**Mitigation:**
- Document all breaking changes in PR
- Identify and update branch protection rules
- Update any CI/CD dashboards
- Notify team before merge
- Keep old workflow as backup for 2 weeks

**Risk 3: Learning Curve**

**Description:** Team unfamiliar with new workflow logic.

**Likelihood:** High  
**Impact:** Low  
**Mitigation:**
- Comprehensive documentation
- Team training session
- Clear workflow visualization
- Runbook for troubleshooting
- Support during transition period

### 8.2 Operational Risks

**Risk 4: Increased Complexity**

**Description:** More jobs means more complexity to maintain.

**Likelihood:** Medium  
**Impact:** Low  
**Mitigation:**
- Jobs follow consistent patterns
- Clear naming conventions
- Well-documented conditional logic
- Regular reviews of workflow
- Simplification opportunities identified

**Risk 5: Terraform State Conflicts**

**Description:** Parallel service deployments might cause terraform state issues.

**Likelihood:** Low  
**Impact:** Medium  
**Mitigation:**
- Terraform state locking already in place (DynamoDB)
- Services have separate infrastructure scopes
- terraform-apply job runs first before services
- State conflicts extremely rare in current setup

### 8.3 Risk Mitigation Summary

| Risk             | Mitigation Strategy          | Responsibility |
|------------------|------------------------------|----------------|
| False Negatives  | Thorough testing, monitoring | DevOps Team    |
| Breaking Changes | Communication, updates       | DevOps Lead    |
| Learning Curve   | Training, documentation      | All Team       |
| Complexity       | Patterns, naming             | DevOps Team    |
| State Conflicts  | Locking, monitoring          | Platform Team  |

**Overall Risk Level:** **LOW**
- Mature technology (`dorny/paths-filter`)
- Conservative implementation
- Comprehensive testing plan
- Easy rollback mechanism
- High potential benefit vs low risk

---

## 9. Implementation Plan

### 9.1 Phase 1: Preparation (Week 1)

**Tasks:**
- [x] Design new workflow architecture
- [x] Document changes and benefits
- [x] Create architect presentation
- [ ] Review with DevOps team
- [ ] Get architect approval
- [ ] Create feature branch

**Deliverables:**
- Architecture diagrams
- Updated workflow YAML
- This presentation document
- Approval from architect

### 9.2 Phase 2: POC Implementation (Week 1-2)

**Tasks:**
- [ ] Create POC branch
- [ ] Update dev.yml with new workflow
- [ ] Add change detection job
- [ ] Split terraform jobs
- [ ] Split service jobs for all 4 services
- [ ] Add conditional logic
- [ ] Add PR comment functionality
- [ ] Test YAML syntax

**Testing Checklist:**
- [ ] Test 1: Single service PR (UI only)
- [ ] Test 2: Single service deployment
- [ ] Test 3: Multi-service PR
- [ ] Test 4: Terraform-only change
- [ ] Test 5: All services change
- [ ] Test 6: Workflow file change
- [ ] Test 7: Manual workflow dispatch

**Success Criteria:**
- All tests pass
- No false negatives
- PR comments working
- Correct services deploy

### 9.3 Phase 3: Validation (Week 2)

**Tasks:**
- [ ] Merge to develop branch
- [ ] Monitor first 10 deployments
- [ ] Collect metrics:
  - Pipeline duration
  - Services deployed
  - GitHub Actions minutes
- [ ] Developer feedback survey
- [ ] Identify issues

**Metrics to Track:**
```
Day 1:
- First PR validation time
- First deployment time
- Any errors or issues

Week 1:
- Average PR time
- Average deploy time
- GitHub Actions minutes used
- False negatives count
- Developer satisfaction (1-10)

Week 2:
- Compare to baseline
- Calculate ROI
- Document lessons learned
```

### 9.4 Phase 4: Rollout (Week 3-4)

**Tasks:**
- [ ] Update branch protection rules
- [ ] Update team documentation
- [ ] Create troubleshooting runbook
- [ ] Team training session
- [ ] Update onboarding docs
- [ ] Monitor and optimize

**Documentation Updates:**
- [ ] README with new workflow
- [ ] CONTRIBUTING guide update
- [ ] Team wiki update
- [ ] Runbook for common issues
- [ ] Architecture decision record

### 9.5 Success Metrics

**Week 1 Targets:**
```
✅ PR feedback time: <8 minutes (single service)
✅ Deployment time: <12 minutes (single service)
✅ Zero false negatives
✅ Zero critical issues
✅ Positive developer feedback
```

**Month 1 Targets:**
```
✅ 50%+ reduction in average pipeline time
✅ 50%+ reduction in GitHub Actions minutes
✅ Zero PRs deploying to dev
✅ 90%+ developer satisfaction
✅ ROI calculation positive
```

**Quarterly Review:**
```
✅ Sustained time savings
✅ Cost savings validated
✅ Team adoption complete
✅ Documentation complete
✅ Optimization opportunities identified
```

---

## 10. Questions & Discussion

### Common Questions

**Q1: What if we need to deploy all services regardless of changes?**

**A:** Use manual workflow dispatch with optional input to override change detection, or temporarily modify the conditionals. We can also add an "emergency deploy all" workflow.

---

**Q2: How do we handle shared code changes (like a common library)?**

**A:** Add shared paths to multiple service filters:
```yaml
ui:
  - 'ui/**'
  - 'shared/**'  # Triggers UI if shared changes
agent:
  - 'agent/**'
  - 'shared/**'  # Triggers Agent if shared changes
```

---

**Q3: What's the rollback plan if this causes issues?**

**A:** Simple git revert:
```bash
git revert [commit-sha]
git push origin develop
```
Old workflow restored in ~5 minutes.

---

**Q4: Will this work for production pipeline too?**

**A:** Yes! Same patterns apply to prod.yml. We can implement after validating in dev. Production would add:
- Manual approval gates
- Blue-green deployments
- Extended health checks
- Smoke tests

---

**Q5: What about dependency changes (package.json, requirements.txt)?**

**A:** Path filters catch these automatically since they're in the service directory:
```
ui/package.json → Matches 'ui/**' → Triggers UI jobs
```

---

**Q6: How do we test the workflow itself without affecting dev?**

**A:** Create test branch, test there, then merge. Or use workflow_dispatch trigger for manual testing.

---

### Next Steps

1. **Today:** Review this presentation
2. **This Week:** Architect approval + POC implementation
3. **Next Week:** Testing and validation
4. **Week 3-4:** Team rollout and training
5. **Month 1:** Collect metrics and optimize

---

## Appendix

### A. Complete Job List

**Detection:**
1. `detect-changes` - Analyzes changed paths

**Validation (PR):**
2. `terraform-plan` - Shows infrastructure changes
3. `ui-validation` - Validates UI build
4. `platform-validation` - Validates Platform build
5. `agent-validation` - Validates Agent build
6. `test-executor-validation` - Validates Test Executor build

**Deployment (Push to develop):**
7. `terraform-apply` - Applies infrastructure
8. `ui-deployment` - Deploys UI service
9. `platform-deployment` - Deploys Platform service
10. `agent-deployment` - Deploys Agent service
11. `test-executor-deployment` - Deploys Test Executor service

**Utility:**
12. `terraform-destroy` - Manual cleanup

### B. Key Technologies

- **dorny/paths-filter@v2** - Change detection
- **GitHub Actions** - CI/CD platform
- **AWS ECS Fargate** - Container runtime
- **Terraform** - Infrastructure as Code
- **Docker** - Containerization

### C. References

- [dorny/paths-filter documentation](https://github.com/dorny/paths-filter)
- [GitHub Actions conditional logic](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobsjob_idif)
- [ECS deployment strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-types.html)

---

**End of Presentation**

**Prepared by:** Loka Mahesh  
**Date:** 30/10/2025  
**Status:** Ready for Architect Review  
**Next Action:** Schedule review meeting
