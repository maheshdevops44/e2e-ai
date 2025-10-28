import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Menu, Plus, Minus, Search } from "lucide-react"
import { getDraftTests } from "@/lib/actions/test"

interface _WorkflowDraft {
  id: string
  testName: string
  currentStep: number
  createdAt: string
  updatedAt: string
}

interface WorkflowSidebarProps {
  children: React.ReactNode
}

export function WorkflowWithSidebar({ children }: WorkflowSidebarProps) {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [expandedMenus, setExpandedMenus] = useState({
    testEnvironments: false,
    testManagement: false,
    automationTools: false,
    drafts: false
  })
  const [drafts, setDrafts] = useState<{id: string, testName: string, currentStep: number}[]>([])

  // Fetch drafts when component mounts
  useEffect(() => {
    const fetchDrafts = async () => {
      try {
        const tests = await getDraftTests()
        // Convert tests to draft format and filter incomplete workflows
        const incompleteDrafts = tests
          .filter(test => test.status === 'DRAFT') // Only show draft status
          .map(test => ({
            id: test.id,
            testName: test.testId,
            currentStep: 1, // All drafts start at step 1
          }))
        setDrafts(incompleteDrafts)
      } catch (error) {
        console.error('Error fetching drafts:', error)
        setDrafts([])
      }
    }
    fetchDrafts()
  }, [])

  const toggleSidebar = () => {
    setSidebarCollapsed(prev => !prev)
  }

  const toggleMenu = (menuKey: keyof typeof expandedMenus) => {
    setExpandedMenus(prev => ({
      ...prev,
      [menuKey]: !prev[menuKey]
    }))
  }

  const handleSubMenuClick = (content: string) => {
    console.log(`Selected: ${content}`)
  }

  const handleCreateNewTest = () => {
    // Navigate to create new test page
    router.push('/create-test')
  }

  return (
    <div className="flex h-full">
      {/* Sidebar Container */}
      <div className="flex-shrink-0">
        <Card 
          className={`h-full transition-all duration-300 ${sidebarCollapsed ? 'w-16' : 'w-64'}`}
          style={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            margin: '8px',
            maxHeight: 'calc(100vh - 16px)'
          }}
        >
          <CardContent className="p-0 h-full overflow-hidden">
            {sidebarCollapsed ? (
              /* Collapsed Sidebar - Only Toggle Button */
              <div className="p-4 flex justify-center">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleSidebar}
                  className="h-10 w-10"
                >
                  <Menu className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              /* Expanded Sidebar - Full Content */
              <div className="h-full flex flex-col">
                {/* Header with Toggle and Search */}
                <div className="p-4 space-y-4 border-b border-gray-100">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={toggleSidebar}
                    className="w-full justify-start"
                  >
                    <Menu className="h-4 w-4 mr-2" />
                  </Button>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input 
                      placeholder="Search" 
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                      style={{ width: '224px', height: '36px' }}
                    />
                  </div>
                </div>
              
                {/* Scrollable Content Area */}
                <div className="flex-1 overflow-y-auto p-4">
                  {/* Main Navigation Links */}
                  <div className="space-y-1 mb-6">
                    <Button
                      variant="ghost"
                      className="w-full justify-start p-2 h-auto hover:bg-transparent"
                      onClick={handleCreateNewTest}
                    >
                      <span className="text-sm font-bold">New Test Cases</span>
                    </Button>
                  </div>

                  {/* Expandable Menu Sections */}
                  <div className="space-y-1">



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
                              <Button 
                                key={draft.id}
                                variant="ghost" 
                                size="sm" 
                                className="w-full justify-start text-xs py-1 h-auto hover:bg-transparent" 
                                onClick={() => {
                                  router.push(`/create-test/workflow/${draft.id}?step=${draft.currentStep}`)
                                }}
                              >
                                {draft.testName}
                              </Button>
                            ))
                          ) : (
                            <p className="text-xs text-gray-500 ml-4 py-1">No drafts found</p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Right Content Area */}
      <div className="flex-1 ml-1">
        {children}
      </div>
    </div>
  )
}