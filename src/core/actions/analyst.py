from core.services.llm_factory import LLMFactory
from core.schemas import InterviewAnalysis, InterviewState
from core.config import PROMPTS
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import json
import os
from typing import List


class KeywordsOutput(BaseModel):
    keywords: List[str] = Field(description="List of extracted keywords.")


class SentimentOutput(BaseModel):
    score: int = Field(description="Sentiment score from 1 to 10.")
    reasoning: str = Field(description="Reasoning for the score.")


class AnalystAction:
    def __init__(self):
        self.fast_llm = LLMFactory.get_fast_model()
        self.analysis_llm = self.fast_llm.with_structured_output(InterviewAnalysis)
        self.keywords_llm = self.fast_llm.with_structured_output(KeywordsOutput)
        self.sentiment_llm = self.fast_llm.with_structured_output(SentimentOutput)

    def _get_transcript(self, state: InterviewState):
        messages = state.get("messages", [])
        transcript = "\n".join([f"{m.type}: {m.content}" for m in messages])
        return transcript

    def create_summary(self, state: InterviewState):
        """Generates the interview analysis summary."""
        topic = state.get("topic")
        transcript = self._get_transcript(state)

        analyst_prompt = (
            PROMPTS["analyst"]["summary_prompt"] + "\nReturn the output in JSON format."
        )

        prompt = ChatPromptTemplate.from_template(analyst_prompt)
        chain = prompt | self.analysis_llm

        analysis = chain.invoke({"topic": topic, "transcript": transcript})
        return {"insights": analysis}

    def save_analysis(self, state: InterviewState):
        """Saves the transcript and analysis to a file."""
        topic = state.get("topic")
        messages = state.get("messages", [])

        # We assume 'insights' might be in state from a previous step, or we generate it if missing?
        # The user requested "another for saving the summary and the trascript from state".
        # So it expects 'insights' (analysis) to be present.
        analysis = state.get("insights")
        if not analysis:
            # Fallback: Generate it if not present (optional safety)
            result = self.create_summary(state)
            analysis = result["insights"]

        structured_transcript = []
        for m in messages:
            role = "AI" if m.type == "ai" else "User"
            structured_transcript.append({"role": role, "content": m.content})

        output_data = {
            "topic": topic,
            "transcript": structured_transcript,
            "analysis": analysis.dict() if hasattr(analysis, "dict") else analysis,
        }

        output_dir = "interview_insights"
        filename = f"analysis_{topic.replace(' ', '_').lower()}.json"
        filepath = os.path.join(output_dir, filename)

        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(output_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save analysis: {e}")

        return {"insights": analysis, "analysis_path": filepath}

    def extract_keywords(self, state: InterviewState):
        """Extracts keywords using config prompt."""
        transcript = self._get_transcript(state)

        prompt_text = PROMPTS["analyst"]["extract_keywords_prompt"]
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.keywords_llm
        result = chain.invoke({"transcript": transcript})

        return {"keywords": result.keywords}

    def analyze_sentiment(self, state: InterviewState):
        """Analyzes sentiment using config prompt."""
        transcript = self._get_transcript(state)

        prompt_text = PROMPTS["analyst"]["analyze_sentiment_prompt"]
        prompt = ChatPromptTemplate.from_template(prompt_text)
        chain = prompt | self.sentiment_llm
        result = chain.invoke({"transcript": transcript})

        return {
            "sentiment_score": result.score,
            "sentiment_reasoning": result.reasoning,
        }
