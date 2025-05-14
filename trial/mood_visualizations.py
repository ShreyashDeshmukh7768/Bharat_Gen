# mood_visualizations.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
from database import SupabaseClient
import json


def prepare_mood_data(diary_entries):
    """Convert diary entries to DataFrame for visualization"""
    if not diary_entries:
        return None
    
    # Initialize lists for DataFrame
    dates = []
    moods = []
    timestamps = []
    
    # Common moods and their numeric values (for sentiment scale)
    mood_values = {
        "happy": 5, "excited": 5, "joyful": 5, "content": 4, "peaceful": 4, "grateful": 4,
        "calm": 3, "neutral": 3, "reflective": 3,
        "confused": 2, "worried": 2, "anxious": 2, "sad": 1, "angry": 1, "frustrated": 1,
        "tired": 2, "lonely": 1, "overwhelmed": 1, "stressed": 1, "disappointed": 1
    }
    
    # Process each entry
    for entry in diary_entries:
        # Get date and time
        created_at = entry.get('created_at', '')
        if 'T' in created_at:
            date_str = created_at.split('T')[0]
            time_str = created_at.split('T')[1].split('.')[0]
        else:
            parts = created_at.split(' ')
            date_str = parts[0]
            time_str = parts[1] if len(parts) > 1 else "00:00:00"
            
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            dates.append(date_obj)
            
            # Get full timestamp - ensure it's timezone-naive
            timestamp = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            timestamps.append(timestamp)
            
            # Get mood
            mood = entry.get('mood', 'neutral').lower()
            moods.append(mood)
        except:
            continue
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'timestamp': timestamps,
        'mood': moods,
        'mood_value': [mood_values.get(m.lower(), 3) for m in moods]  # Default to neutral (3) if not found
    })
    
    return df


