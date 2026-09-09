import numpy as np
from sklearn.linear_model import LinearRegression


def forecast_next_month(monthly_totals: list) -> dict:
    """
    Predict next month's spending using Linear Regression.

    Args:
        monthly_totals: list of (month_index, total_amount) tuples

    Returns:
        dict with predicted amount and trend info
    """
    if len(monthly_totals) < 2:
        avg = monthly_totals[0][1] if monthly_totals else 5000.0
        return {
            'predicted_amount': round(avg, 2),
            'trend': 'insufficient_data',
            'message': 'Need more data for accurate prediction'
        }

    X = np.array([item[0] for item in monthly_totals]).reshape(-1, 1)
    y = np.array([item[1] for item in monthly_totals])

    model = LinearRegression()
    model.fit(X, y)

    next_month_index = X[-1][0] + 1
    predicted = model.predict([[next_month_index]])[0]
    predicted = max(0, predicted)  # No negative spending

    slope = model.coef_[0]
    trend = 'increasing' if slope > 50 else ('decreasing' if slope < -50 else 'stable')

    return {
        'predicted_amount': round(predicted, 2),
        'slope': round(slope, 2),
        'trend': trend,
        'r_squared': round(model.score(X, y), 4),
        'months_analyzed': len(monthly_totals),
        'message': f"Spending trend is {trend}. Predicted next month: ₹{round(predicted, 2)}"
    }


def forecast_category_wise(category_monthly: dict) -> dict:
    """
    Predict next month's spending per category.

    Args:
        category_monthly: dict of {category: [(month_idx, amount), ...]}

    Returns:
        dict of {category: predicted_amount}
    """
    results = {}
    for category, data in category_monthly.items():
        if len(data) >= 2:
            forecast = forecast_next_month(data)
            results[category] = forecast['predicted_amount']
        elif len(data) == 1:
            results[category] = data[0][1]
        else:
            results[category] = 0.0
    return results


if __name__ == '__main__':
    sample_data = [(1, 8000), (2, 8500), (3, 9000), (4, 9200), (5, 9800)]
    result = forecast_next_month(sample_data)
    print("Forecast Result:", result)
