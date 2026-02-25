"""
Strategic Analyst Agent.

Receives ClassificationResult from the Kano Classifier, computes Berger
satisfaction/dissatisfaction coefficients (Berger et al., 1993), builds
a 4-quadrant roadmap, and returns a typed KanoOutput.

This is the terminal agent in the pipeline — its output_type=KanoOutput
causes Runner.run_sync() to terminate and return KanoOutput as final_output.
"""
from __future__ import annotations

from agents import Agent, AgentOutputSchema

from analysis.prompts import ANALYSIS_PROMPT
from analysis.schema import KanoOutput


def get_analysis_agent() -> Agent:
    """Build and return the Strategic Analyst Agent.

    Uses strict_json_schema=False because KanoOutput.summary is dict[str, int],
    which generates additionalProperties in its JSON schema — incompatible with
    the SDK's strict schema mode.
    """
    return Agent(
        name="Strategic Analyst",
        model="o4-mini",
        instructions=ANALYSIS_PROMPT,
        output_type=AgentOutputSchema(KanoOutput, strict_json_schema=False),
    )
