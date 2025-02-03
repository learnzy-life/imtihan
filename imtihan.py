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
def initialize_session_state():
    required_states = {
        'authenticated': False,
        'test_started': False,
        'current_question': 0,
        'user_answers': {},
        'question_start_time': time.time(),
        'username': None
    }
    for key, value in required_states.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Load data once with error handling
@st.cache_data(show_spinner=False)
def load_data():
    try:
        data = pd.read_csv(sheet_url)
        return data.to_dict(orient='records')
    except Exception as e:
        st.error(f"Failed to load data: {str(e)}")
        return []

questions = load_data()

def get_topper_time(user_time):
    return user_time * 0.7  # 30% faster than user time

def get_video_suggestions(topic):
    video_suggestions = {
        'Math': 'https://www.youtube.com/watch?v=Q5H9P9_cLo4',
        'Physics': 'https://www.youtube.com/watch?v=7jB5guIhwcY',
        'Chemistry': 'https://www.youtube.com/watch?v=8glvj2zzVg4'
    }
    return video_suggestions.get(topic, "#")

def authenticate_user():
    with st.form("auth_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if users_db.get(username) == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                return True
            else:
                st.error("Invalid credentials")
                return False
    return False

def display_question(q):
    st.subheader(f"Question {st.session_state.current_question + 1} of {len(questions)}")
    st.markdown(f"**{q['Question Text']}**")
    
    options = [q['Option A'], q['Option B'], q['Option C'], q['Option D']]
    answer = st.radio("Select your answer:", 
                     options=options,
                     key=f"q{st.session_state.current_question}")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Next Question ➡️"):
            process_answer(q, answer)
            st.session_state.current_question += 1
            st.session_state.question_start_time = time.time()
            st.rerun()

def process_answer(q, answer):
    question_id = q['Question ID']
    options = [q['Option A'], q['Option B'], q['Option C'], q['Option D']]
    selected_option = chr(65 + options.index(answer))
    
    st.session_state.user_answers[question_id] = {
        'selected': selected_option,
        'correct': q['Correct Answer'],
        'time_taken': time.time() - st.session_state.question_start_time
    }

def show_results():
    st.balloons()
    st.title("📊 Detailed Performance Report")
    
    # Calculate basic metrics
    total_time = sum(ans['time_taken'] for ans in st.session_state.user_answers.values())
    topper_total_time = total_time * 0.7
    correct = sum(1 for ans in st.session_state.user_answers.values() 
                 if ans['selected'] == ans['correct'])
    accuracy = (correct / len(questions)) * 100

    # --- Time Comparison Section ---
    st.header("⏱ Time Analysis")
    
    # Time metrics columns
    time_col1, time_col2, time_col3 = st.columns(3)
    with time_col1:
        st.metric("Your Total Time", f"{total_time:.1f}s")
    with time_col2:
        st.metric("Topper's Benchmark", f"{topper_total_time:.1f}s")
    with time_col3:
        delta = total_time - topper_total_time
        st.metric("Time Difference", f"{abs(delta):.1f}s", 
                 delta=f"{'Over' if delta > 0 else 'Under'} Benchmark")

    # --- Topic-wise Analysis ---
    st.header("📚 Topic-wise Breakdown")
    
    # Calculate topic statistics
    topic_stats = {}
    for q in questions:
        topic = q['Topic']
        ans = st.session_state.user_answers[q['Question ID']]
        
        if topic not in topic_stats:
            topic_stats[topic] = {
                'total_questions': 0,
                'correct': 0,
                'total_user_time': 0,
                'total_topper_time': 0
            }
        
        topic_stats[topic]['total_questions'] += 1
        topic_stats[topic]['correct'] += 1 if ans['selected'] == ans['correct'] else 0
        topic_stats[topic]['total_user_time'] += ans['time_taken']
        topic_stats[topic]['total_topper_time'] += get_topper_time(ans['time_taken'])

    # Create display dataframe
    analysis_df = pd.DataFrame.from_dict(topic_stats, orient='index')
    analysis_df['accuracy'] = (analysis_df['correct'] / analysis_df['total_questions']) * 100
    analysis_df['avg_user_time'] = analysis_df['total_user_time'] / analysis_df['total_questions']
    analysis_df['avg_topper_time'] = analysis_df['total_topper_time'] / analysis_df['total_questions']
    analysis_df['time_difference'] = analysis_df['avg_user_time'] - analysis_df['avg_topper_time']
    analysis_df['status'] = analysis_df['accuracy'].apply(
        lambda x: '🚨 Needs Improvement' if x < 70 else '✅ Strong')

    # Display topic analysis
    for topic, data in analysis_df.iterrows():
        with st.expander(f"{topic} Analysis", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Accuracy**")
                st.progress(data['accuracy']/100)
                st.caption(f"{data['correct']}/{data['total_questions']} Correct")
                st.metric("Accuracy Score", f"{data['accuracy']:.1f}%")
                
                if data['accuracy'] < 70:
                    st.markdown(f"📚 [Improvement Video]({get_video_suggestions(topic)})")

            with col2:
                st.markdown("**Time Comparison**")
                st.metric("Your Avg Time", f"{data['avg_user_time']:.1f}s")
                st.metric("Topper's Avg Time", f"{data['avg_topper_time']:.1f}s")
                st.metric("Time Difference", 
                         f"{abs(data['time_difference']):.1f}s",
                         delta=f"{'Faster' if data['time_difference'] < 0 else 'Slower'}")

            with col3:
                st.markdown("**Recommendations**")
                if data['accuracy'] < 70:
                    st.error("Focus on this topic!")
                    st.write("Practice similar questions:")
                    st.write(f"- [Practice Set]({get_video_suggestions(topic)})")
                else:
                    st.success("You're doing great!")
                    st.write("Challenge yourself:")
                    st.write(f"- [Advanced Problems]({get_video_suggestions(topic)})")

    # --- Final Summary ---
    st.header("🎯 Key Insights")
    weak_topics = analysis_df[analysis_df['accuracy'] < 70].index.tolist()
    
    if weak_topics:
        st.error(f"**Priority Areas:** {', '.join(weak_topics)}")
    else:
        st.success("**Excellent Performance!** Keep up the good work!")
        
    st.markdown(f"""
    - **Overall Accuracy:** {accuracy:.1f}%
    - **Total Test Duration:** {total_time:.1f}s
    - **Topper's Benchmark Time:** {topper_total_time:.1f}s
    - **Most Time-Consuming Topic:** {analysis_df['avg_user_time'].idxmax()} ({analysis_df['avg_user_time'].max():.1f}s avg)
    """)

    if st.button("🔄 Retake Test"):
        st.session_state.clear()
        st.rerun()

# Main app flow
def main():
    st.title("📝 Smart Mock Test Platform")
    
    if not st.session_state.authenticated:
        authenticate_user()
    else:
        if not st.session_state.test_started:
            st.header(f"Welcome {st.session_state.username}!")
            st.write(f"Total Questions: {len(questions)}")
            if st.button("🚀 Start Test"):
                st.session_state.test_started = True
                st.rerun()
        else:
            if st.session_state.current_question < len(questions):
                q = questions[st.session_state.current_question]
                display_question(q)
            else:
                show_results()

if __name__ == "__main__":
    if not questions:
        st.error("Failed to load questions. Please check the data source.")
    else:
        main()
