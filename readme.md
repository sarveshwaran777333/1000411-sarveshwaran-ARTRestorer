# 1000411-sarveshwaran-Athletic_bot

# Student Details

Name: Sarveshwaran.K
Registration Number: 1000411
Course: Artificial Intelligence
Assignment: Summative Assessment (Generative AI)

# Project Overview
CoachBot AI is a generative AI-powered web application designed to bridge the gap in professional coaching for youth athletes, specifically those in under-resourced
regions. Developed for NextGen Sports Lab, this tool acts as a virtual coach, providing personalized training routines, nutritional guidance, tactical analysis, and
injury management strategies.

The application leverages Google's Gemini Model to analyze user profiles (age, sport, position, injuries) and generate safety-conscious, high-quality advice.

# Project Links

Live App: [https://1000411-sarveshwaran-athleticbot-eqpbdv3faanlnnioh2lsgp.streamlit.app/]

# Research Findings

To ensure CoachBot AI provides accurate and safe advice, the following research areas were explored during the design phase:

1. Youth Sports Safety & Injury Prevention:

Research indicated that youth athletes are highly susceptible to overuse injuries. Consequently, the AI system prompt was designed with a strict "Safety First" rule, ensuring that any reported injury (e.g., "Weak ankles") automatically modifies the suggested workout to be low-impact.

Reference: Stop Sports Injuries - Youth Sports [https://ncys.org/safety/stop-sports-injuries/]

2. Position-Specific Training:

A "one-size-fits-all" approach fails in team sports. Research highlighted that a Goalkeeper requires explosive plyometrics, while a Midfielder requires high aerobic capacity. The application inputs Position and Sport to tailor these outputs.

Reference: ExRx.net - Exercise Prescription [https://exrx.net/Lists/WorkoutMenu]

3. Nutritional Requirements for Young Athletes:

Adolescent athletes have higher caloric and protein needs for growth and recovery. The app supports dietary preferences (Vegan, Non-Veg) to ensure inclusivity.

Reference: Academy of Nutrition and Dietetics [https://www.eatright.org/]

# Model Integration & Configuration

1. Model Used
Model: gemini-2.5-flash (Optimized for speed and high-throughput text generation).

Library: google-genai and streamlit.

2. Hyperparameter Tuning
The application allows for dynamic (user-controlled) and static tuning to balance creativity with safety.
 ______________________________________________________________________________________________________________________________________________________________
|  Parameter   |      Value    |       Justification                                                                                                           |
 ______________|_______________|_______________________________________________________________________________________________________________________________
|  Temperature | 0.4 (Default) |  A lower temperature was chosen to ensure the advice is grounded and realistic, rather than hallucinating dangerous exercises.|
 ______________|_______________|_______________________________________________________________________________________________________________________________
|  Top-P       |      0.9      |  Ensures a diverse range of vocabulary while keeping the context focused on sports science.                                   |
 ______________|_______________|_______________________________________________________________________________________________________________________________
|  Max Tokens  |      5000     |  Allows for detailed, full-day workout plans without cutting off mid-sentence.                                                |
 ______________|_______________|_______________________________________________________________________________________________________________________________
