import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from lightgbm import LGBMRegressor


def test_pipeline_runs():
    df = pd.DataFrame({
        "rooms": [2, 3],
        "bathroom": [1, 2],
        "car": [1, 0],
        "landsize": [200, 300],
        "buildingarea": [100, 150],
        "yearbuilt": [2000, 2010],
        "building_age": [25, 15],
        "suburb": ["Abbotsford", "Abbotsford"],
        "type": ["h", "u"],
        "councilarea": ["Yarra", "Yarra"],
        "regionname": [
            "Northern Metropolitan",
            "Northern Metropolitan"
        ],
        "price": [800000, 1000000],
    })

    X = df.drop("price", axis=1)
    y = df["price"]

    numeric_cols = [
        "rooms", "bathroom", "car",
        "landsize", "buildingarea",
        "yearbuilt", "building_age",
    ]
    categorical_cols = [
        "suburb", "type",
        "councilarea", "regionname",
    ]

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocess = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )

    model = Pipeline(steps=[
        ("preprocess", preprocess),
        ("model", LGBMRegressor(
            n_estimators=10,
            random_state=42,
        )),
    ])

    model.fit(X, y)
    preds = model.predict(X)

    assert len(preds) == len(y)
