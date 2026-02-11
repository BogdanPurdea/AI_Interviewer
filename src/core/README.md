# Core Package Documentation

This directory contains the foundational logic, configuration, and data structures for the AI Interviewer.

## 1. Components

### Actions (`src/core/actions/`)

- **`SafetyAction`**: Screens user topics for safety using a fast LLM and safety prompts
- **`PlannerAction`**: Generates structured `InterviewPlan` with interview goal and 3-5 sequential phases
- **`InterviewerAction`**: Manages the conversation loop:
  - Generates context-aware questions based on current phase
  - Assesses user responses for relevance, skip intent, and cancel intent
  - Provides natural feedback for inadequate responses
- **`AnalystAction`**: Post-processes transcripts to generate comprehensive analysis:
  - Summary (2-3 sentences)
  - Key points (3-5 items)
  - Sentiment analysis (score 1-5 + label)
  - Theme extraction (3-5 themes)
  - Keyword extraction (10-15 keywords)

### Services (`src/core/services/`)

- **`LLMFactory`**: Central factory for instantiating LLM clients
  - Supports multiple providers (Ollama, AWS Bedrock)
  - Configurable via `models.yaml` and environment variables
- **`StorageService`**: Handles saving interview transcripts and analysis to filesystem

### Session Management (`src/core/session.py`)

- **`InterviewSession`**: Central orchestrator for interview lifecycle
  - Maintains `InterviewState` with phase tracking and question counts
  - Manages state transitions: Planning → Interviewing → Analysis
  - Handles user intents:
    - Skip questions (lenient detection)
    - Cancel interview
    - Ask for clarification
  - Automatic session expiration after 30 minutes of inactivity

## 2. Configuration (`src/config/`)

### Prompts (`src/config/prompts/`)
Centralized YAML files for all system prompts:
- **`planner.yaml`**: Interview plan generation prompt
- **`interviewer.yaml`**: 
  - `system_generation_prompt`: Question generation
  - `system_assessment_prompt`: Response assessment (cancel/skip/relevance)
- **`analyst.yaml`**: Comprehensive analysis prompt

### Settings (`src/config/`)
- **`settings.py`**: Application settings using Pydantic BaseSettings
- **`models.yaml`**: LLM provider and model configuration
- **`responses.yaml`**: User-facing message templates (opening, closing, analysis)
- **`config.py`**: Configuration loader with accessors

## 3. Data Contracts (`src/core/schemas/`)

Uses **Pydantic** models for type safety and structured LLM outputs:

### Interview Planning
- **`InterviewPlan`**: Interview goal + list of phase objectives

### Session State
- **`InterviewState`**: Real-time session state
  - Current phase index and objective
  - Question counts (total and per-phase)
  - Conversation history
  - Active status

### Response Assessment
- **`ResponseAssessment`**: User response evaluation
  - `relevant`: int (1-10 score)
  - `reason`: str (explanation)
  - `cancel`: bool (end entire interview)
  - `skip_question`: bool (move to next question)

### Analysis
- **`InterviewAnalysis`**: Post-interview insights
  - `summary`: str
  - `key_points`: list[str]
  - `sentiment_score`: int (1-5)
  - `sentiment_label`: str
  - `key_themes`: list[str]
  - `keywords`: list[str]

### Session Response
- **`SessionResponse`**: Standardized response format
  - `success`: bool
  - `message`: str
  - `error`: Optional[str]
  - `metadata`: dict

## 4. Interview Logic

### Response Assessment Priority
1. **Cancel Detection** (Priority 1): User wants to end entire interview
2. **Skip Detection** (Priority 2): User wants to skip current question
   - Lenient: "I don't know", "not sure", "skip", "next"
3. **Relevance Scoring** (Priority 3): 1-10 scale
   - 9-10: Comprehensive answer
   - 7-8: Good answer
   - 5-6: Partial or clarification question
   - 3-4: Vague but engaged
   - 1-2: Off-topic

### Phase Advancement
- Advances when question count reaches threshold OR user skips
- Relevance thresholds:
  - Question level: 3/10
  - Phase level: 4/10

### Natural Feedback
- For inadequate responses: "I'd like to hear more about that. [reason]"
- Avoids repeating entire previous AI message
- Encourages user to elaborate without being pushy

## 5. Key Design Principles

- **Flexibility**: Lenient skip detection, user-friendly conversation
- **Type Safety**: Pydantic schemas for all data structures
- **Separation of Concerns**: Clear boundaries between actions, services, and session management
- **Centralized Configuration**: All prompts and settings in YAML files
- **Comprehensive Analysis**: Single analysis prompt generates all insights
- **User Experience**: Natural, conversational flow with clear feedback
