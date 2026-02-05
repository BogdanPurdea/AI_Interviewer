# Core Package Documentation

This directory contains the foundational logic, configuration, and data structures for the AI Interviewer.

## 1. Components

### Agents (`src/core/agents/`)
-   **`SafetyAgent`**: Uses a fast LLM to screen user topics for safe/unsafe classification using `prompts.yaml`.
-   **`PlannerAgent`**: Uses a reasoning LLM to generate a structured `InterviewPlan` (JSON) containing an interview goal and sequential phases.
-   **`InterviewerAgent`**: Manages the dynamic conversation loop. It processes history and current phase objectives to generate context-aware questions.
-   **`AnalystAgent`**: post-processes the transcript to generate an `InterviewAnalysis` (JSON) with themes and sentiment.

### Services (`src/core/services/`)
-   **`LLMFactory`**: Central factory for instantiating LLM clients (e.g., `ChatOllama`). Abstraction layer for model providers.
-   **`StorageService`**: Handles saving interview transcripts and analysis results to the filesystem.

### Session Management (`src/core/session.py`)
-   **`InterviewSession`**: The central orchestrator. It maintains the `InterviewState`, instantiates agents, and manages the state transitions (Planning -> Interviewing -> Analysis).

## 2. Configuration (`src/core/`)

-   **`config.py`**: Loads configuration and provides accessors.
-   **`models.yaml`**: Defines LLM provider, model IDs, and base URLs.
-   **`prompts.yaml`**: Centralized repository for all system prompts, personas, and safety guidelines. Separates prompt engineering from code.

## 3. Data Contracts (`src/core/schemas.py`)

Uses **Pydantic** models to ensure type safety and structured LLM outputs:
-   **`InterviewPlan`**: Schema for the interview roadmap.
-   **`InterviewState`**: Schema for the realtime session state.
-   **`InterviewAnalysis`**: Schema for the post-interview insights.
