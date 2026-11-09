# Portfolio AI Chatbot

## Overview
A RAG-powered conversational assistant being developed to answer visitor questions using curated information about Pavan's profile, education, experience, skills, and projects.

## Architecture
- Frontend: Next.js, React, TypeScript
- Backend: FastAPI
- LLM: Google Gemini (`gemini-3.5-flash-lite`) through the OpenAI-compatible Generative Language API endpoint
- Embeddings: Gemini Embedding 2
- Vector database: Qdrant Cloud
- Retrieval: semantic vector search with relevance-score filtering
- Knowledge sources: Markdown files in `knowledge/`

## Implemented elements
- FastAPI chat endpoint: `POST /api/chat`
- Health endpoints, including `/health/live`
- Chat launcher, panel, message rendering, suggested prompts, and input components
- Markdown-based knowledge ingestion, chunking, embedding, and Qdrant indexing
- 768-dimensional Gemini embeddings
- Client-side chat history; persistent conversation storage is not part of the current implementation

## Deployment direction
The main portfolio website is deployed on Vercel. The chatbot backend is planned for separate container hosting, and the chat interface is intended to be integrated into the main portfolio website.

## Current limitations
Backend deployment and final integration into the live portfolio are pending. Do not claim the chatbot is publicly available on the portfolio until integration is completed and verified. Do not claim persistent memory, user accounts, autonomous actions, or guaranteed factual correctness.
