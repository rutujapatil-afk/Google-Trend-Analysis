import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from prophet import Prophet

# App Title
st.title("📊 Google Search Trends Analysis")
st.markdown("""
Welcome to the **Google Search Trends Analysis** app. Upload your dataset to explore trends, correlations, clusters, and future forecasts for topics of interest.
""")

# File Upload Section
st.subheader("📂 Upload Dataset")
uploaded_file = st.file_uploader("Upload your CSV file", type="csv", help="Upload a CSV file containing the search trends data.")

if uploaded_file:
    # Read the CSV file into a DataFrame
    data = pd.read_csv(uploaded_file)
    
    # Convert 'Month' column to datetime format (if not already)
    if 'Month' in data.columns and data['Month'].dtype == 'O':  # Check if 'Month' is a string/object type
        data['Month'] = pd.to_datetime(data['Month'], format='%Y-%m', errors='coerce')
    
    # Ensure 'Month' column exists and is in datetime format
    if 'Month' not in data.columns or data['Month'].isna().any():
        st.error("The dataset must contain a valid 'Month' column in YYYY-MM format.")
    else:
        # Display dataset preview
        st.subheader("📋 Dataset Overview")
        st.dataframe(data.head())

        # Trend Visualization
        with st.expander("1️⃣ Trend Visualization", expanded=True):
            st.subheader("📈 Visualize Search Trends Over Time")
            st.markdown("Select a topic to see its search trend over time.")
            topic = st.selectbox("Select Topic", data.columns[1:], key="trend_topic")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(data['Month'], data[topic], label=topic, color="blue", linewidth=2)
            ax.set_title(f"Trend for '{topic}'", fontsize=16)
            ax.set_xlabel("Month", fontsize=12)
            ax.set_ylabel("Search Interest", fontsize=12)
            ax.legend(loc="upper left")
            st.pyplot(fig)

        # Correlation Analysis
        with st.expander("2️⃣ Correlation Analysis", expanded=True):
            st.subheader("🔗 Explore Correlations Between Topics")
            st.markdown("Analyze the relationship between different topics in the dataset.")
            numeric_data = data.select_dtypes(include=['number'])
            corr_matrix = numeric_data.corr()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, cbar=True)
            st.pyplot(fig)

        # Clustering Topics
        with st.expander("3️⃣ Clustering Topics Based on Trends", expanded=True):
            st.subheader("🔍 Discover Clusters of Similar Topics")
            st.markdown("Group topics based on their search trends.")
            num_clusters = st.selectbox("Select Number of Clusters:", options=[2, 3, 4, 5, 6, 7, 8, 9, 10], index=2)
            st.write(f"Performing clustering with {num_clusters} clusters...")
            
            # Handle non-numeric values and missing data
            data_cleaned = data.select_dtypes(include=['number']).fillna(0)  # Use only numeric data
            
            # Standardize the data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(data_cleaned)
            
            # Apply KMeans clustering
            kmeans = KMeans(n_clusters=num_clusters, random_state=42)
            data['Cluster'] = kmeans.fit_predict(scaled_data)
            
            # Cluster Summary (numeric columns only)
            cluster_summary = data.groupby('Cluster').mean(numeric_only=True)
            st.write("Cluster Assignments")
            st.dataframe(cluster_summary.style.highlight_max(axis=0))
            
            # Visualizing Cluster Centroids
            st.write("Cluster Centroids Heatmap")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(
                pd.DataFrame(kmeans.cluster_centers_, columns=data_cleaned.columns),
                annot=True,
                cmap="coolwarm",
                ax=ax
            )
            st.pyplot(fig)

        # Time-Series Forecasting
        with st.expander("4️⃣ Time-Series Forecasting", expanded=True):
            st.subheader("📅 Predict Future Trends")
            st.markdown("Use the Prophet model to forecast future trends for a selected topic.")
            forecast_topic = st.selectbox("Select Topic for Forecasting", data.columns[1:], key="forecast_topic")
            st.write(f"Forecasting future trends for '{forecast_topic}'...")
            
            # Prepare data for forecasting
            df = data[['Month', forecast_topic]].rename(columns={"Month": "ds", forecast_topic: "y"})
            model = Prophet()
            model.fit(df)
            future = model.make_future_dataframe(periods=12, freq='M')
            forecast = model.predict(future)

            # Plot forecast
            fig = model.plot(forecast)
            st.pyplot(fig)

        # Insights Section
        st.write("📊 **Insights and Recommendations**")
        st.markdown("""
        - Identify growing or declining interest in various topics over time.
        - Use clustering to discover related topics that share similar trends.
        - Plan marketing strategies or research initiatives based on these trends.
        """)

else:
    # If no file is uploaded, show a message prompting the user to upload a file
    st.warning("Please upload a CSV file to proceed with the analysis.")
