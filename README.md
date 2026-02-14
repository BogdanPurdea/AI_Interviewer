# AI Interviewer

An AI-powered application that conducts structured interviews on any topic using LLMs. Supports both web (Gradio) and CLI interfaces.

## Features

- **Dual Interfaces**: Web UI (Gradio) or terminal CLI
- **Dynamic Planning**: Generates 3-5 phase interview plans based on topic
- **Flexible Flow**: Skip questions, ask for clarification, or end early
- **Response Assessment**: Evaluates relevance (1-10 scale) and user intent
- **Post-Interview Analysis**: Summary, sentiment, themes, and keywords
- **Safety Topic Check**: Topic safety restriction
- **Multi-Provider**: Supports Ollama (local), OpenAI and Anthropic (cloud)


## Structure

```
src/
├── config/          # Prompts, settings, model config
├── core/
│   ├── actions/     # Safety, Planner, Interviewer, Analyst
│   ├── schemas/     # Pydantic models
│   ├── services/    # LLM factory, storage, phase management
│   └── session.py   # Session orchestration
├── ui/
│   ├── gradio_app.py  # Web interface
│   └── cli.py         # CLI interface
└── tests/           # Unit and integration tests
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
   python src/ui/gradio_app.py  # http://localhost:7860
   
   # CLI interface
   python src/ui/cli.py
   ```

4. **Test**:
   ```bash
   python -m unittest discover src/tests
   ```

## Configuration

- **Models** (`src/config/models.yaml`): LLM provider and model selection
- **Prompts** (`src/config/prompts/`): System prompts for planner, interviewer, analyst
- **Settings** (`src/config/settings.py`): Thresholds, limits, timeouts

## Interview Flow

1. Enter topic → Safety check
2. Generate interview plan (3-5 phases)
3. Conduct interview with dynamic questions
4. Analyze transcript
5. Save to `data/interviews/`

## Output

- Timestamp-based filenames
- Full transcript
- Analysis (JSON): summary, sentiment, themes, keywords

## License

MIT License - Copyright (c) 2026 Bogdan Purdea

