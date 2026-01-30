import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import io

# --- Page Config ---
st.set_page_config(page_title="AI Photo Restoration", layout="wide")

# Setup - Fetch from Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("Missing GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

def invisible_ai_restore(image_bytes):
    try:
        # STEP 1: Using 1.5-flash for maximum stability
        analysis = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                "Describe this vintage photo in 4K detail. Focus on skin texture, "
                "clothing patterns, and sharp eyes to guide a perfect restoration."
            ]
        )

        # STEP 2: Restoration via Imagen
        response = client.models.generate_image(
            model="imagen-3.0-generate-002",
            prompt=f"A professional photo restoration, ultra-high resolution: {analysis.text}",
            config=types.GenerateImageConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                output_mime_type="image/jpeg"
            )
        )
        return response.generated_images[0].image.image_bytes

    except Exception as e:
        # Check specifically for the 'limit: 0' quota error
        if "429" in str(e):
            st.error("🚨 **Quota Locked (Limit: 0)**")
            st.warning("""
                This happens when a Google Cloud Project hasn't 'verified' its identity. 
                1. Go to [Google Cloud Console](https://console.cloud.google.com/).
                2. Select your project.
                3. Link a Billing Account (even the Free Trial works).
                4. Enable the 'Vertex AI API'.
            """)
        else:
            st.error(f"Error: {e}")
        return None

# --- UI Interface ---
st.title("✨ AI Heritage Restorer")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    img_data = uploaded_file.getvalue()
    
    with col1:
        st.subheader("Original")
        # Updated 2026 Streamlit Syntax: width='stretch' replaces use_container_width=True
        st.image(img_data, width='stretch', caption="Input")
        
        if st.button("Restore Now"):
            with st.spinner("AI Brains are working..."):
                result_bytes = invisible_ai_restore(img_data)
                if result_bytes:
                    st.session_state['result'] = result_bytes

    with col2:
        st.subheader("Restored")
        if 'result' in st.session_state:
            # Updated 2026 Streamlit Syntax
            st.image(st.session_state['result'], width='stretch', caption="AI Output")
            
            st.download_button(
                label="Download Result",
                data=st.session_state['result'],
                file_name="restored.jpg",
                mime="image/jpeg"
            )
        else:
            st.info("Results will appear here.")
