import argparse
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

def make_features(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["lane", "timestamp"])
    df["hour"] = df["timestamp"].dt.hour
    df["minute_of_day"] = df["timestamp"].dt.hour * 60 + df["timestamp"].dt.minute
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["count_lag_1"] = df.groupby("lane")["vehicle_count"].shift(1)
    df["count_lag_2"] = df.groupby("lane")["vehicle_count"].shift(2)
    df["count_lag_4"] = df.groupby("lane")["vehicle_count"].shift(4)
    # Predict count 15 minutes in the future.
    df["target_next"] = df.groupby("lane")["vehicle_count"].shift(-1)
    return df

def usable(df, features):
    """Rows with a known target (for training/testing)."""
    return df.dropna(subset=features + ["target_next"]).copy()

def density_label(count):
    if count < 5:
        return "LOW"
    if count < 12:
        return "MEDIUM"
    return "HIGH"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="traffic_history.csv")
    parser.add_argument("--lane", default=None, help="Lane name; default = first lane in the CSV")
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    required = {"timestamp", "lane", "vehicle_count"}
    if not required.issubset(df.columns):
        raise ValueError("CSV must have columns: timestamp,lane,vehicle_count")

    if args.lane is None:
        args.lane = sorted(df["lane"].unique())[0]
    if args.lane not in set(df["lane"]):
        raise ValueError(f"Lane '{args.lane}' not found. Available lanes: {sorted(df['lane'].unique())}")
    # Train one model per lane: lanes behave differently.
    df = df[df["lane"] == args.lane]
    features = ["hour", "minute_of_day", "day_of_week", "count_lag_1", "count_lag_2", "count_lag_4"]
    full = make_features(df)
    data = usable(full, features)
    if len(data) < 30:
        raise ValueError("Not enough rows after creating history features. Collect more interval-based counts.")

    # Time-ordered split; do not shuffle future records into training.
    data = data.sort_values("timestamp")
    split = int(len(data) * 0.8)
    train, test = data.iloc[:split], data.iloc[split:]
    model = RandomForestRegressor(n_estimators=150, random_state=42, min_samples_leaf=2)
    model.fit(train[features], train["target_next"])
    predictions = model.predict(test[features])
    mae = mean_absolute_error(test["target_next"], predictions)
    print(f"Holdout MAE: {mae:.2f} vehicles per 15-minute interval")
    print("MAE is meaningful only when input data is real and representative.")

    # Use the truly latest observation (its target is unknown, which is what we predict)
    ready = full.dropna(subset=features).sort_values("timestamp")
    last = ready.iloc[-1]
    latest = pd.DataFrame([last[features].to_dict()])
    predicted_count = max(0, round(float(model.predict(latest)[0])))
    print(f"Lane: {args.lane}")
    print(f"Last observed timestamp: {last['timestamp']}")
    print(f"Predicted vehicles in next 15-minute interval: {predicted_count}")
    print(f"Predicted traffic level: {density_label(predicted_count)}")

if __name__ == "__main__":
    main()
