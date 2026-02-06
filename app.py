import streamlit as st
from google import genai
from google.genai import types

# --- CONFIGURATION: MODEL NAME ---
# Ensure this matches your available API model (gemini-1.5-flash is standard)
MODEL_NAME = "gemini-1.5-flash" 

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="CoachBot AI | Smart Fitness Assistant",
    page_icon="👟",
    layout="wide"
)

# --- 2. Sidebar: Settings ---
with st.sidebar:
    st.title("⚙️ CoachBot Settings")
    
    st.header("1. Athlete Profile")
    sport = st.selectbox("Select Sport", ["Cricket", "Football", "Basketball", "Athletics", "Tennis", "Badminton"])
    position = st.text_input("Player Position", placeholder="e.g., Wicketkeeper, Striker (Leave empty if unsure)")
    age = st.number_input("Age", min_value=10, max_value=25, value=15)
    
    st.subheader("⚠️ Health & Safety")
    injury_history = st.text_area("Injury History / Risk Zones", 
                                  placeholder="e.g., Recovering from ankle sprain. Avoid high impact.",
                                  help="The AI will adapt all workouts to accommodate these injuries.")
    
    st.subheader("🥗 Nutrition")
    diet_pref = st.selectbox("Dietary Preference", ["Non-Vegetarian", "Vegetarian", "Vegan", "Eggitarian", "Halal"])

    st.divider()
    
    st.header("2. AI Model Tuning")
    
    # --- FIX 1: INCREASED TOKEN LIMITS ---
    max_tokens = st.slider("Max Response Length (Tokens)", 
                           min_value=500, max_value=5000, value=2000, 
                           help="Higher value (2000+) prevents the answer from being cut off.")
                           
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.4)
    top_p = st.slider("Vocabulary Diversity (Top-P)", 0.0, 1.0, 0.9)

# --- 3. Secure API Connection ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except FileNotFoundError:
    st.error("🚨 **Security Error:** Secrets file not found.")
    st.stop()
except KeyError:
    st.error("🚨 **Configuration Error:** `GEMINI_API_KEY` not found in Streamlit secrets.")
    st.info("Please add your API key to the `.streamlit/secrets.toml` file.")
    st.stop()

# --- 4. The Core Logic ---
def get_coaching_advice(feature_name, specific_instruction):
    """
    Generates a response using the Gemini model.
    """
    # --- FIX 2: BETTER PROMPT TO PREVENT ASKING QUESTIONS ---
    system_prompt = f"""
    ROLE: You are CoachBot AI, a professional youth sports performance coach.
    
    ATHLETE CONTEXT:
    - Age: {age} | Sport: {sport} | Position: {position if position else "General Player"}
    - Diet: {diet_pref}
    - INJURY STATUS: {injury_history}
    
    CRITICAL INSTRUCTIONS:
    1. If the "Sport" is broad (like 'Athletics') and 'Position' is empty, ASSUME a standard event (e.g., 100m Sprinter) and generate the plan immediately. DO NOT ask clarifying questions.
    2. Strictly modify advice to be safe for the "Injury Status".
    3. DO NOT introduce yourself. Start directly with the answer.
    4. Keep the response complete and do not cut off.
    """
    
    full_prompt = f"{system_prompt}\n\nTASK: {specific_instruction}"

    try:
        with st.spinner(f"Coach is generating {feature_name}..."):
            response = client.models.generate_content(
                model=MODEL_NAME, 
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    top_p=top_p,
                    max_output_tokens=max_tokens  # Uses the updated high limit
                ),
                contents=[full_prompt]
            )
            return response.text
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# --- 5. Main User Interface ---
st.title("🏆 CoachBot AI")
st.markdown(f"**Performance Hub for {sport} Athletes**")
st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏋️ Training & Fitness", 
    "🥗 Nutrition & Fuel", 
    "🧠 Tactics & Mindset", 
    "🩹 Recovery & Rehab",
    "💬 Ask Coach"
])

# --- Tab 1: Physical Training ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Position-Specific Workout")
        if st.button("Generate Daily Plan"):
            prompt = f"Design a 60-minute training session for a {position if position else sport} athlete. Include dynamic warm-up, skill drills, and cool-down."
            st.write(get_coaching_advice("Daily Workout", prompt))
            
        st.subheader("2. Speed & Agility")
        if st.button("Get Speed Drills"):
            prompt = f"List 3 specific agility drills to improve acceleration and reaction time for {sport}."
            st.write(get_coaching_advice("Agility Drills", prompt))
            
    with col2:
        st.subheader("3. Stamina Builder")
        if st.button("Create Cardio Routine"):
            prompt = f"Create a cardiovascular endurance plan suitable for a {age}-year-old to last a full match. Ensure it is age-appropriate."
            st.write(get_coaching_advice("Stamina Plan", prompt))

# --- Tab 2: Nutrition ---
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("4. Weekly Meal Plan")
        if st.button("Generate Diet Chart"):
            prompt = f"Create a 7-day meal plan for a {age}-year-old {diet_pref} athlete. Focus on energy for training and muscle recovery."
            st.write(get_coaching_advice("Meal Plan", prompt))
            
    with col2:
        st.subheader("5. Hydration Strategy")
        if st.button("Match Day Hydration"):
            prompt = f"Provide a hydration schedule for match day, including electrolyte strategies to prevent cramping."
            st.write(get_coaching_advice("Hydration", prompt))
            
        st.subheader("6. Safe Supplementation")
        if st.button("Natural Vitamin Sources"):
            prompt = "Identify natural food sources for key athletic vitamins (Magnesium, Zinc, Vitamin D). Do not recommend pills for youth athletes."
            st.write(get_coaching_advice("Nutrition Advice", prompt))

# --- Tab 3: Tactics ---
with tab3:
    st.subheader("7. Game Intelligence (Tactics)")
    if st.button("Get Tactical Analysis"):
        prompt = f"Explain the key tactical responsibilities of a {position if position else 'player'} in {sport}. Give 3 advanced tips to read the game better."
        st.write(get_coaching_advice("Tactics", prompt))
        
    st.subheader("8. Mental Performance")
    if st.button("Pre-Game Visualization"):
        prompt = "Describe a 5-minute guided visualization routine to reduce anxiety and increase focus before a big game."
        st.write(get_coaching_advice("Mental Routine", prompt))

# --- Tab 4: Recovery ---
with tab4:
    st.error("⚠️ Injury Management Zone")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("9. Injury Adaptation Plan")
        if st.button("Get Modified Workout"):
            prompt = f"My injury is: {injury_history}. Create a training plan that maintains fitness without stressing this specific injury."
            st.write(get_coaching_advice("Rehab Plan", prompt))
            
    with col2:
        st.subheader("10. Post-Match Recovery")
        if st.button("Generate Recovery Protocol"):
            prompt = "Generate a comprehensive recovery routine: Active recovery exercises, foam rolling techniques, and sleep advice."
            st.write(get_coaching_advice("Recovery", prompt))

# --- Tab 5: Ask Coach ---
with tab5:
    st.header("💬 Ask the Coach Anything")
    st.markdown("Have a specific doubt? Ask here, and I'll answer based on your athlete profile.")
    
    user_question = st.text_area("Your Question:", height=100, placeholder="e.g., How can I improve my weak foot accuracy?")
    
    if st.button("Get Answer"):
        if user_question.strip():
            st.write(get_coaching_advice("Custom Question", user_question))
        else:
            st.warning("⚠️ Please type a question first!")

# --- Footer ---
st.markdown("---")
st.caption("CoachBot AI | Created for FA-2 Assessment")
