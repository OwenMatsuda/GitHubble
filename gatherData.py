import json
import os

import queries
import query_strings as qs

# Collaborators
print("Querying Contributors")
final_collab = queries.main_query(
    qs.collaborators, "repositories", [qs.single_repo], "repository", ["collaborators"]
)
final_collab_dict = queries.to_dict(final_collab, ["collaborators"])

print("Querying Teams")
final_team = queries.main_query(
    qs.teams,
    "teams",
    [qs.single_team_members, qs.single_team_repos],
    "team",
    ["members", "repositories"],
)
final_team_dict = queries.to_dict(final_team, ["members", "repositories"])


# Last Contribution
print("Gathering Contributors")
contributor_list = queries.get_contributors(final_collab_dict)
organization_id = queries.get_organization_id(qs.organization_id)
print("Querying Last Contributions")
last_contribution_set = queries.contributor_last_contribution(
    qs.last_contribution, contributor_list, organization_id
)

# Save data in data folder
try:
    os.mkdir("./data/")
except:
    pass
with open("data/contributors.json", "w+") as f:
    json.dump(final_collab_dict, f)
print("Saved Contributors in data/contributors.json")
with open("data/contributor_list.json", "w+") as f:
    json.dump(contributor_list, f)
print("Saved Contributor list to data/contributor_list.json")
with open("data/teams.json", "w+") as f:
    json.dump(final_team_dict, f)
print("Saved Teams in data/teams.json")
with open("data/contributions.json", "w+") as f:
    json.dump(last_contribution_set, f)
print("Saved Last Contributions in data/contributions.json")
