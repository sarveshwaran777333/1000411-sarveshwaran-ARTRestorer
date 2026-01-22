#API_KEY: AIzaSyCUHXHze9sRxunWYfLhcUo1xaU5JaIZL4g
#MAGIC_HOUR_KEY: mhk_live_oBBlvwx7K3YTxh8RcDXoUq6law1dk0IF43sqCVharoYJmgxNa9vCiqVQ9ev8qYHCQqarbuNgTIUkYvGx

import streamlit as st
import os
from magic_hour import Client
from google import genai
from google.genai import types

# --- CONFIGURATION ---
# Get your API keys from: 
# 1. https://aistudio.google.com/
# 2. https://magichour.ai/developer-hub
GEMINI_KEY = "AIzaSyCUHXHze9sRxunWYfLhcUo1xaU5JaIZL4g"
MAGIC_HOUR_KEY = "mhk_live_oBBlvwx7K3YTxh8RcDXoUq6law1dk0IF43sqCVharoYJmgxNa9vCiqVQ9ev8qYHCQqarbuNgTIUkYvGx"

client_gemini = genai.Client(api_key=GEMINI_KEY)
client_magic = Client(token=MAGIC_HOUR_KEY)

st.set_page_config(page_title="AI Art Studio", layout="wide")

# --- HELPERS ---
def run_magic_restoration(temp_file_path):
    """Uses Magic Hour AI to Upscale & Restore"""
    # The 'generate' helper automatically uploads, waits, and downloads the result
    response = client_magic.v1.ai_image_upscaler.generate(
        assets={
            "image_file_path": temp_file_path 
        },
        scale=2, # Doubles the resolution
        wait_for_completion=True,
        download_outputs=True,
        download_directory="./restored_outputs/"
    )
    # Returns the path to the downloaded image
    return response.downloaded_file_paths[0]

def gemini_speak(image_bytes):
    """Gemini 2.5 Flash analysis and TTS"""
    response = client_gemini.models.generate_content(
        model="gemini-2.5-flash-tts",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            "Briefly analyze this photo's damage as a curator and suggest restoration."
        ],
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
                )
            )
        )
    )
    return response.candidates[0].content.parts[0].inline_data.data

# --- APP UI ---
st.title("🎨 Hybrid AI Restoration Studio")
uploaded_file = st.file_uploader("Upload an old photo", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Save temp file for Magic Hour to read
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    col1, col2 = st.columns(2)
    
    with col1:
        st.image(uploaded_file, caption="Original Photo", use_container_width=True)
        if st.button("🎙️ Gemini: Analyze & Speak"):
            audio = gemini_speak(uploaded_file.getvalue())
            st.audio(audio, format="audio/wav")

    with col2:
        if st.button("🚀 Magic Hour: Restore & Upscale"):
            with st.spinner("Magic Hour is rebuilding pixels..."):
                restored_path = run_magic_restoration(temp_path)
                st.image(restored_path, caption="Restored by Magic Hour", use_container_width=True)
                st.success("Restoration Complete!")
