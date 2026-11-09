# AI Research Scout

## Overview
AI Research Scout is a research-discovery and digest project designed to explore recent AI papers and turn paper metadata and abstracts into structured summaries and insights.

## Workflow
1. Collect relevant paper information from arXiv.
2. Retrieve metadata and abstracts.
3. Analyse the material with an LLM.
4. Produce structured insights and a research digest.

## Technology
- Python
- arXiv Python client
- OpenRouter model access
- Google Gemini explored in the model-provider context
- LangChain and LangGraph for LLM application/workflow components where used
- Next.js for the web-facing interface

## Code areas mentioned
- `arxiv_collector.py`
- `feed_manager.py`
- `research_analyst.py`
- `digest_generator.py`

The project has used YAML configuration to represent research interests. Do not claim exhaustive paper coverage, peer-reviewed research contributions, publications, validated scientific conclusions, or unverified metrics.
