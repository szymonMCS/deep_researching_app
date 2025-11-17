import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
import asyncio

load_dotenv(override=True)

# Global state to store questions (in production, use proper state management)
_questions_cache = {}


async def run(query: str):
    async for chunk in ResearchManager().run(query):
        yield chunk


async def generate_questions(query: str):
    """Generate clarifying questions for the user query"""
    if not query.strip():
        return "Please enter a research query first.", "", "", "", query

    manager = ResearchManager()
    questions = await manager.get_clarifying_questions(query)

    # Cache questions for later use
    _questions_cache[query] = questions

    return (
        questions.questions[0].question,
        questions.questions[1].question,
        questions.questions[2].question,
        f"**Research Focus:** {questions.research_focus}",
        query  # Return query to store in state
    )


async def run_with_clarification(stored_query: str, answer1: str, answer2: str, answer3: str):
    """Run research with clarification answers"""
    if not stored_query or stored_query not in _questions_cache:
        yield "Please generate questions first by clicking 'Generate Questions'."
        return

    if not all([answer1.strip(), answer2.strip(), answer3.strip()]):
        yield "Please answer all clarifying questions before proceeding."
        return

    user_answers = [answer1, answer2, answer3]
    manager = ResearchManager()
    questions = _questions_cache[stored_query]

    async for chunk in manager.run_with_clarification(stored_query, questions, user_answers):
        yield chunk


with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    gr.Markdown("AI-powered research assistant with intelligent clarification questions")

    with gr.Tab("Standard Research"):
        gr.Markdown("### Quick research without clarification")
        query_textbox = gr.Textbox(
            label="What topic would you like to research?",
            placeholder="e.g., Latest AI agent frameworks in 2025"
        )
        run_button = gr.Button("Run Research", variant="primary")
        report = gr.Markdown(label="Report")

        run_button.click(fn=run, inputs=query_textbox, outputs=report)
        query_textbox.submit(fn=run, inputs=query_textbox, outputs=report)

    with gr.Tab("Research with Clarification"):
        gr.Markdown("### Enhanced research with clarifying questions for better results")

        with gr.Row():
            query_textbox_clarify = gr.Textbox(
                label="What topic would you like to research?",
                placeholder="e.g., Impact of quantum computing on cybersecurity",
                scale=3
            )
            generate_btn = gr.Button("Generate Questions", variant="secondary", scale=1)

        focus_info = gr.Markdown(label="Research Focus")

        # Hidden state to store query
        stored_query_state = gr.State("")

        with gr.Column(visible=True) as questions_section:
            gr.Markdown("### Please answer these clarifying questions:")
            question1 = gr.Textbox(label="Question 1", interactive=False)
            answer1 = gr.Textbox(label="Your Answer", placeholder="Type your answer here...")

            question2 = gr.Textbox(label="Question 2", interactive=False)
            answer2 = gr.Textbox(label="Your Answer", placeholder="Type your answer here...")

            question3 = gr.Textbox(label="Question 3", interactive=False)
            answer3 = gr.Textbox(label="Your Answer", placeholder="Type your answer here...")

            run_clarified_button = gr.Button("Run Enhanced Research", variant="primary", size="lg")

        report_clarified = gr.Markdown(label="Report")

        generate_btn.click(
            fn=generate_questions,
            inputs=query_textbox_clarify,
            outputs=[question1, question2, question3, focus_info, stored_query_state]
        )

        run_clarified_button.click(
            fn=run_with_clarification,
            inputs=[stored_query_state, answer1, answer2, answer3],
            outputs=report_clarified
        )

ui.launch(inbrowser=True)

