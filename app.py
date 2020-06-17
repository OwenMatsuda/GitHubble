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

# ======================
# Dash app
# ======================


def build_header():
    return html.Div(
        children=[
            html.H2(id="header", className="bare_container", children="GITHUBBLE"),
            html.H5(
                id="little_header",
                className="bare_container",
                children="A GitHub Dashboard",
            ),
        ]
    )


def build_tabs():
    return html.Div(
        children=[
            dcc.Tabs(
                id="tabs",
                value="users",
                className="custom_tab_container",
                children=[
                    dcc.Tab(
                        label="Overview",
                        value="overview",
                        className="custom_tab",
                        selected_className="custom_tab_selected",
                    ),
                    dcc.Tab(
                        label="Users",
                        value="users",
                        className="custom_tab",
                        selected_className="custom_tab_selected",
                    ),
                    dcc.Tab(
                        label="Repositories",
                        value="repositories",
                        className="custom_tab",
                        selected_className="custom_tab_selected",
                    ),
                ],
            )
        ]
    )


def build_date_picker_range(id):
    return html.Div(
        children=[
            html.P("Time Period", className="control_label"),
            dcc.DatePickerRange(
                id=id,
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date,
            ),
        ]
    )


def build_include_weekends_checkbox(id):
    return dcc.Checklist(
        className="dcc_control",
        id=id,
        options=[{"label": "Include Weekends", "value": "include_weekends"}],
    )


def build_contribution_type_dropdown(id):
    return html.Div(
        children=[
            html.P("Contribution Type", className="control_label"),
            dcc.Dropdown(
                id=id,
                className="dcc_control",
                value="All",
                options=[
                    {"label": "All", "value": "All"},
                    {"label": "Commit", "value": "Commit"},
                    {"label": "Issue", "value": "Issue"},
                    {"label": "Pull Request", "value": "PullRequest"},
                    {"label": "Pull Request Review", "value": "PullRequestReview"},
                ],
            ),
        ]
    )


def build_repository_dropdown(id):
    return html.Div(
        children=[
            html.P("Repository", className="control_label"),
            dcc.Dropdown(
                id=id, className="dcc_control", value="All", options=repo_list_options
            ),
        ]
    )


def build_team_dropdown(id):
    return html.Div(
        children=[
            html.P("Team", className="control_label"),
            dcc.Dropdown(
                id=id, value="All", className="dcc_control", options=team_list_options
            ),
        ]
    )


def build_contribution_graph_layout(title):
    return dict(
        autosize=True,
        automargin=True,
        margin={"l": 30, "r": 30, "b": 20, "t": 40},
        hovermode="closest",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend={"font": {"size": 10}, "orientation": "h"},
        title=title,
    )


def build_graph(id, title):
    return html.Div(
        className="pretty_container eight columns",
        children=[
            dcc.Graph(id=id, figure=dict(layout=build_contribution_graph_layout(title)))
        ],
    )


def build_table(id, columns=[]):
    return dash_table.DataTable(
        id=id,
        page_size=10,
        sort_action="native",
        filter_action="native",
        columns=columns,
    )


def build_user_dropdown(id):
    return html.Div(
        children=[
            html.P("Select User", className="control_label"),
            dcc.Dropdown(
                id=id,
                className="dcc_control",
                options=[
                    {
                        "label": contributor["name"]
                        if contributor["name"]
                        else contributor["login"],
                        "value": contributor["login"],
                    }
                    for contributor in contributor_list
                ],
            ),
        ]
    )


# Tabs
overview_tab = [
    # Controls and Graph
    html.Div(
        className="row flex_display",
        children=[
            # Controls
            html.Div(
                className="pretty_container four columns",
                children=[
                    build_date_picker_range("all_contribution_date"),
                    build_include_weekends_checkbox("all_include_weekends"),
                    build_contribution_type_dropdown("all_contribution_type"),
                    build_repository_dropdown("all_repo"),
                    build_team_dropdown("all_team"),
                ],
            ),
            build_graph("all_contribution_graph", "All Contributions"),
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
                    className="inline_radio",
                    options=[
                        {"label": "Contributions", "value": "contributions"},
                        {
                            "label": "People who Haven't Contributed",
                            "value": "no_contributions",
                        },
                    ],
                    value="contributions",
                ),
                build_table("all_contribution_table"),
            ],
        ),
    ),
]


users_tab = [
    dcc.Store(id="users_repo_list", data=[]),
    html.Div(
        className="row flex_display",
        children=[
            html.Div(
                className="pretty_container four columns",
                children=[
                    build_user_dropdown("users_person"),
                    build_include_weekends_checkbox("users_include_weekends"),
                    build_contribution_type_dropdown("users_contribution_type"),
                    build_repository_dropdown("users_repo"),
                    build_date_picker_range("users_contribution_date"),
                ],
            ),
            build_graph("users_contribution_graph", "User Contributions"),
        ],
    ),
    html.Div(
        className="row flex_display",
        children=html.Div(
            className="pretty_container twelve columns",
            children=[
                # Title
                html.H4("Contributions Table", className="inline_control_label"),
                build_table(
                    "users_contribution_table",
                    columns=[
                        {"name": col, "id": col}
                        for col in contributions_df.columns[:-1]
                    ],
                ),
            ],
        ),
    ),
    html.Div(
        className="row flex_display",
        children=[
            html.Div(
                className="pretty_container six columns",
                children=[
                    # Title
                    html.H4("Teams User is on", className="inline_control_label"),
                    build_table(
                        "users_teams_table", columns=[{"name": "Team", "id": "team"}]
                    ),
                ],
            ),
            html.Div(
                className="pretty_container six columns",
                children=[
                    # Title
                    html.H4(
                        "Repositories User has access to",
                        className="inline_control_label",
                    ),
                    build_table(
                        "users_repositories_table",
                        columns=[{"name": "Repository", "id": "repository"}],
                    ),
                ],
            ),
        ],
    ),
]

