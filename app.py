import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import json
import datetime
import pandas as pd

# Read in Contributor data
with open("./data/contributors.json", "r") as f:
    data_contributors = json.load(f)
# Read in Contributor list
with open("./data/contributor_list.json", "r") as f:
    contributor_list = json.load(f)
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

# Get list of repos, teams, and contributors
repo_list = list(data_contributors.keys())
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

# Dash app

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
            className="row flex_display",
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
            className="row flex_display",
            children=html.Div(
                className="pretty_container twelve columns",
                children=[
                    # Title
                    html.H4("Contributions Table", className="inline_control_label"),
                    # Has Contributed or not
                    dcc.RadioItems(
                        id="all_show_contributions",
                        className="inline_radio inline_radio_container",
                        options=[
                            {"label": "Contributions", "value": "contributions"},
                            {
                                "label": "People who Haven't Contributed",
                                "value": "no_contributions",
                            },
                        ],
                        value="contributions",
                    ),
                    # Table
                    dash_table.DataTable(
                        id="all_contribution_table",
                        page_size=10,
                        sort_action="native",
                        filter_action="native",
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
        Output("all_contribution_table", "columns"),
    ],
    [
        Input("all_contribution_date", "start_date"),
        Input("all_contribution_date", "end_date"),
        Input("all_include_weekends", "value"),
        Input("all_contribution_type", "value"),
        Input("all_repo", "value"),
        Input("all_team", "value"),
        Input("all_show_contributions", "value"),
    ],
)
def update_all_contrib(
    start_date,
    end_date,
    include_weekends,
    contribution_type,
    repo,
    team,
    show_contributions,
):
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
    contributors = contributor_list
    # Include Weekends
    if not include_weekends:
        contributions = contributions[contributions.is_weekday == True]
        dates = weekdays_only_list
    # Filter by date
    dates = list(filter(lambda d: d >= start_date and d <= end_date, dates))
    contributions = contributions[
        (contributions.date >= start_date) & (contributions.date <= end_date)
    ]
    # Contribution Type
    if contribution_type != "All":
        contributions = contributions[
            contributions.contribution_type == contribution_type
        ]
    # Repository
    if repo != "All":
        contributions = contributions[contributions.repo_name == repo]
        contributors = list(filter(lambda d: d in data_contributors[repo]["collaborators"], contributors))
    # Team
    if team != "All":
        team_users_logins = [user["login"] for user in data_teams[team]["members"]]
        contributions = contributions[
            contributions.contributor_login.isin(team_users_logins)
        ]
        contributors = list(filter(lambda d: d in data_teams[team]["members"], contributors))
    # Get number of contributions for each date
    contribution_num = [
        len(contributions[contributions.date == date].index) for date in dates
    ]
    # Graph Data
    data = [
        dict(
            type="scatter",
            mode="line",
            x=dates,
            y=contribution_num,
            line=dict(shape="spline", smoothing="0.5"),
        )
    ]
    # Set graph output
    graph_output = dict(data=data, layout=layout)

    # Set table output
    # [-1] to disclude the is_weekday column
    columns = [{"name": col, "id": col} for col in contributions.columns[:-1]]
    table_output = contributions.to_dict("records")
    if show_contributions == "no_contributions":
        no_contribution_list = [
            contributor
            for contributor in contributors
            if contributor["login"] not in contributions.contributor_login.unique()
        ]
        # Set table data
        table_output = no_contribution_list
        # Set columns to only name and login
        columns = [{"name": col, "id": col} for col in ["name", "login"]]
    return graph_output, table_output, columns


if __name__ == "__main__":
    app.run_server(debug=True)
