"use client"

import { useState, useEffect, useTransition } from "react"
import { useForm, Controller } from "react-hook-form"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Plus, Trash2 } from "lucide-react"
import { createTest, updateTest } from "@/lib/actions/test"
import { toast } from "@/hooks/use-toast"

interface UserStoryData {
  id?: string
  storyType: "manual" | "upload"
  manualStory: string
  criteriaList: string[]
  testDescription: string
  testId: string
  testSuite: string
  userStoryDescription: string
  acceptanceCriteria: string[]
}

interface UserStoryStepProps {
  initialData?: Partial<UserStoryData>
  workflowId?: string // Add workflowId for updating existing drafts
  onProceed: (data: Partial<UserStoryData>) => void
}

export function UserStoryStepWithRHF({ initialData, workflowId, onProceed }: UserStoryStepProps) {
  // React Hook Form setup
  const { 
    control, 
    handleSubmit, 
    watch, 
    setValue, 
    getValues: _getValues,
    reset,
    formState: { errors }
  } = useForm<UserStoryData>({
    defaultValues: {
      storyType: initialData?.storyType || "manual",
      manualStory: initialData?.manualStory || "",
      testDescription: initialData?.testDescription || "",
      testId: initialData?.testId || "",
      testSuite: initialData?.testSuite || "",
      userStoryDescription: initialData?.userStoryDescription || "",
      acceptanceCriteria: initialData?.acceptanceCriteria || [],
      criteriaList: initialData?.criteriaList || []
    }
  })

  // Reset form when initialData changes (for draft selection)
  useEffect(() => {
    if (initialData) {
      reset({
        storyType: initialData?.storyType || "manual",
        manualStory: initialData?.manualStory || "",
        testDescription: initialData?.testDescription || "",
        testId: initialData?.testId || "",
        testSuite: initialData?.testSuite || "",
        userStoryDescription: initialData?.userStoryDescription || "",
        acceptanceCriteria: initialData?.acceptanceCriteria || [],
        criteriaList: initialData?.criteriaList || []
      })
    }
  }, [initialData, reset])

  // Watch form values
  const storyType = watch("storyType")
  const criteriaList = watch("criteriaList")
  
  // State for acceptance criteria input
  const [acceptanceCriteriaText, setAcceptanceCriteriaText] = useState("")
  
  // State for current workflow ID
  const [currentWorkflowId, setCurrentWorkflowId] = useState<string | undefined>(workflowId)
  
  // Loading state for server action
  const [isPending, startTransition] = useTransition()

  // Auto-save functionality removed - using server actions instead

  // Validation functions
  // Add acceptance criteria function
  const addCriteria = () => {
    if (!acceptanceCriteriaText.trim()) {
      toast({
        title: "Validation Error",
        description: "Please enter acceptance criteria before adding.",
        variant: "destructive",
      })
      return
    }
    
    const newCriteriaList = [...criteriaList, acceptanceCriteriaText.trim()]
    setValue("criteriaList", newCriteriaList)
    setValue("acceptanceCriteria", newCriteriaList)
    setAcceptanceCriteriaText("")
  }

  // Remove acceptance criteria function
  const removeCriteria = (index: number) => {
    const newCriteriaList = criteriaList.filter((_, i) => i !== index)
    setValue("criteriaList", newCriteriaList)
    setValue("acceptanceCriteria", newCriteriaList)
  }

  // Submit handler using server actions
  const onSubmit = async (data: UserStoryData) => {
    // Validate acceptance criteria
    if (!data.criteriaList || data.criteriaList.length === 0) {
      toast({
        title: "Validation Error",
        description: "Please add at least one acceptance criteria before proceeding.",
        variant: "destructive",
      })
      return
    }

    startTransition(async () => {
      try {
        // Create FormData for server action
        const formData = new FormData()
        formData.append("testId", data.testId || "")
        formData.append("description", data.testDescription || "")
        formData.append("userStoryDescription", data.userStoryDescription || "")
        // Only append testSuiteId if it's actually selected and not "none"
        if (data.testSuite && data.testSuite.trim() !== "" && data.testSuite !== "none") {
          formData.append("testSuiteId", data.testSuite)
        } else {
          formData.append("testSuiteId", "")
        }
        formData.append("acceptanceCriteria", JSON.stringify(data.criteriaList || []))
        
        let result
        if (currentWorkflowId) {
          // Update existing test
          result = await updateTest(currentWorkflowId, formData)
        } else {
          // Create new test
          result = await createTest(formData)
        }

        if (result.success) {
          if (result.testId && !currentWorkflowId) {
            setCurrentWorkflowId(result.testId)
          }
          
          // Call the parent onProceed function with the workflow ID
          onProceed({
            ...data,
            id: result.testId || currentWorkflowId
          })
          
          // Optional: Show success message
          console.log("User story saved successfully")
        } else {
          console.error("Error saving user story:", result.error)
          toast({
            title: "Error Saving User Story",
            description: result.error,
            variant: "destructive",
          })
        }
      } catch (error) {
        console.error("Error in form submission:", error)
        toast({
          title: "Unexpected Error",
          description: "An unexpected error occurred. Please try again.",
          variant: "destructive",
        })
      }
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle 
          className="font-sans font-semibold text-base"
          style={{
            lineHeight: '100%',
            letterSpacing: 'var(--font-letter-spacing-tight, -0.025em)'
          }}
        >
          Step 1: Enter User Story and Requirement
        </CardTitle>
        <CardDescription>
          Describe your testing scenario in detail or upload a user story below
        </CardDescription>
      </CardHeader>
      <CardContent className="pb-8">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Story Type Selection */}
          <div className="space-y-2">
            <Controller
              name="storyType"
              control={control}
              rules={{ required: "Please select a story type" }}
              render={({ field }) => (
                <RadioGroup 
                  value={field.value} 
                  onValueChange={field.onChange}
                  className="space-y-4"
                >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Manual Entry Option */}
                <Label htmlFor="manual" className="cursor-pointer">
                  <div className={`p-4 rounded-lg border transition-colors ${
                    storyType === 'manual' 
                      ? 'bg-[#E5E5E5] border-[#171717]' 
                      : 'bg-white border-gray-200'
                  }`} style={storyType === 'manual' ? { borderWidth: '1px' } : {}}>
                    <div className="flex items-center space-x-2 mb-2">
                      <RadioGroupItem value="manual" id="manual" />
                      <span 
                        className="font-sans font-medium text-sm align-middle"
                        style={{
                          lineHeight: '100%',
                          letterSpacing: '0%'
                        }}
                      >
                        Enter Story Manually
                      </span>
                    </div>
                    <p 
                      className="font-sans font-normal text-sm"
                      style={{
                        letterSpacing: '0%',
                        color: 'var(--base-muted-foreground, #737373)'
                      }}
                    >
                      Type your user story out in a details format
                    </p>
                  </div>
                </Label>

                {/* Upload Option */}
                <Label htmlFor="upload" className="cursor-pointer">
                  <div className={`p-4 rounded-lg border transition-colors ${
                    storyType === 'upload' 
                      ? 'bg-[#E5E5E5] border-[#171717]' 
                      : 'bg-white border-gray-200'
                  }`} style={storyType === 'upload' ? { borderWidth: '1px' } : {}}>
                    <div className="flex items-center space-x-2 mb-2">
                      <RadioGroupItem value="upload" id="upload" />
                      <span 
                        className="font-sans font-medium text-sm align-middle"
                        style={{
                          lineHeight: '100%',
                          letterSpacing: '0%'
                        }}
                      >
                        Upload User Story
                      </span>
                    </div>
                    <p 
                      className="font-sans font-normal text-sm"
                      style={{
                        letterSpacing: '0%',
                        color: 'var(--base-muted-foreground, #737373)'
                      }}
                    >
                      Download our template, fill it and upload in CSV
                    </p>
                  </div>
                </Label>
              </div>
                </RadioGroup>
              )}
            />
            {errors.storyType && (
              <p className="text-sm text-red-600">{errors.storyType.message}</p>
            )}
          </div>

          {/* Test Description Section */}
          <div className="space-y-2">
            <h3 
              className="font-sans font-medium text-sm"
              style={{
                lineHeight: '100%',
                letterSpacing: '0%'
              }}
            >
              Test Description
            </h3>
            <Controller
              name="testDescription"
              control={control}
              rules={{ 
                required: "Test description is required",
                maxLength: { value: 200, message: "Max 200 characters allowed" }
              }}
              render={({ field }) => (
                <Input
                  {...field}
                  placeholder="Enter test description"
                  className="rounded-md border w-full"
                  style={{
                    height: '36px',
                    paddingTop: 'var(--spacing-1, 0.25rem)',
                    paddingRight: 'var(--spacing-3, 0.75rem)',
                    paddingBottom: 'var(--spacing-1, 0.25rem)',
                    paddingLeft: 'var(--spacing-3, 0.75rem)',
                    gap: '4px',
                    borderTop: '1px solid var(--base-input, #E5E5E5)',
                    borderRight: '1px solid var(--base-input, #E5E5E5)',
                    borderBottom: '1px solid var(--base-input, #E5E5E5)',
                    borderLeft: '1px solid var(--base-input, #E5E5E5)'
                  }}
                />
              )}
            />
            {errors.testDescription && (
              <p className="text-sm text-red-600">{errors.testDescription.message}</p>
            )}
            <p 
              className="font-sans font-normal text-sm mt-1"
              style={{
                letterSpacing: '0%',
                color: 'var(--base-muted-foreground, #737373)'
              }}
            >
              Max characters- 200
            </p>
          </div>

          {/* Test ID and Test Suite */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h3 
                className="font-sans font-medium text-sm"
                style={{
                  lineHeight: '100%',
                  letterSpacing: '0%'
                }}
              >
                Test ID
              </h3>
              <Controller
                name="testId"
                control={control}
                rules={{ required: "Test ID is required" }}
                render={({ field }) => (
                  <Input
                    {...field}
                    placeholder="Enter test ID"
                    className="rounded-md border"
                    onChange={(e) => {
                      const upperValue = e.target.value.toUpperCase()
                      field.onChange(upperValue)
                    }}
                    style={{
                      height: '36px',
                      paddingTop: 'var(--spacing-1, 0.25rem)',
                      paddingRight: 'var(--spacing-3, 0.75rem)',
                      paddingBottom: 'var(--spacing-1, 0.25rem)',
                      paddingLeft: 'var(--spacing-3, 0.75rem)',
                      gap: '4px',
                      borderTop: '1px solid var(--base-input, #E5E5E5)',
                      borderRight: '1px solid var(--base-input, #E5E5E5)',
                      borderBottom: '1px solid var(--base-input, #E5E5E5)',
                      borderLeft: '1px solid var(--base-input, #E5E5E5)'
                    }}
                  />
                )}
              />
              {errors.testId && (
                <p className="text-sm text-red-600">{errors.testId.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <h3 
                className="font-sans font-medium text-sm"
                style={{
                  lineHeight: '100%',
                  letterSpacing: '0%'
                }}
              >
                Add to a test suite
              </h3>
              <Controller
                name="testSuite"
                control={control}
                rules={{ required: false }} // Made optional temporarily
                render={({ field }) => (
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger 
                      className="rounded-md border"
                      style={{
                        height: '36px',
                        paddingTop: 'var(--spacing-1, 0.25rem)',
                        paddingRight: 'var(--spacing-3, 0.75rem)',
                        paddingBottom: 'var(--spacing-1, 0.25rem)',
                        paddingLeft: 'var(--spacing-3, 0.75rem)',
                        gap: '4px',
                        borderTop: '1px solid var(--base-input, #E5E5E5)',
                        borderRight: '1px solid var(--base-input, #E5E5E5)',
                        borderBottom: '1px solid var(--base-input, #E5E5E5)',
                        borderLeft: '1px solid var(--base-input, #E5E5E5)'
                      }}
                    >
                      <SelectValue placeholder="Select test suite" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">None (Optional)</SelectItem>
                      <SelectItem value="sprint-1-2">Sprint 1.2</SelectItem>
                      <SelectItem value="sprint-1-3">Sprint 1.3</SelectItem>
                      <SelectItem value="sprint-2-1">Sprint 2.1</SelectItem>
                      <SelectItem value="regression-suite">Regression Suite</SelectItem>
                      <SelectItem value="smoke-tests">Smoke Tests</SelectItem>
                    </SelectContent>
                  </Select>
                )}
              />
              {errors.testSuite && (
                <p className="text-sm text-red-600">{errors.testSuite.message}</p>
              )}
            </div>
          </div>

          {/* User Story Section */}
          <div className="space-y-2">
            <h3 
              className="font-sans font-medium text-sm"
              style={{
                lineHeight: '100%',
                letterSpacing: '0%',
                color: 'var(--base-foreground, #0A0A0A)'
              }}
            >
              Describe your user story below
            </h3>
            <Controller
              name="userStoryDescription"
              control={control}
              rules={{ 
                required: "Test description is required",
                minLength: { value: 10, message: "Test description must be at least 10 characters" },
                maxLength: { value: 2000, message: "Test description must be less than 2000 characters" }
              }}
              render={({ field }) => (
                <Textarea
                  {...field}
                  placeholder="Enter your test description"
                  className="rounded-md border w-full"
                  style={{
                    height: '174px',
                    minHeight: '60px',
                    paddingTop: 'var(--spacing-2, 0.5rem)',
                    paddingRight: 'var(--spacing-3, 0.75rem)',
                    paddingBottom: 'var(--spacing-2, 0.5rem)',
                    paddingLeft: 'var(--spacing-3, 0.75rem)',
                    gap: '10px',
                    background: 'var(--custom-background-dark-input-30, #FFFFFF)'
                  }}
                />
              )}
            />
            {errors.userStoryDescription && (
              <p className="text-sm text-red-600">{errors.userStoryDescription.message}</p>
            )}
          </div>

          {/* Acceptance Criteria Section */}
          <div className="space-y-2">
            <h3 
              className="font-sans font-medium text-sm"
              style={{
                lineHeight: '100%',
                letterSpacing: '0%',
                color: 'var(--base-foreground, #0A0A0A)'
              }}
            >
              Specify the acceptance criteria below.
            </h3>
            <div className="relative w-full max-w-full">
              <Input
                value={acceptanceCriteriaText}
                onChange={(e) => setAcceptanceCriteriaText(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addCriteria()
                  }
                }}
                placeholder="Enter acceptance criteria"
                className="rounded-xl border pr-12 w-full"
                style={{
                  height: '44px',
                  paddingTop: '4px',
                  paddingRight: '48px', // Extra space for the button
                  paddingBottom: '4px',
                  paddingLeft: '16px',
                  opacity: 1,
                  borderRadius: '12px', // rounded-xl
                  borderWidth: '1px',
                  background: 'var(--base-card, #FFFFFF)',
                  borderTop: '1px solid var(--base-border, #E5E5E5)',
                  borderRight: '1px solid var(--base-border, #E5E5E5)',
                  borderBottom: '1px solid var(--base-border, #E5E5E5)',
                  borderLeft: '1px solid var(--base-border, #E5E5E5)'
                }}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={addCriteria}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 hover:bg-transparent"
                style={{
                  width: '36px',
                  height: '36px',
                  background: 'transparent'
                }}
              >
                <Plus className="h-4 w-4 text-gray-600" />
              </Button>
            </div>

            {/* Display Added Criteria as Cards */}
            {criteriaList.length > 0 && (
              <div className="space-y-3 mt-4">
                <div className="space-y-2">
                  {criteriaList.map((criteria, index) => (
                    <div 
                      key={index} 
                      className="relative w-full max-w-full"
                      style={{
                        height: '36px',
                        opacity: 1
                      }}
                    >
                      <div 
                        className="w-full px-4 py-2 pr-12 rounded-md border bg-white flex items-center"
                        style={{
                          height: '36px',
                          background: 'var(--base-card, #FFFFFF)',
                          border: '1px solid var(--base-border, #E5E5E5)',
                          color: 'var(--base-foreground, #0A0A0A)'
                        }}
                      >
                        <p 
                          className="text-sm font-medium leading-none truncate flex-1"
                          style={{
                            color: 'var(--base-foreground, #0A0A0A)',
                            fontSize: '14px',
                            fontWeight: '500'
                          }}
                        >
                          {criteria}
                        </p>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeCriteria(index)}
                          className="absolute right-2 top-1/2 transform -translate-y-1/2 hover:bg-gray-100 rounded-sm"
                          style={{
                            width: '28px',
                            height: '28px',
                            background: 'transparent',
                            color: '#000000'
                          }}
                        >
                          <Trash2 className="h-4 w-4" style={{ color: '#000000' }} />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end mt-6">
            <Button 
              type="submit" 
              disabled={isPending}
              className="font-sans font-medium text-sm align-middle px-4 py-2"
              style={{
                minWidth: '80px',
                height: '40px',
                background: '#000000',
                color: '#FFFFFF',
                letterSpacing: '0%',
                border: 'none'
              }}
            >
              {isPending ? "Saving..." : "Proceed"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}