import streamlit as st
import pandas as pd
import time
import csv
import os

# Google Sheets CSV URL
sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRL4XMpdsZB_DFz0LTbfUhV5sd_HkleNAcDSJle-QSrECMN2Q8PA7iP6XNR97w5z20kNpVAdIK3a1ZE/pub?output=csv'

# User authentication dictionary (username: password)
users_db = {
    'user1': 'password1',
    'user2': 'password2',
}

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}

# Load data once
@st.cache_data
def load_data():
    data = pd.read_csv(sheet_url)
    return data.to_dict(orient='records')

questions = load_data()

# Streamlit optimized functions
def get_topper_time(user_time):
    return round(user_time * 0.7, 2)

def get_video_suggestions(topic):
    video_suggestions = {
        'Math': 'https://www.youtube.com/watch?v=Q5H9P9_cLo4',
        'Physics': 'https://www.youtube.com/watch?v=7jB5guIhwcY',
        'Chemistry': 'https://www.youtube.com/watch?v=8glvj2zzVg4'
    }
    return video_suggestions.get(topic, "No video suggestion available.")

def authenticate_user():
    with st.form("auth_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if users_db.get(username) == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Welcome {username}!")
            else:
                st.error("Invalid credentials")

def display_question(q):
    st.subheader(f"Question {st.session_state.current_question + 1}")
    st.write(q['Question Text'])
    
    options = [q['Option A'], q['Option B'], q['Option C'], q['Option D']]
    answer = st.radio("Select your answer:", 
                     options=options,
                     key=f"q{st.session_state.current_question}")
    
    if st.button("Next Question"):
        process_answer(q, answer)
        st.session_state.current_question += 1
        st.experimental_rerun()

def process_answer(q, answer):
    # Track time and answers in session state
    question_id = q['Question ID']
    correct_answer = q['Correct Answer']
    selected_option = chr(65 + options.index(answer))
    
    st.session_state.user_answers[question_id] = {
        'selected': selected_option,
        'correct': correct_answer,
        'time_taken': time.time() - st.session_state.question_start_time
    }

def show_results():
    st.balloons()
    st.title("Test Results")
    
    # Calculate metrics
    total_time = sum(ans['time_taken'] for ans in st.session_state.user_answers.values())
    correct = sum(1 for ans in st.session_state.user_answers.values() if ans['selected'] == ans['correct'])
    accuracy = (correct / len(questions)) * 100
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Time", f"{total_time:.2f}s")
    with col2:
        st.metric("Accuracy", f"{accuracy:.2f}%")
    with col3:
        st.metric("Correct Answers", f"{correct}/{len(questions)}")
    
    # Show detailed analysis
    with st.expander("Detailed Analysis"):
        st.subheader("Topic-wise Performance")
        topic_data = {}
        for q in questions:
            ans = st.session_state.user_answers[q['Question ID']]
            topic = q['Topic']
            if topic not in topic_data:
                topic_data[topic] = {'correct': 0, 'total': 0, 'time': 0}
            topic_data[topic]['total'] += 1
            topic_data[topic]['time'] += ans['time_taken']
            if ans['selected'] == ans['correct']:
                topic_data[topic]['correct'] += 1
        
        for topic, data in topic_data.items():
            st.write(f"**{topic}**")
            st.progress(data['correct']/data['total'])
            st.write(f"Score: {data['correct']}/{data['total']}")
            st.write(f"Time Spent: {data['time']:.2f}s")
            
            if (data['correct']/data['total']) < 0.7:
                st.write(f"📚 Suggestion: {get_video_suggestions(topic)}")

# Main app flow
st.title("Online Mock Test Platform")

if not st.session_state.authenticated:
    authenticate_user()
else:
    if not st.session_state.test_started:
        if st.button("Start Test"):
            st.session_state.test_started = True
            st.session_state.question_start_time = time.time()
            st.experimental_rerun()
    else:
        if st.session_state.current_question < len(questions):
            q = questions[st.session_state.current_question]
            display_question(q)
            st.session_state.question_start_time = time.time()
        else:
            show_results()
            if st.button("Retake Test"):
                st.session_state.clear()
                st.experimental_rerun()