def create_mood_timeline(diary_entries):
    """Create a timeline visualization of mood entries"""
    df = prepare_mood_data(diary_entries)
    if df is None or df.empty:
        st.info("Not enough data to generate mood timeline.")
        return
    
    # Create mood color mapping
    mood_colors = {
        5: "#28A745",  # Positive moods - green
        4: "#8CD47E",  # Slightly positive - light green
        3: "#FFC107",  # Neutral moods - yellow
        2: "#F77F50",  # Slightly negative - orange
        1: "#DC3545"   # Negative moods - red
    }
    
    # Create timeline chart
    fig = px.line(df, 
                  x='timestamp', 
                  y='mood_value',
                  labels={'timestamp': 'Date', 'mood_value': 'Mood'},
                  title='Your Mood Timeline')
    
    # Add scatter points with mood as hover text
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['mood_value'],
            mode='markers',
            marker=dict(
                size=10,
                color=[mood_colors.get(val, "#FFC107") for val in df['mood_value']],
                line=dict(width=2, color='DarkSlateGrey')
            ),
            text=df['mood'],
            hoverinfo='text+x'
        )
    )
    
    # Customize layout
    fig.update_layout(
        hovermode="closest",
        yaxis=dict(
            tickvals=[1, 2, 3, 4, 5],
            ticktext=["Negative", "Slightly Negative", "Neutral", "Slightly Positive", "Positive"],
            range=[0.5, 5.5]
        ),
        xaxis_title="Date",
        yaxis_title="Mood",
        height=400,
        margin=dict(l=60, r=40, t=80, b=80)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_mood_distribution(diary_entries):
    """Create a donut chart showing distribution of moods"""
    df = prepare_mood_data(diary_entries)
    if df is None or df.empty:
        st.info("Not enough data to generate mood distribution.")
        return
    
    # Count moods
    mood_counts = df['mood'].value_counts()
    
    # Group similar moods for better visualization
    mood_groups = {
        "Positive": ["happy", "excited", "joyful", "content", "grateful", "peaceful", "proud"],
        "Neutral": ["neutral", "calm", "reflective"],
        "Anxious": ["anxious", "worried", "stressed", "overwhelmed"],
        "Sad": ["sad", "lonely", "disappointed"],
        "Angry": ["angry", "frustrated"],
        "Other": ["confused", "tired"]
    }
    
    # Create the grouped counts
    grouped_counts = {}
    for group, moods in mood_groups.items():
        count = sum(mood_counts.get(mood, 0) for mood in moods)
        if count > 0:
            grouped_counts[group] = count
    
    # Create color mapping for groups
    color_map = {
        "Positive": "#28A745",  # Green
        "Neutral": "#FFC107",   # Yellow
        "Anxious": "#17A2B8",   # Blue
        "Sad": "#6F42C1",       # Purple
        "Angry": "#DC3545",     # Red
        "Other": "#6C757D"      # Grey
    }
    
    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=list(grouped_counts.keys()),
        values=list(grouped_counts.values()),
        hole=.4,
        marker_colors=[color_map.get(mood, "#6C757D") for mood in grouped_counts.keys()]
    )])
    
    fig.update_layout(
        title_text="Mood Distribution",
        height=350,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def create_weekly_mood_chart(diary_entries):
    """Create a heatmap of moods by day of week and time of day"""
    df = prepare_mood_data(diary_entries)
    if df is None or df.empty:
        st.info("Not enough data to generate weekly mood patterns.")
        return
    
    # Add day of week and hour columns
    df['day_of_week'] = df['timestamp'].dt.day_name()
    df['hour'] = df['timestamp'].dt.hour
    
    # Create time buckets (morning, afternoon, evening, night)
    time_buckets = []
    for hour in df['hour']:
        if 5 <= hour < 12:
            time_buckets.append('Morning (5-11am)')
        elif 12 <= hour < 17:
            time_buckets.append('Afternoon (12-4pm)')
        elif 17 <= hour < 21:
            time_buckets.append('Evening (5-8pm)')
        else:
            time_buckets.append('Night (9pm-4am)')
    
    df['time_bucket'] = time_buckets
    
    # Order days correctly
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    time_order = ['Morning (5-11am)', 'Afternoon (12-4pm)', 'Evening (5-8pm)', 'Night (9pm-4am)']
    
    # Calculate average mood by day and time bucket
    avg_mood = df.groupby(['day_of_week', 'time_bucket'])['mood_value'].mean().reset_index()
    
    # Create pivot table
    pivot_df = avg_mood.pivot(index='day_of_week', columns='time_bucket', values='mood_value')
    
    # Reorder based on days_order and time_order
    pivot_df = pivot_df.reindex(days_order)
    pivot_df = pivot_df.reindex(columns=time_order)
    
    # Create heatmap
    fig = px.imshow(
        pivot_df,
        labels=dict(x="Time of Day", y="Day of Week", color="Mood Score"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale=[
            [0, "rgb(220, 53, 69)"],       # Negative - red
            [0.25, "rgb(247, 127, 80)"],   # Slightly negative - orange
            [0.5, "rgb(255, 193, 7)"],     # Neutral - yellow
            [0.75, "rgb(140, 212, 126)"],  # Slightly positive - light green
            [1, "rgb(40, 167, 69)"]        # Positive - green
        ],
        zmin=1, zmax=5
    )
    
    fig.update_layout(
        title="Weekly Mood Patterns",
        height=350,
        margin=dict(l=20, r=20, t=60, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def get_recent_mood_trend(diary_entries, days=7):
    """Calculate the mood trend over the specified days"""
    df = prepare_mood_data(diary_entries)
    if df is None or df.empty:
        return "neutral", "steady"
    
    # Filter for recent entries - ensure timezone-naive comparison
    now = datetime.now()
    start_date = now - timedelta(days=days)
    recent_df = df[df['date'] >= start_date]
    
    if recent_df.empty:
        return "neutral", "steady"
    
    # Calculate average mood
    avg_mood = recent_df['mood_value'].mean()
    
    # Determine dominant mood category
    if avg_mood >= 4.5:
        dominant_mood = "very positive"
    elif avg_mood >= 3.5:
        dominant_mood = "positive"
    elif avg_mood >= 2.5:
        dominant_mood = "neutral"
    elif avg_mood >= 1.5:
        dominant_mood = "negative"
    else:
        dominant_mood = "very negative"
    
    # Calculate trend if there are enough entries
    if len(recent_df) >= 3:
        # Split into first and second half
        recent_df = recent_df.sort_values('timestamp')
        half_point = len(recent_df) // 2
        first_half = recent_df.iloc[:half_point]
        second_half = recent_df.iloc[half_point:]
        
        avg_first = first_half['mood_value'].mean()
        avg_second = second_half['mood_value'].mean()
        
        if avg_second > avg_first + 0.5:
            trend = "improving"
        elif avg_second < avg_first - 0.5:
            trend = "declining"
        else:
            trend = "steady"
    else:
        trend = "steady"
    
    return dominant_mood, trend


def create_dashboard_mood_summary(user_id):
    """Create a summary of mood data for the dashboard"""
    db = SupabaseClient()
    diary_entries = db.get_emotional_diary_history(user_id)
    
    if not diary_entries:
        st.warning("No mood data available. Start using the Emotional Diary to track your moods.")
        return
    
    dominant_mood, trend = get_recent_mood_trend(diary_entries)
    
    # Display current mood trend
    st.subheader("Your Recent Mood")
    
    # Define emoji and color based on mood
    mood_emoji = {
        "very positive": "😊",
        "positive": "🙂",
        "neutral": "😐",
        "negative": "😔",
        "very negative": "😢"
    }
    
    trend_emoji = {
        "improving": "↗️",
        "steady": "➡️",
        "declining": "↘️"
    }
    
    mood_color = {
        "very positive": "#28A745",
        "positive": "#8CD47E",
        "neutral": "#FFC107",
        "negative": "#F77F50",
        "very negative": "#DC3545"
    }
    
    # Create mood indicator
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<h1 style='text-align: center; color: {mood_color.get(dominant_mood, '#FFC107')};'>{mood_emoji.get(dominant_mood, '😐')}</h1>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"**Overall Mood:** {dominant_mood.title()}")
        st.markdown(f"**Trend:** {trend.title()} {trend_emoji.get(trend, '➡️')}")
        
        # Display entry count - FIX: Make both datetimes timezone-naive
        now = datetime.now().replace(tzinfo=None)  # Make naive
        recent_count = sum(1 for entry in diary_entries if (
            now - datetime.fromisoformat(entry['created_at'].replace('Z', '')).replace(tzinfo=None)
        ).days <= 7)
        st.markdown(f"**Recent entries:** {recent_count} in the last week")
    
    # Create mini mood timeline
    df = prepare_mood_data(diary_entries)
    if df is not None and not df.empty:
        # Filter to last 14 days - ensure timezone-naive comparison
        recent_date = datetime.now() - timedelta(days=14)
        recent_df = df[df['date'] >= recent_date]
        
        if not recent_df.empty:
            # Create simplified timeline chart
            fig = px.line(recent_df, 
                          x='timestamp', 
                          y='mood_value',
                          title='')
            
            # Add points
            fig.add_trace(
                go.Scatter(
                    x=recent_df['timestamp'], 
                    y=recent_df['mood_value'],
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=recent_df['mood_value'],
                        colorscale=[
                            [0, "#DC3545"],    # Red for lowest values
                            [0.25, "#F77F50"], # Orange
                            [0.5, "#FFC107"],  # Yellow
                            [0.75, "#8CD47E"], # Light green
                            [1, "#28A745"]     # Green for highest values
                        ],
                        cmin=1,
                        cmax=5
                    ),
                    showlegend=False
                )
            )
            
            # Customize layout
            fig.update_layout(
                height=180,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                yaxis=dict(
                    visible=False,
                    range=[0.5, 5.5]
                ),
                xaxis=dict(showgrid=False),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)


def display_mood_visualizations(user_id):
    """Display all mood visualizations on the diary page"""
    db = SupabaseClient()
    diary_entries = db.get_emotional_diary_history(user_id)
    
    if not diary_entries:
        st.warning("No mood data available. Start using the diary to see visualizations.")
        return

    st.markdown("## Your Mood Analytics")
    
    # First row - Timeline and Distribution
    col1, col2 = st.columns([3, 2])
    
    with col1:
        create_mood_timeline(diary_entries)
    
    with col2:
        create_mood_distribution(diary_entries)
    
    # Second row - Weekly patterns
    create_weekly_mood_chart(diary_entries)