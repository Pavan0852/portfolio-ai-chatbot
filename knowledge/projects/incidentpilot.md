# IncidentPilot AI

## Overview
IncidentPilot AI is a personal project exploring an AI-assisted workflow for incident triage, diagnosis, and resolution recommendations.

## Workflow
1. Accept an incident description.
2. Triage and classify the incident.
3. Analyse likely causes.
4. Generate suggested resolution steps.
5. Present the analysis through the application interface.

## Architecture and technology
- Backend: FastAPI
- Frontend: Next.js and React
- Language: Python
- Agent orchestration: LangGraph
- LLM application tooling: LangChain

## Engineering work
The project has included separate triage, diagnosis, and resolution workflow components, API integration, structured workflow state, validation, logging/error-handling considerations, and automated tests.

## Limitations
Recommendations require human review. Do not claim autonomous remediation, production-system changes, real-time streaming, guaranteed root-cause identification, or unverified performance metrics.
