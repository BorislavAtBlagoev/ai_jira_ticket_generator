import { Link, useNavigate } from 'react-router-dom'

const example = {
  ticket_details:
    'Users report intermittent 500 errors when submitting the account settings form. It happens mostly when the profile includes a new phone number. We need to stabilize submission, improve validation feedback, and ensure proper logging for failures.',
  issue_type: 'Bug',
  priority: 'High',
  project_key: 'APP',
  labels: 'backend, validation, settings'
}

export default function HelpPage() {
  const navigate = useNavigate()

  const useExample = () => {
    const params = new URLSearchParams(example)
    navigate(`/?${params.toString()}`)
  }

  return (
    <div className="page">
      <header>
        <h1>Help</h1>
        <p>How to use the AI Jira Ticket Generator.</p>
        <Link to="/">Back to generator</Link>
      </header>

      <section className="panel">
        <h2>Input fields</h2>
        <ul>
          <li><strong>Ticket details:</strong> Describe the request, problem, expected behavior, and context.</li>
          <li><strong>Issue type:</strong> Choose Bug, Task, or Story.</li>
          <li><strong>Priority:</strong> Choose Low, Medium, or High urgency.</li>
          <li><strong>Project key (optional):</strong> Jira project prefix such as APP or CORE.</li>
          <li><strong>Labels (optional):</strong> Comma-separated labels you want to enforce.</li>
          <li><strong>Output format:</strong> Jira markdown (fixed).</li>
        </ul>
      </section>

      <section className="panel">
        <h2>Example input</h2>
        <p><strong>Ticket details</strong></p>
        <pre>{example.ticket_details}</pre>
        <p><strong>Issue type:</strong> {example.issue_type}</p>
        <p><strong>Priority:</strong> {example.priority}</p>
        <p><strong>Project key:</strong> {example.project_key}</p>
        <p><strong>Labels:</strong> {example.labels}</p>
        <button onClick={useExample}>Use example</button>
      </section>

      <section className="panel">
        <h2>Output snippet</h2>
        <pre>{`# Stabilize account settings submission errors

- **Issue type:** Bug
- **Priority:** High
- **Project key:** APP

## Acceptance criteria
- Given a valid phone number, when the user saves settings, then the request succeeds without 500 errors.`}</pre>
      </section>
    </div>
  )
}
