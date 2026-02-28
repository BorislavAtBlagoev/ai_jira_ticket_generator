import { FormEvent, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { GenerateEnvelope, GeneratePayload, IssueType, Priority } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type Tab = 'preview' | 'markdown' | 'json'

function parsePrefill(searchParams: URLSearchParams): GeneratePayload {
  return {
    ticket_details: searchParams.get('ticket_details') ?? '',
    issue_type: (searchParams.get('issue_type') as IssueType) || 'Task',
    priority: (searchParams.get('priority') as Priority) || 'Medium',
    project_key: searchParams.get('project_key'),
    labels: searchParams.get('labels')
  }
}

function downloadFile(content: string, fileName: string, contentType: string) {
  const blob = new Blob([content], { type: contentType })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = fileName
  anchor.click()
  URL.revokeObjectURL(url)
}

export default function GeneratorPage() {
  const [searchParams] = useSearchParams()
  const initial = useMemo(() => parsePrefill(searchParams), [searchParams])

  const [ticketDetails, setTicketDetails] = useState(initial.ticket_details)
  const [issueType, setIssueType] = useState<IssueType>(initial.issue_type)
  const [priority, setPriority] = useState<Priority>(initial.priority)
  const [projectKey, setProjectKey] = useState(initial.project_key ?? '')
  const [labels, setLabels] = useState(initial.labels ?? '')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<GenerateEnvelope | null>(null)
  const [tab, setTab] = useState<Tab>('preview')

  const payload = (): GeneratePayload => ({
    ticket_details: ticketDetails,
    issue_type: issueType,
    priority,
    project_key: projectKey.trim() || null,
    labels: labels.trim() || null
  })

  const runGeneration = async () => {
    setError('')
    if (!ticketDetails.trim()) {
      setError('Ticket details are required.')
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload())
      })

      if (!response.ok) {
        const body = await response.json().catch(() => ({}))
        throw new Error(body.detail || 'Generation failed.')
      }

      const data = (await response.json()) as GenerateEnvelope
      setResult(data)
      setTab('preview')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error.')
    } finally {
      setLoading(false)
    }
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    await runGeneration()
  }

  const clearForm = () => {
    setTicketDetails('')
    setIssueType('Task')
    setPriority('Medium')
    setProjectKey('')
    setLabels('')
    setResult(null)
    setError('')
  }

  return (
    <div className="page">
      <header>
        <h1>AI Jira Ticket Generator</h1>
        <p>Generate a Jira ticket draft in consistent Jira markdown and JSON formats.</p>
        <Link to="/help">Open help</Link>
      </header>
      <div className="grid">
        <section className="panel">
          <h2>Input</h2>
          <form onSubmit={submit}>
            <label>
              Ticket details
              <textarea
                value={ticketDetails}
                onChange={(e) => setTicketDetails(e.target.value)}
                rows={12}
                placeholder="Describe the request or problem statement..."
              />
            </label>

            <label>
              Issue type
              <select value={issueType} onChange={(e) => setIssueType(e.target.value as IssueType)}>
                <option>Bug</option>
                <option>Task</option>
                <option>Story</option>
              </select>
            </label>

            <label>
              Priority
              <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>
                <option>Low</option>
                <option>Medium</option>
                <option>High</option>
              </select>
            </label>

            <label>
              Project key (optional)
              <input
                type="text"
                value={projectKey}
                onChange={(e) => setProjectKey(e.target.value)}
                placeholder="DE, APP, CORE"
              />
            </label>

            <label>
              Labels (optional)
              <input
                type="text"
                value={labels}
                onChange={(e) => setLabels(e.target.value)}
                placeholder="backend, auth, validation"
              />
            </label>

            <div className="output-format">Output format: <strong>Jira markdown</strong></div>

            <div className="actions">
              <button type="submit" disabled={loading}>{loading ? 'Generating...' : 'Generate'}</button>
              <button type="button" onClick={clearForm}>Clear</button>
              <button type="button" onClick={runGeneration} disabled={loading}>Regenerate</button>
            </div>
          </form>
          {error && <p className="error">{error}</p>}
        </section>

        <section className="panel">
          <h2>Result</h2>
          <div className="tabs">
            <button className={tab === 'preview' ? 'active' : ''} onClick={() => setTab('preview')}>Preview</button>
            <button className={tab === 'markdown' ? 'active' : ''} onClick={() => setTab('markdown')}>Markdown</button>
            <button className={tab === 'json' ? 'active' : ''} onClick={() => setTab('json')}>JSON</button>
          </div>

          {!result && <p>No generated output yet.</p>}

          {result && (
            <>
              {tab === 'preview' && (
                <div className="preview">
                  <h3>{result.ticket.title}</h3>
                  <p><strong>Issue type:</strong> {result.ticket.issue_type} | <strong>Priority:</strong> {result.ticket.priority}</p>
                  {result.ticket.project_key && <p><strong>Project key:</strong> {result.ticket.project_key}</p>}
                  <h4>Description</h4>
                  <p><strong>Problem:</strong> {result.ticket.description.problem}</p>
                  <p><strong>Proposed solution:</strong> {result.ticket.description.proposed_solution}</p>
                  <p><strong>Notes:</strong> {result.ticket.description.notes}</p>
                  <h4>Acceptance criteria</h4>
                  <ul>{result.ticket.acceptance_criteria.map((x) => <li key={x}>{x}</li>)}</ul>
                  <h4>Definition of done</h4>
                  <ul>{result.ticket.definition_of_done.map((x) => <li key={x}>{x}</li>)}</ul>
                  <p><strong>Labels:</strong> {result.ticket.labels.join(', ')}</p>
                  <p><strong>Estimate:</strong> {result.ticket.estimate}</p>
                  <h4>Assumptions</h4>
                  <ul>{result.ticket.assumptions.map((x) => <li key={x}>{x}</li>)}</ul>
                </div>
              )}

              {tab === 'markdown' && <pre>{result.markdown}</pre>}
              {tab === 'json' && <pre>{JSON.stringify(result.ticket, null, 2)}</pre>}

              <div className="actions">
                <button onClick={() => navigator.clipboard.writeText(result.markdown)}>Copy Markdown</button>
                <button onClick={() => navigator.clipboard.writeText(JSON.stringify(result.ticket, null, 2))}>Copy JSON</button>
                <button onClick={() => downloadFile(result.markdown, 'jira-ticket.md', 'text/markdown')}>Download .md</button>
                <button onClick={() => downloadFile(JSON.stringify(result.ticket, null, 2), 'jira-ticket.json', 'application/json')}>Download .json</button>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  )
}
