
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix,
)
from xgboost import XGBClassifier
sys.path.append(str(Path(__file__).resolve().parents[2]))
from ml.features.extractor import extract_features, feature_names

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "PhiUSIIL_Phishing_URL_Dataset.csv"
ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
SAMPLE_SIZE = 15000      
RANDOM_STATE = 42        
def load_and_sample_data():
    print(f"Loading dataset from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)
    print(f"Full dataset: {len(df)} rows")
    print(f"Class counts: {df['label'].value_counts().to_dict()}")
    per_class = SAMPLE_SIZE // 2
    legit = df[df["label"] == 1].sample(n=min(per_class, (df["label"] == 1).sum()), random_state=RANDOM_STATE)
    phish = df[df["label"] == 0].sample(n=min(per_class, (df["label"] == 0).sum()), random_state=RANDOM_STATE)
    df_sampled = pd.concat([legit, phish]).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    print(f"Sampled down to: {len(df_sampled)} rows")
    return df_sampled
def build_feature_table(df):
    print("Extracting features from each URL (this can take a minute)...")
    rows = []
    for url in df["URL"]:
        rows.append(extract_features(url))
    features_df = pd.DataFrame(rows)
    labels = df["label"].values
    return features_df, labels
def evaluate_model(name, model, X_test, y_test):
    preds = model.predict(X_test)
    metrics = {
        "accuracy": round(accuracy_score(y_test, preds), 4),
        "precision": round(precision_score(y_test, preds), 4),
        "recall": round(recall_score(y_test, preds), 4),
        "f1": round(f1_score(y_test, preds), 4),
        "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
    }
    print(f"\n{name}")
    print(f"  accuracy:  {metrics['accuracy']}")
    print(f"  precision: {metrics['precision']}")
    print(f"  recall:    {metrics['recall']}")
    print(f"  f1:        {metrics['f1']}")
    print(f"  confusion matrix: {metrics['confusion_matrix']}")
    return metrics


def main():
    df = load_and_sample_data()
    X, y = build_feature_table(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\nTrain size: {len(X_train)}, Test size: {len(X_test)}")

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE),
        "xgboost": XGBClassifier(eval_metric="logloss", random_state=RANDOM_STATE),
    }

    results = {}
    trained_models = {}

    for name, model in models.items():
        start = time.time()
        model.fit(X_train, y_train)
        elapsed = round(time.time() - start, 2)
        print(f"\nTrained {name} in {elapsed}s")
        results[name] = evaluate_model(name, model, X_test, y_test)
        trained_models[name] = model

    # Pick the final model. Recall matters most here -- missing a real
    # phishing URL (false negative) is worse than wrongly flagging a
    # safe one -- so we sort by recall first. But recall alone can tie
    # between models, and a tie shouldn't be broken arbitrarily. When
    # models are within 0.005 recall of each other, treat that as a
    # tie and break it using F1 (which balances precision and recall),
    # so the model that's actually stronger overall wins the tie.
    best_recall = max(results[n]["recall"] for n in results)
    tied_models = [n for n in results if best_recall - results[n]["recall"] <= 0.005]

    if len(tied_models) > 1:
        best_name = max(tied_models, key=lambda n: results[n]["f1"])
        tie_note = (
            f"Tied on recall (~{best_recall}) with {tied_models}, "
            f"broke the tie using F1 score."
        )
    else:
        best_name = tied_models[0]
        tie_note = "Clear winner on recall, no tie to break."

    best_model = trained_models[best_name]

    print(f"\n{'='*40}")
    print(f"Selected model: {best_name}")
    print(f"Reason: highest recall ({results[best_name]['recall']}) among the three,")
    print("which matters most for not missing real phishing URLs.")
    print(tie_note)
    print(f"{'='*40}")

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = ARTIFACTS_DIR / "model.joblib"
    joblib.dump(best_model, model_path)
    print(f"\nSaved model to {model_path}")

   
    feature_metadata = {
        "features": feature_names(),
        "num_features": len(feature_names()),
    }
    with open(ARTIFACTS_DIR / "feature_metadata.json", "w") as f:
        json.dump(feature_metadata, f, indent=2)

   
    model_metadata = {
        "model": best_name,
        "version": "1.0",
        "features": feature_names(),
        "training_dataset": "PhiUSIIL Phishing URL Dataset (sampled, n={})".format(len(df)),
        "metrics": results[best_name],
        "all_models_compared": {k: v for k, v in results.items()},
        "selection_reasoning": (
            f"Selected for highest recall ({results[best_name]['recall']}), "
            f"prioritized over raw accuracy because missing a real phishing "
            f"URL (false negative) is more costly than wrongly flagging a "
            f"safe one. {tie_note}"
        ),
        "training_date": datetime.now(timezone.utc).isoformat(),
    }
    with open(ARTIFACTS_DIR / "model_metadata.json", "w") as f:
        json.dump(model_metadata, f, indent=2)

    print(f"Saved metadata to {ARTIFACTS_DIR}/")
    print("\nDone.")


if __name__ == "__main__":
    main()
