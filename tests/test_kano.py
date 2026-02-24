"""
Tests for Kano Model agent: schemas, coefficients, orchestrator (mocked), CLI.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError


class TestClassificationSchema:
    """Tests for classification/schema.py"""

    def test_kano_category_has_five_values(self):
        from classification.schema import KanoCategory
        categories = list(KanoCategory)
        assert len(categories) == 5

    def test_kano_category_string_values(self):
        from classification.schema import KanoCategory
        assert KanoCategory.ATTRACTIVE == "Attractive"
        assert KanoCategory.ONE_DIMENSIONAL == "One-dimensional"
        assert KanoCategory.MUST_BE == "Must-be"
        assert KanoCategory.INDIFFERENT == "Indifferent"
        assert KanoCategory.REVERSE == "Reverse"

    def test_classified_feature_valid(self):
        from classification.schema import ClassifiedFeature, KanoCategory
        f = ClassifiedFeature(
            id="feat-001",
            name="Dark Mode",
            category=KanoCategory.ATTRACTIVE,
            reasoning="Unexpected visual comfort feature — delights users.",
        )
        assert f.id == "feat-001"
        assert f.category == KanoCategory.ATTRACTIVE

    def test_classification_result_valid(self):
        from classification.schema import ClassificationResult, ClassifiedFeature, KanoCategory
        result = ClassificationResult(
            product_name="TestApp",
            product_description="A test SaaS product",
            classified_features=[
                ClassifiedFeature(
                    id="f1",
                    name="Login",
                    category=KanoCategory.MUST_BE,
                    reasoning="Required for product access.",
                )
            ],
        )
        assert result.product_name == "TestApp"
        assert len(result.classified_features) == 1

    def test_classification_result_accepts_none_target_market(self):
        from classification.schema import ClassificationResult
        result = ClassificationResult(
            product_name="X", product_description="Y", classified_features=[]
        )
        assert result.target_market is None
