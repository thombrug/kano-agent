"""
Classification Specialist Agent.

Classifies product features into Kano categories (Kano et al., 1984) and
hands off structured ClassificationResult to the Strategic Analyst Agent.

Uses the OpenAI Agents SDK handoff mechanism with input_type=ClassificationResult
to pass structured data to the next agent in the pipeline.
"""
from __future__ import annotations

from agents import Agent, handoff

from classification.prompts import CLASSIFICATION_PROMPT
from classification.schema import ClassificationResult


def get_classification_agent() -> Agent:
    """
    Build and return the Classification Specialist Agent.

    Called at runtime to allow the analysis agent to be fully initialized first.
    Uses handoff() with input_type=ClassificationResult so the LLM passes
    structured classification data to the Strategic Analyst.
    """
    from analysis.agent import get_analysis_agent  # lazy import avoids circular init

    analysis_agent = get_analysis_agent()

    return Agent(
        name="Kano Classifier",
        model="o4-mini",
        instructions=CLASSIFICATION_PROMPT,
        handoffs=[
            handoff(
                agent=analysis_agent,
                input_type=ClassificationResult,
                tool_name_override="hand_off_to_strategic_analyst",
                tool_description_override=(
                    "Hand off the classified features to the Strategic Analyst. "
                    "Call this after classifying ALL features in the input."
                ),
            )
        ],
    )
