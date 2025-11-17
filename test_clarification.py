"""
Test script for the clarification agent functionality.
Run this to test the question generation and query enrichment.
"""

import asyncio
from query_enrichment import generate_clarifying_questions, enrich_query_with_answers


async def test_clarification_flow():
    """Test the complete clarification flow"""

    # Test query
    test_query = "AI agents in 2025"

    print("=" * 60)
    print("CLARIFICATION AGENT TEST")
    print("=" * 60)
    print(f"\nOriginal Query: {test_query}\n")

    # Step 1: Generate clarifying questions
    print("Step 1: Generating clarifying questions...")
    questions = await generate_clarifying_questions(test_query)

    print(f"\nResearch Focus: {questions.research_focus}\n")
    print("Clarifying Questions:")
    for i, q in enumerate(questions.questions, 1):
        print(f"\n{i}. {q.question}")
        print(f"   Reasoning: {q.reasoning}")

    # Step 2: Simulate user answers
    print("\n" + "=" * 60)
    print("Step 2: Simulating user answers...")
    simulated_answers = [
        {
            "question": questions.questions[0].question,
            "answer": "I'm interested in business applications, particularly in customer service and automation"
        },
        {
            "question": questions.questions[1].question,
            "answer": "I need technical depth - architecture patterns and implementation details"
        },
        {
            "question": questions.questions[2].question,
            "answer": "Focus on open-source frameworks and those with good LangChain integration"
        }
    ]

    for i, qa in enumerate(simulated_answers, 1):
        print(f"\nQ{i}: {qa['question']}")
        print(f"A{i}: {qa['answer']}")

    # Step 3: Enrich query
    print("\n" + "=" * 60)
    print("Step 3: Enriching query with answers...")
    enriched = await enrich_query_with_answers(test_query, simulated_answers)

    print(f"\n**Enriched Context:**\n{enriched.enriched_context}\n")
    print(f"**Key Focus Areas:**")
    for area in enriched.key_focus_areas:
        print(f"  - {area}")
    print(f"\n**Suggested Scope:** {enriched.suggested_scope}")

    print("\n" + "=" * 60)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_clarification_flow())
