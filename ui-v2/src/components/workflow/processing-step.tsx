"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { LoaderPinwheel, CheckCircle } from "lucide-react"

interface WorkflowData {
  id?: string
  testId?: string
  testDescription?: string
  storyType?: "manual" | "upload"
  manualStory?: string
  userStoryDescription?: string
  criteriaList?: string[]
  currentStep?: number
  testSuite?: string
}

interface ProcessingStepProps {
  workflowData?: WorkflowData
  onProceed: () => void
}

export function ProcessingStep({ onProceed }: ProcessingStepProps) {
  const [isButtonEnabled, setIsButtonEnabled] = useState(false)
  const [countdown, setCountdown] = useState(15)

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1)
      }, 1000)
      
      return () => clearTimeout(timer)
    } else {
      setIsButtonEnabled(true)
    }
  }, [countdown])
  return (
    <Card>
      <CardHeader>
        <CardTitle 
          className="font-sans font-semibold text-base leading-none tracking-tight text-black"
        >
          Step 2: Agent is processing your test case
        </CardTitle>
        <CardDescription>
          Agent will take a few seconds to process your test plan
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="mb-6">
          <Card 
            className="border-2 border-dashed border-gray-300 bg-white w-full h-44 rounded-lg"
          >
            <CardContent className="p-6">
              <div className="text-center space-y-4">
                <div className="flex justify-center">
                  <Card className="bg-white shadow-sm p-3 w-fit h-fit">
                    {isButtonEnabled ? (
                      <CheckCircle 
                        className="text-black w-6 h-6"
                      />
                    ) : (
                      <LoaderPinwheel 
                        className="animate-spin text-black w-6 h-6"
                      />
                    )}
                  </Card>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-black mb-2">
                    {isButtonEnabled ? "AI has generated your test plan" : "AI is generating your test cases"}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {isButtonEnabled ? "Click on Proceed below to view" : "Our AI is breaking down the scenario into testable steps"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Proceed Button - Right aligned, enabled after 15 seconds */}
        <div className="flex justify-end px-4">
          <Button 
            onClick={onProceed}
            disabled={!isButtonEnabled}
            className={`px-8 py-3 transition-all duration-300 ${
              isButtonEnabled 
                ? 'bg-black hover:bg-gray-800 text-white' 
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
            size="lg"
          >
            {isButtonEnabled ? 'Proceed' : `Processing... ${countdown}s`}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}