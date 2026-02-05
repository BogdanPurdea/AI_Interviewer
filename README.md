# AI Interviewer

A modular, AI-powered interviewing application capable of conducting structured, dynamic interviews on any topic.

## 🚀 Key Features

-   **Dynamic Interviewing**: Generates a custom interview plan based on the user's topic.
-   **Adaptive Persona**: Adopts a professional "AI Interviewer" persona.
-   **Modular Architecture**: Built with distinct Agents (`Safety`, `Planner`, `Interviewer`, `Analyst`) for robustness and scalability.
-   **Provider Agnostic**: Configurable to use different LLM providers (currently optimized for local inference with **Ollama**).
-   **Safety First**: Includes pre-interview topic safety checks and real-time input monitoring.
-   **Structured Analysis**: Automatically analyzes the interview transcript to extract themes and sentiment.

## 🛠️ Architecture

The project follows a clean, modular architecture:

```text
src/
├── core/
│   ├── agents/         # Intelligence Modules (Safety, Planner, Interviewer, Analyst)
│   ├── services/       # Infrastructure (LLMFactory, Storage)
│   ├── config.py       # Configuration Loader
│   ├── models.yaml     # Model Configuration
│   ├── prompts.yaml    # System Prompts & Personas
│   └── session.py      # Session State Management
├── ui/
│   └── cli.py          # Terminal Interface
└── tests/
    └── test_core_flow.py # End-to-End Test Suite
```

## 📋 Prerequisites

-   **Python 3.9+**
-   **Ollama**: Installed and running locally (`ollama serve`).
-   **Models**: Pull the required model (default: `llama3.1`).
    ```bash
    ollama pull llama3.1
    ```

## ⚡ Quick Start

1.  **Clone the repository**:
    ```bash
    git clone <repository_url>
    cd AI_Interviewer
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r src/requirements.txt
    ```

3.  **Run the Application**:
    ```bash
    python src/ui/cli.py
    ```

4.  **Run Tests**:
    ```bash
    python src/tests/test_core_flow.py
    ```

## ⚙️ Configuration

Modify `src/core/models.yaml` to configure your LLMS:

```yaml
provider: ollama
models:
  reasoning: llama3.1
  fast: llama3.1
base_url: http://localhost:11434
```

## 🧠 Core Agents

-   **SafetyAgent**: Filters unsafe topics.
-   **PlannerAgent**: Creates a multi-phase interview structure.
-   **InterviewerAgent**: Conducts the interview, managing phases and conversation context.
-   **AnalystAgent**: Summarizes the session and extracts insights.
