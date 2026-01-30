#API_KEY: AIzaSyBqv9g9IrTMYxL6n7zun52j1vPo67iR6-8
#MAGIC_HOUR_KEY: mhk_live_oBBlvwx7K3YTxh8RcDXoUq6law1dk0IF43sqCVharoYJmgxNa9vCiqVQ9ev8qYHCQqarbuNgTIUkYvGx

import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import io

# --- Page Config ---
st.set_page_config(page_title="AI Photo Restoration", layout="wide")

# Setup - Use Streamlit Secrets for the API Key
# Go to Streamlit Cloud Settings -> Secrets and add: GEMINI_API_KEY = "your_key"
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    st.error("Missing API Key! Please add 'GEMINI_API_KEY' to Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

def invisible_ai_restore(image_bytes):
    try:
        # Step 1: Gemini analyzes the image to create a high-fidelity prompt
        analysis = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                "Describe this photo in extreme detail. Focus on the person's features, "
                "clothing, and background. Describe it as a flawless, 4K high-definition "
                "professional photograph, free of any noise, scratches, or blur."
            ]
        )
        detailed_prompt = analysis.text

        # Step 2: Imagen 3 generates the high-res version based on that description
        response = client.models.generate_image(
            model="imagen-3.0-generate-002",
            prompt=f"A professional photo restoration, ultra-high resolution: {detailed_prompt}",
            config=types.GenerateImageConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                output_mime_type="image/jpeg"
            )
        )
        
        # Extract image bytes from the response
        return response.generated_images[0].image.image_bytes

    except Exception as e:
        st.error(f"Restoration Error: {e}")
        return None

# --- Streamlit Interface ---
st.title("✨ Hidden Engine Restorer")
st.markdown("This tool uses **Gemini 2.0** to analyze damage and **Imagen 3** to rebuild the pixels.")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    img_data = uploaded_file.getvalue()
    
    with col1:
        st.subheader("Original")
        st.image(img_data, use_container_width=True)
        if st.button("Restore Now"):
            with st.spinner("Analyzing and Rebuilding..."):
                result_bytes = invisible_ai_restore(img_data)
                if result_bytes:
                    st.session_state['result'] = result_bytes

    with col2:
        st.subheader("Restored")
        if 'result' in st.session_state:
            st.image(st.session_state['result'], use_container_width=True)
            
            # Add a Download Button
            st.download_button(
                label="Download Restored Image",
                data=st.session_state['result'],
                file_name="restored_image.jpg",
                mime="image/jpeg"
            )
        else:
            st.info("Click 'Restore Now' to see the AI magic.")
