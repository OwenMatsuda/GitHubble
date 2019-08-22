import os
import requests
import collections

from dotenv import load_dotenv

load_dotenv()

# Get environment variables
API_KEY = os.getenv("API_KEY")
ORGANIZATION = os.getenv("ORGANIZATION")

# Raise exception if environment variable doesn't exist
for env_var in [API_KEY, ORGANIZATION]:
    if env_var is None:
        raise Exception(
            "{} is not in environment. Make sure to put it in your .env file".format(
                env_var
            )
        )

print("Querying information for {}".format(ORGANIZATION))

# Run a GraphQL query
def run_query(query, run_num=0):
    # Set up Authorization
    headers = {"Authorization": "Bearer " + API_KEY}

    # Send Query Request
    request = requests.post(
        "https://api.github.com/graphql", json={"query": query}, headers=headers
    )
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(
            "Query failed to run by returning code of {}. Make sure that your API KEY is correct, in your .env, and has read:org, read:user, and repo permissions.".format(
                request.status_code
            )
        )


# Main query to get information
"""
query_str_main is query string that gets most of the data
query_type_main is the type of query ("repositories" or "teams")
query_str_extras is a list for secondary queries that get the rest of the information
  - this exists as a workaround to make the queries more efficient
query_type1 is a GitHub API keyword to select certain info ("repository" or "team")
query_type2 is a list of secondary GitHub API keywords to further select info
  - it is paired with query_str_extras to gather further data
"""


def main_query(
    query_str_main, query_type_main, query_str_extras, query_type1, query_type2
):
    final_data = []
    start_cursor = ""
    total_entries = 0
    # Continue querying information while each query returns the max(100) entries
    while (total_entries % 100) == 0:
        # Sort through query_type
        query = query_str_main.format(ORGANIZATION, start_cursor)
        result = run_query(query)
        # Test to make sure data was actually received
        try:
            data_list = result["data"]["organization"][query_type_main]
        except:
            raise Exception(
                "API Key does not have full permission. You must give complete read access."
            )
        # Add queried data to final_data list
        final_data.extend(data_list["edges"])
        # Move pagination cursor
        end_cursor = data_list["pageInfo"]["endCursor"]
        start_cursor = ', after:"' + end_cursor + '"'
        # Print information to screen
        total_entries = len(final_data)
        print("Gathered {} entries".format(total_entries))
    # Gather remaining information
    for i, this_query_str in enumerate(query_str_extras):
        # Get query type from query_type2 list
        this_query_type = query_type2[i]
        # Sort through queried data to see if extras are needed
        for entry in final_data:
            item = entry["node"]
            values = item[this_query_type]
            # If values is None, all of the values have been queried and nothing else needs to be fetched
            if values is None:
                continue
            child_count = values["totalCount"]
            # Original query gets 100 entries, so if greater than 100, need to get more
            if child_count > 100:
                item_name = item["name"]
                # Set pagination cursor to the last one queried
                end_cursor = values["pageInfo"]["endCursor"]
                # Gather rest of the info
                for i in range(100, child_count, 100):
                    # Format query string
                    new_query = this_query_str.format(
                        ORGANIZATION, item_name, end_cursor
                    )
                    result = run_query(new_query)
                    # Add new info to the existing list
                    new_entry = result["data"]["organization"][query_type1][
                        this_query_type
                    ]
                    item[this_query_type]["edges"].extend(new_entry["edges"])
                    # Update pagination cursor
                    end_cursor = new_entry["pageInfo"]["endCursor"]
    return final_data


# Converts the data into a more easily read/parsed python dictionary
# The GraphQL query returns data with many extra layers that makes it hard to read
def to_dict(data_list, query_types):
    data_dict = {}
    for entry in data_list:
        item = entry["node"]
        item_name = item["name"]
        for query in query_types:
            if item_name not in data_dict:
                data_dict[item_name] = {}
            data_dict[item_name][query] = []
            item_list = item[query]
            if item_list is None:
                continue
            total_count = item_list["totalCount"]
            data_dict[item_name][query] = [i["node"] for i in item_list["edges"]]
    ordered_dict = dict(
        collections.OrderedDict(sorted(data_dict.items(), key=lambda k: k[0].lower()))
    )
    return ordered_dict


