"""
ResearchManager V2 - Using agent tools instead of direct agent calls.

This version demonstrates how to use agent_tools for a more modular approach.
The original research_manager.py is kept for backward compatibility.
"""

from agents import Runner, trace, gen_trace_id
from agent_tools import (
    plan_research_searches,
    perform_web_search,
    write_research_report,
    evaluate_report_quality
)
from planner_agent import WebSearchPlan, WebSearchItem, planner_agent
from writer_agent import ReportData, writer_agent
from evaluator_agent import EvaluationResult, evaluator_agent
from raport_evaluation import evaluate_with_feedback
from query_enrichment import generate_clarifying_questions, enrich_query_with_answers
from clarification_agent import ClarificationQuestions, EnrichedQuery
from email_agent import email_agent
import asyncio


class ResearchManagerV2:
    """
    Version 2 of ResearchManager using agent tools.

    This version uses function_tool wrappers for better modularity
    and prepares for coordinator agent integration.
    """

    async def get_clarifying_questions(self, query: str) -> ClarificationQuestions:
        """Generate clarifying questions for the user query"""
        print("Generating clarifying questions...")
        questions = await generate_clarifying_questions(query)
        print(f"Generated {len(questions.questions)} clarifying questions")
        return questions

    async def run(self, query: str, questions: ClarificationQuestions, user_answers: list[str]):
        """Run the deep research process, yielding status updates and final report"""
        trace_id = gen_trace_id()
        with trace("Research trace V2 (using agent tools)", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"

            # Step 1: Enrich query
            print("Enriching query with user answers...")
            yield "Enriching query with clarification answers..."
            qa_pairs = [
                {"question": q.question, "answer": ans}
                for q, ans in zip(questions.questions, user_answers)
            ]
            enriched = await enrich_query_with_answers(query, qa_pairs)
            print(f"Research focus areas: {enriched.key_focus_areas}")
            yield f"Research focus identified: {', '.join(enriched.key_focus_areas)}"

            # Step 2: Plan searches using tool
            print("Planning searches using agent tool...")
            yield "Planning targeted searches..."
            # Note: We still use direct agent call here for structured output
            # But could be replaced with tool + parsing in coordinator
            search_plan = await self.plan_searches_direct(enriched.enriched_context)

            # Step 3: Perform searches
            yield "Searches planned, starting to search..."
            search_results = await self.perform_searches(search_plan)

            # Step 4: Write report using direct call (need structured ReportData)
            yield "Searches complete, writing report..."
            report = await self.write_report_direct(enriched.enriched_context, search_results)

            # Step 5: Evaluate using direct call (need structured EvaluationResult)
            yield "Creating report completed, evaluating quality..."
            evaluation, feedback = await evaluate_with_feedback(query, report, enriched)

            yield f"Evaluation complete: {evaluation.decision} (Score: {evaluation.scores.average_score:.1f}/10)"
            yield feedback

            # Step 6: Conditional email
            if evaluation.is_approved:
                yield "Report approved! Sending email..."
                await self.send_email(report)
                yield "Email sent, research complete"
            else:
                yield f"Report needs improvement (Score: {evaluation.scores.average_score:.1f}/10). Review feedback above."

            yield report.markdown_report

    async def plan_searches_direct(self, query: str) -> WebSearchPlan:
        """Plan searches using direct agent call (for structured output)"""
        print("Planning searches...")
        result = await Runner.run(planner_agent, f"Query: {query}")
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """Perform searches using agent tool"""
        print("Searching...")
        num_completed = 0
        tasks = [
            asyncio.create_task(self.search_with_tool(item))
            for item in search_plan.searches
        ]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search_with_tool(self, item: WebSearchItem) -> str | None:
        """Perform a single search using the agent tool"""
        try:
            # Use the function_tool wrapper
            result = await perform_web_search(item.query, item.reason)
            return result
        except Exception as e:
            print(f"Search error: {e}")
            return None

    async def write_report_direct(self, query: str, search_results: list[str]) -> ReportData:
        """Write report using direct agent call (for structured output)"""
        print("Thinking about report...")
        input_text = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(writer_agent, input_text)
        print("Finished writing report")
        return result.final_output_as(ReportData)

    async def send_email(self, report: ReportData) -> None:
        """Send email with the report"""
        print("Writing email...")
        result = await Runner.run(email_agent, report.markdown_report)
        print("Email sent")
        return report

    async def evaluate_report_quality(
        self,
        query: str,
        report: ReportData,
        enriched: EnrichedQuery | None = None
    ) -> tuple[EvaluationResult, str]:
        """Evaluate a research report and return evaluation with feedback"""
        print("Evaluating report quality...")
        evaluation, feedback = await evaluate_with_feedback(query, report, enriched)
        print(f"Evaluation: {evaluation.decision} (Score: {evaluation.scores.average_score:.1f}/10)")
        return evaluation, feedback
