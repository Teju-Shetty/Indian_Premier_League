import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import numpy as np

# Function to load data
@st.cache(allow_output_mutation=True)
def load_data():
    deliveries_data = pd.read_excel('analysis_ball_by_ball_2008_2023.xlsx')
    match_data = pd.read_excel('analysis_ipl_match_result_2008_2023.xlsx')
    return deliveries_data, match_data

# Function to preprocess data
@st.cache(allow_output_mutation=True)
def preprocess_data(deliveries_data, match_data):
    # Merge data to get season-wise total runs
    season_data = match_data[['id', 'Season']].merge(deliveries_data, left_on='id', right_on='id', how='left').drop('id', axis=1)
    season = season_data.groupby(['Season'])['total_runs'].sum().reset_index()
    
    # Number of matches played in each season
    match_data['Season'] = pd.DatetimeIndex(match_data['Date']).year
    match_per_season = match_data.groupby(['Season'])['id'].count().reset_index().rename(columns={'id': 'matches'})
    
    # Calculate runs scored per match across seasons
    runs_per_season = pd.concat([match_per_season, season.iloc[:, 1]], axis=1)
    runs_per_season['Runs scored per match'] = runs_per_season['total_runs'] / runs_per_season['matches']
    runs_per_season.set_index('Season', inplace=True)
    
    return match_per_season, season, runs_per_season

# Function to generate the plots
@st.cache(allow_output_mutation=True)
def generate_plots(match_per_season, season, runs_per_season):
    colors = ['turquoise',] * 16
    colors[5] = 'crimson'

    # Plot 1: Number of matches played in each season
    fig_matches = px.bar(data_frame=match_per_season, x='Season', y='matches', labels=dict(x="Season", y="Count"))
    fig_matches.update_layout(
        title="Number of matches played in different seasons",
        titlefont={'size': 26},
        template='simple_white'
    )
    fig_matches.update_traces(marker_line_color='black', marker_line_width=2.5, opacity=1, marker_color=colors)

    # Plot 2: Total Runs Across the Seasons
    fig_runs = px.line(season, x='Season', y='total_runs')
    fig_runs.update_layout(
        title="Total Runs Across the Seasons",
        titlefont={'size': 26},
        template='simple_white'
    )
    
    # Plot 3: Runs scored per match across seasons
    fig_runs_per_match = px.line(runs_per_season, x=runs_per_season.index, y="Runs scored per match")
    fig_runs_per_match.update_layout(
        title="Runs scored per match across seasons",
        titlefont={'size': 26},
        template='simple_white'
    )

    return fig_matches, fig_runs, fig_runs_per_match

# Function to generate toss-related plots
@st.cache(allow_output_mutation=True)
def generate_toss_plots(match_data):
    colors = ['turquoise',] * 18
    colors[0] = 'crimson'

    # Plot 4: Number of tosses win by a team
    toss = match_data['TossWinner'].value_counts()
    fig_toss_win = px.bar(y=toss, x=toss.index, labels=dict(x="Season", y="Count"))
    fig_toss_win.update_layout(title="No. of tosses won by each team",
                               titlefont={'size': 26},
                               template='simple_white'
                               )
    fig_toss_win.update_traces(marker_line_color='black', marker_line_width=2.5, opacity=1, marker_color=colors)

    # Plot 5: Decision made after winning a toss
    temp_series = match_data.TossDecision.value_counts()
    labels = (np.array(temp_series.index))
    values = (np.array((temp_series / temp_series.sum()) * 100))
    fig_toss_decision = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig_toss_decision.update_traces(hoverinfo='label+percent', textinfo='label+percent', textfont_size=20,
                                    marker=dict(colors=colors, line=dict(color='#000000', width=3)))
    fig_toss_decision.update_layout(title="Toss decision percentage",
                                    titlefont={'size': 30},
                                    )

    # Plot 6: Toss decision across season
    fig_toss_decision_across_season = px.histogram(data_frame=match_data, x='Season', color='TossDecision',
                                                   color_discrete_sequence=colors, barmode='group')
    fig_toss_decision_across_season.update_layout(title="Toss decision in different seasons",
                                                  titlefont={'size': 26}, template='simple_white'
                                                  )
    fig_toss_decision_across_season.update_traces(marker_line_color='black', marker_line_width=2.5, opacity=1)

    # Plot 7: Winning Toss implies winning game?
    match_data['toss_win_game_win'] = np.where((match_data.TossWinner == match_data.WinningTeam), 'Yes', 'No')
    match_data.head()
    labels = ["Yes", 'No']
    values = match_data['toss_win_game_win'].value_counts()
    fig_toss_win_implication = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    fig_toss_win_implication.update_traces(hoverinfo='label+percent', textinfo='label+percent', textfont_size=20,
                                           marker=dict(colors=colors, line=dict(color='#000000', width=3)))
    fig_toss_win_implication.update_layout(title="Winning toss implies winning matches?",
                                           titlefont={'size': 30},
                                           )

    return fig_toss_win, fig_toss_decision, fig_toss_decision_across_season, fig_toss_win_implication


