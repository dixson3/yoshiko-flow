---
title: CodeMage
created: 2026-05-13
tags:
- incubator
- agents
- monorepo
- dev-tools
- mesh
status: incubating
last_reviewed: 2026-05-17
priority: normal
aliases:
- codemage
- CodeMage
type: Incubator
okf_spec: OKF-INCUBATOR
---

## Resume

- **Last reviewed**: 2026-05-17
- **State**: Concept + onboarding-agent spec drafted. Marketecture diagram exists. No code.
- **Next action**: Validate the three-pass onboarding-agent flow against a small real repo.
- **Open threads**:
  - Six operational modes — only Onboarding is specified; Feature Development / Test Development / Software Architect / Compliance Architect / Designer are placeholders.
  - Mesh networking model for multi-instance cooperation needs concrete protocol/transport.
  - Embedded GIT + IssueDB choices (Dolt? beads?).
- **Context to reload**: [00Index.md](00Index.md) (concept + modes), [Onboarding.md](Onboarding.md) (agent spec), `codemage marketecture.excalidraw`.

## Status

Specification phase. Onboarding agent fully specified (three-pass micro→macro→generation); other operational modes are named but unspecified.

## Premise

A collection of skills and agents that work in conjunction with a team of developers to manage large monorepos. When introduced to a monorepo, CodeMage analyzes the entire source tree, change history, issues, and specifications to develop a grounding understanding of the code base, how it is constructed, and its operational goals.

### Operational modes
- **Onboarding** — scans the codebase, determines key design elements / architecture / flows, generates specifications, builds a RAG of code + commit history. (Spec: [Onboarding.md](Onboarding.md).)
- **Feature Development**
- **Test Development**
- **Software Architect**
- **Compliance Architect**
- **Designer**

### Architecture

CodeMage can be run locally or on a dedicated server. There is a cloud component that can receive webhook events from CI/CD environments.

CodeMage can also be run cooperatively. Multiple CodeMage instances can be clustered (leveraging user-space, private tailscale-like mesh-VPN networking) to allow different developers to manage their own instances. Common facts and decisions are shared across the mesh.

**Key facts:**
- Decentralized
- Mesh networked — multiple instances communicate over shared project channels
- Embedded GIT — run CodeMage standalone as a private Git server; manages bare repos locally and uses worktrees for interactive coding sessions
- Embedded issue DB — issues are tracked in a shared DB just like code; either per-Git-repo or per-project collection
- Agentic — embedded agents keep the project consistent over time and space and provide immediate feedback to human-in-the-loop interactions

## Open questions

1. Specify the remaining five operational modes — what does each agent take in / produce?
2. Mesh transport: real tailscale, native userspace WireGuard, or just authenticated WebSockets?
3. Issue DB: Dolt, beads, sqlite, something else?

## Decision log

## Files

- `README.md` — this state file
- [00Index.md](00Index.md) — concept + operational-mode overview
- [Onboarding.md](Onboarding.md) — full Onboarding-agent specification (three-pass model, sub-agent prompts, config)
- `codemage marketecture.excalidraw` — architecture diagram

## Beads to file

- Specify Feature Development mode
- Specify Test Development mode
- Specify Software Architect mode
- Specify Compliance Architect mode
- Specify Designer mode
- Decide mesh transport
- Decide issue DB
