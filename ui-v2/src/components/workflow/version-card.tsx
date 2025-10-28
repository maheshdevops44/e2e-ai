'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Download } from 'lucide-react'

export type SummaryLine = {
  label: string
  value: string
}

export type TestPlan = {
  objective: string
  applicationsInvolved: string[]
  summary: SummaryLine[]
  testFlow: string[]
}

type VersionCardProps = {
  title: string // e.g. "Version 1"
  plan: TestPlan
  onModify?: () => void
  onProceed?: () => void
}

export default function VersionCard({ title, plan, onModify, onProceed }: VersionCardProps) {
  return (
    <Card className="rounded-[10px] border border-muted/100 font-sans shadow-sm">
      <CardHeader className="flex flex-row justify-between space-y-0">
        <CardTitle className="min-w-0 text-base font-semibold">{title}</CardTitle>
        <Button variant="ghost" size="icon" className="shrink-0 rounded-full" aria-label="Download">
          <Download className="h-5 w-5" />
        </Button>
      </CardHeader>
      <CardContent>
        <Card className="rounded-[10px] border border-gray-100 border-muted/100 bg-gray-50 shadow-sm">
          <CardContent className="space-y-4 py-6">
            <section>
              <h3 className="mb-1 text-sm font-medium">Objective</h3>
              <p className="text-sm">{plan.objective}</p>
            </section>

            <section className="rounded-md">
              <h2 className="mb-2 text-sm font-medium">Applications Involved</h2>
              <div className="flex flex-col flex-wrap gap-2">
                {plan.applicationsInvolved.map((app) => (
                  <ul key={app} className="text-sm font-normal">
                    {app}
                  </ul>
                ))}
              </div>
            </section>

            <section>
              <h3 className="mb-2 text-sm font-medium">Summary</h3>
              <div className="grid gap-1">
                {plan.summary.map(({ label, value }) => (
                  <div key={label} className="text-sm">
                    <span className="">{label}:</span> <span className="font-normal">{value}</span>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="mb-2 text-sm font-medium">Test Flow</h3>
              <ul className="space-y-1 text-sm">
                {plan.testFlow.map((step, idx) => (
                  <li key={idx}>{step}</li>
                ))}
              </ul>
            </section>
          </CardContent>
        </Card>
        <div className="flex justify-between pt-6">
          <Button className="w-32 rounded-lg text-sm" variant="outline" onClick={onModify} disabled>
            Make Changes
          </Button>
          <Button className="w-32 rounded-lg text-sm" onClick={onProceed}>
            Proceed
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
