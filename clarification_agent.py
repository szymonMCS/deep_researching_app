from pydantic import BaseModel, Field
from agents import Agent

INSTRUCTIONS = """You are a research clarification specialist. Your job is to understand the user's research query deeply by asking precise, targeted follow-up questions.

Given an initial research query, you must:
1. Analyze what aspects of the query might be ambiguous or could benefit from clarification
2. Generate EXACTLY 3 follow-up questions that will help gather crucial context
3. Focus on: scope, target audience, specific aspects of interest, time frame, or depth of analysis needed

Your questions should be:
- Specific and actionable
- Designed to narrow down the research focus
- Helpful for planning better searches
- Not too technical or overwhelming

Example:
Query: "AI agents in 2025"
Questions might ask about: specific use cases, industries of interest, technical depth required, etc.
"""


class ClarifyingQuestion(BaseModel):
    question: str = Field(description="A clarifying question to ask the user")
    reasoning: str = Field(description="Why this question is important for the research")


class ClarificationQuestions(BaseModel):
    questions: list[ClarifyingQuestion] = Field(
        description="Exactly 3 clarifying questions to ask the user",
        min_length=3,
        max_length=3
    )
    research_focus: str = Field(
        description="A brief summary of what aspects need clarification"
    )


class EnrichedQuery(BaseModel):
    original_query: str = Field(description="The original user query")
    clarifying_qa: list[dict[str, str]] = Field(
        description="List of Q&A pairs from clarification. Each dict has 'question' and 'answer' keys"
    )
    enriched_context: str = Field(
        description="A comprehensive research brief combining the original query with answers to clarifying questions"
    )
    key_focus_areas: list[str] = Field(
        description="3-5 key focus areas identified from the clarification process"
    )
    suggested_scope: str = Field(
        description="Suggested scope for the research (broad/medium/narrow)"
    )


clarification_agent = Agent(
    name="ClarificationAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ClarificationQuestions,
)
