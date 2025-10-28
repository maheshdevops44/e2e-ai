'use client'

import { useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LoaderPinwheel } from 'lucide-react'
import { generateDummyTestScript } from '@/lib/actions/test-script'
import { useRouter } from 'next/navigation'

interface TestScriptStepProps {
  workflowData?: { id?: string; testId?: string }
  onComplete: () => void
}

export function TestScriptStep({ workflowData, onComplete }: TestScriptStepProps) {
  const route = useRouter()
  useEffect(() => {
    async function run() {
      try {
        await generateDummyTestScript({
          testRecordId: workflowData?.id,
          testId: workflowData?.testId,
          overwrite: true,
        })
      } catch (e) {
        console.error('Failed to generate dummy test script:', e)
      }
    }

    run()
  }, [workflowData?.id, workflowData?.testId])

  return (
    <div className="space-y-6">
      <Card className="rounded-[10px] border border-muted/100 font-sans shadow-sm">
        <CardHeader>
          <CardTitle className="text-base font-semibold">
            Step 4: Generating your test script
          </CardTitle>
          <CardDescription className="text-sm">
            Agent will take a few seconds to process your test scripts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Card className="w-full rounded-[10px] border-2 border-dashed border-gray-300 bg-white">
            <CardContent className="flex flex-col items-center justify-center space-y-6 py-10">
              <Card className="h-fit w-fit rounded-[10px] bg-white p-3 shadow-sm">
                <LoaderPinwheel className="order-0 h-6 w-6 flex-none flex-grow-0 animate-spin text-black" />
              </Card>
              <p className="text-lg font-semibold">
                Sit back while AI writes your test script — you can keep working on other tasks.
              </p>
              <p className="!mt-2 text-sm text-muted-foreground">
                Check your test library for further updates
              </p>
              <div className="flex w-full flex-col gap-3">
                <Button
                  className="rounded-lg"
                  onClick={() => {
                    route.push('/create-test')
                  }}
                >
                  Create New Test
                </Button>
                <Button className="rounded-lg" variant="outline">
                  Visit Test Library
                </Button>
              </div>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  )
}