# Gets a list of all contributors in data_dict
def get_contributors(data_dict):
    contributor_list = []
    for name, item in data_dict.items():
        contributor_list.extend(item["collaborators"])
    contributor_list = list({v["login"]: v for v in contributor_list}.values())
    print("Gathered {} Contributors".format(len(contributor_list)))
    contributor_list = sorted(
        contributor_list,
        key=lambda d: d["name"].lower() if d["name"] else d["login"].lower(),
    )
    return contributor_list


# Gets the organization id
def get_organization_id(query_str):
    result = run_query(query_str.format(ORGANIZATION))
    organization_id = result["data"]["organization"]["id"]
    print("Got organization_id {}".format(organization_id))
    return organization_id


# Organizes contributions into repos
def get_contribution_type(
    contribution_list,
    contribution_name,
    contributor_login,
    contributor_name,
    last_contribution_set,
):
    for repo in contribution_list:
        # Gather the rest of the data
        repo_name = repo["repository"]["name"]
        contributions = repo["contributions"]
        all_contributions_list = contributions["edges"]
        total_count = contributions["totalCount"]
        print("  {} - Found {} {}s".format(repo_name, total_count, contribution_name))

        for contribution in all_contributions_list:
            last_contribution_set["contributor_login"].append(contributor_login)
            last_contribution_set["contributor_name"].append(contributor_name)
            last_contribution_set["repo_name"].append(repo_name)
            last_contribution_set["contribution_type"].append(contribution_name)
            last_contribution_set["date"].append(
                contribution["node"]["occurredAt"][0:10]
            )
    return last_contribution_set


# Gets all the last contributions by type and repository
# types: commits, issues, PR's, PRR's
def contributor_last_contribution(query_str, contributor_list, organization_id):
    last_contribution_set = {
        "contributor_login": [],
        "contributor_name": [],
        "repo_name": [],
        "contribution_type": [],
        "date": [],
    }
    for contributor in contributor_list:
        contributor_login = contributor["login"]
        contributor_name = contributor["name"]

        print(
            "Querying contributions for {}".format(
                contributor_name if contributor_name else contributor_login
            )
        )

        # Run contributor query
        contributor_query = query_str.format(contributor_login, organization_id)
        result = run_query(contributor_query)

        contributions = result["data"]["user"]["contributionsCollection"]
        contribution_count = contributions["contributionCalendar"]["totalContributions"]
        contribution_types = [
            "commitContributionsByRepository",
            "issueContributionsByRepository",
            "pullRequestContributionsByRepository",
            "pullRequestReviewContributionsByRepository",
        ]
        contribution_names = ["Commit", "Issue", "PullRequest", "PullRequestReview"]

        last_contributions = {}
        all_contributions = []
        for contribution_num, contribution_type in enumerate(contribution_types):
            this_contribution = contributions[contribution_type]
            this_contribution_name = contribution_names[contribution_num]
            last_contribution_set = get_contribution_type(
                this_contribution,
                this_contribution_name,
                contributor_login,
                contributor_name,
                last_contribution_set,
            )
    return last_contribution_set


# =====================================
# Format of final_collab_dict
# =====================================

"""
GitHub repo{
    [
        {
            name: 'Name'
            login: 'Username'
        }
    ]
}
"""

# =====================================
# Format of final_team_dict
# =====================================

"""
GitHub Team{
    [
        Members[
            {
                name: 'Name'
                login: 'Username'
            }
        ]
        Repos[
            {
                name: 'Repo Name'
            }
        ]
    ]
}
"""

# =====================================
# Format of last_contributions
# =====================================

"""
{
    "contributor_login": [],
    "contributor_name": [],
    "repo_name": [],
    "contribution_type": [],
    "date": []
}
"""
