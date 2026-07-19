---
title: 00Index
created: '2026-05-13'
tags: []
type: Concept
okf_spec: OKF-INCUBATOR
---

This is a collection of skills and agents that work in conjuction with a team of developers to manage large monorepos.

When CodeMage is introduced to a monorepo, it analyzes the entire source tree, change history, issues and specifications to develop a grounding understanding of the code base, how it is constructed and its operational goals.

CodeMage has the following operational modes:

- Onboarding :: in this mode, CodeMage will scan the code base and determine key design elements, architecture and flows. CodeMage will generate a series of specifications that captures what it has learned and generate a RAG of the codebase and its commit history
- Feature Development :: blah
- Test Development :: blah
- Software Architect :: blah
- Compliance Architect :: blah
- Designer :: blah

## Architecture

CodeMage can be run locally or on a dedicated server. There is a cloud component that can receive webhook events from CI/CD environments. 

CodeMage can also be run cooperatively. Multiple CodeMage instances can be clustered (leveraging user-space, private tailscale-like mesh-vpn networking) to allow different developers to manage their own instances. This allows common facts and decisions to be shared without.

Key Facts:
- Decentralized
- Mesh Networked :: Multiple instances of CodeMage will communicate with each other over shared project channels
- Embedded GIT :: run CodeMage standalone as a private GIT server; CodeMage will manage bare repos locally and use worktrees for interactive coding sessions
- Embedded Issue DB :: issues are tracked in a shared DB just like code; issueDB are either per-git repo or per-project collection
- Agentic :: embedded agents keep the project consistent over time and space and provide immedate feedback to human-in-the-loop interactions
- 