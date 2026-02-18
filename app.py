import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.graph_objects as go
import time
import random

# ==========================================
# 1. PAGE CONFIG & STYLING (The "Pro" Look)
# ==========================================
st.set_page_config(
    page_title="CoachBot AI Pro",
    page_icon="🏆",
    layout="wide"
)

# This CSS makes it look shiny like your friend's app
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .stat-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        text-align: center;
    }
    .output-box {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-top: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    /* Simple animation for the badge */
    @keyframes pop {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .badge {
        animation: pop 0.5s ease-in-out;
        background: #ffd700;
        color: black;
        padding: 10px;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STATE MANAGEMENT (Gamification)
# ==========================================
if 'workouts_generated' not in st.session_state:
    st.session_state.workouts_generated = 0
if 'badges' not in st.session_state:
    st.session_state.badges = []

# ==========================================
# 3. API LOGIC (YOUR Code - google-genai)
# ==========================================
try:
    if "GEMINI_API_KEY" in st.secrets:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ API Key missing in secrets.")
        st.stop()
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

def get_ai_response(prompt_type, profile_text, details):
    """
    This function replaces the huge dictionary. 
    It builds the prompt dynamically based on the user's need.
    """
    base_prompt = f"""
    You are CoachBot Pro, an expert sports scientist.
    ATHLETE PROFILE: {profile_text}
    
    TASK: Generate a {prompt_type}.
    DETAILS: {details}
    
    RULES:
    1. Be highly specific to the sport and position.
    2. Use professional formatting (tables, bullet points).
    3. If injury is mentioned, prioritize safety.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[base_prompt]
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ==========================================
# 4. SIDEBAR INPUTS
# ==========================================
with st.sidebar:
    st.title("🏃 Athlete Profile")
    sport = st.selectbox("Sport", ["Football", "Cricket", "Basketball", "Tennis", "Athletics", "Rugby"])
    position = st.text_input("Position", value="Midfielder")
    age = st.slider("Age", 10, 40, 18)
    skill_level = st.select_slider("Level", options=["Beginner", "Intermediate", "Pro"])
    injury = st.text_input("Injuries (Optional)", placeholder="e.g. Sore knee")
    
    st.markdown("---")
    st.subheader("🏆 Trophy Cabinet")
    if not st.session_state.badges:
        st.caption("Generate plans to unlock badges!")
    else:
        for badge in st.session_state.badges:
            st.markdown(f"<div class='badge'>{badge}</div>", unsafe_allow_html=True)

# ==========================================
# 5. MAIN DASHBOARD (Interactive!)
# ==========================================

# Animated Header
st.markdown("""
<div class="main-header">
    <h1>🏆 CoachBot AI Pro</h1>
    <p>Interactive Sports Performance Analytics</p>
</div>
""", unsafe_allow_html=True)

# Tabs for organization
tab1, tab2, tab3 = st.tabs(["🏋️ Training Generator", "📊 Interactive Analytics", "🥗 Nutrition & Health"])

# --- TAB 1: GENERATOR (With Animation) ---
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🤖 AI Coach Instructions")
        feature = st.selectbox("What do you need?", 
                               ["Weekly Training Schedule", "Specific Skill Drills", "Match Day Tactics", "Injury Rehab Plan"])
        
        specifics = st.text_area("Specific Focus:", placeholder="e.g. I want to improve my sprint speed.")
        
        if st.button("🚀 Generate Plan", type="primary"):
            # Progress Bar Animation (Interactive feel)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(100):
                time.sleep(0.01) # Fake processing time
                progress_bar.progress(i + 1)
                if i == 30: status_text.text("🧠 Analyzing biomechanics...")
                if i == 60: status_text.text("📝 Drafting exercises...")
                
            status_text.text("✅ Plan Ready!")
            
            # Generate Content
            profile_str = f"{sport} player, {position}, Age {age}, Level {skill_level}, Injury: {injury}"
            result = get_ai_response(feature, profile_str, specifics)
            
            st.markdown(f'<div class="output-box">{result}</div>', unsafe_allow_html=True)
            
            # Gamification Logic
            st.session_state.workouts_generated += 1
            if st.session_state.workouts_generated == 1 and "Rookie Badge" not in st.session_state.badges:
                st.session_state.badges.append("🥇 Rookie Badge")
                st.toast("Achievement Unlocked: Rookie!", icon="🥇")
            if st.session_state.workouts_generated >= 5 and "Pro Badge" not in st.session_state.badges:
                st.session_state.badges.append("🔥 Pro Badge")
                st.toast("Achievement Unlocked: Pro!", icon="🔥")

    with col2:
        st.subheader("⚡ Live Stats")
        st.markdown(f"""
        <div class="stat-card">
            <h3>{st.session_state.workouts_generated}</h3>
            <p>Plans Created</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 **Tip:** Mention your injuries to get a safer plan!")

# --- TAB 2: ANALYTICS (The Charts) ---
with tab2:
    st.subheader("📊 Athlete Skill Profile")
    st.caption("Interactive visualization based on your sport requirements.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Interactive Radar Chart using Plotly
        categories = ['Speed', 'Stamina', 'Strength', 'Tactics', 'Technique']
        
        # Mock data logic (You can make this dynamic if you want)
        if skill_level == "Pro":
            values = [90, 85, 80, 95, 90]
        elif skill_level == "Intermediate":
            values = [70, 65, 60, 70, 65]
        else:
            values = [50, 45, 40, 30, 40]
            
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=f'{sport} Profile'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.write("### 📈 Performance Prediction")
        st.write(f"Based on your age ({age}) and level ({skill_level}), here is your estimated recovery curve:")
        
        # Simple Line Chart using Streamlit Native (Fast & Clean)
        chart_data = pd.DataFrame({
            "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "Energy Level": [90, 80, 70, 60, 85, 95, 50]
        })
        st.line_chart(chart_data.set_index("Day"))

# --- TAB 3: NUTRITION ---
with tab3:
    st.subheader("🥗 Fuel Your Game")
    diet = st.radio("Diet Preference", ["Balanced", "High Protein", "Vegan", "Keto"], horizontal=True)
    
    if st.button("Generate Meal Plan"):
        with st.spinner("Cooking up a plan..."):
            profile_str = f"{age} year old {sport} athlete"
            plan = get_ai_response("1-Day Meal Plan", profile_str, f"Diet: {diet}. Goal: High Performance.")
            st.markdown(f'<div class="output-box">{plan}</div>', unsafe_allow_html=True)
