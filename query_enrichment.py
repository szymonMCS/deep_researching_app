"""
Module for enriching user queries with clarifying questions and answers.
This helps create better research context for downstream agents.
"""

from agents import Agent, Runner
from clarification_agent import ClarificationQuestions, EnrichedQuery

ENRICHMENT_INSTRUCTIONS = """You are a research context synthesizer.

Given:
- An original research query
- A set of clarifying questions and user answers

Your task is to:
1. Synthesize all information into a comprehensive research brief
2. Identify key focus areas based on the clarifications
3. Determine appropriate research scope

The enriched context should be detailed enough to guide search planning and report writing,
incorporating all nuances from the user's answers."""


enrichment_agent = Agent(
    name="QueryEnrichmentAgent",
    instructions=ENRICHMENT_INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=EnrichedQuery,
)


async def generate_clarifying_questions(query: str) -> ClarificationQuestions:
    """
    Generate 3 clarifying questions for a given research query.

    Args:
        query: The original user research query

    Returns:
        ClarificationQuestions object with 3 questions and reasoning
    """
    from clarification_agent import clarification_agent

    result = await Runner.run(
        clarification_agent,
        f"Research query: {query}",
    )

    return result.final_output_as(ClarificationQuestions)


async def enrich_query_with_answers(
    original_query: str,
    qa_pairs: list[dict[str, str]]
) -> EnrichedQuery:
    """
    Enrich the original query with clarifying Q&A pairs.

    Args:
        original_query: The original user query
        qa_pairs: List of dicts with 'question' and 'answer' keys

    Returns:
        EnrichedQuery with comprehensive research context
    """
    qa_text = "\n\n".join([
        f"Q: {qa['question']}\nA: {qa['answer']}"
        for qa in qa_pairs
    ])

    input_text = f"""Original Query: {original_query}

Clarifying Questions and Answers:
{qa_text}

Please synthesize this into a comprehensive research brief."""

    result = await Runner.run(
        enrichment_agent,
        input_text,
    )

    enriched = result.final_output_as(EnrichedQuery)

    # Ensure original data is preserved
    enriched.original_query = original_query
    enriched.clarifying_qa = qa_pairs

    return enriched


async def process_clarification_flow(
    query: str,
    user_answers: list[str]
) -> EnrichedQuery:
    """
    Complete clarification flow: generate questions and process answers.

    Args:
        query: Original user query
        user_answers: List of 3 user answers to the generated questions

    Returns:
        EnrichedQuery with full context
    """
    # Generate questions
    questions_result = await generate_clarifying_questions(query)

    # Build Q&A pairs
    qa_pairs = [
        {
            "question": q.question,
            "answer": a
        }
        for q, a in zip(questions_result.questions, user_answers)
    ]

    # Enrich query
    return await enrich_query_with_answers(query, qa_pairs)
