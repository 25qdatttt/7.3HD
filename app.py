import streamlit as st
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from lightgbm import LGBMRegressor

# ==========================
# Load dataset (smaller version for speed)
# ==========================
df = pd.read_csv("Melbourne_full_clean.csv")

# Features & target
target = "price"
numeric_cols = ["rooms", "bathroom", "car", "landsize", "buildingarea", "yearbuilt", "building_age"]
categorical_cols = ["suburb", "type", "councilarea", "regionname"]

X = df[numeric_cols + categorical_cols]
y = df[target]

# ==========================
# Preprocessing
# ==========================
numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocess = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_cols),
        ("cat", categorical_transformer, categorical_cols)
    ]
)

# ==========================
# Model (LightGBM)
# ==========================
model = Pipeline(steps=[
    ("preprocess", preprocess),
    ("model", LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=-1,
        random_state=42,
        n_jobs=-1
    ))
])
model.fit(X, y)

# ==========================
# Streamlit UI
# ==========================
st.set_page_config(page_title="Melbourne Housing Price Predictor", page_icon="🏡", layout="wide")

st.markdown("<h1 style='text-align: center; color: #2E86C1;'>🏡 Melbourne Housing Price Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:16px;'>Predict housing prices based on property details and location 📍</p>", unsafe_allow_html=True)

user_input = {}

# --- Row 1: main sliders ---
st.subheader("Basic Information")
col1, col2, col3 = st.columns(3)
with col1:
    user_input["rooms"] = st.slider("🛏️ Rooms", min_value=1, max_value=5, value=3)
with col2:
    user_input["bathroom"] = st.slider("🚿 Bathrooms", min_value=1, max_value=5, value=2)
with col3:
    user_input["car"] = st.slider("🚗 Car Spaces", min_value=0, max_value=5, value=1)

# --- Row 2: Optional numeric in expander ---
with st.expander("🔧 More House Details (optional)"):
    col4, col5, col6, col7 = st.columns(4)
    for col, name, label in zip([col4, col5, col6, col7],
                                ["landsize", "buildingarea", "yearbuilt", "building_age"],
                                ["📐 Land Size (m²)", "🏗️ Building Area (m²)", "📅 Year Built", "⏳ Building Age"]):
        with col:
            val = st.text_input(label, value="")
            if val.strip() == "":
                user_input[name] = np.nan
            else:
                try:
                    user_input[name] = float(val)
                except:
                    user_input[name] = np.nan

# --- Row 3: Categorical ---
st.subheader("Location Information")
col8, col9 = st.columns(2)
with col8:
    suburb_val = st.selectbox("🏘️ Suburb", [""] + sorted(df["suburb"].dropna().unique().tolist()))
    user_input["suburb"] = np.nan if suburb_val == "" else suburb_val
with col9:
    type_val = st.selectbox("🏠 Property Type", [""] + sorted(df["type"].dropna().unique().tolist()))
    user_input["type"] = np.nan if type_val == "" else type_val

col10, col11 = st.columns(2)
with col10:
    council_val = st.selectbox("🏛️ Council Area", [""] + sorted(df["councilarea"].dropna().unique().tolist()))
    user_input["councilarea"] = np.nan if council_val == "" else council_val
with col11:
    region_val = st.selectbox("🌏 Region Name", [""] + sorted(df["regionname"].dropna().unique().tolist()))
    user_input["regionname"] = np.nan if region_val == "" else region_val

# Convert to DataFrame
input_df = pd.DataFrame([user_input])

# --- Prediction Button ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔮 Predict Price"):
    prediction = model.predict(input_df)[0]
    st.markdown(
        f"<h2 style='text-align:center; color:#27AE60;'>💰 Estimated Price: ${prediction:,.0f} AUD</h2>",
        unsafe_allow_html=True
    )
