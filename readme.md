# 1000411-sarveshwaran-Athletic_bot

# Student Details

Name: Sarveshwaran.K
Registration Number: 1000411
Course: Artificial Intelligence
Assignment: Summative Assessment (Generative AI)

# CoachBot AI Pro 🏆
Empowering the Next Generation of Athletes with Generative AI
CoachBot AI Pro is a cutting-edge, generative AI-powered web assistant designed to bridge the gap in professional sports coaching for youth athletes. Built using Python, Streamlit, and the Gemini 1.5 API, this application provides personalized training, injury-safe recovery plans, tactical advice, and nutritional guidance tailored to an athlete's specific sport, position, and physical condition.

# Live Demo
[https://1000411-sarveshwaran-athleticbot-eqpbdv3faanlnnioh2lsgp.streamlit.app/]

# Research Findings & Project Influence
The development of CoachBot AI was guided by several key areas of research:

Sport-Specific Biomechanics: Research into how different positions (e.g., Goalkeepers vs. Strikers) require distinct physical conditioning and reactive drills.

Youth Injury Prevention: Studies on common youth sports injuries (like ACL strains or Osgood-Schlatter disease) influenced the "Safety First" logic in the AI's recovery modules.

Nutritional Science for Adolescents: Guidelines from organizations like EatRight.org were used to frame prompts ensuring the AI suggests balanced macros suitable for growing athletes.

Generative AI in SportsTech: Analysis of how LLMs can simulate a "coaching persona" to provide encouraging and technically accurate feedback.

# Technical Stack & Model Configuration
Core Technologies
Frontend: Streamlit (Custom CSS for "Dark Mode" visibility and responsive UI)

AI Engine: Google Gemini 2.5 Flash (via google-genai SDK)

Data Visualization: Plotly (Radar Charts) and Pandas (Recovery Tracking)

Deployment: Streamlit Cloud & GitHub

Model Parameters
To ensure the perfect balance between professional accuracy and creative engagement, the following hyperparameters were used:

Temperature: 0.7 (Balances technical coaching precision with creative, engaging delivery).

Top_P & Top_K: Defaulted for high-quality token diversity.

Safety Settings: Configured to prioritize physical safety when "Injury" data is detected in the user profile.

# Prompt Engineering
The application utilizes a library of 10 primary prompt templates designed to act as "Coach Ace." Examples include:

Weekly Plan: Create a detailed 7-day training schedule for a {position} in {sport}.

Technical Drills: List 3 specific technical drills to improve {goal} for a {position}.

Injury Recovery: Design a safe, low-impact recovery session for an athlete with {injury}.

Mental Edge: Give a 5-minute visualization routine to reduce anxiety before a match.

Nutrition: Create a 1-day meal plan for a {diet} athlete focused on {goal}.
(Plus 5 additional features including Warm-ups, Tactics, Hydration, Strength, and Speed circuits.)

📸 Project Demonstration
1. Athlete Dashboard
Users can input their sport, position, age, and any current injuries in the sidebar.

[Insert Screenshot of Sidebar/Profile here]

2. Personalized Training Output
The AI generates structured, easy-to-read plans with clear headers and encouraging coaching tones.

[Insert Screenshot of Generated Training Plan here]

3. Performance Analytics
Visual radar charts allow users to see their simulated performance metrics.

[Insert Screenshot of Radar Chart here]

⚙️ Installation & Setup
Clone the repository:

Bash
git clone https://github.com/[Your-Username]/[Your-Repo-Name].git
Install dependencies:

Bash
pip install -r requirements.txt
Configure API Key:
Create a .streamlit/secrets.toml file and add your Gemini API key:

Ini, TOML
GEMINI_API_KEY = "your_api_key_here"
Run the app:

Bash
streamlit run app.py
✅ Assessment Checklist
Student Name: [Your Full Name]

Registration Number: [Your Reg Number]

Course: Artificial Intelligence - Generative A.I

Repository Access: Shared with ai.assignments@wacpinternational.org
