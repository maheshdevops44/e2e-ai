import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export function DashboardContent() {
  return (
    <div className="flex flex-1 flex-col gap-4 p-4">
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Total Tests</CardTitle>
            <CardDescription>Active test cases</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">24</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Passed</CardTitle>
            <CardDescription>Successful tests</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">18</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Failed</CardTitle>
            <CardDescription>Failed tests</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">6</div>
          </CardContent>
        </Card>
      </div>
      
      <Card className="flex-1">
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest test executions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex items-center justify-between p-2 border rounded">
              <span>Test Case 1: Login Flow</span>
              <span className="text-green-600 font-medium">Passed</span>
            </div>
            <div className="flex items-center justify-between p-2 border rounded">
              <span>Test Case 2: User Registration</span>
              <span className="text-green-600 font-medium">Passed</span>
            </div>
            <div className="flex items-center justify-between p-2 border rounded">
              <span>Test Case 3: Payment Flow</span>
              <span className="text-red-600 font-medium">Failed</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}