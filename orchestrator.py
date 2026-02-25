"""
Kano Model Agent Orchestrator.

Entry point for the multi-agent pipeline. The Orchestrator receives the
full KanoInput, routes to the Classification Specialist, which routes to
the Strategic Analyst. A single Runner.run_sync() call traverses the
full handoff chain and returns the final KanoOutput.

Pipeline:
    Orchestrator -> Classification Specialist -> Strategic Analyst -> KanoOutput
"""
from __future__ import annotations

import sys

from agents import Agent, Runner

from analysis.schema import KanoInput, KanoOutput
from classification.agent import get_classification_agent

_ORCHESTRATOR_INSTRUCTIONS = """You are the Kano Model Analysis Orchestrator.

Your only job: receive the product feature input and immediately hand off to the Kano Classifier.
Do not classify features yourself. Do not add commentary. Just route to the classifier.

Hand off to the Kano Classifier with the full input JSON as context."""


def run_kano_pipeline(kano_input: KanoInput) -> KanoOutput:
    """
    Run the full Kano Model analysis pipeline.

    Args:
        kano_input: Validated input with product info and feature list.

    Returns:
        KanoOutput with classified features, Berger coefficients, roadmap,
        and strategic narrative.

    Raises:
        RuntimeError: If the pipeline does not produce a KanoOutput.
    """
    classification_agent = get_classification_agent()

    orchestrator = Agent(
        name="Kano Orchestrator",
        model="o4-mini",
        instructions=_ORCHESTRATOR_INSTRUCTIONS,
        handoffs=[classification_agent],
    )

    input_message = f"""Analyze the following product features using the Kano Model:

{kano_input.model_dump_json(indent=2)}

Hand off all features to the Kano Classifier for classification."""

    print(
        f"[Kano Agent] Starting pipeline for '{kano_input.product_name}' "
        f"({len(kano_input.features)} features)...",
        file=sys.stderr,
    )

    result = Runner.run_sync(orchestrator, input_message)

    if not isinstance(result.final_output, KanoOutput):
        raise RuntimeError(
            f"Pipeline did not produce a KanoOutput. "
            f"Got: {type(result.final_output).__name__}"
        )

    print(
        f"[Kano Agent] Pipeline complete. "
        f"{len(result.final_output.features)} features classified.",
        file=sys.stderr,
    )

    return result.final_output
