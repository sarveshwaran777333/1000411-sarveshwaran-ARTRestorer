import streamlit as st
from google import genai
from google.genai import types

# --- Page Configuration ---
st.set_page_config(
    page_title="CoachBot AI - Smart Fitness Assistant",
    page_icon="🏆",
    layout="wide"
)

# --- Student/Project Details (Footer info) ---
STUDENT_NAME = "K.Sarveshwaran"
REG_NO = "1000411"
COURSE = "Artificial Intelligence"

# --- Sidebar: Configuration & User Profile ---
with st.sidebar:
    st.header("⚙️ Configuration")
    # API Key Handling
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        api_key = st.text_input("Enter Gemini API Key", type="password")
        
    st.divider()
    
    st.header("👤 Athlete Profile")
    sport = st.selectbox("Sport", ["Cricket", "Football", "Basketball", "Athletics", "Tennis", "Badminton"])
    position = st.text_input("Position / Role", placeholder="e.g., Bowler, Striker, Point Guard")
    age = st.number_input("Age", min_value=10, max_value=25, value=16)
    injury_history = st.text_area("Injury History", placeholder="e.g., ACL tear 6 months ago, or 'None'")
    diet_pref = st.selectbox("Dietary Preference", ["Non-Vegetarian", "Vegetarian", "Vegan", "Eggitarian"])
    
    st.subheader("Model Tuning")
    temperature = st.slider("Creativity Level (Temperature)", 0.0, 1.0, 0.4, help="Lower for strict safety, higher for creative tactics.")

# --- Gemini Client Setup ---
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.warning("Please provide an API Key to proceed.")
    st.stop()

# --- Main Logic: The Coaching Engine ---
def ask_coach(prompt_type, specific_request):
    """
    Generates a response from Gemini 1.5 Flash based on the athlete's profile.
    """
    system_instruction = f"""
    You are CoachBot AI, an elite youth sports performance coach.
    
    ATHLETE PROFILE:
    - Sport: {sport}
    - Position: {position}
    - Age: {age}
    - Injury History: {injury_history} (CRITICAL: Adjust all exercises to be safe for this injury)
    - Diet: {diet_pref}
    
    Your goal is to provide professional, encouraging, and safety-conscious advice.
    """
    
    full_prompt = f"{system_instruction}\n\nUSER REQUEST: {specific_request}"
    
    try:
        with st.spinner(f"Coach is analyzing {prompt_type}..."):
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                config=types.GenerateContentConfig(temperature=temperature),
                contents=[full_prompt]
            )
            return response.text
    except Exception as e:
        return f"Error: {e}"

# --- UI Layout ---
st.title("🏆 CoachBot AI")
st.markdown(f"**Welcome, {sport} Athlete!** | *Powered by Gemini 1.5 Pro*")
st.markdown("---")

# Creating Tabs for the 10 Required Features
tab1, tab2, tab3, tab4 = st.tabs(["🏋️ Workout & Fitness", "🥗 Nutrition & Health", "🧠 Tactics & Mindset", "🩹 Recovery & Safety"])

# --- TAB 1: WORKOUT & FITNESS (Features 1-3) ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Position-Specific Workout")
        if st.button("Generate Daily Workout"):
            prompt = f"Create a detailed 1-hour workout session specifically for a {sport} {position}. Include warm-up, skill drills, and cool-down."
            st.write(ask_coach("Workout", prompt))

        st.subheader("2. Speed & Agility Drills")
        if st.button("Get Agility Drills"):
            prompt = f"List 3 specific agility drills to improve speed and reaction time for a {position} in {sport}."
            st.write(ask_coach("Agility", prompt))
            
    with col2:
        st.subheader("3. Stamina Builder")
        if st.button("Generate Cardio Plan"):
            prompt = f"Design a cardiovascular endurance plan suitable for a {age}-year-old athlete to last a full match of {sport}."
            st.write(ask_coach("Stamina", prompt))

# --- TAB 2: NUTRITION & HEALTH (Features 4-6) ---
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("4. Weekly Meal Plan")
        if st.button("Generate Diet Plan"):
            prompt = f"Create a 7-day meal plan for a {age}-year-old athlete who is {diet_pref}. Focus on muscle recovery and energy."
            st.write(ask_coach("Diet", prompt))
            
    with col2:
        st.subheader("5. Hydration Strategy")
        if st.button("Get Hydration Tips"):
            prompt = f"Provide a hydration strategy for match day, including electrolyte balance for a {sport} player."
            st.write(ask_coach("Hydration", prompt))
            
        st.subheader("6. Supplement Advice")
        if st.button("Safe Supplement Guide"):
            prompt = f"What are natural food sources for vitamins/minerals needed for {sport}? Avoid recommending synthetic pills for a minor."
            st.write(ask_coach("Supplements", prompt))

# --- TAB 3: TACTICS & MINDSET (Features 7-8) ---
with tab3:
    st.subheader("7. Tactical IQ")
    if st.button("Get Tactical Advice"):
        prompt = f"Explain the key responsibilities of a {position} in {sport}. Give 3 tactical tips to outsmart opponents."
        st.write(ask_coach("Tactics", prompt))
        
    st.subheader("8. Pre-Match Visualization")
    if st.button("Mental Focus Routine"):
        prompt = "Describe a 5-minute pre-game visualization and breathing routine to reduce anxiety and improve focus."
        st.write(ask_coach("Mindset", prompt))

# --- TAB 4: RECOVERY & SAFETY (Features 9-10) ---
with tab4:
    st.error("⚠️ Safety Zone")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("9. Injury Adaptation")
        if st.button("Get Modified Routine"):
            prompt = f"My injury history is: {injury_history}. Suggest specific exercise modifications to train safely without aggravating this injury."
            st.write(ask_coach("Safety", prompt))
            
    with col2:
        st.subheader("10. Post-Match Recovery")
        if st.button("Recovery Protocol"):
            prompt = "Generate a post-match recovery routine including stretching, foam rolling, and rest strategies."
            st.write(ask_coach("Recovery", prompt))

# --- Footer ---
st.markdown("---")
st.caption(f"Developed by {STUDENT_NAME} ({REG_NO}) | {COURSE} | Jain Vidyalaya IB World School")
