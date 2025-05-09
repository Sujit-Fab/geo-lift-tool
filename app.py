import streamlit as st
import pandas as pd
import requests
import tempfile
import plotly.express as px

# ----------------------
# GeoLift Analysis Function
# ----------------------
def run_geolift_analysis(uploaded_file, holdout_percent, pre_test_weeks):
    # Save CSV to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        uploaded_file.seek(0)
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    
    # Call R Plumber API
    response = requests.post(
        "http://localhost:8000/geolift",
        json={
            "data_path": tmp_path,
            "params": {
                "holdout_percent": holdout_percent,
                "pre_test_weeks": pre_test_weeks
            }
        }
    )
    return response.json()

# ----------------------
# Main App
# ----------------------
def main():
    st.title("GeoLift Test Designer")
    
    # Sidebar: Upload & Parameters
    with st.sidebar:
        st.header("Upload & Settings")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        holdout_percent = st.slider("Holdout (%)", 5, 30, 10)
        pre_test_weeks = st.number_input("Pre-Test Weeks", min_value=4, value=8)
        
        if st.button("Run Analysis") and uploaded_file:
            try:
                results = run_geolift_analysis(uploaded_file, holdout_percent, pre_test_weeks)
                st.session_state.results = results
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Main Panel: Results
    if uploaded_file:
        st.subheader("Data Preview")
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head())
        
        if "results" in st.session_state:
            st.subheader("GeoLift Results")
            tab1, tab2, tab3 = st.tabs(["Groups", "Trends", "Recommendations"])
            
            with tab1:
                st.dataframe(st.session_state.results["groups"])
            
            with tab2:
                fig = px.line(
                    st.session_state.results["historical_data"],
                    x="date",
                    y="metric",
                    color="group",
                    title="Pre-Test Trends"
                )
                st.plotly_chart(fig)
            
            with tab3:
                st.write(f"**Test Duration:** {st.session_state.results['duration']} weeks")
                st.write(f"**Power:** {st.session_state.results['power']}%")
                st.write("**Next Steps:** Monitor metric deviations daily during the test.")

if __name__ == "__main__":
    main()