#AIzaSyCUHXHze9sRxunWYfLhcUo1xaU5JaIZL4g

import streamlit as st
import cv2
import numpy as np
from gfpgan import GFPGANer
from google import genai
from google.genai import types
from PIL import Image
import io

# --- 1. SETUP & CONFIG ---
# Replace with your actual API key
client = genai.Client(api_key="AIzaSyCUHXHze9sRxunWYfLhcUo1xaU5JaIZL4g")

st.set_page_config(page_title="ArtRestorer Pro", layout="wide")

# --- 2. LOAD LOCAL ENGINE (Cached) ---
@st.cache_resource
def load_restorer():
    # Ensure GFPGANv1.3.pth is in your project folder
    model_path = 'GFPGANv1.3.pth' 
    return GFPGANer(model_path=model_path, upscale=2, arch='clean', channel_multiplier=2)

restorer = load_restorer()

# --- 3. HELPER FUNCTIONS ---
def analyze_and_speak(image_bytes):
    """Gemini 2.5 Flash for Text Analysis + Speech"""
    analysis_prompt = "You are an Expert Art Conservator. Briefly analyze this photo and tell me 3 steps to restore it."
    
    # Text Analysis
    text_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            analysis_prompt
        ]
    )
    analysis_text = text_response.text
    
    # Audio Generation (Native 2026 TTS)
    speech_response = client.models.generate_content(
        model="gemini-2.5-flash-tts",
        contents=f"In a professional curator voice: {analysis_text}",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                )
            )
        )
    )

    audio_bytes = speech_response.candidates[0].content.parts[0].inline_data.data
    return analysis_text, audio_bytes

# --- 4. STREAMLIT UI ---
st.title("🎨 Professional Art Restoration Studio")
st.markdown("---")

uploaded_file = st.file_uploader("Upload a degraded photograph", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Prepare Image Data
    image_bytes = uploaded_file.getvalue()
    input_img_cv = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), 1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Original Artifact")
        st.image(uploaded_file, use_container_width=True)
        
        if st.button("🎙️ Analyze & Listen"):
            with st.spinner("Gemini is inspecting the artifact..."):
                text, audio = analyze_and_speak(image_bytes)
                st.info(text)
                st.audio(audio, format="audio/wav")

    with col2:
        st.subheader("2. Digital Reconstruction")
        if st.button("✨ Run GFPGAN Restoration"):
            with st.spinner("Reconstructing facial features locally..."):
                # Local Pixel Enhancement
                _, _, restored_img = restorer.enhance(
                    input_img_cv, has_aligned=False, only_center_face=False, paste_back=True
                )
                restored_rgb = cv2.cvtColor(restored_img, cv2.COLOR_BGR2RGB)
                
                st.image(restored_rgb, caption="Enhanced by Local Engine", use_container_width=True)
                st.success("Restoration successful!")
