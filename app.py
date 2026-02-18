import streamlit as st
import google.generativeai as genai
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random

# ==========================================
# 1. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="CoachBot AI Pro - Ultimate Sports Assistant",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    /* Main Styles */
    .main-header {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: gradientShift 3s ease infinite;
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    .output-box {
        background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 3px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.1);
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .achievement-badge {
        background: linear-gradient(135deg, #ffd700 0%, #ffec8b 100%);
        color: #333;
        padding: 1rem;
        border-radius: 50%;
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        margin: 0.5rem auto;
        box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
        animation: bounce 2s ease infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }
    
    .fade-in {
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 5px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE
# ==========================================
if 'generated' not in st.session_state:
    st.session_state.generated = []
if 'user_inputs' not in st.session_state:
    st.session_state.user_inputs = []
if 'achievements' not in st.session_state:
    st.session_state.achievements = []
if 'workout_progress' not in st.session_state:
    st.session_state.workout_progress = 0
if 'daily_streak' not in st.session_state:
    st.session_state.daily_streak = 1 # Start with 1 for demo
if 'total_workouts' not in st.session_state:
    st.session_state.total_workouts = 0

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return os.getenv("GEMINI_API_KEY")

def initialize_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        st.error(f"Error initializing Gemini: {str(e)}")
        return None

def generate_response(model, prompt, temperature=0.7):
    generation_config = {
        "temperature": temperature,
        "top_k": 40,
        "top_p": 0.95,
        "max_output_tokens": 4000,
    }
    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

def format_ai_response(text):
    """Clean up markdown for better HTML display if necessary"""
    return text.replace("\n", "<br>")

def check_achievements():
    """Gamification Logic"""
    updates = []
    if st.session_state.total_workouts >= 1 and "Rookie Starter" not in st.session_state.achievements:
        st.session_state.achievements.append("Rookie Starter")
        updates.append("🏅 Unlocked: Rookie Starter!")
    
    if st.session_state.total_workouts >= 5 and "Consistent Grinder" not in st.session_state.achievements:
        st.session_state.achievements.append("Consistent Grinder")
        updates.append("🔥 Unlocked: Consistent Grinder!")
        
    if st.session_state.workout_progress >= 50 and "Halfway Hero" not in st.session_state.achievements:
        st.session_state.achievements.append("Halfway Hero")
        updates.append("⭐ Unlocked: Halfway Hero!")

    if updates:
        for update in updates:
            st.toast(update, icon="🎉")

# ==========================================
# 4. PROMPTS DICTIONARY
# ==========================================
PROMPTS = {
    "📅 AI Weekly Training Schedule": """Generate a comprehensive weekly training schedule for a {position} in {sport}.
    Create a day-by-day breakdown (Monday through Sunday) with specific times, exercises, and focus areas.
    Format as a structured table with columns: Day, Time, Activity, Duration, Intensity, Focus.
    Include morning, afternoon, and evening sessions.
    Add recovery days and rest periods.
    Consider: {context}""",
    
    "🏋️ Full-Body Workout Plan": """Generate a comprehensive full-body workout plan for a {position} in {sport}.
    Structure it in sections: Warm-up, Main Workout, Cool-down, and Stretching.
    Include specific exercises, sets, reps, rest times, and technique tips.
    Add difficulty levels (Beginner, Intermediate, Advanced) for progression.
    Format with clear headings and bullet points.
    Consider: {context}""",
    
    "🏥 Safe Recovery Training Schedule": """Create a safe, low-impact recovery training schedule for an athlete recovering from {injury}.
    Generate a progressive 4-week plan with weekly intensity increases.
    Include specific exercises, duration, and recovery metrics.
    Add warning signs to watch for and when to stop.
    Format as a week-by-week breakdown.
    Consider: {context}""",
    
    "🎯 Tactical Coaching Tips": """Provide advanced tactical coaching tips to improve {skill} in {sport} for a {position}.
    Create sections: Position Strategy, Decision Making, Mental Preparation, Drills, and Game Situations.
    Include specific scenarios and how to handle them.
    Add visual descriptions of positioning and movement patterns.
    Consider: {context}""",
    
    "🥗 Week-Long Nutrition Guide": """Suggest a detailed week-long nutrition guide for a {age}-year-old athlete following a {diet_type} diet.
    Create daily meal plans (Breakfast, Lunch, Dinner, Snacks) with recipes.
    Include macronutrient breakdown, calorie targets, and meal timing.
    Add hydration schedules and supplement recommendations.
    Format as a structured daily breakdown.
    Consider: {context}""",
    
    "🌅 Warm-up and Cool-down Routine": """Generate a personalized warm-up and cool-down routine for {sport} and {position}.
    Create two distinct sections: Pre-workout Warm-up and Post-workout Cool-down.
    Include specific stretches, mobility exercises, and activation drills.
    Add duration recommendations and progression levels.
    Format with exercise name, description, and timing.
    Consider: {context}""",
    
    "💪 Stamina Building Routines": """Design specific stamina-building routines for a {position} in {sport}.
    Create a 6-week progressive program with weekly challenges.
    Include cardiovascular exercises, interval training, and endurance drills.
    Add heart rate zones and performance metrics to track.
    Format as weekly schedules with specific workouts.
    Consider: {context}""",
    
    "🦵 Post-Injury Mobility Workouts": """Create mobility-focused workouts for an athlete recovering from {injury}.
    Generate a 3-phase recovery program: Phase 1 (Week 1-2), Phase 2 (Week 3-4), Phase 3 (Week 5-6).
    Include range of motion exercises, strengthening, and functional movements.
    Add progression criteria and when to advance phases.
    Format as a phased rehabilitation plan.
    Consider: {context}""",
    
    "🧠 Pre-Match Mental Preparation": """Provide pre-match mental preparation techniques for a {position} in {sport}.
    Create sections: Visualization, Focus Techniques, Confidence Building, Anxiety Management, and Game Day Routine.
    Include specific exercises with step-by-step instructions.
    Add timing recommendations (when to do each exercise).
    Consider: {context}""",
    
    "⚡ Strength and Power Training": """Develop a strength and power training program for a {position} in {sport}.
    Create an 8-week periodization plan with distinct phases.
    Include compound movements, explosive exercises, and sport-specific power moves.
    Add weekly progression, deload weeks, and testing protocols.
    Format as a structured 8-week program.
    Consider: {context}""",
    
    "💧 Hydration and Electrolyte Strategy": """Create a comprehensive hydration and electrolyte replacement strategy for training and competition in {sport}.
    Generate protocols for: Pre-exercise, During Exercise, Post-exercise, and Recovery.
    Include fluid recommendations, electrolyte timing, and weather adjustments.
    Add hydration monitoring and warning signs of dehydration.
    Format as actionable guidelines with specific quantities.
    Consider: {context}""",
    
    "🏃 Speed and Agility Drills": """Design speed and agility drills specifically for a {position} in {sport}.
    Create drill categories: Acceleration, Deceleration, Change of Direction, and Reaction Time.
    Include specific drills with setup, execution, and coaching points.
    Add progression from basic to advanced levels.
    Format as drill cards with difficulty ratings.
    Consider: {context}""",
    
    "🛡️ Injury Prevention Program": """Develop a comprehensive injury prevention program for a {position} in {sport}.
    Identify common injury risks and create targeted prevention strategies.
    Include strengthening exercises, mobility work, and recovery protocols.
    Add weekly schedule and monitoring guidelines.
    Format as a risk assessment with prevention plan.
    Consider: {context}""",
    
    "📊 Performance Tracking & Analytics": """Generate a performance tracking system for a {position} in {sport}.
    Create specific metrics to track: Speed, Strength, Endurance, Agility, and Technical Skills.
    Include testing protocols, recording methods, and progression benchmarks.
    Add data interpretation guidelines and goal-setting templates.
    Format as a comprehensive tracking framework.
    Consider: {context}""",
    
    "😴 Sleep & Recovery Optimization": """Create a sleep and recovery optimization plan for a {position} in {sport}.
    Generate recommendations for: Sleep duration, sleep quality, pre-sleep routine, and recovery strategies.
    Include specific techniques, timing, and monitoring methods.
    Add protocols for training days vs. rest days.
    Format as a daily recovery schedule.
    Consider: {context}""",
    
    "🏆 Competition Preparation Protocol": """Design a comprehensive competition preparation protocol for a {position} in {sport}.
    Create phases: Tapering, Peak Week, Competition Day, and Post-competition Recovery.
    Include specific training adjustments, nutrition, and mental preparation.
    Add timeline and checklist for each phase.
    Format as a timeline-based preparation plan.
    Consider: {context}""",
    
    "🥋 Equipment & Gear Recommendations": """Generate equipment and gear recommendations for a {position} in {sport}.
    Create categories: Essential Equipment, Performance Enhancers, Safety Gear, and Training Tools.
    Include specific product types, features, and usage guidelines.
    Add budget-friendly options and professional-grade recommendations.
    Format as a prioritized equipment guide.
    Consider: {context}""",
    
    "🧘 Breathing & Meditation Exercises": """Create breathing and meditation exercises tailored for a {position} in {sport}.
    Generate exercises for: Pre-training, During competition, Recovery, and Mental focus.
    Include step-by-step instructions, duration, and benefits.
    Add progression from beginner to advanced levels.
    Format as exercise cards with visual descriptions.
    Consider: {context}""",
    
    "🎉 Achievement & Motivation System": """Generate an achievement and motivation system for a {position} in {sport}.
    Create achievement categories: Training Milestones, Performance Goals, Consistency, and Personal Records.
    Include specific criteria, rewards, and celebration ideas.
    Add motivational quotes and daily affirmations.
    Format as a gamified achievement tracker.
    Consider: {context}""",
    
    "📹 Exercise Library Generator": """Generate an exercise library specifically for a {position} in {sport}.
    Create exercise categories: Strength, Cardio, Flexibility, and Sport-Specific movements.
    Include exercise name, description, target muscles, equipment needed, and difficulty level.
    Add technique tips and common mistakes to avoid.
    Format as a comprehensive exercise reference.
    Consider: {context}"""
}

# ==========================================
# 5. MAIN APPLICATION
# ==========================================
def main():
    # Get API key
    api_key = get_api_key()
    
    if not api_key:
        st.error("⚠️ API Key Not Found!")
        st.info("Please set your GEMINI_API_KEY in .streamlit/secrets.toml")
        st.stop()
    
    # Initialize model
    model = initialize_gemini(api_key)
    if not model:
        return
    
    # Animated Header
    st.markdown("""
    <div class="main-header fade-in">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🏆 CoachBot AI Pro</h1>
        <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">Your Ultimate AI-Powered Sports Companion</h2>
        <div style="margin-top: 1.5rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.25rem;">✨ 20+ AI Features</span>
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; margin: 0.25rem;">📊 Smart Analytics</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏋️ Training Hub", "📊 Analytics Dashboard", "🥗 Nutrition & Recovery", "🎯 Performance Tracking", "🏆 Achievements"])
    
    # ==================== TAB 1: TRAINING HUB ====================
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown("### 🎯 Your Profile")
            sport = st.selectbox("Select Sport", ["Football", "Cricket", "Basketball", "Tennis", "Athletics", "Swimming", "Boxing", "MMA", "Volleyball", "Rugby"])
            position = st.text_input("Position", "Midfielder")
            age = st.number_input("Age", 10, 35, 15)
            
            st.markdown("---")
            st.markdown("### 📋 Details")
            training_goal = st.selectbox("Goal", ["Build Stamina", "Strength", "Speed", "Recovery", "Tactics"])
            experience_level = st.selectbox("Level", ["Beginner", "Intermediate", "Advanced", "Pro"])
            training_days = st.slider("Days/Week", 1, 7, 5)
            session_duration = st.slider("Minutes/Session", 30, 180, 90)
            equipment_available = st.multiselect("Equipment", ["Dumbbells", "Barbell", "Pull-up Bar", "Bands", "Kettlebells", "None"])
            injury = st.text_area("Injuries", placeholder="None")
            skill = st.text_input("Specific Skill", placeholder="e.g. Shooting")
            diet_type = st.selectbox("Diet", ["Vegetarian", "Non-Veg", "Vegan", "Keto", "Paleo"])
            intensity = st.slider("Intensity", 1, 10, 5)
            context = st.text_area("Notes", placeholder="Competition in 2 weeks...")
        
        with col2:
            st.markdown("### 🚀 AI Coach Features")
            
            # Simplified Feature selection for clearer UX
            feature_map = {
                "📅 Plan Weekly Schedule": "📅 AI Weekly Training Schedule",
                "🏋️ Create Workout": "🏋️ Full-Body Workout Plan",
                "🏃 Speed Drills": "🏃 Speed and Agility Drills",
                "🏥 Rehab Plan": "🏥 Safe Recovery Training Schedule",
                "🧠 Mental Prep": "🧠 Pre-Match Mental Preparation",
                "🎯 Tactics Guide": "🎯 Tactical Coaching Tips"
            }
            
            selected_display_name = st.selectbox("What do you need?", list(feature_map.keys()))
            selected_feature = feature_map[selected_display_name]
            
            temp_mode = st.radio("AI Style", ["🎯 Balanced", "🛡️ Safe", "💡 Creative"], horizontal=True)
            temperature = 0.3 if "Safe" in temp_mode else (0.8 if "Creative" in temp_mode else 0.6)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Generate Plan", type="primary", use_container_width=True):
                with st.spinner("🤖 CoachBot is thinking..."):
                    # Progress Animation
                    prog_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        prog_bar.progress(i+1)
                    
                    # Context Building
                    full_context = f"""
                    Profile: {sport} ({position}), Age {age}, Level {experience_level}.
                    Goal: {training_goal}. Days: {training_days}, Time: {session_duration}m.
                    Equipment: {equipment_available}. Injuries: {injury}.
                    Diet: {diet_type}. Intensity: {intensity}.
                    User Notes: {context}
                    """
                    
                    # Prompt Formatting
                    prompt_template = PROMPTS.get(selected_feature, PROMPTS["🏋️ Full-Body Workout Plan"])
                    final_prompt = prompt_template.format(
                        sport=sport, position=position, age=age, 
                        context=full_context, injury=injury, 
                        skill=skill, diet_type=diet_type
                    )
                    
                    # Generate
                    response_text = generate_response(model, final_prompt, temperature)
                    
                    # Output
                    st.markdown(f"""
                    <div class="output-box fade-in">
                        <h3>📋 {selected_feature}</h3>
                        {response_text}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Update State
                    st.session_state.total_workouts += 1
                    st.session_state.workout_progress = min(100, st.session_state.workout_progress + 10)
                    check_achievements()
                    st.rerun()

        with col3:
            st.markdown("### 📊 Stats")
            st.markdown(f"""
            <div class="stat-card">
                <h2>{st.session_state.total_workouts}</h2>
                <p>Plans Created</p>
            </div>
            <div class="stat-card">
                <h2>{st.session_state.daily_streak} 🔥</h2>
                <p>Day Streak</p>
            </div>
            <div class="stat-card">
                <h2>{st.session_state.workout_progress}%</h2>
                <p>Level Progress</p>
            </div>
            """, unsafe_allow_html=True)

    # ==================== TAB 2: ANALYTICS ====================
    with tab2:
        st.subheader("📊 Athlete Analytics Dashboard")
        col1, col2 = st.columns(2)
        
        with col1:
            # Mock Data for Radar Chart
            st.markdown("#### Skills Analysis")
            categories = ['Speed', 'Stamina', 'Strength', 'Tactics', 'Technique']
            # Randomize slightly for demo effect
            r_vals = [random.randint(50, 90) for _ in range(5)]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=r_vals,
                theta=categories,
                fill='toself',
                name=f'{position} Profile'
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown("#### Training Consistency")
            dates = pd.date_range(start=datetime.today() - timedelta(days=7), periods=7)
            consistency = [random.randint(60, 100) for _ in range(7)]
            
            df_cons = pd.DataFrame({'Date': dates, 'Score': consistency})
            fig2 = px.line(df_cons, x='Date', y='Score', markers=True, title="Weekly Adherence Score")
            fig2.update_traces(line_color='#667eea')
            st.plotly_chart(fig2, use_container_width=True)

    # ==================== TAB 3: NUTRITION ====================
    with tab3:
        st.subheader("🥗 Nutrition & Recovery Hub")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🍎 Meal Planning")
            if st.button("Generate 7-Day Meal Plan"):
                with st.spinner("Chef AI is cooking..."):
                    prompt = PROMPTS["🥗 Week-Long Nutrition Guide"].format(age=15, diet_type="Balanced", context="High Protein needed")
                    res = generate_response(model, prompt)
                    st.markdown(f'<div class="output-box">{res}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown("#### 💧 Hydration")
            if st.button("Get Match-Day Hydration Strategy"):
                 with st.spinner("Analyzing fluid needs..."):
                    prompt = PROMPTS["💧 Hydration and Electrolyte Strategy"].format(sport="General", context="Hot weather")
                    res = generate_response(model, prompt)
                    st.markdown(f'<div class="output-box">{res}</div>', unsafe_allow_html=True)

    # ==================== TAB 4: PERFORMANCE ====================
    with tab4:
        st.subheader("🎯 Performance & KPI Tracking")
        st.info("Track your sprint times, max lifts, and match ratings here.")
        
        # Simple Data Entry for demo
        with st.form("kpi_form"):
            col1, col2 = st.columns(2)
            with col1:
                metric = st.text_input("Metric Name", "100m Sprint")
            with col2:
                value = st.text_input("Current Value", "12.5s")
            
            if st.form_submit_button("Log Metric"):
                st.success(f"Logged: {metric} - {value}")
                st.session_state.workout_progress = min(100, st.session_state.workout_progress + 5)

    # ==================== TAB 5: ACHIEVEMENTS ====================
    with tab5:
        st.subheader("🏆 Trophy Cabinet")
        
        if not st.session_state.achievements:
            st.info("No achievements yet. Start generating plans to unlock badges!")
        else:
            cols = st.columns(4)
            for i, badge in enumerate(st.session_state.achievements):
                with cols[i % 4]:
                    st.markdown(f"""
                    <div class="achievement-badge">🏅</div>
                    <p style="text-align:center; font-weight:bold;">{badge}</p>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