repositories_tab = [
    html.Div(
        className="row flex_display",
        children=[
            html.Div(
                className="pretty_container four columns",
                children=[
                    build_repository_dropdown("repos_repo"),
                    build_include_weekends_checkbox("repos_include_weekends"),
                    build_contribution_type_dropdown("repos_contribution_type"),
                    build_user_dropdown("repos_person"),
                    build_date_picker_range("repos_contribution_date"),
                ],
            ),
            build_graph("repos_contribution_graph", "User Contributions"),
        ],
    )
]

app = dash.Dash(__name__, external_stylesheets=["./assets/styles.css"])
app.config["suppress_callback_exceptions"] = True

# Page
app.layout = html.Div(
    id="page", children=[build_header(), build_tabs(), html.Div(id="tab_content")]
)

# Tab navigation
@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def display_content(tab):
    if tab == "overview":
        return overview_tab
    elif tab == "users":
        return users_tab
    elif tab == "repositories":
        return repositories_tab


# ======================
# All Contributions
# ======================

# Graph and Table
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
    layout = build_contribution_graph_layout("All Contributions")
    # Filter df
    contributions = contributions_df
    dates = all_days_list
    contributors = contributor_list
    # Filter by Include Weekends
    if not include_weekends:
        contributions = contributions[contributions.is_weekday == True]
        dates = weekdays_only_list
    # Filter by date
    dates = list(filter(lambda d: d >= start_date and d <= end_date, dates))
    contributions = contributions[
        (contributions.date >= start_date) & (contributions.date <= end_date)
    ]
    # Filter by Contribution Type
    if contribution_type != "All":
        contributions = contributions[
            contributions.contribution_type == contribution_type
        ]
    # Filter by Repository
    if repo != "All":
        contributions = contributions[contributions.repo_name == repo]
        contributors = list(
            filter(
                lambda d: d in data_contributors[repo]["collaborators"], contributors
            )
        )
    # Filter by Team
    if team != "All":
        team_users_logins = [user["login"] for user in data_teams[team]["members"]]
        contributions = contributions[
            contributions.contributor_login.isin(team_users_logins)
        ]
        contributors = list(
            filter(lambda d: d in data_teams[team]["members"], contributors)
        )
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


# ======================
# User Contributions
# ======================

# Calendar start date
@app.callback(
    Output("users_contribution_date", "start_date"), [Input("users_person", "value")]
)
def update_calendar_start(user):
    contributions = contributions_df[contributions_df.contributor_login == user]
    if contributions.empty:
        return min_date
    user_first_contribution = contributions.date.min()
    return user_first_contribution


# Repositories specific to user
@app.callback(
    [Output("users_repo_list", "data"), Output("users_repo", "options")],
    [Input("users_person", "value")],
)
def create_user_repo_list(user):
    repo_list = ["All"]
    for repo_name, repo_content in data_contributors.items():
        login_list = [
            contributor["login"] for contributor in repo_content["collaborators"]
        ]
        if user in login_list:
            repo_list.append(repo_name)
    repo_list_options = [
        {"label": repo_name, "value": repo_name} for repo_name in repo_list
    ]
    return repo_list, repo_list_options


# Graph and Table
@app.callback(
    [
        Output("users_contribution_graph", "figure"),
        Output("users_contribution_table", "data"),
        Output("users_teams_table", "data"),
        Output("users_repositories_table", "data"),
    ],
    [
        Input("users_person", "value"),
        Input("users_include_weekends", "value"),
        Input("users_contribution_type", "value"),
        Input("users_repo", "value"),
        Input("users_contribution_date", "start_date"),
        Input("users_contribution_date", "end_date"),
    ],
    [State("users_repo_list", "data")],
)
def update_user_contrib(
    user,
    include_weekends,
    contribution_type,
    repo,
    start_date,
    end_date,
    users_repo_list,
):
    # Layout
    layout = build_contribution_graph_layout("User Contributions")
    # Filter df
    contributions = contributions_df[contributions_df.contributor_login == user]
    dates = all_days_list
    # Filter by Include Weekends
    if not include_weekends:
        contributions = contributions[contributions.is_weekday == True]
        dates = weekdays_only_list
    # Filter by date
    dates = list(filter(lambda d: d >= start_date and d <= end_date, dates))
    contributions = contributions[
        (contributions.date >= start_date) & (contributions.date <= end_date)
    ]
    # Filter by Contribution Type
    if contribution_type != "All":
        contributions = contributions[
            contributions.contribution_type == contribution_type
        ]
    # Filter by Repository
    if repo != "All":
        contributions = contributions[contributions.repo_name == repo]
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
    graph_output = dict(data=data, layout=layout)

    # Set table output
    contributions_table_output = contributions.to_dict("records")

    # Teams Table
    teams_table_output = []
    for team_name, team_content in data_teams.items():
        login_list = [team_member["login"] for team_member in team_content["members"]]
        if user in login_list:
            teams_table_output.append({"team": team_name})
    # Repos Table
    repos_table_output = [{"repository": repo_name} for repo_name in users_repo_list]
    return (
        graph_output,
        contributions_table_output,
        teams_table_output,
        repos_table_output,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
