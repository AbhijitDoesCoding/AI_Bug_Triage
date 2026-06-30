# AI Bug Triage & Release Operator

## Project Goal
An agentic application on Lemma that takes unstructured bug reports from support channels, structures them into a database, and automates release note drafting.

## Architecture

### Tables
- `bugs` — Structured bug tickets with columns: id, title, priority, raw_complaint, repro_steps, status

### Agents
- `triage_agent` — Parses unstructured reports, creates bug records, drafts release notes

### Workflows
- `release-notes` — Triggered on UPDATE to `bugs` table; when status changes to `Fixed`, drafts a release note and pauses for human approval

## Stack
- **Platform:** Lemma (local-first AI-native infrastructure)
- **Format:** Plain JSON configuration files in a pod bundle
- **Auth:** Lemma CLI with email-based authentication