# Streamlit app code
def main():
    st.title('IPL Matches Analysis')
    
    # Load data
    deliveries_data, match_data = load_data()

    # Preprocess data
    match_per_season, season, runs_per_season = preprocess_data(deliveries_data, match_data)
    
    # Create checkboxes for showing the plots
    show_matches_plot = st.checkbox("Show Number of matches played in different seasons")
    show_runs_plot = st.checkbox("Show Total Runs Across the Seasons")
    show_runs_per_match_plot = st.checkbox("Show Runs scored per match across seasons")
    show_toss_analysis = st.checkbox("Show Toss Analysis")

    # Generate and display the plots based on checkbox selection
    if show_matches_plot:
        fig_matches, _, _ = generate_plots(match_per_season, season, runs_per_season)
        st.plotly_chart(fig_matches, use_container_width=True)  # Adjust the width to fit the plot
    
    if show_runs_plot:
        _, fig_runs, _ = generate_plots(match_per_season, season, runs_per_season)
        st.plotly_chart(fig_runs, use_container_width=True)  # Adjust the width to fit the plot
    
    if show_runs_per_match_plot:
        _, _, fig_runs_per_match = generate_plots(match_per_season, season, runs_per_season)
        st.plotly_chart(fig_runs_per_match, use_container_width=True)  # Adjust the width to fit the plot
    
    if show_toss_analysis:
        fig_toss_win, fig_toss_decision, fig_toss_decision_across_season, fig_toss_win_implication = generate_toss_plots(match_data)
        
        # Arrange the recent four graphs in two rows with two graphs in each row
        col1, col2 = st.beta_columns(2)
        
        with col1:
            #st.subheader("Number of tosses won by each team")
            st.plotly_chart(fig_toss_win, use_container_width=True)  # Adjust the width to fit the plot
            
            #st.subheader("Toss decision in different seasons")
            st.plotly_chart(fig_toss_decision_across_season, use_container_width=True)  # Adjust the width to fit the plot
            
        with col2:
            #st.subheader("Toss decision percentage")
            st.plotly_chart(fig_toss_decision, use_container_width=True)  # Adjust the width to fit the plot
        
            #st.subheader("Winning toss implies winning matches?")
            st.plotly_chart(fig_toss_win_implication, use_container_width=True)  # Adjust the width to fit the plot

if __name__ == "__main__":
    main()

# Credit Section
# Define the developer name and their GitHub and LinkedIn URLs
developer_name = "Tejasvi Shetty"
github_url = "https://github.com/Teju-Shetty"
linkedin_url = "https://www.linkedin.com/in/tejasvi-shetty-8801ba228"

# Create a row with the name and icons

st.title("")
st.markdown("<p style='text-align: center; color: #E9E8E8; font-family:'alata', sans-serif;'>Developed by </p>", unsafe_allow_html=True)

#container = st.container()
#container.markdown(f"<div style='display: flex; align-items: center; justify-content: center;'><p style='margin-right: 10px;'>{developer_name} <a href='{github_url}' target='_blank'><img style='margin-right: 10px; width:25px;height:25px; background-color: white; border-radius: 50%;' src='https://github.com/favicon.ico' alt='GitHub'></a> <a href='{linkedin_url}' target='_blank'><img style='width: 20px; height: 20px;' src='https://www.linkedin.com/favicon.ico' alt='LinkedIn'></a></p></div>", unsafe_allow_html=True)

       
# container.markdown(f"<div style='display: flex; align-items: center; justify-content: center;'><p style='margin-right: 10px;'>{developer_name1} <a href='{github_url1}' target='_blank'><img style='margin-right: 10px;width:25px;height:25px;  background-color: white; border-radius: 50%;' src='https://github.com/favicon.ico' alt='GitHub'></a> <a href='{linkedin_url1}' target='_blank'><img style='width: 20px; height: 20px;' src='https://www.linkedin.com/favicon.ico' alt='LinkedIn'></a></p></div>", unsafe_allow_html=True)


st.title("")

# Contact Support


st.markdown("<h2 style='text-align: center; color: #E9E8E8; font-family:'alata', sans-serif;'>Feedback</h2>", unsafe_allow_html=True)


contact_form = """
<form action="https://formsubmit.co/feedback.wachatanalyzer@gmail.com" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required >
     <input type="email" name="email" placeholder="Your email" required>
     <textarea name="message" placeholder="Your message here" ></textarea>
     <button type="submit">Send</button>
</form>
"""

st.markdown(contact_form, unsafe_allow_html=True)

# Use Local CSS File
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style/style.css")

# Support Ends

st.caption('© 2023. All rights reserved.')
