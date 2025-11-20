from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from query_enrichment import generate_clarifying_questions, enrich_query_with_answers
from clarification_agent import ClarificationQuestions, EnrichedQuery
from report_evaluation import evaluate_report, evaluate_with_feedback
from evaluator_agent import EvaluationResult
import asyncio

class ResearchManager:

    async def get_clarifying_questions(self, query: str) -> ClarificationQuestions:
        """ Generate clarifying questions for the user query """
        print("Generating clarifying questions...")
        questions = await generate_clarifying_questions(query)
        print(f"Generated {len(questions.questions)} clarifying questions")
        return questions

    async def evaluate_report_quality(
        self,
        query: str,
        report: ReportData,
        enriched: EnrichedQuery | None = None
    ) -> tuple[EvaluationResult, str]:
        """ Evaluate a research report and return evaluation with feedback """
        print("Evaluating report quality...")
        evaluation, feedback = await evaluate_with_feedback(query, report, enriched)
        print(f"Evaluation: {evaluation.decision} (Score: {evaluation.scores.average_score:.1f}/10)")
        return evaluation, feedback

    async def run_with_clarification(self, query: str, questions: ClarificationQuestions, user_answers: list[str]):
        """ Run the deep research process with clarification questions """
        trace_id = gen_trace_id()
        with trace("Research trace with clarification", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"

            print("Enriching query with user answers...")
            yield "Enriching query with clarification answers..."

            # Build Q&A pairs from actual questions
            qa_pairs = [
                {"question": q.question, "answer": ans}
                for q, ans in zip(questions.questions, user_answers)
            ]

            enriched = await enrich_query_with_answers(query, qa_pairs)

            print(f"Research focus areas: {enriched.key_focus_areas}")
            yield f"Research focus identified: {', '.join(enriched.key_focus_areas)}"

            print("Planning searches based on enriched context...")
            yield "Planning targeted searches..."
            search_plan = await self.plan_searches(enriched.enriched_context)

            yield "Searches planned, starting to search..."
            search_results = await self.perform_searches(search_plan)

            yield "Searches complete, writing comprehensive report..."
            report = await self.write_report(enriched.enriched_context, search_results)

            yield "Report written, evaluating quality..."
            evaluation, feedback = await evaluate_with_feedback(query, report, enriched)

            yield f"Evaluation complete: {evaluation.decision} (Score: {evaluation.scores.average_score:.1f}/10)"
            yield feedback

            if evaluation.is_approved:
                yield "Report approved! Sending email..."
                await self.send_email(report)
                yield "Email sent, research complete"
            else:
                yield f"Report needs improvement (Score: {evaluation.scores.average_score:.1f}/10). Review feedback above."

            yield report.markdown_report

    async def run(self, query: str):
        """ Run the deep research process, yielding the status updates and the final report"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Starting research...")
            search_plan = await self.plan_searches(query)
            yield "Searches planned, starting to search..."
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, search_results)

            yield "Report written, evaluating quality..."
            evaluation, feedback = await evaluate_with_feedback(query, report, None)

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