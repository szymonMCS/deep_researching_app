"""
Agent Tools - Transform specialized agents into reusable function tools.

This module converts agents (planner, search, writer, evaluator) into function_tool
wrappers that can be used by other agents or the coordinator.
"""

from agents import function_tool, Runner
from planner_agent import planner_agent, WebSearchPlan
from search_agent import search_agent
from writer_agent import writer_agent, ReportData
from evaluator_agent import evaluator_agent, EvaluationResult
from clarification_agent import clarification_agent, ClarificationQuestions
from query_enrichment import enrich_query_with_answers
from clarification_agent import EnrichedQuery


@function_tool
async def generate_clarification_questions(query: str) -> str:
    """
    Generate 3 clarifying questions for a research query.

    Args:
        query: The original research query to clarify

    Returns:
        JSON string with questions and research focus
    """
    result = await Runner.run(
        clarification_agent,
        f"Research query: {query}"
    )

    questions = result.final_output_as(ClarificationQuestions)

    # Format as readable string for agent consumption
    output = f"Research Focus: {questions.research_focus}\n\nQuestions:\n"
    for i, q in enumerate(questions.questions, 1):
        output += f"{i}. {q.question}\n   Reasoning: {q.reasoning}\n"

    return output


@function_tool
async def enrich_query_context(original_query: str, qa_pairs_json: str) -> str:
    """
    Enrich a query with clarification Q&A pairs.

    Args:
        original_query: The original user query
        qa_pairs_json: JSON string of Q&A pairs [{"question": "...", "answer": "..."}, ...]

    Returns:
        Enriched research context with key focus areas
    """
    import json

    qa_pairs = json.loads(qa_pairs_json)
    enriched = await enrich_query_with_answers(original_query, qa_pairs)

    output = f"""Enriched Research Context:
{enriched.enriched_context}

Key Focus Areas:
"""
    for area in enriched.key_focus_areas:
        output += f"- {area}\n"

    output += f"\nSuggested Scope: {enriched.suggested_scope}"

    return output


@function_tool
async def plan_research_searches(query: str) -> str:
    """
    Plan web searches for a research query.

    Args:
        query: The research query or enriched context to plan searches for

    Returns:
        JSON string with planned searches and reasoning
    """
    result = await Runner.run(
        planner_agent,
        f"Query: {query}"
    )

    plan = result.final_output_as(WebSearchPlan)

    # Format as readable string
    output = f"Planned {len(plan.searches)} searches:\n\n"
    for i, item in enumerate(plan.searches, 1):
        output += f"{i}. Search: \"{item.query}\"\n"
        output += f"   Reason: {item.reason}\n\n"

    return output


@function_tool
async def perform_web_search(search_term: str, reason: str) -> str:
    """
    Perform a single web search and summarize results.

    Args:
        search_term: The search query to execute
        reason: Why this search is important (for context)

    Returns:
        Concise summary of search results (2-3 paragraphs, <300 words)
    """
    input_text = f"Search term: {search_term}\nReason for searching: {reason}"

    try:
        result = await Runner.run(
            search_agent,
            input_text
        )
        return str(result.final_output)
    except Exception as e:
        return f"Search failed: {str(e)}"


@function_tool
async def write_research_report(query: str, search_results: str) -> str:
    """
    Write a comprehensive research report from search results.

    Args:
        query: The original research query or enriched context
        search_results: Summarized search results (concatenated)

    Returns:
        Detailed markdown report (1000+ words) with summary
    """
    input_text = f"Original query: {query}\nSummarized search results: {search_results}"

    result = await Runner.run(
        writer_agent,
        input_text
    )

    report = result.final_output_as(ReportData)

    output = f"""Short Summary: {report.short_summary}

Follow-up Questions:
"""
    for q in report.follow_up_questions:
        output += f"- {q}\n"

    output += f"\n---\n\n{report.markdown_report}"

    return output


@function_tool
async def evaluate_report_quality(
    original_query: str,
    report: str,
    enriched_context: str = ""
) -> str:
    """
    Evaluate the quality of a research report.

    Args:
        original_query: The original user query
        report: The generated research report to evaluate
        enriched_context: Optional enriched query context (if available)

    Returns:
        Evaluation with scores, decision, and feedback
    """
    # Build evaluation input
    context_info = ""
    if enriched_context:
        context_info = f"\nEnriched Context:\n{enriched_context}\n"

    evaluation_input = f"""Please evaluate the following research report.

Original Query: {original_query}
{context_info}
Research Report:
{report}

Please provide a comprehensive evaluation with scores, feedback, and recommendations."""

    result = await Runner.run(
        evaluator_agent,
        evaluation_input
    )

    evaluation = result.final_output_as(EvaluationResult)

    # Format evaluation as readable string
    output = f"""Decision: {evaluation.decision}
Average Score: {evaluation.scores.average_score:.1f}/10

Scores:
- Completeness: {evaluation.scores.completeness}/10
- Depth: {evaluation.scores.depth}/10
- Relevance: {evaluation.scores.relevance}/10
- Coverage: {evaluation.scores.coverage}/10
- Overall Quality: {evaluation.scores.overall_quality}/10

Strengths:
"""
    for s in evaluation.strengths:
        output += f"+ {s}\n"

    if evaluation.gaps:
        output += "\nGaps:\n"
        for g in evaluation.gaps:
            output += f"- {g}\n"

    if evaluation.improvement_suggestions:
        output += "\nImprovement Suggestions:\n"
        for suggestion in evaluation.improvement_suggestions:
            output += f"→ {suggestion}\n"

    if evaluation.suggested_searches:
        output += "\nSuggested Additional Searches:\n"
        for search in evaluation.suggested_searches:
            output += f"🔍 {search}\n"

    output += f"\nOverall Feedback: {evaluation.overal_feedback_result}"

    return output


# Export all tools as a list for easy registration
AGENT_TOOLS = [
    generate_clarification_questions,
    enrich_query_context,
    plan_research_searches,
    perform_web_search,
    write_research_report,
    evaluate_report_quality,
]
