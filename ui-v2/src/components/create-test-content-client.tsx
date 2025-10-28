"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Menu, Plus, Minus } from "lucide-react"
import { NewTestWorkflow } from "./new-test-workflow"

interface WorkflowDraft {
  id: string
  testName: string
  testId: string
  description: string
  userStoryDescription?: string
  testSuite?: { id: string; name: string } | null
  currentStep: number
  createdAt: string
  updatedAt: string
}

interface CreateTestContentClientProps {
  initialDrafts: WorkflowDraft[]
}

export function CreateTestContentClient({ initialDrafts }: CreateTestContentClientProps) {
  const router = useRouter()
  const [selectedContent, setSelectedContent] = useState("")

  // Auto-select "New Test Cases" when component mounts
  useEffect(() => {
    setSelectedContent("New Test Cases")
  }, [])
  const [searchQuery, setSearchQuery] = useState("")
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [expandedMenus, setExpandedMenus] = useState({
    drafts: false
  })
  const [drafts, setDrafts] = useState<WorkflowDraft[]>(initialDrafts)

  // Update drafts when initialDrafts prop changes
  useEffect(() => {
    setDrafts(initialDrafts)
  }, [initialDrafts])

  const refreshDrafts = async () => {
    // With server-side rendering, we need to refresh the page to get updated data
    // In a production app, you might want to use router.refresh() for more granular updates
    window.location.reload()
  }

  const handleSubMenuClick = (content: string) => {
    setSelectedContent(content)
  }

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed)
  }

  const toggleMenu = (menuKey: keyof typeof expandedMenus) => {
    setExpandedMenus(prev => ({
      ...prev,
      [menuKey]: !prev[menuKey]
    }))
  }

  return (
    <div className="flex min-h-screen">
      {/* Sidebar Container */}
      <div className="flex-shrink-0 min-h-full">
        <Card 
          className={`transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-64'} min-h-full`}
          style={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            margin: '8px',
            minHeight: 'calc(100vh - 16px)'
          }}
        >
          <CardContent className="p-0 h-full flex flex-col">
      {/* Left Sidebar Menu - Single Card Container */}
      
          {sidebarCollapsed ? (
            /* Collapsed Sidebar - Only Toggle Button */
            <div className="p-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleSidebar}
                className="w-full h-8"
              >
                <Menu className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            /* Expanded Sidebar - Full Content */
            <>
              {/* Header with Toggle and Search */}
              <div className="p-4 space-y-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleSidebar}
                  className="w-full justify-start"
                >
                  <Menu className="h-4 w-4" />
                </Button>
                <Input 
                  placeholder="Search tests..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full"
                />
              </div>
              
              <div className="flex flex-1 flex-col gap-3 p-4">
                {/* Main Navigation Links - No Individual Cards */}
                <div className="space-y-1">
                  <Button
                    variant="ghost"
                    className="w-full justify-start p-2 h-auto hover:bg-transparent"
                    onClick={() => handleSubMenuClick("New Test Cases")}
                  >
                    <span className={`text-sm ${selectedContent === "New Test Cases" ? 'font-bold' : 'font-medium'}`}>New Test Cases</span>
                  </Button>
                </div>

                {/* Expandable Menu Sections */}
                <div className="space-y-1 mt-4">
                  {/* Drafts Menu */}
                  <div>
                    <Button
                      variant="ghost"
                      className="w-full justify-between p-2 h-auto hover:bg-transparent"
                      onClick={() => toggleMenu('drafts')}
                    >
                      <span className="text-sm font-medium">Drafts</span>
                      {expandedMenus.drafts ? (
                        <Minus className="h-4 w-4" />
                      ) : (
                        <Plus className="h-4 w-4" />
                      )}
                    </Button>
                    {expandedMenus.drafts && (
                      <div className="ml-4 mt-1 space-y-1">
                        {drafts.length > 0 ? (
                          drafts.map((draft) => (
                            <div key={draft.id} className="space-y-1">
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                className="w-full justify-start text-xs py-1 h-auto hover:bg-transparent" 
                                onClick={() => {
                                  // Navigate to the workflow with current step
                                  router.push(`/create-test/workflow/${draft.id}?step=${draft.currentStep}`)
                                }}
                              >
                                <div className="text-left w-full">
                                  <div className="font-medium">{draft.testId || draft.id.substring(0, 8)}</div>
                                  {draft.testSuite && (
                                    <div className="text-gray-500 text-xs">Suite: {draft.testSuite.name}</div>
                                  )}
                                </div>
                              </Button>
                            </div>
                          ))
                        ) : (
                          <p className="text-xs text-gray-500 ml-4 py-1">No drafts found</p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
      </div>

      {/* Right Content Area - No divider needed */}
      <div className="flex-1">
        {selectedContent === "New Test Cases" ? (
          <NewTestWorkflow onDraftCreated={refreshDrafts} />
        ) : (
          <div className="p-6">
            <Card>
              <CardHeader>
                <CardTitle>Welcome to Test Management Dashboard</CardTitle>
                <CardDescription>Select any menu item from the left sidebar to get started</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p>Choose from the available options to get started:</p>
                  
                  <div className="grid grid-cols-1 gap-4 mt-6">
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-semibold mb-2">New Test Cases</h4>
                      <p className="text-sm text-gray-600">Start creating new test cases with our guided workflow</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* NEW: Testing Workflow Steps Section */}
            <div className="mt-2">
              <Card className="bg-gray-50">
                <CardContent className="p-2">
                  <div className="w-full">
                    <h3 className="text-lg font-semibold mb-6">Start your testing workflow</h3>
                    
                    {/* Testing Steps Flow - Horizontal with ChevronRight */}
                    <div className="flex items-center justify-between gap-4 w-full">
                      
                      {/* Step 1 - UserStory (Active Button) */}
                      <Button
                        variant="ghost"
                        className="flex-1 justify-center p-3 h-auto bg-blue-50 text-blue-700 hover:bg-blue-50"
                        onClick={() => handleSubMenuClick("New Test Cases")}
                      >
                        <span className="font-medium text-sm">UserStory</span>
                      </Button>

                      {/* ChevronRight Icon */}
                      <div className="text-gray-400">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>

                      {/* Step 2 - Processing (Normal Text) */}
                      <div className="flex-1 text-center p-3">
                        <span className="font-medium text-sm text-gray-600">Processing</span>
                      </div>

                      {/* ChevronRight Icon */}
                      <div className="text-gray-400">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>

                      {/* Step 3 - Planoutput (Normal Text) */}
                      <div className="flex-1 text-center p-3">
                        <span className="font-medium text-sm text-gray-600">Planoutput</span>
                      </div>

                      {/* ChevronRight Icon */}
                      <div className="text-gray-400">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>

                      {/* Step 4 - Test Script Generation (Normal Text) */}
                      <div className="flex-1 text-center p-3">
                        <span className="font-medium text-sm text-gray-600">Test Script Generation</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}