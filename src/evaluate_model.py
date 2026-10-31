
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print("=" * 55)
print("WORLDCORE MODEL EVALUATION")
print("=" * 55)

df = pd.read_csv("reports/model_predictions.csv")

actual = df["actual"]
predicted = df["predicted"]
baseline = df["baseline_prediction"]

mae = mean_absolute_error(actual, predicted)
rmse = np.sqrt(mean_squared_error(actual, predicted))
r2 = r2_score(actual, predicted)

baseline_mae = mean_absolute_error(actual, baseline)
baseline_rmse = np.sqrt(mean_squared_error(actual, baseline))

print("\nMODEL PERFORMANCE")
print(f"Model MAE: {mae:.4f} cm")
print(f"Model RMSE: {rmse:.4f} cm")
print(f"Model R2: {r2:.4f}")

print("\nBASELINE PERFORMANCE")
print(f"Baseline MAE: {baseline_mae:.4f} cm")
print(f"Baseline RMSE: {baseline_rmse:.4f} cm")

Path("reports").mkdir(exist_ok=True)

# Actual vs predicted
plt.figure(figsize=(12, 5))
plt.plot(actual.values, label="Actual")
plt.plot(predicted.values, label="Predicted")
plt.title("Actual vs Predicted Water Levels")
plt.xlabel("Test Observation")
plt.ylabel("Water Level (cm)")
plt.legend()
plt.tight_layout()
plt.savefig("reports/actual_vs_predicted.png")
plt.close()

# Prediction errors
errors = actual.values - predicted.values

plt.figure(figsize=(9, 5))
plt.hist(errors, bins=30)
plt.title("Prediction Error Distribution")
plt.xlabel("Prediction Error (cm)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("reports/prediction_error_distribution.png")
plt.close()

# Baseline comparison
comparison = pd.DataFrame({
    "Model": ["Random Forest", "Baseline"],
    "MAE": [mae, baseline_mae],
    "RMSE": [rmse, baseline_rmse]
})

comparison.to_csv("reports/model_comparison.csv", index=False)

print("\nCharts saved:")
print("reports/actual_vs_predicted.png")
print("reports/prediction_error_distribution.png")
print("reports/model_comparison.csv")

print("\nWORLDCORE EVALUATION COMPLETED!")
