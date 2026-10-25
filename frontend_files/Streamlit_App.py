import streamlit as st
import requests
import pandas as pd
import io

# Configure page title and styling
st.set_page_config(page_title="SuperKart Sales Forecaster", layout="wide")

st.title("🏪 SuperKart Store Sales Forecaster")
st.write("Provide product and store specifications below to predict the total sales revenue.")

# Backend API base URL (configured via Docker internal network or public Codespace URL)
# By default, we use localhost for local testing, but it can be changed via sidebar input
backend_url = st.sidebar.text_input("Backend API Base URL", "http://backend:7860")

tabs = st.tabs(["🎯 Online Prediction", "📊 Batch Prediction"])

with tabs[0]:
    st.header("Single Product Sales Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_weight = st.number_input("Product Weight (kg)", min_value=0.0, max_value=50.0, value=12.5, step=0.1)
        product_sugar = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        allocated_area = st.number_input("Product Allocated Area (ratio)", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
        product_mrp = st.number_input("Product MRP ($)", min_value=0.0, max_value=1000.0, value=150.0, step=1.0)
        product_id_char = st.selectbox("Product Category Identifier", ["FD", "DR", "NC"])
        
    with col2:
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_city = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
        store_age = st.number_input("Store Age (Years)", min_value=1, max_value=100, value=15, step=1)
        product_type_cat = st.selectbox("Product Perishability Category", ["Perishables", "Non Perishables"])

    if st.button("Predict Sales"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar,
            "Product_Allocated_Area": allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_city,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": int(store_age),
            "Product_Type_Category": product_type_cat
        }
        
        try:
            response = requests.post(f"{backend_url}/v1/predict", json=payload)
            if response.status_code == 200:
                result = response.json()
                predicted_sales = result["prediction"]
                st.success(f"💰 Predicted Store Sales Total: **${predicted_sales:,.2f}**")
            else:
                st.error(f"Error from server (Status {response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"Could not connect to backend server: {str(e)}")

with tabs[1]:
    st.header("Upload CSV for Bulk Predictions")
    uploaded_file = st.file_uploader("Upload Batch CSV file", type=["csv"])
    
    if uploaded_file is not None:
        # Read and preview uploaded data
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head())
        
        if st.button("Run Batch Inference"):
            # Reset the file pointer to the beginning for uploading
            uploaded_file.seek(0)
            files = {"file": (uploaded_file.name, uploaded_file.read(), "text/csv")}
            
            try:
                response = requests.post(f"{backend_url}/v1/predictbatch", files=files)
                if response.status_code == 200:
                    predictions = response.json()
                    # Map predictions back to the DataFrame
                    pred_series = pd.Series(predictions).astype(float)
                    df["Predicted_Sales"] = pred_series.values
                    st.success("Batch predictions completed successfully!")
                    st.dataframe(df)
                else:
                    st.error(f"Error from server (Status {response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"Could not connect to backend server: {str(e)}")