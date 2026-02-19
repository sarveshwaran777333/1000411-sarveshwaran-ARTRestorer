import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.graph_objects as go
import time
import random
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & VISIBILITY STYLING
# ==========================================
st.set_page_config(
    page_title="CoachBot AI Pro",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS: Includes the "Black Text" fix and Mascot Animations
st.markdown("""
<style>
    /* Main Gradient Header */
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    /* Mascot Animation */
    .mascot-icon {
        font-size: 5rem;
        display: inline-block;
        animation: bounce 2s infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }

    /* THE FIX: Force all generated output text to be BLACK and Visible */
    .black-text-container {
        color: #000000 !important;
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #FFD700; /* Gold border for "Pro" feel */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 1.1rem;
        line-height: 1.6;
    }
    /* Force internal elements to black */
    .black-text-container h1, .black-text-container h2, .black-text-container strong {
        color: #1e3c72 !important; /* Dark Blue headers */
    }
    .black-text-container p, .black-text-container li {
        color: #000000 !important;
    }

    /* Badge Styling */
    .badge {
        background: #FFD700;
        color: #333;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE (Gamification)
# ==========================================
if 'generated_count' not in st.session_state:
    st.session_state.generated_count = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []

# ==========================================
# 3. API SETUP (Using google-genai)
# ==========================================
try:
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ API Key missing. Please check .streamlit/secrets.toml")
        st.stop()
except Exception as e:
    st.error(f"Setup Error: {e}")
    st.stop()

# ==========================================
# 4. CORE LOGIC & PROMPTS
# ==========================================
def check_achievements():
    """Unlocks badges based on usage."""
    count = st.session_state.generated_count
    new_badge = None
    
    if count == 1 and "🥇 Rookie" not in st.session_state.badges:
        new_badge = "🥇 Rookie"
    elif count >= 5 and "🔥 Pro" not in st.session_state.badges:
        new_badge = "🔥 Pro"
    
    if new_badge:
        st.session_state.badges.append(new_badge)
        st.toast(f"New Badge Unlocked: {new_badge}!", icon="🎉")

def generate_advice(prompt_key, user_details, profile_ctx):
    """
    Generates advice using the 10 required prompts.
    """
    # 1. The Prompt Database (Assignment Requirement: 10 Prompts)
    prompts_db = {
        "weekly_plan": "Create a detailed 7-day training schedule for a {position} in {sport}. Use bold headers for each day (e.g., **Day 1**).",
        "drills": "List 3 specific technical drills to improve {goal} for a {position}. Explain the setup for each.",
        "recovery": "Design a safe, low-impact recovery session for an athlete with {injury}. PRIORITIZE SAFETY.",
        "tactics": "Explain the tactical role of a {position} in {sport} during a specific game situation.",
        "nutrition": "Create a 1-day meal plan for a {diet} athlete focused on {goal}.",
        "hydration": "Provide a match-day hydration strategy (pre, during, post-game).",
        "mental": "Give a 5-minute visualization routine to reduce anxiety before a match.",
        "warmup": "Generate a dynamic warm-up routine specific to {sport} movements.",
        "strength": "Suggest 5 gym exercises for explosive power suitable for a {age} year old.",
        "speed": "Provide a speed and agility circuit training plan."
    }
    
    # 2. Construct the Full Prompt
    base_instruction = prompts_db.get(prompt_key, "Provide expert coaching advice.")
    
    system_prompt = f"""
    You are Coach Ace 🦾, an elite youth sports coach.
    
    ATHLETE PROFILE:
    {profile_ctx}
    
    YOUR TASK:
    {base_instruction}
    User Specifics: {user_details}
    
    FORMATTING RULES:
    1. Use clear Markdown headers and bullet points.
    2. Be encouraging and energetic.
    3. If injury is present ({profile_ctx.split('Injury:')[1]}), strictly modify advice for safety.
    """
    
    # 3. Call API with Error Handling
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            config=types.GenerateContentConfig(temperature=0.7),
            contents=[system_prompt]
        )
        return response.text if response.text else "Coach Ace is thinking... try again!"
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

# ==========================================
# 5. SIDEBAR: PROFILE & BADGES
# ==========================================
with st.sidebar:
    st.header("🏃 Athlete Profile")
    sport = st.selectbox("Sport", ["Football", "Cricket", "Basketball", "Tennis", "Athletics", "Rugby"])
    position = st.text_input("Position", value="Striker")
    age = st.slider("Age", 10, 30, 16)
    diet = st.selectbox("Diet", ["Balanced", "Vegetarian", "Vegan", "High Protein"])
    injury = st.text_input("Injuries (Crucial)", value="None", help="Coach Ace will adapt plans for this injury.")
    
    st.markdown("---")
    st.subheader("🏆 Trophy Cabinet")
    if st.session_state.badges:
        st.markdown(" ".join([f"<span class='badge'>{b}</span>" for b in st.session_state.badges]), unsafe_allow_html=True)
    else:
        st.caption("Generate plans to unlock badges!")

# ==========================================
# 6. MAIN LAYOUT
# ==========================================

# Header
st.markdown("""
<div class="main-header">
    <div class="mascot-icon">🦾</div>
    <h1>CoachBot AI Pro</h1>
    <p>Your Personal AI Training Partner</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🏋️ Training Hub", "📊 Analytics (Pro)", "🥗 Nutrition & Wellness"])

# --- TAB 1: TRAINING HUB (The Main Feature) ---
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🤖 Ask Coach Ace")
        
        # Map readable names to prompt keys
        task_map = {
            "📅 Weekly Schedule": "weekly_plan",
            "🏃 Speed & Agility": "speed",
            "⚽ Technical Drills": "drills",
            "🏥 Injury Recovery": "recovery",
            "🧠 Tactical Analysis": "tactics",
            "🔥 Warm-up Routine": "warmup"
        }
        
        selected_task = st.selectbox("What is your focus today?", list(task_map.keys()))
        user_focus = st.text_input("Specific Goal:", placeholder="e.g. Improve sprint speed")
        
        if st.button("🚀 Generate Plan", type="primary"):
            with st.spinner("Coach Ace is planning your session..."):
                # 1. Build Context
                profile_context = f"Sport: {sport}, Pos: {position}, Age: {age}, Diet: {diet}, Injury: {injury}"
                prompt_key = task_map[selected_task]
                
                # 2. Get Advice
                result = generate_advice(prompt_key, user_focus, profile_context)
                
                # 3. DISPLAY WITH BLACK TEXT FIX
                st.markdown("### 📋 Your Personalized Plan")
                st.markdown(f"""
                <div class="black-text-container">
                    {result}
                </div>
                """, unsafe_allow_html=True)
                
                # 4. Gamification
                st.balloons()
                st.session_state.generated_count += 1
                check_achievements()

    with col2:
        st.subheader("📝 Stats")
        st.info(f"Plans Generated: {st.session_state.generated_count}")
        st.markdown("**Tip:** Mention any injuries in the sidebar to get a safe recovery plan!")

# --- TAB 2: ANALYTICS (Interactive Plotly) ---
with tab2:
    st.subheader("📊 Performance Radar")
    st.caption("Interactive assessment based on your position.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Dynamic Data Visualization
        categories = ['Pace', 'Shooting', 'Passing', 'Dribbling', 'Physical']
        values = [random.randint(60, 95) for _ in range(5)]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=f'{position} Stats',
            line_color='#2a5298'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("📈 Recovery Tracker")
        chart_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Energy": [80, 75, 60, 85, 90, 40, 60]
        })
        st.line_chart(chart_data, x="Day", y="Energy")

# --- TAB 3: NUTRITION & WELLNESS ---
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🍎 Fuel Your Game")
        if st.button("Generate Meal Plan"):
            with st.spinner("Calculating macros..."):
                ctx = f"Sport: {sport}, Diet: {diet}, Age: {age}, Injury: {injury}"
                res = generate_advice("nutrition", "High performance", ctx)
                st.markdown(f'<div class="black-text-container">{res}</div>', unsafe_allow_html=True)
                
    with col2:
        st.subheader("🧘 Mental Edge")
        if st.button("Pre-Game Visualization"):
            with st.spinner("Calming mind..."):
                ctx = f"Sport: {sport}, Injury: {injury}"
                res = generate_advice("mental", "Reduce anxiety", ctx)
                st.markdown(f'<div class="black-text-container">{res}</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("CoachBot AI Pro | NextGen Sports Lab | Summative Assessment Project")
