import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="Fruit Quality Grading System",
    page_icon="🍎",
    layout="centered"
)

st.title("🍎 Automated Fruit Quality Grading and Freshness Classification System")
st.markdown("Upload a fruit image (**JPG** or **PNG**) to analyze its quality and freshness status.")

# File Uploader Widget
uploaded_file = st.file_uploader("Choose a fruit image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display Image Preview
    st.image(uploaded_file, caption="Uploaded Produce Preview", use_container_width=True)
    
    if st.button("🔍 Classify Fruit Quality", type="primary"):
        with st.spinner("Running ONNX inference via backend..."):
            try:
                # Prepare file payload
                file_bytes = uploaded_file.getvalue()
                files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type)}
                
                # Send request to FastAPI backend endpoint
                response = requests.post("http://127.0.0.1:8000/predict", files=files, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    prediction = result["prediction"]
                    confidence = result["confidence"]
                    is_fresh = result["is_fresh"]
                    probabilities = result["probabilities"]
                    
                    st.success("Analysis complete!")
                    st.divider()
                    
                    # Layout: Status Badge & Confidence Metric
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if is_fresh:
                            st.markdown(f"### 🟢 Status: **FRESH**")
                        else:
                            st.markdown(f"### 🔴 Status: **ROTTEN**")
                        st.markdown(f"**Identified Produce:** `{prediction.replace('_', ' ').title()}`")
                    
                    with col2:
                        st.metric(label="Top Confidence", value=f"{confidence:.2f}%")
                    
                    # Convert probabilities to percentages for the chart
                    pct_probabilities = {k: round(v * 100, 2) for k, v in probabilities.items()}
                    
                    # Display Class Probability Breakdown
                    st.subheader("Class Probability Distribution (%)")
                    st.bar_chart(pct_probabilities)
                    
                else:
                    try:
                        error_detail = response.json().get("detail", "Unknown server error")
                    except Exception:
                        error_detail = response.text
                    st.error(f"Server Error ({response.status_code}): {error_detail}")
                    
            except requests.exceptions.ConnectionError:
                st.warning("Backend REST API is unavailable. Please ensure your FastAPI server is running (`uvicorn backend.main:app --reload --port 8000`).")
            except requests.exceptions.Timeout:
                st.error("Inference request timed out. Check backend resource usage.")