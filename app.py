#API_KEY: AIzaSyCnmHfN3pQyjuZv1D5Dumr7Nff9lvNuNsU
#MAGIC_HOUR_KEY: mhk_live_oBBlvwx7K3YTxh8RcDXoUq6law1dk0IF43sqCVharoYJmgxNa9vCiqVQ9ev8qYHCQqarbuNgTIUkYvGx

import streamlit as st
import os
import requests
from magic_hour import Client
from google import genai
from google.genai import types

# --- 1. CONFIGURATION ---
# It is safer to use st.secrets on Streamlit Cloud, but you can paste keys here for local testing.
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyCnmHfN3pQyjuZv1D5Dumr7Nff9lvNuNsU")
MAGIC_HOUR_KEY = st.secrets.get("MAGIC_HOUR_API_KEY", "mhk_live_oBBlvwx7K3YTxh8RcDXoUq6law1dk0IF43sqCVharoYJmgxNa9vCiqVQ9ev8qYHCQqarbuNgTIUkYvGx")

client_gemini = genai.Client(api_key=GEMINI_KEY)
client_magic = Client(token=MAGIC_HOUR_KEY)

st.set_page_config(page_title="ArtRestorer AI Pro", layout="wide")

# --- 2. HELPER FUNCTIONS ---

def gemini_analyze_and_speak(image_bytes):
    """
    Pass 1: Use Flash to SEE the image.
    Pass 2: Use TTS to SPEAK the text.
    """
    # STEP A: Analysis (Multimodal)
    analysis_prompt = "You are a professional art conservator. Analyze the damage in this photo and give 3 short restoration steps."
    
    text_response = client_gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            analysis_prompt
        ]
    )
    report_text = text_response.text

    # STEP B: Speech (Text-to-Speech)
    # The TTS model is 'blind' and only accepts text.
    speech_response = client_gemini.models.generate_content(
        model="gemini-2.5-flash-tts",
        contents=f"In a calm curator voice, say: {report_text}",
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
    return report_text, audio_bytes

def run_magic_hour_restoration(input_path):
    # Mandatory folder setup
    if not os.path.exists("./restored_outputs"):
        os.makedirs("./restored_outputs")
        
    response = client_magic.v1.ai_image_upscaler.generate(
        assets={"image_file_path": input_path},
        scale_factor=2.0, # Use 4.0 if you have a Creator plan for 4K results
        style={
            "enhancement": "Creative", # Reconstructs sharp details from scratch
        },
        # Optional: Some 2026 SDK versions allow a prompt to guide the AI
        # name="Hyper-realistic portrait restoration, sharp focus, 8k details",
        wait_for_completion=True,
        download_outputs=True,
        download_directory="./restored_outputs"
    )
    
    import glob
    list_of_files = glob.glob('./restored_outputs/*')
    return max(list_of_files, key=os.path.getctime)
# --- 3. STREAMLIT UI ---

st.title("🎨 ArtRestorer: Expert Analysis & AI Reconstruction")
st.write("Analyze old photos with Gemini's voice and restore them with Magic Hour.")

uploaded_file = st.file_uploader("Upload an old photograph", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Save a temporary file for the Magic Hour API to read
    temp_input_path = f"temp_{uploaded_file.name}"
    with open(temp_input_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Original Artifact")
        st.image(uploaded_file, use_container_width=True)
        
        if st.button("🎙️ Analyze & Listen"):
            with st.spinner("Gemini is examining the photo..."):
                try:
                    report, audio = gemini_analyze_and_speak(uploaded_file.getvalue())
                    st.info(report)
                    st.audio(audio, format="audio/wav")
                except Exception as e:
                    st.error(f"Gemini Error: {e}")

    with col2:
        st.subheader("2. AI Reconstruction")
        if st.button("🚀 Run Magic Hour Restoration"):
            with st.spinner("Magic Hour is rebuilding pixels..."):
                try:
                    restored_img_path = run_magic_hour_restoration(temp_input_path)
                    st.image(restored_img_path, caption="Restored Version", use_container_width=True)
                    st.success("Restoration complete!")
                    
                    # Add a download button for the result
                    with open(restored_img_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Restored Image",
                            data=file,
                            file_name=f"restored_{uploaded_file.name}",
                            mime="image/jpeg"
                        )
                except Exception as e:
                    st.error(f"Magic Hour Error: {e}")
