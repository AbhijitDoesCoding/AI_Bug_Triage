# AI Bug Triage & Release Operator

## Project Goal
An agentic application on Lemma that takes unstructured bug reports from support
channels, structures them into a database (catching duplicates), and automates
release-note drafting with a human-in-the-loop approval step.

## Architecture

### Tables
- `bugs` — Structured bug tickets. Business columns: `title`, `priority`
  (Low/Medium/High), `component` (Auth/Billing/UI/API/Data/Performance/Other),
  `raw_complaint`, `repro_steps`, `triage_reasoning`, `reporter`, `duplicate_of`,
  `status` (Open/In_Progress/Fixed), `release_note`, `release_notes_approved`.
  System columns `id`, `created_at`, `updated_at` are added automatically.
  Shared table (`enable_rls: false`) — the whole team sees every bug.

### Agents
- `triage_agent` — Conversational. Parses an unstructured report, **checks the table
  for duplicates first**, then assigns priority + component with a written reason and
  inserts a structured row. String in / string out (a chat agent).
- `release_writer` — Typed. Given a `bug_id`, reads the row and drafts a concise,
  user-facing release note. Has an `output_schema` (`{ release_note }`) so the
  workflow can consume it reliably. Read-only.

### Functions
- `save_release_note` — Deterministic write-back: stores the approved note on the bug
  and sets `release_notes_approved = true`.

### Schedules (triggers)
- `release-notes-trigger` — a `DATASTORE` schedule on `bugs` (operation `UPDATE`) that
  starts the `release-notes` workflow. A workflow's `DATASTORE_EVENT` start only
  declares the expected shape; **this schedule is the actual tripwire** that subscribes
  to the table. Without it, the workflow never fires.

### Workflows
- `release-notes` — Started by `release-notes-trigger` on every `UPDATE` to `bugs`.
  Guard → draft → approve → save:
  1. `check_fixed` (DECISION): proceed only when `status == 'Fixed'` **and**
     `release_notes_approved != true`. The second clause is the **re-entry guard** —
     it stops the workflow from re-firing on its own write-back.
  2. `draft_note` (AGENT → `release_writer`): drafts the note. Reads the changed row's
     id from `start.metadata.record_id` (NOT `start.payload.id`, which is null for
     datastore triggers).
  3. `approval` (FORM): human reviews; the drafted note is pre-filled and editable.
  4. `approve_route` (DECISION): approved → save; otherwise → end.
  5. `save_note` (FUNCTION → `save_release_note`): persists the approved note.

## Build / import order (Lemma dependency rule)
tables → functions → agents → workflows → schedules. Validate each layer, then the next:
```bash
lemma pods import . --dry-run        # validate the whole bundle without writing
lemma pods import .                  # apply
```

## Stack
- **Platform:** Lemma (local-first, AI-native infrastructure)
- **Format:** Plain JSON config files in a pod bundle (`.toml` files are
  human-readable mirrors; the JSON is authoritative)
- **Auth:** `lemma auth login` (browser-based)

## Roadmap (not yet built)
- **Ingress surface** — a Slack surface or a webhook-triggered workflow so real
  messages flow straight into triage.
- **Dashboard app** — a live view of open bugs by priority/component, the status
  funnel, and the release-note approval queue.
- **Seed data** — a set of realistic sample reports (including a duplicate) to make
  the demo run itself.
