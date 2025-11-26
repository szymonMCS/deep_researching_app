"""
Coordinator Workflow - Manages research workflow using Coordinator Agent.

This replaces the imperative ResearchManager with an autonomous Coordinator Agent
that delegates to specialists via handoffs, while maintaining streaming updates for the UI.
"""

from agents import Runner, trace, gen_trace_id
from coordinator_agent import coordinator_agent
from clarification_agent import ClarificationQuestions, EnrichedQuery, QAPair, clarification_agent
from query_utils import build_enriched_query_object
from writer_agent import ReportData
from evaluator_agent import EvaluationResult
import json
import re


class CoordinatorWorkflow:
    """
    Workflow manager using Coordinator Agent with handoffs.

    Maintains backward-compatible interface with ResearchManager for UI,
    but internally uses autonomous Coordinator Agent with specialist delegation.
    """

    async def get_clarifying_questions(self, query: str) -> ClarificationQuestions:
        """Generate clarifying questions for the user query"""
        print("Coordinator: Delegating to clarification specialist...")

        instructions = f"""
        User query: "{query}"

        Generate 3 clarifying questions using the generate_clarification_questions tool.
        Return the questions you received from the tool.
        """

        result = await Runner.run(coordinator_agent, instructions)

        # Coordinator used the tool, now we parse the response
        # Fallback: call clarification agent directly if coordinator didn't use tool properly
        result_direct = await Runner.run(
            clarification_agent,
            f"Research query: {query}"
        )
        questions = result_direct.final_output_as(ClarificationQuestions)

        print(f"Coordinator: Received {len(questions.questions)} clarifying questions")
        return questions

    async def run(self, query: str, questions: ClarificationQuestions, user_answers: list[str]):
        """
        Run research workflow using Coordinator Agent with handoffs.

        Yields status updates for UI while Coordinator autonomously manages specialists.
        """
        trace_id = gen_trace_id()
        with trace("Coordinator Research Workflow", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"

            # Build enriched query (pure Python - no AI needed)
            qa_pairs = [
                QAPair(question=q.question, answer=ans)
                for q, ans in zip(questions.questions, user_answers)
            ]

            print("Enriching query with user answers...")
            yield "Enriching query with clarification answers..."
            enriched = build_enriched_query_object(query, qa_pairs)

            print(f"Research focus areas: {enriched.key_focus_areas}")
            yield f"Research focus identified: {', '.join(enriched.key_focus_areas)}"

            # COORDINATOR TAKES OVER - Autonomous workflow execution
            print("\n" + "=" * 70)
            print("COORDINATOR AGENT: Taking control of research workflow")
            print("=" * 70)

            yield "Coordinator Agent: Planning research strategy..."

            # Build comprehensive instructions for coordinator
            coordinator_instructions = f"""
You are conducting a deep research project. Here is the context:

**Original Query:** {query}

**Enriched Context:**
{enriched.enriched_context}

**Key Focus Areas:**
{', '.join(enriched.key_focus_areas)}

**Your mission:**
Conduct comprehensive research and deliver a high-quality report.

**Workflow to execute:**
1. Plan 3-5 targeted web searches using plan_research_searches tool
2. Execute each search using perform_web_search tool (you can do them in parallel for speed)
3. Collect all search results
4. Write a comprehensive research report (1000+ words) using write_research_report tool
5. Evaluate the report quality using evaluate_report_quality tool
6. If quality score is below 8.0, note what additional work would be needed (but return the report anyway)
7. Return the final report content and evaluation summary

**Important:**
- Pass the full enriched context to your tools for better results
- When searching, use the 'reason' parameter to provide context
- When writing report, include all search results
- Be thorough and comprehensive

Execute this workflow autonomously using your available tools.
Return the final report and evaluation results.
"""

            # Let Coordinator execute the full workflow
            yield "Coordinator: Executing autonomous research workflow..."
            yield "(Coordinator is delegating to specialists: Planner → Search → Writer → Evaluator)"

            print("\nCoordinator executing workflow...")
            coordinator_result = await Runner.run(
                coordinator_agent,
                coordinator_instructions
            )

            print("\nCoordinator workflow completed")
            coordinator_output = str(coordinator_result.final_output)

            # Parse coordinator's output to extract report
            yield "Coordinator: Workflow completed, processing results..."

            # Try to extract markdown report from coordinator's output
            # Look for markdown headers or significant text blocks
            report_content = self._extract_report_content(coordinator_output)

            if not report_content:
                # Fallback: use coordinator's full output as report
                report_content = coordinator_output

            # Extract evaluation if present
            evaluation_summary = self._extract_evaluation(coordinator_output)

            if evaluation_summary:
                yield f"Coordinator: {evaluation_summary}"
            else:
                yield "Coordinator: Research completed successfully"

            # Yield the final report
            yield "\n" + "=" * 70
            yield "FINAL RESEARCH REPORT"
            yield "=" * 70
            yield report_content

            print("\n✓ Coordinator workflow completed successfully")

    def _extract_report_content(self, text: str) -> str:
        """Extract the main report content from coordinator's output"""
        # Look for markdown report patterns

        # Try to find content between markdown headers
        if "# " in text or "## " in text:
            # Find the start of actual content (after initial meta-text)
            lines = text.split('\n')
            report_lines = []
            in_report = False

            for line in lines:
                # Start collecting when we hit a major markdown header
                if line.startswith('# ') and not in_report:
                    in_report = True

                if in_report:
                    report_lines.append(line)

            if report_lines:
                return '\n'.join(report_lines)

        # Fallback: return full text if no clear structure
        return text

    def _extract_evaluation(self, text: str) -> str:
        """Extract evaluation summary from coordinator's output"""
        # Look for evaluation keywords
        patterns = [
            r'(?:Evaluation|Quality Score|Decision):\s*([^\n]+)',
            r'(?:Score|Rating):\s*(\d+(?:\.\d+)?)/10',
            r'(?:APPROVED|NEEDS_IMPROVEMENT|REJECTED)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract surrounding context for summary
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 200)
                context = text[start:end].strip()

                # Clean up and return
                if len(context) > 300:
                    context = context[:300] + "..."

                return context

        return ""


# Create global instance for backward compatibility
coordinator_workflow = CoordinatorWorkflow()


# Convenience functions matching old ResearchManager interface
async def get_clarifying_questions(query: str) -> ClarificationQuestions:
    """Get clarifying questions for a query (backward compatible)"""
    return await coordinator_workflow.get_clarifying_questions(query)


async def run_research(query: str, questions: ClarificationQuestions, user_answers: list[str]):
    """Run research workflow (backward compatible generator)"""
    async for update in coordinator_workflow.run(query, questions, user_answers):
        yield update
