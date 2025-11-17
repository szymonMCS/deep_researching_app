# Deep Research Agent

An AI-powered deep research application built with OpenAI Agents SDK. This application performs comprehensive web research on any topic by orchestrating multiple specialized AI agents.

## Features

- **Multi-Agent System**: Coordinates specialized agents for planning, searching, writing, and emailing
- **Intelligent Search Planning**: Automatically generates optimal search queries for your research topic
- **Web Search Integration**: Leverages OpenAI's Web Search Tool to gather current information
- **Comprehensive Reports**: Generates detailed, well-structured research reports (1000+ words)
- **Gradio UI**: User-friendly web interface for easy interaction
- **Email Integration**: Optionally sends formatted reports via email using SendGrid
- **Real-time Progress**: See live updates as the research progresses

## Architecture

The application consists of several specialized agents:

- **Planner Agent**: Analyzes your query and creates a strategic search plan
- **Search Agent**: Performs web searches and summarizes findings
- **Writer Agent**: Synthesizes research into a comprehensive markdown report
- **Email Agent**: Formats and sends reports via email (optional)
- **Research Manager**: Orchestrates the entire workflow

## Prerequisites

- Python 3.8+
- OpenAI API key
- SendGrid API key (optional, only needed for email functionality)

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Add your API keys to the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here  # Optional
```

## Configuration

### Email Settings (Optional)

If you want to use the email functionality:

1. Sign up for a free SendGrid account at https://sendgrid.com
2. Create an API key
3. Verify your sender email in SendGrid
4. Update the email addresses in `email_agent.py`:
   - Line 13: Set your verified sender email
   - Line 14: Set the recipient email

### Search Configuration

You can adjust the number of searches performed by editing `planner_agent.py`:
- Default: 5 searches per query (line 4)

## Usage

1. Start the application:
```bash
python deep_research.py
```

2. The Gradio interface will open in your browser automatically

3. Enter your research topic in the text box

4. Click "Run" or press Enter

5. Watch the progress updates as the agents work

6. View the final research report in markdown format

## Example Queries

- "Latest AI Agent frameworks in 2025"
- "Impact of quantum computing on cybersecurity"
- "Best practices for sustainable architecture"
- "Recent advances in gene therapy"

## Cost Considerations

**Important**: The OpenAI Web Search Tool costs $2.50 per search call. With the default configuration (5 searches per query), each research session may cost $12.50-$15.00 in API fees.

To reduce costs:
- Decrease `HOW_MANY_SEARCHES` in `planner_agent.py`
- Use `gpt-4o-mini` model (already configured)
- Monitor your usage at https://platform.openai.com/usage

## Viewing Traces

The application generates trace IDs for debugging and monitoring. View traces at:
https://platform.openai.com/traces

## Project Structure

```
deep_research/
├── deep_research.py       # Main Gradio UI application
├── research_manager.py    # Orchestrates the research workflow
├── planner_agent.py       # Creates search plans
├── search_agent.py        # Performs web searches
├── writer_agent.py        # Generates research reports
├── email_agent.py         # Handles email sending
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Troubleshooting

### API Key Errors
- Ensure your `.env` file is in the same directory as `deep_research.py`
- Verify your OpenAI API key is valid and has credits
- Check that `load_dotenv(override=True)` is called before using the API

### Email Not Sending
- Verify your SendGrid API key is correct
- Ensure sender email is verified in SendGrid
- Check SendGrid dashboard for error logs

### Application Won't Start
- Confirm all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.8+)

## License

This project is part of an educational course on AI Agents.

## Credits

Built with:
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Gradio](https://gradio.app/)
- [SendGrid](https://sendgrid.com/)
