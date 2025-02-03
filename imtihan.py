import time
import streamlit as st

# Initialize global variables to track results
total_time = 0
correct_answers = 0
time_per_question = []
topic_time = {}
incorrect_questions = []
topic_scores = {}
topic_counts = []
question_times = []

# Dummy questions for the mock test
questions = [
    {
        'Question ID': 1,
        'Question Text': 'What is the capital of France?',
        'Option A': 'Paris',
        'Option B': 'London',
        'Option C': 'Rome',
        'Option D': 'Berlin',
        'Correct Answer': 'A',
        'Topic': 'Geography'
    },
    {
        'Question ID': 2,
        'Question Text': 'Who developed the theory of relativity?',
        'Option A': 'Isaac Newton',
        'Option B': 'Albert Einstein',
        'Option C': 'Galileo Galilei',
        'Option D': 'Nikola Tesla',
        'Correct Answer': 'B',
        'Topic': 'Physics'
    },
    # Add more questions as needed
]

# Function to analyze performance after test completion
def analyze_performance(username, total_test_time):
    global correct_answers, total_time, topic_scores, topic_counts, time_per_question, topic_time, incorrect_questions
    
    st.write(f"Test completed! Well done, {username}!")
    st.write(f"Total time taken: {total_test_time} seconds.")
    st.write(f"Correct answers: {correct_answers} out of {len(questions)}")
    st.write(f"Total time spent: {total_time} seconds")
    
    # Displaying time per question
    st.write("Time taken per question:")
    for q_id, time_taken in time_per_question:
        st.write(f"Question {q_id}: {time_taken} seconds")
    
    # Displaying time spent per topic
    st.write("Time spent per topic:")
    for topic, time_spent in topic_time.items():
        st.write(f"{topic}: {time_spent} seconds")
    
    # Displaying incorrect questions
    st.write("Incorrect Questions:")
    for q_id in incorrect_questions:
        st.write(f"Question {q_id} was answered incorrectly.")
    
    # Displaying topic-wise scores
    st.write("Topic-wise Scores:")
    for topic, score in topic_scores.items():
        total_topic_questions = topic_counts.get(topic, 0)
        st.write(f"{topic}: {score}/{total_topic_questions} correct")

# Function to start the mock test
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

        # Ask the user for input with a unique key for each question
        user_answer = st.radio(
            "Your answer:",
            ['A', 'B', 'C', 'D'],
            key=f"question_{q['Question ID']}"  # Unique key based on the question ID
        )

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

# Streamlit interface to log in and start the mock test
def main():
    # Login page
    st.title("Welcome to the Mock Test App")
    username = st.text_input("Enter your username")

    if username:
        if st.button("Start Mock Test"):
            start_mock_test(username)
        else:
            st.write("Please enter your username and click 'Start Mock Test' to begin.")

if __name__ == "__main__":
    main()
