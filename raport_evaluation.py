from agents import Agent, Runner
from evaluator_agent import EvaluationResult, evaluator_agent
from writer_agent import ReportData
from clarification_agent import EnrichedQuery

async def evaluate_report(
    original_query: str,
    report: ReportData,
    enriched_context: EnrichedQuery | None = None
) -> EvaluationResult:
    """
    Evaluate a research report for quality and completeness.

    Args:
        original_query: The original user query
        report: The generated research report
        enriched_context: Optional enriched query context from clarification

    Returns:
        EvaluationResult with scores, feedback, and recommendations
    """
    # Build evaluation input
    context_info = ""
    if enriched_context:
        focus_areas = "\n".join([f"  - {area}" for area in enriched_context.key_focus_areas])
        context_info = f"""
Enriched Context:
{enriched_context.enriched_context}

Key Focus Areas:
{focus_areas}

Clarification Q&A:
"""
        for qa in enriched_context.clarifying_qa:
            context_info += f"Q: {qa.question}\nA: {qa.answer}\n\n"

    evaluation_input = f"""Please evaluate the following research report.

Original Query: {original_query}

{context_info}

Research Report:
{report.markdown_report}

Short Summary: {report.short_summary}

Please provide a comprehensive evaluation with scores, feedback, and recommendations."""

    result = await Runner.run(
        evaluator_agent,
        evaluation_input,
    )

    return result.final_output_as(EvaluationResult)

async def evaluate_with_feedback(
    original_query: str,
    report: ReportData,
    enriched_context: EnrichedQuery | None = None
) -> tuple[EvaluationResult, str]:
    """
    Evaluate report and return both evaluation and formatted feedback.

    Args:
        original_query: The original user query
        report: The generated research report
        enriched_context: Optional enriched query context

    Returns:
        Tuple of (EvaluationResult, formatted_feedback_string)
    """
    evaluation = await evaluate_report(original_query, report, enriched_context)

    # Format feedback for display
    feedback = f"""## Report Evaluation

**Decision:** {evaluation.decision}
**Average Score:** {evaluation.scores.average_score:.1f}/10

### Scores
- Completeness: {evaluation.scores.completeness}/10
- Depth: {evaluation.scores.depth}/10
- Relevance: {evaluation.scores.relevance}/10
- Coverage: {evaluation.scores.coverage}/10
- Overall Quality: {evaluation.scores.overall_quality}/10

### Strengths
"""
    for strength in evaluation.strengths:
        feedback += f"- {strength}\n"

    if evaluation.gaps:
        feedback += "\n### Identified Gaps\n"
        for gap in evaluation.gaps:
            feedback += f"- {gap}\n"

    if evaluation.improvement_suggestions:
        feedback += "\n### Improvement Suggestions\n"
        for suggestion in evaluation.improvement_suggestions:
            feedback += f"- {suggestion}\n"

    if evaluation.suggested_searches:
        feedback += "\n### Suggested Additional Searches\n"
        for search in evaluation.suggested_searches:
            feedback += f"- {search}\n"

    feedback += f"\n### Overall Feedback\n{evaluation.overal_feedback_result}"

    return evaluation, feedback