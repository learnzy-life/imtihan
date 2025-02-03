def show_results():
    st.balloons()
    st.title("📊 Detailed Performance Analysis")
    
    # Calculate basic metrics
    total_time = sum(ans['time_taken'] for ans in st.session_state.user_answers.values())
    correct = sum(1 for ans in st.session_state.user_answers.values() if ans['selected'] == ans['correct'])
    accuracy = (correct / len(questions)) * 100
    topper_total_time = total_time * 0.7  # Topper's total time (30% less)

    # --- Time Analysis Section ---
    st.header("⏱ Time Management Analysis")
    
    # Create columns for time metrics
    time_col1, time_col2, time_col3 = st.columns(3)
    with time_col1:
        st.metric("Your Total Time", f"{total_time:.2f}s", delta="Your Time")
    with time_col2:
        st.metric("Topper's Benchmark Time", f"{topper_total_time:.2f}s", delta_color="off")
    with time_col3:
        time_diff = total_time - topper_total_time
        st.metric("Time Difference", f"{time_diff:.2f}s", 
                 delta=f"{'Over' if time_diff > 0 else 'Under'} Benchmark")

    # Add time comparison chart
    st.subheader("Question-wise Time Comparison")
    time_data = []
    for q in questions:
        user_time = st.session_state.user_answers[q['Question ID']]['time_taken']
        topper_time = get_topper_time(user_time)
        time_data.append({
            'Question': q['Question ID'],
            'Your Time': user_time,
            'Topper Time': topper_time
        })
    
    # Display as bar chart
    time_df = pd.DataFrame(time_data).set_index('Question')
    st.bar_chart(time_df)

    # --- Topic-wise Analysis Section ---
    st.header("📚 Topic-wise Performance Breakdown")
    
    # Calculate topic statistics
    topic_stats = {}
    for q in questions:
        topic = q['Topic']
        ans = st.session_state.user_answers[q['Question ID']]
        
        if topic not in topic_stats:
            topic_stats[topic] = {
                'correct': 0,
                'total': 0,
                'user_time': 0,
                'topper_time': 0
            }
        
        topic_stats[topic]['total'] += 1
        topic_stats[topic]['user_time'] += ans['time_taken']
        topic_stats[topic]['topper_time'] += get_topper_time(ans['time_taken'])
        
        if ans['selected'] == ans['correct']:
            topic_stats[topic]['correct'] += 1

    # Create dataframe for display
    analysis_df = pd.DataFrame.from_dict(topic_stats, orient='index')
    analysis_df['Accuracy'] = (analysis_df['correct'] / analysis_df['total']) * 100
    analysis_df['Avg Time/Question'] = analysis_df['user_time'] / analysis_df['total']
    analysis_df['Topper Avg Time'] = analysis_df['topper_time'] / analysis_df['total']
    analysis_df['Time Difference'] = analysis_df['Avg Time/Question'] - analysis_df['Topper Avg Time']
    analysis_df['Status'] = analysis_df.apply(lambda x: 
        "🚨 Needs Improvement" if x['Accuracy'] < 70 else "✅ Strong", axis=1)

    # Display topic analysis in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Accuracy Analysis")
        for topic, data in analysis_df.iterrows():
            st.write(f"**{topic}**")
            st.progress(data['Accuracy']/100)
            st.caption(f"{data['correct']}/{data['total']} correct ({data['Accuracy']:.1f}%)")
            
            if data['Accuracy'] < 70:
                st.markdown(f"💡 **Suggestion:** [Watch Video]({get_video_suggestions(topic)})")

    with col2:
        st.subheader("Time Efficiency")
        for topic, data in analysis_df.iterrows():
            st.write(f"**{topic}**")
            st.metric(
                label="Avg Time/Question",
                value=f"{data['Avg Time/Question']:.1f}s",
                delta=f"{data['Time Difference']:.1f}s vs Topper",
                delta_color="inverse"
            )

    # --- Detailed Data Table ---
    with st.expander("📋 View Detailed Statistics Table"):
        st.dataframe(
            analysis_df[['Accuracy', 'Avg Time/Question', 'Topper Avg Time', 'Status']].style
                .format({
                    'Accuracy': "{:.1f}%",
                    'Avg Time/Question': "{:.1f}s",
                    'Topper Avg Time': "{:.1f}s"
                })
                .applymap(lambda x: 'background-color: #ffcccc' if x == "🚨 Needs Improvement" else ''),
            use_container_width=True
        )

    # --- Final Summary ---
    st.header("🎯 Key Takeaways")
    weak_topics = analysis_df[analysis_df['Accuracy'] < 70].index.tolist()
    
    if weak_topics:
        st.error(f"**Focus Areas:** You need improvement in {', '.join(weak_topics)}")
    else:
        st.success("**Great Job!** You're performing well across all topics!")

    st.write(f"**Overall Accuracy:** {accuracy:.1f}%")
    st.write(f"**Total Test Time:** {total_time:.2f}s (Topper Benchmark: {topper_total_time:.2f}s)")
