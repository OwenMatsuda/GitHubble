# GitHubble

### Instructions

1. In a terminal, clone the repo: `git clone github.com/OwenMatsuda/GitHubble`
2. cd into the folder: `cd GitHubble`
3. Set up a virtual environment: `python3 -m venv venv`. Activate it with `source venv/bin/activate`. Install the requirements with `pip install -r requirements.txt`.
4. Set ORGANIZATION and API_KEY within the .env file. If you don't already have an api key, you can create one [here](https://github.com/settings/tokens). Make sure to give it full read access, or it might cause an error.
5. To collect the information: `python gatherData.py`. This could take anywhere from a few seconds to a few minutes depending on how many repositories, users, teams, and contributions there are in your organization.
6. Run `python app.py`, copy the address in your terminal `http://127.0.0.1:8050/`, and paste it into the browser.

### Notes

 - Due to limitations of GitHub's GraphQL API
     1. A max of 100 repositories will be included for each of commit, issue, PR, and PRR contributions for each individual. I'm not sure how these repositories are chosen.
     2. Only the 100 most recent contributions will be included for each individual in the past year
     3. Only contributions to public repositories are shown (this is being worked on)
     4. The repositories tab isn't finished
