"""
Kano Model Agent Orchestrator.

Entry point for the two-agent pipeline. Runner.run_sync() starts with the
Classification Specialist, which classifies features and hands off to the
Strategic Analyst. The Strategic Analyst returns the final KanoOutput.

Pipeline:
    Classification Specialist -> Strategic Analyst -> KanoOutput
"""
from __future__ import annotations

import sys

from agents import Runner

from analysis.schema import KanoInput, KanoOutput
from classification.agent import get_classification_agent


def run_kano_pipeline(kano_input: KanoInput) -> KanoOutput:
    """
    Run the full Kano Model analysis pipeline.

    Starts Runner.run_sync() directly with the Classification Specialist.
    The classifier hands off to the Strategic Analyst via the SDK handoff
    mechanism, which produces the final KanoOutput.

    Args:
        kano_input: Validated input with product info and feature list.

    Returns:
        KanoOutput with classified features, Berger coefficients, roadmap,
        and strategic narrative.

    Raises:
        RuntimeError: If the pipeline does not produce a KanoOutput.
    """
    classification_agent = get_classification_agent()

    input_message = kano_input.model_dump_json(indent=2)

    print(
        f"[Kano Agent] Starting pipeline for '{kano_input.product_name}' "
        f"({len(kano_input.features)} features)...",
        file=sys.stderr,
    )

    result = Runner.run_sync(classification_agent, input_message)

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
