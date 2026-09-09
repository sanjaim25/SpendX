import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app.ml_models.naive_bayes_model import predict_category, predict_category_with_confidence
from backend.app.ml_models.linear_regression_model import forecast_next_month


class TestNaiveBayes:
    def test_food_categorization(self):
        assert predict_category("swiggy order biryani") == "Food"

    def test_transport_categorization(self):
        assert predict_category("uber cab ride") == "Transport"

    def test_entertainment_categorization(self):
        assert predict_category("netflix subscription streaming") == "Entertainment"

    def test_bills_categorization(self):
        assert predict_category("electricity bill payment") == "Bills"

    def test_confidence_output(self):
        result = predict_category_with_confidence("zomato pizza")
        assert 'category' in result
        assert 'confidence_score' in result
        assert 0 <= result['confidence_score'] <= 100


class TestSemanticClassifier:
    def test_food_categorization(self):
        from backend.app.ml_models.semantic_classifier import predict_category_semantic
        result = predict_category_semantic("swiggy order biryani")
        assert result["category"] == "Food"

    def test_transport_categorization(self):
        from backend.app.ml_models.semantic_classifier import predict_category_semantic
        result = predict_category_semantic("uber cab ride")
        assert result["category"] == "Transport"

    def test_entertainment_categorization(self):
        from backend.app.ml_models.semantic_classifier import predict_category_semantic
        result = predict_category_semantic("netflix subscription streaming")
        assert result["category"] == "Entertainment"

    def test_bills_categorization(self):
        from backend.app.ml_models.semantic_classifier import predict_category_semantic
        result = predict_category_semantic("electricity bill payment")
        assert result["category"] == "Bills"

    def test_gibberish_categorization(self):
        from backend.app.ml_models.semantic_classifier import predict_category_semantic
        result = predict_category_semantic("xyzzy foobar blargh")
        assert result["category"] == "Uncategorized"

    def test_confidence_output(self):
        from backend.app.ml_models.semantic_classifier import predict_category_semantic
        result = predict_category_semantic("zomato pizza")
        assert 'category' in result
        assert 'confidence' in result
        assert 'all_scores' in result
        assert 0.0 <= result['confidence'] <= 1.0


class TestLinearRegression:
    def test_forecast_with_enough_data(self):
        data = [(1, 5000), (2, 5500), (3, 6000), (4, 6500)]
        result = forecast_next_month(data)
        assert result['predicted_amount'] > 0
        assert result['trend'] in ['increasing', 'decreasing', 'stable']

    def test_forecast_with_insufficient_data(self):
        data = [(1, 5000)]
        result = forecast_next_month(data)
        assert result['trend'] == 'insufficient_data'

    def test_forecast_no_negative(self):
        data = [(1, 1000), (2, 500), (3, 100)]
        result = forecast_next_month(data)
        assert result['predicted_amount'] >= 0
