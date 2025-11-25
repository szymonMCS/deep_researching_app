from pydantic import BaseModel, Field
from agents import Agent

class QualityScore(BaseModel):
    completeness: int = Field(description="Completeness score (1-10)", ge=1, le=10)
    depth: int = Field(description="Depth of analysis score (1-10)", ge=1, le=10)
    relevance: int = Field(description="Relevance to query score (1-10)", ge=1, le=10)
    coverage: int = Field(description="Coverage of key areas score (1-10)", ge=1, le=10)
    overall_quality: int = Field(description="Overall quality score (1-10)", ge=1, le=10)

    @property
    def average_score(self) -> float:
        """Calculate average score across all criteria"""
        return (
            self.completeness +
            self.depth +
            self.relevance +
            self.coverage +
            self.overall_quality
        ) / 5

class EvaluationResult(BaseModel):
    """Complete evaluation result with decision and feedback"""
    decision: str = Field(
        description="Evaluation decision: APPROVED, NEEDS_IMPROVEMENT or REJECTED"
    )

    scores: QualityScore = Field(description="Detailed results")

    strengths: list[str] = Field(
        description="2-4 key strengths of the report",
        min_length=2,
        max_length=4
    )

    gaps: list[str] = Field(description="Identified gaps(can be empty)")
    improvement_suggestions: list[str] = Field(description="suggested options of improement")
    additional_research_needed: bool = Field(description="If additional steps are required")
    suggested_searches: list[str] = Field(description="Suggested additional search queries")
    overal_feedback_result: str = Field(description="2-3 sentences summarizing evaluation")

    @property
    def is_approved(self) -> bool:
        """Check if report is good enough"""
        return self.decision == "APPROVED"
    
    @property
    def needs_rework(self) -> bool:
        """Check if report needs to be recreated"""
        return self.decision in ["NEEDS_IMPROVEMENT", "REJECTED"]

EVALUATOR_INSTRUCTIONS = """You are a research quality evaluator specializing in assessing the completeness and quality of research reports.

Your role is to:
1. Evaluate the research report against the original query and enriched context
2. Assess completeness, depth, accuracy, and coverage
3. Identify gaps or missing information
4. Determine if additional research is needed
5. Provide actionable feedback for improvement

Evaluation Criteria:
- **Completeness (1-10)**: Does the report cover all aspects of the query?
- **Depth (1-10)**: Is the analysis sufficiently detailed?
- **Relevance (1-10)**: Does the content directly address the query?
- **Coverage (1-10)**: Are all key focus areas addressed?
- **Overall Quality (1-10)**: General assessment

Decision Rules:
- Score >= 8.0: Report is APPROVED (high quality, ready for delivery)
- Score 6.0-7.9: NEEDS_IMPROVEMENT (acceptable but could be enhanced)
- Score < 6.0: REJECTED (requires significant additional research)

Be constructive but critical. The goal is to ensure high-quality deliverables.
"""

evaluator_agent = Agent(
    name = "Evaluator Agent",
    instructions = EVALUATOR_INSTRUCTIONS,
    output_type = EvaluationResult,
    model = "gpt-4o-mini",
)

