#API_KEY: AIzaSyBqv9g9IrTMYxL6n7zun52j1vPo67iR6-8
#MAGIC_HOUR_KEY: mhk_live_oBBlvwx7K3YTxh8RcDXoUq6law1dk0IF43sqCVharoYJmgxNa9vCiqVQ9ev8qYHCQqarbuNgTIUkYvGx

import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import io

# Setup - Use your Gemini API Key
GEMINI_API_KEY = "AIzaSyBqv9g9IrTMYxL6n7zun52j1vPo67iR6-8"
client = genai.Client(api_key=GEMINI_API_KEY)

def invisible_ai_restore(image_bytes):
    """
    Step 1: Gemini analyzes the blur.
    Step 2: Imagen 4 generates the restored version.
    """
    try:
        # First, Gemini 'looks' at the photo to understand what to fix
        analysis = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                "Describe this photo in extreme detail so an artist could recreate it "
                "perfectly but in 4K high definition, removing all blur and noise."
            ]
        )
        detailed_prompt = analysis.text

        # Second, we send that 'perfect description' to the Image Engine
        # This model is specifically built to output IMAGE pixels.
        response = client.models.generate_image(
            model="imagen-3.0-generate-002", # Or 'imagen-4.0-generate-001' if available
            prompt=f"A professional 4K photo restoration: {detailed_prompt}",
            config=types.GenerateImageConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                output_mime_type="image/jpeg"
            )
        )
        
        # Get the actual image data
        return response.generated_images[0].image.image_bytes

    except Exception as e:
        st.error(f"Restoration Error: {e}")
        return None

# --- Streamlit Interface ---
st.title("✨ Hidden Engine Restorer")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"])

if uploaded_file:
    col1, col2 = st.columns(2)
    with col1:
        st.image(uploaded_file, caption="Original")
        if st.button("Restore Now"):
            with st.spinner("AI Brains are working..."):
                result = invisible_ai_restore(uploaded_file.getvalue())
                if result:
                    st.session_state['result'] = result

    with col2:
        if 'result' in st.session_state:
            st.image(st.session_state['result'], caption="Restored")
