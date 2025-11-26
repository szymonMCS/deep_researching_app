"""
Query utilities - Pure Python helpers for query processing.

No AI agents needed - just simple string formatting and data manipulation.
"""

from clarification_agent import QAPair, EnrichedQuery


def format_enriched_query(
    original_query: str,
    qa_pairs: list[QAPair]
) -> str:
    """
    Format original query with Q&A pairs into enriched context string.

    This is pure string formatting - no AI inference needed.

    Args:
        original_query: The original user query
        qa_pairs: List of question-answer pairs from clarification

    Returns:
        Formatted string combining query and clarifications
    """
    enriched = f"Original Query: {original_query}\n\n"
    enriched += "Clarification Context:\n"

    for i, qa in enumerate(qa_pairs, 1):
        enriched += f"\nQ{i}: {qa.question}\n"
        enriched += f"A{i}: {qa.answer}\n"

    enriched += "\nPlease conduct research addressing the original query with the above clarifications in mind."

    return enriched


def extract_key_focus_areas(qa_pairs: list[QAPair]) -> list[str]:
    """
    Extract key focus areas from Q&A pairs.

    Simple extraction based on answer keywords and structure.

    Args:
        qa_pairs: List of question-answer pairs

    Returns:
        List of 3-5 key focus areas
    """
    focus_areas = []

    for qa in qa_pairs:
        # Take first sentence or up to 100 chars from each answer
        answer_summary = qa.answer.split('.')[0][:100]
        if answer_summary:
            focus_areas.append(answer_summary.strip())

    # Limit to 5 areas
    return focus_areas[:5]


def determine_research_scope(qa_pairs: list[QAPair]) -> str:
    """
    Determine research scope based on answer lengths and complexity.

    Args:
        qa_pairs: List of question-answer pairs

    Returns:
        Scope string: "broad", "medium", or "narrow"
    """
    total_length = sum(len(qa.answer) for qa in qa_pairs)
    avg_length = total_length / len(qa_pairs) if qa_pairs else 0

    if avg_length > 200:
        return "broad"
    elif avg_length > 100:
        return "medium"
    else:
        return "narrow"


def build_enriched_query_object(
    original_query: str,
    qa_pairs: list[QAPair]
) -> EnrichedQuery:
    """
    Build complete EnrichedQuery object from original query and Q&A pairs.

    Combines all utility functions to create structured output.

    Args:
        original_query: The original user query
        qa_pairs: List of question-answer pairs

    Returns:
        EnrichedQuery object with all fields populated
    """
    return EnrichedQuery(
        original_query=original_query,
        clarifying_qa=qa_pairs,
        enriched_context=format_enriched_query(original_query, qa_pairs),
        key_focus_areas=extract_key_focus_areas(qa_pairs),
        suggested_scope=determine_research_scope(qa_pairs)
    )
