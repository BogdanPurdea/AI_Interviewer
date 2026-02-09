from core.services.llm_factory import LLMFactory
from core.schemas import InterviewAnalysis, InterviewState
from core.config import PROMPTS
from langchain_core.prompts import ChatPromptTemplate
import json
import os

class AnalystAction:
    def __init__(self):
        self.llm = LLMFactory.get_fast_model()
        self.structured_llm = self.llm.with_structured_output(InterviewAnalysis)

    def __call__(self, state: InterviewState):
        """Stage 3: Extracts insights."""
        topic = state.get("topic")
        transcript = state.get("transcript")

        # If transcript string isn't pre-computed, build it from messages
        if not transcript:
            messages = state.get("messages", [])
            transcript = "\n".join([f"{m.type}: {m.content}" for m in messages])

        analyst_prompt = (
            PROMPTS["analyst"]["system_prompt"] + "\nReturn the output in JSON format."
        )

        prompt = ChatPromptTemplate.from_template(analyst_prompt)
        chain = prompt | self.structured_llm

        analysis = chain.invoke({"topic": topic, "transcript": transcript})

        # Prepare structured transcript for JSON output
        messages = state.get("messages", [])
        structured_transcript = []
        for m in messages:
            role = "AI" if m.type == "ai" else "User"
            structured_transcript.append({"role": role, "content": m.content})

        # Save output
        output_data = {
            "topic": topic,
            "transcript": structured_transcript,
            "analysis": analysis.model_dump(),
        }

        # Generate filename and path
        output_dir = "interview_insights"
        filename = f"interview_analysis_{topic.replace(' ', '_').lower()}.json"
        filepath = os.path.join(output_dir, filename)

        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(filepath, "w") as f:
                json.dump(output_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save analysis: {e}")

        return {"insights": analysis, "transcript": transcript}
