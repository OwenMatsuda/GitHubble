# =====================================
# Collaborators
# =====================================

collaborators = """{{
    organization(login: "{}") {{
        repositories(first: 100{}){{
            pageInfo{{
                endCursor
            }}
            edges {{
                node {{
                    name
                    collaborators(first:100){{
                        totalCount
                        pageInfo{{
                            endCursor
                        }}
                        edges {{
                            node{{
                                name
                                login
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
}}
"""

single_repo = """{{
    organization(login: "{}") {{
        repository(name: "{}"){{
            collaborators(first: 100, after: "{}"){{
                pageInfo{{
                    endCursor
                }}
                edges{{
                    node{{
                        name
                        login
                    }}
                }}
            }}
        }}
    }}
}}
"""


# =====================================
# Teams
# =====================================

teams = """{{
    organization(login:"{}"){{
        teams(first: 100){{
            pageInfo{{
                endCursor
            }}
            edges{{
                node{{
                    name
                    members(first:100){{
                        totalCount
                        pageInfo{{
                            endCursor
                        }}
                        edges{{
                            node{{
                                name
                                login
                            }}
                        }}
                    }}
                    repositories(first:100){{
                        totalCount
                        pageInfo{{
                            endCursor
                        }}
                        edges{{
                            node{{
                                name
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
}}
"""

single_team_members = """{{
    organization(login: "{}") {{
        team(slug: "{}") {{
            members(first:100, after: "{}"){{
                pageInfo{{
                    endCursor
                }}
                edges{{
                    node{{
                        name
                        login
                    }}
                }}
            }}
        }}
    }}
}}
"""

single_team_repos = """{{
    organization(login: "{}"){{
        team(slug: "{}"){{
            repositories(first:100, after: "{}"){{
                pageInfo{{
                    endCursor
                }}
                edges{{
                    node{{
                        name
                    }}
                }}
            }}
        }}
    }}
}}
"""


# =====================================
# Last Contribution
# =====================================

organization_id = """{{
    organization(login: "{}") {{
        id
    }}
}}
"""

last_contribution = """{{
    user(login: "{}") {{
        contributionsCollection(organizationID: "{}") {{
            hasAnyContributions
            contributionCalendar {{
                totalContributions
            }}
            commitContributionsByRepository(maxRepositories: 100) {{
                repository {{
                    name
                }}
                contributions(first: 100) {{
                    totalCount
                    pageInfo{{
                        endCursor
                    }}
                    edges {{
                        node {{
                            occurredAt
                        }}
                    }}
                }}
            }}
            issueContributionsByRepository(maxRepositories: 100) {{
                repository {{
                    name
                }}
                contributions(first: 100) {{
                    totalCount
                    pageInfo{{
                        endCursor
                    }}
                    edges {{
                        node {{
                            occurredAt
                        }}
                    }}
                }}
            }}
            pullRequestContributionsByRepository(maxRepositories: 100) {{
                repository {{
                    name
                }}
                contributions(first: 100) {{
                    totalCount
                    pageInfo{{
                        endCursor
                    }}
                    edges {{
                        node {{
                            occurredAt
                        }}
                    }}
                }}
            }}
            pullRequestReviewContributionsByRepository(maxRepositories: 100) {{
                repository {{
                    name
                }}
                contributions(first: 100) {{
                    totalCount
                    pageInfo{{
                        endCursor
                    }}
                    edges {{
                        node {{
                            occurredAt
                        }}
                    }}
                }}
            }}
        }}
    }}
}}
"""
