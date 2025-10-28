"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { UserStoryStepWithRHF } from "./workflow/user-story-step-with-rhf"
import { ProcessingStep } from "./workflow/processing-step"
import { PlanOutputStep } from "./workflow/plan-output-step"
import { TestScriptStep } from "./workflow/test-script-step"

interface WorkflowData {
  id?: string
  testId?: string
  testDescription?: string
  storyType: "manual" | "upload"
  manualStory: string
  userStoryDescription?: string
  criteriaList: string[]
  currentStep: number
  testSuite?: string
}

interface NewTestWorkflowProps {
  workflowId?: string
  initialData?: WorkflowData
  onStepComplete?: (stepData: Partial<WorkflowData>) => Promise<void>
  onDraftCreated?: () => void
}

export function NewTestWorkflow({ workflowId, initialData, onStepComplete, onDraftCreated }: NewTestWorkflowProps) {
  const router = useRouter()
  const [workflowData, setWorkflowData] = useState<WorkflowData>(
    initialData || {
      storyType: "manual",
      manualStory: "",
      criteriaList: [],
      currentStep: 1
    }
  )
  
  // Update workflowData when initialData changes (for URL navigation)
  useEffect(() => {
    if (initialData) {
      setWorkflowData(initialData)
    }
  }, [initialData])
  
  // Get current step from initialData to ensure it's always in sync with URL
  // Use initialData as the source of truth for currentStep
  const currentStep = initialData?.currentStep || 1



  const steps = [
    { id: 1, title: 'UserStory', active: currentStep === 1 },
    { id: 2, title: 'Processing', active: currentStep === 2 },
    { id: 3, title: 'Planoutput', active: currentStep === 3 },
    { id: 4, title: 'Test Script Generation', active: currentStep === 4 },
  ]

  const handleStepProceed = async (stepData: Partial<WorkflowData>) => {
    const nextStep = currentStep + 1;
    const updatedData = { ...workflowData, ...stepData, currentStep: nextStep };
    setWorkflowData(updatedData);

    // If this is a URL-based workflow, use the callback
    if (onStepComplete) {
      await onStepComplete(stepData);
      return;
    }

    // Navigate to next step - if we have a workflow ID, navigate to the workflow page
    if (stepData.id) {
      router.push(`/create-test/workflow/${stepData.id}?step=${nextStep}`);
      // Don't call onDraftCreated after navigation as it would reload the page
      return;
    }

    // For new workflows without ID, notify parent about draft creation
    if (onDraftCreated) {
      onDraftCreated();
    }
    
    // If no workflow ID, the component will re-render with the updated currentStep
  }

  const handleComplete = () => {
    alert('Workflow completed successfully!')
    // TODO: Navigate back to dashboard or drafts
  }

  return (
    <div className="max-w-6xl mx-auto px-1 pb-8">
      {/* Workflow Title */}
      <div className="mb-4">
        <h2 
          className="font-sans font-semibold text-2xl"
          style={{
            color: '#0A0A0A',
            letterSpacing: 'var(--typography-components-h3-letter-spacing, normal)'
          }}
        >
          Start your testing workflow
        </h2>
      </div>

      {/* Step Progress Header */}
      <div className="mb-4">
        <Card style={{ backgroundColor: '#F5F5F5' }}>
          <CardContent className="p-1">
            <div className="w-full">
              {/* Testing Steps Flow - Horizontal */}
              <div className="flex items-center justify-between gap-2 w-full">
                {steps.map((step, index) => (
                  <div key={step.id} className="flex items-center flex-1">
                    {/* Active Step - Button Style */}
                    {step.active ? (
                      <Button
                        variant="outline"
                        className="flex-1 justify-center h-10 transition-colors bg-white border-[#E5E5E5] shadow-sm"
                        style={{ borderWidth: '1px' }}
                      >
                        <span className="flex items-center gap-2">
                          <span 
                            className="font-sans font-medium text-sm align-middle"
                            style={{
                              color: '#0A0A0A',
                              letterSpacing: '0%'
                            }}
                          >
                            {step.id}.
                          </span>
                          <span 
                            className="font-sans font-medium text-sm align-middle"
                            style={{
                              color: '#0A0A0A',
                              letterSpacing: '0%'
                            }}
                          >
                            {step.title === "UserStory" ? "User Story" : 
                             step.title === "Planoutput" ? "Plan Output" : 
                             step.title}
                          </span>
                        </span>
                      </Button>
                    ) : (
                      /* Inactive Step - Plain Text Style */
                      <div 
                        className="flex-1 text-center font-sans font-medium text-sm align-middle"
                        style={{
                          color: '#0A0A0A',
                          letterSpacing: '0%'
                        }}
                      >
                        {step.id}. {step.title === "UserStory" ? "User Story" : 
                                    step.title === "Planoutput" ? "Plan Output" : 
                                    step.title}
                      </div>
                    )}

                    {/* ChevronRight Icon (only between steps) */}
                    {index < steps.length - 1 && (
                      <div className="text-gray-400 mx-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Dynamic Step Content */}
      <div className="space-y-8 mb-8">        
        {currentStep === 1 && (
          <UserStoryStepWithRHF
            initialData={{
              testId: workflowData.testId || "",  // Use testId from workflow data
              testDescription: workflowData.testDescription || "",  // Use testDescription
              storyType: workflowData.storyType,
              manualStory: workflowData.manualStory,
              criteriaList: workflowData.criteriaList,
              acceptanceCriteria: workflowData.criteriaList,
              testSuite: workflowData.testSuite || "",
              userStoryDescription: workflowData.userStoryDescription || ""  // Use userStoryDescription
            }}
            workflowId={workflowId}
            onProceed={handleStepProceed}
          />
        )}

        {currentStep === 2 && (
          <ProcessingStep
            workflowData={workflowData}
            onProceed={() => handleStepProceed({})}
          />
        )}

        {currentStep === 3 && (
          <PlanOutputStep
            workflowData={workflowData}
            onProceed={() => handleStepProceed({})}
          />
        )}

        {currentStep === 4 && (
          <TestScriptStep
            workflowData={workflowData}
            onComplete={handleComplete}
          />
        )}
      </div>
    </div>
  )
}