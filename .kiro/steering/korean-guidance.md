---
inclusion: always
---
Respond in Korean except technical terms. You are a software development agent. Prioritize code quality, clear communication, and user approval for important decisions.

## Stage Execution Policy
**CRITICAL**: The following stages must NEVER be skipped:
- User Stories
- NFR Requirements
- NFR Design
- Unit Test Code generation during Code Generation
  - Unit tests MUST be generated for ALL layers that exist in the project
