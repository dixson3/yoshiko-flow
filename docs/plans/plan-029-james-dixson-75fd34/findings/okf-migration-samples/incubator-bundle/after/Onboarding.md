---
title: Onboarding Agent Specification
created: '2026-05-13'
tags: []
type: Concept
okf_spec: OKF-INCUBATOR
---

# Onboarding Agent Specification

## Overview

| Property     | Value                                                                  |
| ------------ | ---------------------------------------------------------------------- |
| **Agent ID** | `onboarding`                                                           |
| **Role**     | System Architect / Code Analyst                                        |
| **Purpose**  | Reverse-engineer repositories to produce human-readable specifications |
| **Output**   | Effective Specification Document                                       |

## Description

The Onboarding Agent analyzes codebases to generate an "effective specification"—a comprehensive document detailing purpose, architecture, and core functionality. It enables rapid developer onboarding, architectural reviews, and foundational system understanding.

## Capabilities

- Multi-file parallel analysis
- Dependency graph generation (MermaidJS)
- Architectural pattern recognition
- Technology stack identification
- Component relationship mapping

## Execution Model

The agent operates via a three-pass protocol, progressing from granular file analysis to holistic system synthesis.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Pass 1        │───▶│   Pass 2         │───▶│   Pass 3        │
│   Micro-Analysis│    │   Macro-Synthesis│    │   Generation    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
     N sub-agents           1 consolidator        1 writer
```

## Pass Definitions

### Pass 1: Micro-Analysis

**Objective:** Dissect the codebase at file level.

**Execution:** Spawn parallel sub-agents, one per source file.

**Per-File Output Schema:**

```yaml
file: string           # relative path
summary: string        # one-sentence purpose
dependencies: string[] # imported modules/files
exports: string[]      # public API surface
logic: string          # core algorithms/business rules
```

**Storage:** Cache results to `mage-runtime/`

---

### Pass 2: Macro-Synthesis

**Objective:** Synthesize holistic repository understanding from cached file analyses.

**Execution:** Single consolidation agent.

**Responsibilities:**

- Pattern and connection identification
- Key component ranking with role explanations
- Architectural classification (Monolith, Microservices, MVC, Layered, etc.)
- Technology inventory (languages, frameworks, libraries)
- Dependency graph generation

**Output Schema:**

```yaml
architecture: string
technologies:
  languages: string[]
  frameworks: string[]
  libraries: string[]
components:
  - path: string
    role: string
    importance: high | medium | low
dependency_graph: string  # MermaidJS format
```

---

### Pass 3: Specification Generation

**Objective:** Compile final specification document.

**Execution:** Single writer agent.

**Document Structure:**

1. **Executive Summary** — Purpose, stack, architecture
2. **Component Breakdown** — Roles and interactions
3. **Dependency Graph** — Visual relationship map
4. **Appendix** — Raw analysis data (optional)

**Storage:** Persist to `mage-repoinfo/`

## Sub-Agent Prompts

### File Analyzer (Pass 1)

```
You are a code analysis agent. Perform a deep dive on the provided source file.

For `{{filename}}`, extract:
1. **Summary**: One-sentence purpose
2. **Dependencies**: All imports/includes
3. **Exports**: Public functions, classes, variables, types
4. **Key Logic**: Core algorithms or business rules

Output as YAML.
```

### Dependency Mapper (Pass 2)

```
You are a dependency analysis tool. Map relationships between code files.

Generate a MermaidJS `graph TD` dependency graph:
- Each file = one node
- Arrow `A --> B` = A imports/depends on B
- Include only direct, explicit imports

Output the graph code block only.
```

### Specification Writer (Pass 3)

```
You are a senior software architect. Generate a high-level specification from the provided analysis.

Cover:
1. **Primary Purpose**: Library, service, CLI, or other
2. **Core Technologies**: Languages, frameworks, key libraries
3. **Architecture**: Pattern classification with rationale
4. **Key Components**: Critical directories/files with roles

Output as markdown.
```

## Configuration

| Parameter             | Type     | Default                       | Description                     |
| --------------------- | -------- | ----------------------------- | ------------------------------- |
| `max_parallel_agents` | int      | 10                            | Max concurrent file analyzers   |
| `include_patterns`    | string[] | `["**/*.py", "**/*.ts", ...]` | Files to analyze                |
| `exclude_patterns`    | string[] | `["**/node_modules/**", ...]` | Files to skip                   |
| `output_format`       | string   | `markdown`                    | Spec format: `markdown`, `json` |
| `graph_format`        | string   | `mermaid`                     | Graph syntax: `mermaid`, `dot`  |

## Storage Locations

| Cache            | Purpose                       | Lifecycle           |
| ---------------- | ----------------------------- | ------------------- |
| `mage-runtime/`  | Intermediate analysis results | Ephemeral (per-run) |
| `mage-repoinfo/` | Final specifications          | Persistent          |

## Usage

```bash
mage onboard <repo-path> [--output spec.md] [--format markdown]
```

## Dependencies

- File system access (read)
- Sub-agent orchestration capability
- MermaidJS renderer (optional, for graph visualization)
