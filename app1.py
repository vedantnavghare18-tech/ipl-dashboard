import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="IPL Official Analytics", layout="wide")

# ---------------- THEME ----------------
st.markdown("""
<style>
.stApp {
    background-color: #ADD8E6;
    color: black;
}
h1, h2, h3 {
    color: #002366;
}
</style>
""", unsafe_allow_html=True)

st.title("🏏 IPL Official Analytics Dashboard")

# ---------------- LOAD DATA ----------------
matches = pd.read_csv("matches.csv")
deliveries = pd.read_csv("deliveries.csv")

# Add season column to deliveries
deliveries = deliveries.merge(matches[['id','season']],
                              left_on='match_id',
                              right_on='id')

# ---------------- SIDEBAR ----------------
menu = st.sidebar.selectbox("Select Analysis", [
    "Home",
    "Team Analysis",
    "Player Analysis",
    "Head to Head",
    "Orange Cap",
    "Purple Cap",
    "Powerplay Stats",
    "Death Overs",
    "Toss Impact"
])

# ---------------- HOME ----------------
if menu == "Home":

    st.header("🏠 IPL Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Matches", matches.shape[0])
    col2.metric("Total Runs", deliveries['total_runs'].sum())
    col3.metric("Total Wickets", deliveries['is_wicket'].sum())
    col4.metric("Total Seasons", matches['season'].nunique())


# ---------------- TEAM ANALYSIS ----------------
elif menu == "Team Analysis":

    st.header("🏏 Team Analysis")

    team = st.selectbox("Search Team", sorted(matches['team1'].unique()))

    season_filter = st.selectbox(
        "Select Season (Optional)",
        ["All"] + sorted(matches['season'].unique())
    )

    team_matches = matches[
        (matches['team1'] == team) |
        (matches['team2'] == team)
    ]

    if season_filter != "All":
        team_matches = team_matches[team_matches['season'] == season_filter]

    wins = team_matches[team_matches['winner'] == team].shape[0]

    st.write("Matches Played:", team_matches.shape[0])
    st.write("Wins:", wins)


# ---------------- PLAYER ANALYSIS ----------------
elif menu == "Player Analysis":

    st.header("👤 Player Analysis")

    player = st.selectbox(
        "Search Player",
        sorted(deliveries['batter'].unique())
    )

    player_data = deliveries[deliveries['batter'] == player]

    total_runs = player_data['batsman_runs'].sum()
    total_balls = player_data.shape[0]

    st.metric("Total Runs", total_runs)
    st.metric("Total Balls Faced", total_balls)


# ---------------- HEAD TO HEAD ----------------
elif menu == "Head to Head":

    st.header("🤝 Head to Head Comparison")

    teams = sorted(matches['team1'].unique())

    team1 = st.selectbox("Select Team 1", teams)
    team2 = st.selectbox("Select Team 2", teams)

    h2h = matches[
        ((matches['team1'] == team1) & (matches['team2'] == team2)) |
        ((matches['team1'] == team2) & (matches['team2'] == team1))
    ]

    st.write("Total Matches:", h2h.shape[0])
    st.write("Wins -", team1, ":", h2h[h2h['winner'] == team1].shape[0])
    st.write("Wins -", team2, ":", h2h[h2h['winner'] == team2].shape[0])


# ---------------- ORANGE CAP ----------------
elif menu == "Orange Cap":

    st.header("🟠 Orange Cap - Top Run Scorers")

    season = st.selectbox(
        "Select Season",
        sorted(deliveries['season'].unique())
    )

    orange = deliveries[deliveries['season'] == season] \
        .groupby('batter')['batsman_runs'].sum() \
        .sort_values(ascending=False).head(10)

    fig = px.bar(
        orange,
        x=orange.index,
        y=orange.values,
        labels={'x': 'Player', 'y': 'Runs'},
        title=f"Top 10 Run Scorers - {season}"
    )

    st.plotly_chart(fig)

    st.download_button(
        "Download Report",
        orange.to_csv(),
        f"orange_cap_{season}.csv"
    )


# ---------------- PURPLE CAP ----------------
elif menu == "Purple Cap":

    st.header("🟣 Purple Cap - Top Wicket Takers")

    season = st.selectbox(
        "Select Season",
        sorted(deliveries['season'].unique())
    )

    wickets = deliveries[
        (deliveries['season'] == season) &
        (deliveries['dismissal_kind'] != 'run out')
    ]

    purple = wickets.groupby('bowler')['is_wicket'] \
        .sum().sort_values(ascending=False).head(10)

    fig = px.bar(
        purple,
        x=purple.index,
        y=purple.values,
        labels={'x': 'Bowler', 'y': 'Wickets'},
        title=f"Top 10 Wicket Takers - {season}"
    )

    st.plotly_chart(fig)

    st.download_button(
        "Download Report",
        purple.to_csv(),
        f"purple_cap_{season}.csv"
    )


# ---------------- POWERPLAY ----------------
elif menu == "Powerplay Stats":

    st.header("⚡ Powerplay Statistics")

    team = st.selectbox(
        "Search Team",
        sorted(deliveries['batting_team'].unique())
    )

    powerplay = deliveries[
        (deliveries['over'] <= 6) &
        (deliveries['batting_team'] == team)
    ]

    total_runs = powerplay['total_runs'].sum()

    st.metric("Total Powerplay Runs", total_runs)


# ---------------- DEATH OVERS ----------------
elif menu == "Death Overs":

    st.header("💀 Death Over Statistics")

    team = st.selectbox(
        "Search Team",
        sorted(deliveries['batting_team'].unique())
    )

    death = deliveries[
        (deliveries['over'] >= 16) &
        (deliveries['batting_team'] == team)
    ]

    total_runs = death['total_runs'].sum()

    st.metric("Total Death Over Runs", total_runs)


# ---------------- TOSS IMPACT ----------------
elif menu == "Toss Impact":

    st.header("🎯 Toss Impact Analysis")

    season = st.selectbox(
        "Select Season",
        ["All"] + sorted(matches['season'].unique())
    )

    data = matches.copy()

    if season != "All":
        data = data[data['season'] == season]

    toss_win = data[data['toss_winner'] == data['winner']]
    percentage = (len(toss_win) / len(data)) * 100 if len(data) > 0 else 0

    st.metric("Win % After Winning Toss", round(percentage, 2))

    pie_data = pd.DataFrame({
        'Result': ['Won After Toss', 'Lost After Toss'],
        'Count': [len(toss_win), len(data) - len(toss_win)]
    })

    fig = px.pie(
        pie_data,
        names='Result',
        values='Count',
        title="Toss Impact"
    )

    st.plotly_chart(fig)