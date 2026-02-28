export type IssueType = 'Bug' | 'Task' | 'Story'
export type Priority = 'Low' | 'Medium' | 'High'

export interface GeneratePayload {
  ticket_details: string
  issue_type: IssueType
  priority: Priority
  project_key: string | null
  labels: string | null
}

export interface TicketResponse {
  title: string
  issue_type: IssueType
  priority: Priority
  project_key: string | null
  description: {
    problem: string
    proposed_solution: string
    notes: string
  }
  acceptance_criteria: string[]
  definition_of_done: string[]
  labels: string[]
  estimate: 'S' | 'M' | 'L'
  assumptions: string[]
}

export interface GenerateEnvelope {
  ticket: TicketResponse
  markdown: string
}
