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


class TestAnalysisSchema:
    """Tests for analysis/schema.py"""

    def test_kano_input_valid(self):
        from analysis.schema import KanoInput, Feature
        inp = KanoInput(
            product_name="My SaaS",
            product_description="A project management tool",
            features=[
                Feature(id="f1", name="Real-time sync", description="Sync data across devices instantly"),
                Feature(id="f2", name="Dark mode", description="Dark color theme for the UI"),
            ],
        )
        assert len(inp.features) == 2
        assert inp.target_market is None

    def test_satisfaction_coefficient_must_be_zero_to_one(self):
        from analysis.schema import ClassifiedFeatureWithCoefficients
        from classification.schema import KanoCategory
        with pytest.raises(ValidationError):
            ClassifiedFeatureWithCoefficients(
                id="f1", name="X",
                category=KanoCategory.ATTRACTIVE,
                reasoning="test",
                satisfaction_coefficient=1.5,       # invalid — must be <= 1.0
                dissatisfaction_coefficient=-0.1,
            )

    def test_dissatisfaction_coefficient_must_be_negative(self):
        from analysis.schema import ClassifiedFeatureWithCoefficients
        from classification.schema import KanoCategory
        with pytest.raises(ValidationError):
            ClassifiedFeatureWithCoefficients(
                id="f1", name="X",
                category=KanoCategory.MUST_BE,
                reasoning="test",
                satisfaction_coefficient=0.1,
                dissatisfaction_coefficient=0.2,    # invalid — must be <= 0.0
            )

    def test_coefficients_are_rounded_to_three_decimals(self):
        from analysis.schema import ClassifiedFeatureWithCoefficients
        from classification.schema import KanoCategory
        f = ClassifiedFeatureWithCoefficients(
            id="f1", name="Login",
            category=KanoCategory.MUST_BE,
            reasoning="Required.",
            satisfaction_coefficient=0.05123456,
            dissatisfaction_coefficient=-0.94876543,
        )
        assert f.satisfaction_coefficient == 0.051
        assert f.dissatisfaction_coefficient == -0.949

    def test_kano_output_structure(self):
        from analysis.schema import KanoOutput, Roadmap, ClassifiedFeatureWithCoefficients
        from classification.schema import KanoCategory
        output = KanoOutput(
            product_name="TestApp",
            features=[
                ClassifiedFeatureWithCoefficients(
                    id="f1", name="Login",
                    category=KanoCategory.MUST_BE,
                    reasoning="Required.",
                    satisfaction_coefficient=0.05,
                    dissatisfaction_coefficient=-0.95,
                )
            ],
            summary={"Must-be": 1},
            roadmap=Roadmap(
                immediate_priorities=["Login"],
                performance_investments=[],
                innovation_bets=[],
                deprioritize=[],
            ),
            strategic_narrative="Prioritize must-be features immediately.",
        )
        assert output.product_name == "TestApp"
        assert output.html_report is None  # not set by LLM




class TestOrchestrator:
    """Tests for orchestrator.py — mocked Runner."""

    def test_run_kano_pipeline_returns_kano_output(self, monkeypatch):
        from unittest.mock import MagicMock, patch
        from analysis.schema import KanoInput, KanoOutput, Roadmap, Feature, ClassifiedFeatureWithCoefficients
        from classification.schema import KanoCategory
        from orchestrator import run_kano_pipeline

        mock_output = KanoOutput(
            product_name="TestApp",
            features=[
                ClassifiedFeatureWithCoefficients(
                    id="feat-001",
                    name="Login",
                    category=KanoCategory.MUST_BE,
                    reasoning="Required for access.",
                    satisfaction_coefficient=0.1,
                    dissatisfaction_coefficient=-0.9,
                )
            ],
            summary={"Must-be": 1},
            roadmap=Roadmap(
                immediate_priorities=["Login"],
                performance_investments=[],
                innovation_bets=[],
                deprioritize=[],
            ),
            strategic_narrative="Implement login immediately.",
        )

        mock_result = MagicMock()
        mock_result.final_output = mock_output

        with patch("orchestrator.get_classification_agent", return_value=MagicMock()), \
             patch("orchestrator.Runner.run_sync", return_value=mock_result):
            kano_input = KanoInput(
                product_name="TestApp",
                product_description="A test application",
                features=[Feature(id="feat-001", name="Login", description="User login")],
            )
            result = run_kano_pipeline(kano_input)

        assert isinstance(result, KanoOutput)
        assert result.product_name == "TestApp"
        assert len(result.features) == 1

    def test_run_kano_pipeline_raises_on_wrong_output_type(self):
        from unittest.mock import MagicMock, patch
        from analysis.schema import KanoInput, Feature
        from orchestrator import run_kano_pipeline

        mock_result = MagicMock()
        mock_result.final_output = "not a KanoOutput"

        with patch("orchestrator.get_classification_agent", return_value=MagicMock()), \
             patch("orchestrator.Runner.run_sync", return_value=mock_result):
            kano_input = KanoInput(
                product_name="X",
                product_description="Y",
                features=[Feature(id="f1", name="F", description="D")],
            )
            with pytest.raises(RuntimeError, match="KanoOutput"):
                run_kano_pipeline(kano_input)
