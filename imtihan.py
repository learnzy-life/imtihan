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
    # Add more users as needed
}

# Load the dataset from Google Sheets
data = pd.read_csv(sheet_url)

# List of questions with options and correct answer
questions = data[['Question ID', 'Question Text', 'Option A', 'Option B', 'Option C', 'Option D', 'Correct Answer', 'Topic']].to_dict(orient='records')

# Initialize variables for tracking time and performance
total_time = 0
correct_answers = 0
time_per_question = []
topic_time = {}
incorrect_questions = []
question_times = []  # Stores the time taken for each question
topic_scores = {}  # Stores correct answers for each topic
topic_counts = {}  # Stores the total number of questions for each topic

# Function to calculate topper's time (30% less)
def get_topper_time(user_time):
    return round(user_time * 0.7, 2)

# Function to provide video suggestions for weak topics
def get_video_suggestions(topic):
    # Dictionary of video suggestions for weak topics
    video_suggestions = {
        'Math': 'https://www.youtube.com/watch?v=Q5H9P9_cLo4',
        'Physics': 'https://www.youtube.com/watch?v=7jB5guIhwcY',
        'Chemistry': 'https://www.youtube.com/watch?v=8glvj2zzVg4'
        # Add more topics and links as required
    }
    return video_suggestions.get(topic, "No video suggestion available for this topic.")

# Function to authenticate the user using Streamlit
def authenticate_user():
    st.title('Login Page')
    username = st.text_input('Username:')
    password = st.text_input('Password:', type='password')

    if st.button('Login'):
        if users_db.get(username) == password:
            st.success(f"Welcome {username}!")
            return username
        else:
            st.error("Invalid username or password. Please try again.")
            return None

# Function to store the results persistently
def store_results(username, total_time, accuracy, time_per_question, topic_time, incorrect_questions):
    # Create or append to the results CSV file
    file_name = f'{username}_results.csv'

    # Check if the file exists, and if not, create a new one with headers
    file_exists = os.path.isfile(file_name)

    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            # Write header if file doesn't exist
            writer.writerow(['Username', 'Total Time', 'Accuracy', 'Question ID', 'Time Taken', 'Topic', 'Incorrect Questions'])

        # Write user data and performance details
        for q_id, time_taken in time_per_question:
            for topic, time_spent in topic_time.items():
                writer.writerow([username, total_time, accuracy, q_id, time_taken, topic, incorrect_questions])

# Simulate a mock test function
def start_mock_test(username):
    global total_time, correct_answers, time_per_question, topic_time, incorrect_questions, topic_scores, topic_counts
    total_time = 0
    correct_answers = 0
    time_per_question = []
    topic_time = {}
    incorrect_questions = []
    topic_scores = {}
    topic_counts = {}

    # Record the start time of the test
    test_start_time = time.time()

    for q in questions:
        st.write(f"\n**{q['Question Text']}**")
        st.write(f"A. {q['Option A']}")
        st.write(f"B. {q['Option B']}")
        st.write(f"C. {q['Option C']}")
        st.write(f"D. {q['Option D']}")

        # Ask the user for input
        user_answer = st.radio("Your answer:", ['A', 'B', 'C', 'D'])

        # Record the start time of the question
        question_start_time = time.time()

        if user_answer:
            # Record the end time after user selection
            question_end_time = time.time()

            time_taken = round(question_end_time - question_start_time, 2)
            total_time += time_taken

            # Track time per question
            time_per_question.append((q['Question ID'], time_taken))

            # Track time spent on each topic
            if q['Topic'] not in topic_time:
                topic_time[q['Topic']] = 0
            topic_time[q['Topic']] += time_taken

            # Track score per topic
            if q['Topic'] not in topic_scores:
                topic_scores[q['Topic']] = 0
                topic_counts[q['Topic']] = 0

            # Check if the answer is correct
            if user_answer == q['Correct Answer']:
                correct_answers += 1
                topic_scores[q['Topic']] += 1
            else:
                incorrect_questions.append(q['Question ID'])

            # Track the total number of questions for each topic
            topic_counts[q['Topic']] += 1

            # Record the time for each question
            question_times.append(time_taken)

    # Calculate the total time of the test
    test_end_time = time.time()
    total_test_time = round(test_end_time - test_start_time, 2)

    # Calculate performance insights after the test is complete
    analyze_performance(username, total_test_time)

# Function to analyze performance after test completion
def analyze_performance(username, total_test_time):
    global total_time, correct_answers, question_times, topic_time, incorrect_questions, topic_scores, topic_counts

    # Calculate the overall accuracy
    accuracy = (correct_answers / len(questions)) * 100

    # Display test completion insights
    st.write("\n**Test completed!**")
    st.write(f"Total Time: {total_test_time:.2f} seconds")
    st.write(f"Accuracy: {accuracy:.2f}%")

    # Show time per question
    st.write("\n**Time per question:**")
    for q_id, time_taken in time_per_question:
        st.write(f"Question ID {q_id}: {time_taken:.2f} seconds")

    # Show time spent per topic
    st.write("\n**Time spent per topic:**")
    for topic, time_spent in topic_time.items():
        st.write(f"{topic}: {time_spent:.2f} seconds")

    # Show topper's time and your time comparison
    st.write("\n**Your time and Topper's time:**")
    for time_taken in question_times:
        topper_time = get_topper_time(time_taken)
        st.write(f"Your time: {time_taken:.2f} seconds | Topper's time: {topper_time:.2f} seconds")

    # Show incorrect questions
    st.write(f"\n**Incorrect questions:** {incorrect_questions}")

    # Topic-wise performance and suggestions for weak topics
    st.write("\n**Topic-wise performance:**")
    for topic in topic_scores:
        topic_percentage = (topic_scores[topic] / topic_counts[topic]) * 100
        st.write(f"{topic}: {topic_percentage:.2f}%")

        # If topic percentage is less than 70%, it's a weak topic
        if topic_percentage < 70:
            st.write(f"Weak Topic: {topic}")
            st.write(f"Suggestion: Improve this topic by watching the video: ", get_video_suggestions(topic))

    # Store the results persistently in a CSV file
    store_results(username, total_test_time, accuracy, time_per_question, topic_time, incorrect_questions)

# Main function to run the test
def main():
    username = authenticate_user()
    if username:
        if st.button('Start Mock Test'):
            start_mock_test(username)

# Run the main function
if __name__ == "__main__":
    main()
