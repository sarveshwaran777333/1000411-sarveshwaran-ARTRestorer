import streamlit as st
from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.5-flash" 

st.set_page_config(
    page_title="CoachBot AI | Smart Fitness Assistant",
    page_icon="👟",
    layout="wide"
)

with st.sidebar:
    st.title("CoachBot Profile")
    
    sport = st.selectbox("Sport", ["Cricket", "Football", "Basketball", "Athletics", "Tennis", "Badminton"])
    position = st.text_input("Position", placeholder="e.g., Striker")
    age = st.number_input("Age", 10, 25, 15)
    diet_pref = st.selectbox("Diet", ["Non-Veg", "Veg", "Vegan", "Eggitarian"])
    injury_history = st.text_area("Injury History", placeholder="e.g., Weak ankles")

    st.markdown("---")
    
    st.header("Ask Coach")
    user_question = st.text_area("Type your doubt here:", height=100)
    
    if st.button("Get Answer", type="primary"):
        if user_question.strip():
            st.session_state['custom_question'] = user_question
        else:
            st.warning("Type a question first!")

    st.markdown("---")
    
    with st.expander("Model Settings"):
        st.info(f"Model: {MODEL_NAME}")
        
        max_tokens = st.slider("Max Tokens", 
                               min_value=1000, 
                               max_value=8192, 
                               value=5000,
                               help="Controls the length of the response.")
                               
        temperature = st.slider("Creativity", 0.0, 1.0, 0.4)
        top_p = st.slider("Top-P", 0.0, 1.0, 0.9)

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"API Key Error: {e}")
    st.stop()

def get_coaching_advice(feature_name, specific_instruction):
    system_prompt = f"""
    ROLE: You are CoachBot AI, a youth sports coach.
    CONTEXT: Age: {age} | Sport: {sport} | Position: {position} | Injury: {injury_history}
    RULES:
    1. Direct answer only (No "Hello", "I am CoachBot").
    2. Strict safety for injuries.
    3. Keep it concise and formatted.
    4. ALWAYS provide specific exercises/drills when asked. Do NOT refuse to answer.
    5. Also provide diet plans if asked without any questions
    6. BE CONCISE: Keep answers under 400 words unless asked for a full plan.
    """
    full_prompt = f"{system_prompt}\n\nTASK: {specific_instruction}"

    try:
        with st.spinner(f"Coach is thinking about {feature_name}..."):
            response = client.models.generate_content(
                model=MODEL_NAME, 
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=top_p,
                    max_output_tokens=max_tokens
                ),
                contents=[full_prompt]
            )
            return response.text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

st.title("CoachBot AI Dashboard")

if 'custom_question' in st.session_state and st.session_state['custom_question']:
    st.info(f"**You Asked:** {st.session_state['custom_question']}")
    answer = get_coaching_advice("Custom Question", st.session_state['custom_question'])
    st.success(answer)
    del st.session_state['custom_question']
    st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "Training", 
    "Nutrition", 
    "Tactics", 
    "Recovery"
])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Daily Plan"):
            st.write(get_coaching_advice("Daily Workout", f"Design a detailed 60-min session for {position}."))
    with col2:
        if st.button("Get Speed Drills"):
            st.write(get_coaching_advice("Speed Drills", f"3 agility drills for {sport}."))

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Diet Chart"):
            st.write(get_coaching_advice("Meal Plan", f"7-day meal plan for {diet_pref} athlete."))
    with col2:
        if st.button("Match Day Hydration"):
            st.write(get_coaching_advice("Hydration", "Hydration schedule for match day."))

with tab3:
    if st.button("Get Tactical Analysis"):
        st.write(get_coaching_advice("Tactics", f"Tactical duties for {position} in {sport}."))

with tab4:
    if st.button("Get Modified Workout (Injury Safe)"):
        st.write(get_coaching_advice("Rehab", f"Training plan safe for injury: {injury_history}."))
