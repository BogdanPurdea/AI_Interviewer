# AI Interviewer

An AI-powered application that conducts structured interviews on any topic using LLMs. Supports both web (Gradio) and CLI interfaces.

## Live Demo

**Note**: The app is accessible via a Gradio public share link. These links are **temporary and expire after 1 week** — the previous link expired on **2026-02-21**.

**[Updated link (available until 2026-02-28)](https://053b752c5db39a0d55.gradio.live)**

## Features

- **Dual Interfaces**: Web UI (Gradio) or terminal CLI
- **Dynamic Planning**: Generates 3-5 phase interview plans based on topic
- **Flexible Flow**: Skip questions, ask for clarification, or end early
- **Response Assessment**: Evaluates relevance (1-10 scale) and user intent
- **Post-Interview Analysis**: Summary, sentiment, themes, and keywords
- **Safety Topic Check**: Topic safety restriction
- **Multi-Provider**: Supports Ollama (local), OpenAI and Anthropic (cloud)

## Architecture & Design

The application follows a **Modular Action Pattern**, where specialized "agents" handle distinct parts of the interview lifecycle:

1.  **Planner Action**:
    -   Analyzes the user's topic.
    -   Generates a structured plan with 3-5 sequential phases (e.g., Introduction, Deep Dive, Conclusion).
    -   Sets a clear goal for the interview.

2.  **Interviewer Action**:
    -   Generates context-aware questions based on the current phase.
    -   Assesses user responses for relevance before proceeding.
    -   Maintains conversation flow and handles topic adherence.

3.  **Analyst Action**:
    -   Runs after the interview concludes.
    -   Processes the entire transcript to extract insights (sentiment, keywords, themes).

4.  **Session Manager**:
    -   Orchestrates the interaction between the user, UI, and Actions.
    -   Manages state (current phase, question count, history).

## Structure

```
.
├── src/
│   ├── config/          # Prompts, settings, model config
│   ├── core/
│   │   ├── actions/     # Safety, Planner, Interviewer, Analyst
│   │   ├── schemas/     # Pydantic models
│   │   ├── services/    # LLM factory, storage, phase management
│   │   └── session.py   # Session orchestration
│   └── tests/           # Unit and integration tests
├── ui/                  # User Interfaces (moved from src/ui)
│   ├── gradio_app.py    # Web interface
│   └── cli.py           # CLI interface
├── data/                # Interview transcripts and analysis
├── docs/                # Documentation
└── README.md            # Project documentation
```

## Setup

**Prerequisites**: Python 3.10+, LLM provider (Ollama or AWS Bedrock)

1. **Install**:
   ```bash
   pip install -r src/requirements.txt
   ```

2. **Configure** (create `src/.env`):
   ```bash
   # OpenAI
   OPENAI_API_KEY=sk-your-openai-api-key-here
   
   # Anthropic
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
   
   # LangSmith (for call tracing)
   LANGSMITH_API_KEY=lsv2_pt_your-langsmith-api-key-here
   LANGSMITH_TRACING=true
   ```

3. **Run**:
   ```bash
   # Web interface
   python ui/gradio_app.py # http://localhost:7860
   
   # CLI interface
   python ui/cli.py
   ```

4. **Test**:
   ```bash
   python -m unittest discover src/tests
   ```

## Configuration

- **Models** (`src/config/models.yaml`): Switch between providers and specific models.
- **Prompts** (`src/config/prompts/`): distinct YAML files for `planner`, `interviewer`, and `analyst` allow you to customize the AI's persona and instructions without changing code.
- **Settings** (`src/config/settings.py`): Adjust operational parameters like:
    - `max_questions`: Length of interview.
    - `question_relevance_threshold`: How strict the assessment is.

## Interview Flow

1.  **Initialization**: User enters a topic.
2.  **Planning**: System validates safety and generates a multi-phase plan.
3.  **The Loop**:
    -   AI asks a question for the current phase.
    -   User answers.
    -   **Assessment**: AI evaluates if the answer is relevant.
        -   *Relevant*: Move to next question/phase.
        -   *Irrelevant/Too Short*: Ask follow-up or guide user back.
        -   *User Question/Demand*: Addressed directly by the interviewer.
4.  **Completion**: Reached max questions or natural conclusion.
5.  **Analysis**: AI generates a summary report and saves to JSON.

## Output

- **Location**: `data/interviews/`
- **Format**: JSON file containing:
    -   Full conversation transcript
    -   Structured analysis (Summary, Sentiment Score, Keywords, Themes)

## License

MIT License - Copyright (c) 2026 Bogdan Purdea
