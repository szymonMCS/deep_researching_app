# Changelog

All notable changes to the Deep Research project will be documented in this file.

## [Unreleased]

### Added - Commit 1: Question Refinement Agent (2025-11-17)

- **Clarification Agent** (`clarification_agent.py`): New AI agent that generates 3 targeted clarifying questions for any research query
  - Analyzes query ambiguity and focus areas
  - Provides reasoning for each question
  - Identifies research focus for better planning

- **Query Enrichment Module** (`query_enrichment.py`): Processes clarifying questions and user answers
  - `generate_clarifying_questions()`: Generates 3 clarifying questions
  - `enrich_query_with_answers()`: Synthesizes Q&A into enriched context
  - `process_clarification_flow()`: Complete end-to-end clarification workflow

- **Enhanced Research Manager**:
  - `get_clarifying_questions()`: Method to generate questions for a query
  - `run_with_clarification()`: Run research with enriched context from clarifications
  - Maintains backward compatibility with original `run()` method

- **Improved Gradio UI**:
  - Two-tab interface: "Standard Research" and "Research with Clarification"
  - Interactive clarification workflow:
    1. User enters query
    2. AI generates 3 clarifying questions
    3. User answers questions
    4. Enhanced research runs with enriched context
  - Real-time display of research focus areas
  - State management for question-answer pairs

- **Testing Tools**:
  - `test_clarification.py`: Test script demonstrating the complete clarification flow

### Benefits

- **Better Results**: Clarifying questions help narrow research focus and gather crucial context
- **Targeted Searches**: Enriched context leads to more relevant search queries
- **User Control**: Users can choose between quick research or enhanced clarification-based research
- **Flexibility**: Backward compatible - existing functionality remains unchanged

### Technical Details

- Uses Pydantic models for structured outputs (`ClarificationQuestions`, `EnrichedQuery`)
- Leverages OpenAI Agents SDK for agent orchestration
- Question generation uses `gpt-4o-mini` for cost efficiency
- Questions cached in-memory for seamless UI flow

### Cost Impact

- Additional cost: ~$0.01-0.03 per clarification (question generation + enrichment)
- Minimal overhead compared to web search costs ($2.50 per search)
