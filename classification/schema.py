"""
Classification schemas for the Kano Model agent.

Defines the 5 Kano categories (Kano et al., 1984) and the structured
output of the Classification Specialist Agent.
"""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class KanoCategory(str, Enum):
    """
    Kano Model feature categories (Kano et al., 1984).

    Attractive (Delighters): Unexpected features that delight customers when
        present but whose absence goes unnoticed.
    One-dimensional (Performance): More = higher satisfaction; less = dissatisfaction.
    Must-be (Basics): Minimum expected features. Presence is taken for granted;
        absence causes significant dissatisfaction.
    Indifferent: Customers do not care either way.
    Reverse: Unwanted by some customer segments.
    """
    ATTRACTIVE = "Attractive"
    ONE_DIMENSIONAL = "One-dimensional"
    MUST_BE = "Must-be"
    INDIFFERENT = "Indifferent"
    REVERSE = "Reverse"


class ClassifiedFeature(BaseModel):
    """A single feature with its Kano category assignment."""
    id: str
    name: str
    category: KanoCategory
    reasoning: str


class ClassificationResult(BaseModel):
    """
    Structured output of the Classification Specialist Agent.
    Passed via handoff input_type to the Strategic Analyst.
    """
    product_name: str
    product_description: str
    target_market: str | None = None
    classified_features: list[ClassifiedFeature]
