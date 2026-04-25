import gradio as gr
from dotenv import load_dotenv
from coordinator_workflow import CoordinatorWorkflow

load_dotenv(override=True)

# Global state to store questions
_questions_cache = {}


async def run(stored_query: str, answer1: str, answer2: str, answer3: str):
    """Run research with clarification answers"""
    if not stored_query or stored_query not in _questions_cache:
        yield "Please generate questions first by clicking 'Generate Questions'."
        return

    if not all([answer1.strip(), answer2.strip(), answer3.strip()]):
        yield "Please answer all clarifying questions before proceeding."
        return

    user_answers = [answer1, answer2, answer3]
    questions = _questions_cache[stored_query]

    async for chunk in CoordinatorWorkflow().run(stored_query, questions, user_answers):
        yield chunk


async def generate_questions(query: str):
    """Generate clarifying questions for the user query"""
    if not query.strip():
        return "Please enter a research query first.", "", "", "", query

    questions = await CoordinatorWorkflow().get_clarifying_questions(query)

    _questions_cache[query] = questions

    return (
        questions.questions[0].question,
        questions.questions[1].question,
        questions.questions[2].question,
        f"**Research Focus:** {questions.research_focus}",
        query
    )

with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    gr.Markdown("AI-powered research assistant with intelligent clarification questions")
    query_textbox = gr.Textbox(
            label="What topic would you like to research?",
            placeholder="e.g., Latest AI agent frameworks in 2025"
    )
    generate_btn = gr.Button("Generate Questions", variant="secondary", scale=1)
    focus_info = gr.Markdown(label="Research Focus")

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
        inputs=query_textbox,
        outputs=[question1, question2, question3, focus_info, stored_query_state]
    )

    run_clarified_button.click(
        fn=run,
        inputs=[stored_query_state, answer1, answer2, answer3],
        outputs=report_clarified
    )

if __name__ == "__main__":
    ui.launch(server_name="0.0.0.0", server_port=7860)
else:
    ui.launch()
