---
title: AI_Interviewer
app_file: src/ui/gradio_app.py
sdk: gradio
sdk_version: 6.5.1
---
# AI Interviewer

A modular, AI-powered interviewing application that conducts structured, dynamic interviews on any topic through an intuitive web interface.

## Key Features

- **Web-Based Interface**: Clean, modern Gradio UI for seamless interview experience
- **Dynamic Interview Planning**: Automatically generates custom interview plans (3-5 phases) based on your topic
- **Flexible Interview Flow**: 
  - Skip questions you don't want to answer
  - Ask for clarification when needed
  - End the interview at any time
- **Intelligent Response Assessment**: Evaluates responses for relevance and user intent (1-10 scale)
- **Comprehensive Analysis**: Automatic post-interview analysis including:
  - Summary of key perspectives
  - Key points extraction
  - Sentiment analysis (1-5 scale with labels)
  - Theme identification
  - Keyword extraction
- **Safety First**: Pre-interview topic safety checks and real-time input monitoring
- **Provider Agnostic**: Configurable to use different LLM providers (optimized for **Ollama** and **AWS Bedrock**)

## Architecture

The project follows a clean, modular architecture:

```text
src/
├── config/
│   ├── prompts/          # System prompts (planner, interviewer, analyst)
│   ├── responses.yaml    # User-facing message templates
│   ├── settings.py       # Application settings
│   └── models.yaml       # LLM model configuration
├── core/
│   ├── actions/          # Core logic (Safety, Planner, Interviewer, Analyst)
│   ├── schemas/          # Pydantic data models
│   ├── services/         # Infrastructure (LLMFactory, Storage)
│   ├── config.py         # Configuration loader
│   └── session.py        # Session state management
├── ui/
│   └── gradio_app.py     # Web interface
└── tests/
    └── test_session_logic.py  # Test suite
```

## Prerequisites

- **Python 3.10+**
- **LLM Provider** (choose one):
  - **Ollama**: Installed and running locally (`ollama serve`)
    ```bash
    ollama pull llama3.1
    ```
  - **AWS Bedrock**: AWS credentials configured with access to Claude models

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd AI_Interviewer
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r src/requirements.txt
   ```

3. **Configure Environment**:
   Create a `.env` file in `src/` directory:
   ```bash
   # For Ollama (local)
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   
   # OR for AWS Bedrock
   LLM_PROVIDER=bedrock
   AWS_REGION=us-east-1
   # AWS credentials via environment or ~/.aws/credentials
   ```

4. **Run the Application**:
   ```bash
   python src/ui/gradio_app.py
   ```
   Then open your browser to `http://localhost:7860`

5. **Run Tests**:
   ```bash
   python src/tests/test_session_logic.py
   ```

## Configuration

### LLM Models (`src/config/models.yaml`)

```yaml
provider: ollama  # or 'bedrock'
models:
  reasoning: llama3.1
  fast: llama3.1
base_url: http://localhost:11434
```

### Prompts (`src/config/prompts/`)

All system prompts are centralized in YAML files:
- `planner.yaml` - Interview plan generation
- `interviewer.yaml` - Question generation and response assessment
- `analyst.yaml` - Post-interview analysis

### Response Templates (`src/config/responses.yaml`)

Customize user-facing messages like opening, closing, and analysis display.

## Core Components

### Actions
- **SafetyAction**: Filters unsafe topics before interview starts
- **PlannerAction**: Creates structured interview plans with 3-5 phases
- **InterviewerAction**: Generates questions and assesses user responses
- **AnalystAction**: Analyzes transcripts to extract insights

### Session Management
- **InterviewSession**: Orchestrates the entire interview lifecycle
- Manages state transitions: Planning → Interviewing → Analysis
- Handles user intents: skip questions, cancel interview, ask for clarification
- Automatic session cleanup after 30 minutes of inactivity

### Response Assessment
Evaluates user responses on multiple criteria:
1. **Cancel Detection** - User wants to end the interview
2. **Skip Detection** - User wants to move to next question (lenient)
3. **Relevance Scoring** - 1-10 scale based on answer quality

## Interview Flow

1. **Start**: User enters a topic
2. **Safety Check**: Topic is validated for appropriateness
3. **Planning**: AI generates a structured interview plan
4. **Interview**: AI asks questions, user responds naturally
   - Can skip questions ("I don't know", "next question")
   - Can ask for clarification
   - Can end early ("stop", "cancel")
5. **Analysis**: Automatic analysis with summary, sentiment, themes, and keywords
6. **Save**: Transcript and analysis saved to `data/interviews/`

## Web Interface Features

- **Clean, Modern Design**: Intuitive chat-based interface
- **Real-time Feedback**: Messages appear instantly
- **Keyboard Shortcuts**: Press Enter to submit responses
- **Session Management**: Automatic cleanup of inactive sessions
- **Status Notifications**: Clear success/error messages

## Output

Interviews are saved in `data/interviews/` with:
- Timestamp-based filenames
- Full conversation transcript
- Comprehensive analysis (JSON format)

## Development

### Project Structure
- Modular design with clear separation of concerns
- Type-safe with Pydantic schemas
- Centralized configuration management
- Comprehensive test coverage

### Adding New Features
1. Update schemas in `src/core/schemas/`
2. Modify prompts in `src/config/prompts/`
3. Update actions in `src/core/actions/`
4. Test with `src/tests/test_session_logic.py`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Bogdan Purdea
