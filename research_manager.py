from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from clarification_agent import ClarificationQuestions, EnrichedQuery, QAPair, clarification_agent
from evaluator_agent import EvaluationResult, evaluator_agent
from query_utils import build_enriched_query_object
import asyncio

class ResearchManager:

    async def get_clarifying_questions(self, query: str) -> ClarificationQuestions:
        """ Generate clarifying questions for the user query """
        print("Generating clarifying questions...")
        result = await Runner.run(
            clarification_agent,
            f"Research query: {query}"
        )
        questions = result.final_output_as(ClarificationQuestions)
        print(f"Generated {len(questions.questions)} clarifying questions")
        return questions

    async def run(self, query: str, questions: ClarificationQuestions, user_answers: list[str]):
        """ Run the deep research process, yielding the status updates and the final report"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"

            # Build QAPair objects from questions and answers
            qa_pairs = [
                QAPair(question=q.question, answer=ans)
                for q, ans in zip(questions.questions, user_answers)
            ]

            print("Enriching query with user answers...")
            yield "Enriching query with clarification answers..."
            # Use utility to build enriched query (no AI needed)
            enriched = build_enriched_query_object(query, qa_pairs)

            print(f"Research focus areas: {enriched.key_focus_areas}")
            yield f"Research focus identified: {', '.join(enriched.key_focus_areas)}"
            
            print("Planning searches based on enriched context...")
            yield "Planning targeted searches..."
            print(f"enriched.context: {enriched.enriched_context}")
            search_plan = await self.plan_searches(enriched.enriched_context)

            yield "Searches planned, starting to search..."
            search_results = await self.perform_searches(search_plan)

            yield "Searches complete, writing report..."
            report = await self.write_report(enriched.enriched_context, search_results)

            yield "Creating raport completed, evaluating quality..."
            evaluation, feedback = await self.evaluate_report_quality(query, report, enriched)

            yield f"Evaluation complete: {evaluation.decision} (Score: {evaluation.scores.average_score:.1f}/10)"
            yield feedback

            if evaluation.is_approved:
                yield "Report approved! Sending email..."
                await self.send_email(report)
                yield "Email sent, research complete"
            else:
                yield f"Report needs improvement (Score: {evaluation.scores.average_score:.1f}/10). Review feedback above."

            yield report.markdown_report
        

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """ Plan the searches to perform for the query """
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """ Perform the searches to perform for the query """
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """ Perform a search for the query """
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """ Write the report for the query """
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing report")
        return result.final_output_as(ReportData)
    
    async def send_email(self, report: ReportData) -> None:
        print("Writing email...")
        result = await Runner.run(
            email_agent,
            report.markdown_report,
        )
        print("Email sent")
        return report
    
    async def evaluate_report_quality(
        self,
        query: str,
        report: ReportData,
        enriched: EnrichedQuery | None = None
    ) -> tuple[EvaluationResult, str]:
        """ Evaluate a research report and return evaluation with feedback """
        print("Evaluating report quality...")

        # Build evaluation input
        context_info = ""
        if enriched:
            context_info = f"\nEnriched Context:\n{enriched.enriched_context}\n"
            context_info += f"Key Focus Areas: {', '.join(enriched.key_focus_areas)}\n"

        evaluation_input = f"""Please evaluate the following research report.

Original Query: {query}
{context_info}
Research Report:
{report.markdown_report}

Please provide a comprehensive evaluation with scores, feedback, and recommendations."""

        result = await Runner.run(
            evaluator_agent,
            evaluation_input
        )

        evaluation = result.final_output_as(EvaluationResult)

        # Format feedback string
        feedback = f"""Evaluation: {evaluation.decision}
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
            feedback += f"+ {s}\n"

        if evaluation.gaps:
            feedback += "\nGaps:\n"
            for g in evaluation.gaps:
                feedback += f"- {g}\n"

        if evaluation.improvement_suggestions:
            feedback += "\nImprovement Suggestions:\n"
            for suggestion in evaluation.improvement_suggestions:
                feedback += f"-> {suggestion}\n"

        if evaluation.suggested_searches:
            feedback += "\nSuggested Additional Searches:\n"
            for search in evaluation.suggested_searches:
                feedback += f"* {search}\n"

        feedback += f"\nOverall Feedback: {evaluation.overal_feedback_result}"

        print(f"Evaluation: {evaluation.decision} (Score: {evaluation.scores.average_score:.1f}/10)")
        return evaluation, feedback