#API_KEY: AIzaSyCnmHfN3pQyjuZv1D5Dumr7Nff9lvNuNsU
#MAGIC_HOUR_KEY: mhk_live_oBBlvwx7K3YTxh8RcDXoUq6law1dk0IF43sqCVharoYJmgxNa9vCiqVQ9ev8qYHCQqarbuNgTIUkYvGx

import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# 1. Setup - The user never sees this part
GEMINI_API_KEY = "AIzaSyCnmHfN3pQyjuZv1D5Dumr7Nff9lvNuNsU"  # Replace with your actual key
client = genai.Client(api_key=GEMINI_API_KEY)

def restore_with_gemini(image_bytes):
    """
    Sends the image to Gemini 'behind the scenes' and gets a 
    restored version back as the response.
    """
    prompt = (
        "ACT AS A PROFESSIONAL PHOTO RESTORER. Reconstruct this image. "
        "1. Remove all digital noise, blur, and artifacts. "
        "2. Sharpen facial features, eyes, and textures. "
        "3. Ensure the lighting is natural. "
        "Output ONLY the final restored image."
    )

    try:
        # We use the multimodal 'gemini-3-flash' model for reasoning + generation
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )
        
        # Extract the image data from Gemini's response
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                return part.inline_data.data
        return None
    except Exception as e:
        st.error(f"Gemini Restoration Error: {e}")
        return None

# 2. The Web Interface (Streamlit)
st.set_page_config(page_title="Gemini Photo Restorer", layout="wide")
st.title("✨ AI Photo Restoration")
st.write("The intelligence of Gemini, hidden behind your own app.")

col1, col2 = st.columns(2)

with col1:
    st.header("Upload")
    uploaded_file = st.file_uploader("Choose a blurry photo...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Original Image", use_container_width=True)
        
        # This is the button that triggers your "Hidden AI" idea
        if st.button("🚀 Restore with Gemini"):
            with st.spinner("Gemini is rebuilding your photo..."):
                # Convert the uploaded file to bytes for the API
                img_bytes = uploaded_file.getvalue()
                
                # Run the restoration logic
                restored_data = restore_with_gemini(img_bytes)
                
                if restored_data:
                    st.session_state['restored_image'] = restored_data
                else:
                    st.error("Restoration failed. Please try again.")

with col2:
    st.header("Restored Result")
    if 'restored_image' in st.session_state:
        st.image(st.session_state['restored_image'], caption="Fixed by Gemini", use_container_width=True)
        st.download_button(
            label="Download Restored Image",
            data=st.session_state['restored_image'],
            file_name="gemini_fixed.png",
            mime="image/png"
        )
    else:
        st.info("Your restored photo will appear here.")
