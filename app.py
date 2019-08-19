import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import json
import datetime
import pandas as pd

# Read in Collaborator data
with open("./data/collaborators.json", "r") as f:
    data_collaborators = json.load(f)
# Read in Team data
with open("./data/teams.json", "r") as f:
    data_teams = json.load(f)
# Read in Contribution data
with open("./data/contributions.json", "r") as f:
    data_contributions = json.load(f)

# Construct pandas DataFrame
contributions_df = pd.DataFrame(data=data_contributions)
# Add datetime dates as pandas column
datetime_dates = list(
    map(
        lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"), list(contributions_df.date)
    )
)
contributions_df["datetime_date"] = datetime_dates
# Add is_weekend to pandas column
def is_weekday_func(date):
    if date.weekday() < 5:
        return True
    else:
        return False


is_weekday_list = list(map(is_weekday_func, list(contributions_df.datetime_date)))
contributions_df["is_weekday"] = is_weekday_list

# Get list of repos and teams
repo_list = list(data_collaborators.keys())
team_list = list(data_teams.keys())

# Convert list to options
repo_list_options = [{"label": "All", "value": "All"}] + [
    {"label": repo, "value": repo} for repo in repo_list
]
team_list_options = [{"label": "All", "value": "All"}] + [
    {"label": team, "value": team} for team in team_list
]

# Get dates for DatePickerRange
min_date = contributions_df.datetime_date.min()
max_date = contributions_df.datetime_date.max()
# Get a list of days, datetime, and string format, with and without weekends
def datetime_list_to_string_list(date_list):
    return list(
        map(lambda date: datetime.datetime.strftime(date, "%Y-%m-%d"), date_list)
    )


datetime_days = [
    min_date + datetime.timedelta(days=i) for i in range((max_date - min_date).days + 1)
]
all_days_list = datetime_list_to_string_list(datetime_days)
weekdays_only_list = datetime_list_to_string_list(
    filter(is_weekday_func, datetime_days)
)

app = dash.Dash(__name__, external_stylesheets=["./assets/styles.css"])

# Page
app.layout = html.Div(
    className="page",
    children=[
        # Header
        html.H2(id="header", className="bare_container", children="GITHUBBLE"),
        html.H5(
            id="little_header",
            className="bare_container",
            children="A GitHub Dashboard",
        ),
        # Controls and Graph
        html.Div(
            className="row flex-display",
            children=[
                # Controls
                html.Div(
                    className="pretty_container four columns",
                    children=[
                        # Date Picker
                        html.P("Time Period", className="control_label"),
                        dcc.DatePickerRange(
                            className="dcc_control",
                            id="all_contribution_date",
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            start_date=min_date,
                            end_date=max_date,
                        ),
                        # Include Weekends
                        dcc.Checklist(
                            className="dcc_control",
                            id="all_include_weekends",
                            options=[
                                {
                                    "label": "Include Weekends",
                                    "value": "include_weekends",
                                }
                            ],
                            value=[],
                        ),
                        # Contribution Type
                        html.P("Contribution Type", className="control_label"),
                        dcc.Dropdown(
                            id="all_contribution_type",
                            className="dcc_control",
                            value="All",
                            options=[
                                {"label": "All", "value": "All"},
                                {"label": "Commit", "value": "Commit"},
                                {"label": "Issue", "value": "Issue"},
                                {"label": "Pull Request", "value": "PullRequest"},
                                {
                                    "label": "Pull Request Review",
                                    "value": "PullRequestReview",
                                },
                            ],
                        ),
                        # Repository
                        html.P("Repository", className="control_label"),
                        dcc.Dropdown(
                            id="all_repo",
                            className="dcc_control",
                            value="All",
                            options=repo_list_options,
                        ),
                        # Team
                        html.P("Team", className="control_label"),
                        dcc.Dropdown(
                            id="all_team",
                            value="All",
                            className="dcc_control",
                            options=team_list_options,
                        ),
                    ],
                ),
                # All Contributions Graph
                html.Div(
                    className="pretty_container eight columns",
                    children=[dcc.Graph(id="all_contribution_graph")],
                ),
            ],
        ),
        # Table
        html.Div(
            className="row flex-display",
            children=html.Div(
                className="pretty_container twelve columns",
                children=[
                    html.H4("Contributions Table", className="control_label"),
                    dash_table.DataTable(
                        id="all_contribution_table",
                        page_size=10,
                        sort_action="native",
                        filter_action="native",
                        columns=[
                            # Don't include the is_weekday column
                            {"name": col, "id": col} for col in contributions_df.columns[:-1]
                        ],
                    ),
                ],
            ),
        ),
    ],
)


# All Contributions Graph
@app.callback(
    [
        Output("all_contribution_graph", "figure"),
        Output("all_contribution_table", "data"),
    ],
    [
        Input("all_contribution_date", "start_date"),
        Input("all_contribution_date", "end_date"),
        Input("all_include_weekends", "value"),
        Input("all_contribution_type", "value"),
        Input("all_repo", "value"),
        Input("all_team", "value"),
    ],
)
def update_all_contrib(start_date, end_date, include_weekends, contribution_type, repo, team):
    # Layout
    layout = dict(
        autosize=True,
        automargin=True,
        margin={"l": 30, "r": 30, "b": 20, "t": 40},
        hovermode="closest",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend={"font": {"size": 10}, "orientation": "h"},
        title="All Contributions",
    )
    # Filter df
    contributions = contributions_df
    dates = all_days_list
    # Include Weekends
    if not include_weekends:
        contributions = contributions[contributions.is_weekday == True]
        dates = weekdays_only_list
    # Filter by date
    dates = list(filter(lambda d: d >= start_date and d <= end_date, dates))
    contributions = contributions[(contributions.date >= start_date) & (contributions.date <= end_date)]
    # Contribution Type
    if contribution_type != "All":
        contributions = contributions[
            contributions.contribution_type == contribution_type
        ]
    # Repository
    if repo != "All":
        contributions = contributions[contributions.repo_name == repo]
    # Team
    if team != "All":
        team_users_logins = [user["login"] for user in data_teams[team]["members"]]
        contributions = contributions[
            contributions.contributor_login.isin(team_users_logins)
        ]
    # Get number of contributions for each date
    contribution_num = [
        len(contributions[contributions.date == date].index) for date in dates
    ]
    data = [
        dict(
            type="scatter",
            mode="line",
            x=dates,
            y=contribution_num,
            line=dict(shape="spline", smoothing="0.5"),
        )
    ]
    # Set output vars
    graph_output = dict(data=data, layout=layout)
    table_output = contributions.to_dict("records")
    return graph_output, table_output


if __name__ == "__main__":
    app.run_server(debug=True)
