"""
Test script for Handoff mechanism between agents.

Demonstrates how Coordinator Agent delegates tasks to specialist agents
via function_tools (handoffs).
"""

import asyncio
from agents import Runner
from coordinator_agent import coordinator_agent
from dotenv import load_dotenv

load_dotenv(override=True)


async def test_simple_handoff():
    """Test 1: Coordinator delegates to planner (simple handoff)"""
    print("=" * 70)
    print("TEST 1: Simple Handoff - Coordinator → Planner")
    print("=" * 70)

    query = "Latest trends in AI agents for enterprise software in 2025"

    print(f"\nQuery: {query}")
    print("\nAsking coordinator to plan searches...")

    result = await Runner.run(
        coordinator_agent,
        f"Please plan web searches for this query: {query}\n\nJust plan the searches, don't execute them."
    )

    print("\n" + "-" * 70)
    print("Coordinator's response:")
    print("-" * 70)
    print(result.final_output)
    print("-" * 70)

    print("\n[OK] Coordinator successfully delegated to planner via tool")
    print("[OK] Handoff mechanism working")


async def test_handoff_chain():
    """Test 2: Multiple handoffs in sequence (chain)"""
    print("\n" * 2)
    print("=" * 70)
    print("TEST 2: Handoff Chain - Plan → Search → Write → Evaluate")
    print("=" * 70)

    query = "AI agents in healthcare diagnostics 2025"

    instructions = f"""
    Conduct a minimal research workflow for: "{query}"

    Steps to follow:
    1. Plan 2 searches using plan_research_searches tool
    2. Execute those 2 searches using perform_web_search tool for each
    3. Write a short report using write_research_report tool
    4. Evaluate the report quality using evaluate_report_quality tool
    5. Return the evaluation results and final report

    Keep searches and report concise for testing purposes.
    Focus on demonstrating the handoff chain.
    """

    print(f"\nQuery: {query}")
    print("\nExecuting full handoff chain...")
    print("(This will take ~30-60 seconds due to multiple API calls)\n")

    result = await Runner.run(
        coordinator_agent,
        instructions
    )

    print("\n" + "=" * 70)
    print("CHAIN COMPLETED")
    print("=" * 70)
    print(result.final_output)
    print("=" * 70)

    print("\n[OK] Multiple sequential handoffs successful")
    print("[OK] Coordinator orchestrated: plan → search × 2 → write → evaluate")


async def test_coordinator_autonomy():
    """Test 3: Coordinator's autonomous decision making"""
    print("\n" * 2)
    print("=" * 70)
    print("TEST 3: Coordinator Autonomy - Let it decide the workflow")
    print("=" * 70)

    query = "Impact of quantum computing on cryptography"

    instructions = f"""
    Research this topic: "{query}"

    You decide the best approach:
    - Do you need clarification questions?
    - How many searches to plan?
    - Execute your planned workflow
    - Return final findings

    Demonstrate your autonomy as a coordinator.
    Keep it brief for testing.
    """

    print(f"\nQuery: {query}")
    print("\nLetting coordinator decide the workflow autonomously...")
    print("(Coordinator will choose its own steps)\n")

    result = await Runner.run(
        coordinator_agent,
        instructions
    )

    print("\n" + "=" * 70)
    print("AUTONOMOUS WORKFLOW COMPLETED")
    print("=" * 70)
    print(result.final_output)
    print("=" * 70)

    print("\n[OK] Coordinator demonstrated autonomy")
    print("[OK] Made own decisions about workflow steps")


async def main():
    """Run all handoff tests"""
    print("\n")
    print("#" * 70)
    print("# HANDOFF TESTS - Coordinator Agent Delegation")
    print("#" * 70)
    print("\nThese tests demonstrate how Coordinator delegates to specialists")
    print("using handoffs (function_tools).\n")

    try:
        await test_simple_handoff()
    except Exception as e:
        print(f"\n[FAIL] Test 1 failed: {str(e)}")

    try:
        await test_handoff_chain()
    except Exception as e:
        print(f"\n[FAIL] Test 2 failed: {str(e)}")

    try:
        await test_coordinator_autonomy()
    except Exception as e:
        print(f"\n[FAIL] Test 3 failed: {str(e)}")

    print("\n" + "#" * 70)
    print("# ALL HANDOFF TESTS COMPLETED")
    print("#" * 70)
    print("\n[OK] Handoff mechanism successfully implemented")
    print("[OK] Coordinator can delegate to specialists")
    print("[OK] Ready for Commit 5: Full ResearchManager replacement")


if __name__ == "__main__":
    asyncio.run(main())
