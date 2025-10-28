'use client'

import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { X } from 'lucide-react'
import { TestPlan } from './version-card'

export type ChangeRequest = {
  id: string
  section: string
  message: string
}

type Props = {
  onClose?: () => void
  plan: TestPlan
  onMakeChanges?: (requests: ChangeRequest[]) => void
}

const SECTIONS = ['Objective', 'Applications', 'Summary', 'Test Flow']

function getSectionContent(plan: TestPlan, section: string) {
  switch (section) {
    case 'Objective':
      return plan.objective
    case 'Applications':
      return plan.applicationsInvolved.join(', ')
    case 'Summary':
      return plan.summary.map((s) => `${s.label}: ${s.value}`).join('\n')
    case 'Test Flow':
      return plan.testFlow.map((s, i) => `${i + 1}. ${s}`).join('\n')
    default:
      return ''
  }
}

export default function ChangeRequestPanel({ onClose, plan, onMakeChanges }: Props) {
  const [section, setSection] = useState(SECTIONS[0])
  const [message, setMessage] = useState(getSectionContent(plan, SECTIONS[0]))
  const [requests, setRequests] = useState<ChangeRequest[]>([])

  const addRequest = () => {
    if (!message.trim()) return
    setRequests((prev) => [...prev, { id: crypto.randomUUID(), section, message: message.trim() }])
    setMessage('')
  }

  const removeRequest = (id: string) => {
    setRequests((prev) => prev.filter((r) => r.id !== id))
  }

  return (
    <Card className="border border-muted/60 shadow-sm">
      <CardHeader className="flex w-full flex-row items-center justify-between">
        <CardTitle className="text-base font-semibold">Change Requests</CardTitle>
        {onClose && (
          <button onClick={onClose} className="rounded-full p-1 transition hover:bg-muted">
            <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
          </button>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Section selection */}
        <div className="space-y-2">
          <Label className="text-sm">Select section</Label>
          <div className="flex flex-wrap gap-2">
            {SECTIONS.map((s) => (
              <Badge
                key={s}
                variant={s === section ? 'default' : 'secondary'}
                className="cursor-pointer"
                onClick={() => {
                  setSection(s)
                  setMessage(getSectionContent(plan, s))
                }}
              >
                {s}
              </Badge>
            ))}
          </div>
        </div>

        {/* Textarea for message */}
        <div className="space-y-2">
          <Label htmlFor="cr-msg" className="text-sm">
            Enter request
          </Label>
          <Textarea
            id="cr-msg"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Describe what should change..."
            className="min-h-[100px]"
          />
          <div className="flex justify-end">
            <Button variant="outline" size="sm" onClick={addRequest}>
              Add
            </Button>
          </div>
        </div>

        {/* List of requests */}
        <div className="space-y-2">
          <Label className="text-sm">Queued requests</Label>
          {requests.length === 0 ? (
            <p className="text-sm text-muted-foreground">No requests added yet.</p>
          ) : (
            <ul className="space-y-2">
              {requests.map((r) => (
                <li key={r.id} className="rounded-md border p-3 text-sm">
                  <div className="mb-1 flex items-center justify-between">
                    <Badge variant="secondary">{r.section}</Badge>
                    {/* <Button variant="ghost" size="sm" onClick={() => removeRequest(r.id)}>
                      Remove
                    </Button> */}
                    <button
                      onClick={() => removeRequest(r.id)}
                      className="rounded-full p-1 transition hover:bg-muted"
                    >
                      <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
                    </button>
                  </div>
                  <p className="whitespace-pre-wrap text-muted-foreground">{r.message}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full" onClick={() => onMakeChanges?.(requests)}>
          Make Changes
        </Button>
      </CardFooter>
    </Card>
  )
}
