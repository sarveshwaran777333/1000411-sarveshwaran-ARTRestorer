#API_KEY: AIzaSyCnmHfN3pQyjuZv1D5Dumr7Nff9lvNuNsU
#MAGIC_HOUR_KEY: mhk_live_oBBlvwx7K3YTxh8RcDXoUq6law1dk0IF43sqCVharoYJmgxNa9vCiqVQ9ev8qYHCQqarbuNgTIUkYvGx

import streamlit as st
import os
import tempfile
import glob
from magic_hour import Client
from google import genai
from google.genai import types
st.set_page_config(
    page_title="ArtRestorer AI Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

GEMINI_KEY = st.secrets.get("GEMINI_API_KEY")
MAGIC_HOUR_KEY = st.secrets.get("MAGIC_HOUR_API_KEY")

if GEMINI_KEY is None or MAGIC_HOUR_KEY is None:
    st.error("Missing API keys. Add GEMINI_API_KEY and MAGIC_HOUR_API_KEY in Streamlit Secrets.")
    st.stop()


client_gemini = genai.Client(api_key=GEMINI_KEY)
client_magic = Client(token=MAGIC_HOUR_KEY)

OUTPUT_DIR = "restored_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
@st.cache_data(show_spinner=False)
def gemini_analyze_and_speak(image_bytes: bytes):
    """Analyze artwork damage and generate curator-style speech"""

    analysis_prompt = (
        "You are a professional art conservator. "
        "Analyze the damage in this photograph and provide exactly "
        "3 concise restoration steps."
    )

    # Image Analysis
    analysis = client_gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            ),
            analysis_prompt
        ]
    )

    report_text = analysis.text.strip()
    speech = client_gemini.models.generate_content(
        model="gemini-2.5-flash-tts",
        contents=f"Speak calmly like a museum curator: {report_text}",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"
                    )
                )
            )
        )
    )

    audio_bytes = speech.candidates[0].content.parts[0].inline_data.data
    return report_text, audio_bytes


def run_magic_hour_restoration(input_path: str) -> str:
    """Run Magic Hour AI upscaling and restoration"""

    client_magic.v1.ai_image_upscaler.generate(
        assets={"image_file_path": input_path},
        scale_factor=4.0,
        style={"enhancement": "Creative"},
        wait_for_completion=True,
        download_outputs=True,
        download_directory=OUTPUT_DIR
    )

    restored_files = glob.glob(f"{OUTPUT_DIR}/*")
    return max(restored_files, key=os.path.getctime)
st.title("🎨 ArtRestorer AI Pro")
st.caption("AI-powered artwork damage analysis, voice explanation, and restoration")

uploaded_file = st.file_uploader(
    "Upload an old photograph",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Original Artifact")
        st.image(uploaded_file, use_container_width=True)

        analyze_btn = st.button("🎙️ Analyze & Listen")

        if analyze_btn:
            with st.spinner("Analyzing damage with Gemini AI..."):
                try:
                    report, audio = gemini_analyze_and_speak(
                        uploaded_file.getvalue()
                    )
                    st.success("Analysis Complete")
                    st.info(report)
                    st.audio(audio, format="audio/wav")
                except Exception as e:
                    st.error("Gemini analysis failed.")
                    st.exception(e) 
    with col2:
        st.subheader("2. AI Reconstruction")

        restore_btn = st.button("🚀 Run Magic Hour Restoration")

        if restore_btn:
            with st.spinner("Restoring artwork using Magic Hour AI..."):
                try:
                    restored_path = run_magic_hour_restoration(temp_path)
                    st.image(
                        restored_path,
                        caption="Restored Version",
                        use_container_width=True
                    )

                    with open(restored_path, "rb") as img:
                        st.download_button(
                            "📥 Download Restored Image",
                            data=img,
                            file_name=f"restored_{uploaded_file.name}",
                            mime="image/jpeg"
                        )

                    st.success("Restoration completed successfully.")

                except Exception as e:
                    st.error("Restoration failed.")
                    st.exception(e)

    # Cleanup temp file
    os.remove(temp_path)
