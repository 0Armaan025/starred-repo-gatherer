import streamlit as st
import requests
import pandas as pd


def fetch_user_repos(token, username):
    """
    Fetch repositories owned by the user (not starred repositories).
    """
    base_url = "https://api.github.com"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"{base_url}/users/{username}/repos"

    page = 1
    user_repos = []

    while True:
        response = requests.get(f"{url}?per_page=100&page={page}", headers=headers)
        if response.status_code != 200:
            st.error(f"Error: {response.status_code} - {response.json().get('message')}")
            break

        repos = response.json()
        if not repos:
            break

        # Include only repos owned by the user
        user_repos.extend([repo for repo in repos if repo["owner"]["login"] == username])

        page += 1
        if page > 5:  # Limit pages for testing
            st.warning("Stopping early for testing. Adjust the page limit.")
            break

    return user_repos


def fetch_stargazers(token, stargazers_url):
    """
    Fetch stargazers for a given repository.
    """
    headers = {"Authorization": f"Bearer {token}"}
    page = 1
    stargazers = set()

    while True:
        response = requests.get(f"{stargazers_url}?per_page=100&page={page}", headers=headers, timeout=10)
        if response.status_code != 200:
            break

        stargazers_page = response.json()
        if not stargazers_page:
            break

        stargazers.update([user["login"] for user in stargazers_page])
        page += 1
        if page > 2:  # Limit for testing
            break

    return stargazers


# Streamlit App
st.title("GitHub Repository Stars Summary")
st.markdown(
    "Enter your **GitHub Token** and **Username** to fetch a summary of stars on repositories you own."
)

# Input fields
github_token = st.text_input("GitHub Token", type="password", help="Enter your GitHub Personal Access Token")
github_username = st.text_input("GitHub Username", help="Enter your GitHub username")

if st.button("Fetch Summary"):
    if github_token and github_username:
        with st.spinner("Fetching data..."):
            # Fetch user-owned repositories
            repos = fetch_user_repos(github_token, github_username)
            if repos:
                total_stars = 0
                all_stargazers = set()
                genuine_stargazers = set()

                for repo in repos:
                    repo_name = repo["name"]
                    stars = repo["stargazers_count"]
                    stargazers = fetch_stargazers(github_token, repo["stargazers_url"])

                    total_stars += stars
                    all_stargazers.update(stargazers)

                    # Exclude stars by the username itself
                    genuine_stargazers.update(stargazers - {github_username})

                # Prepare data for the summary
                data = {
                    "Total Stars": [total_stars],
                    "Unique Stargazers": [len(all_stargazers)],
                    "Genuine Stars (By Others)": [len(genuine_stargazers)],
                }

                # Display results in a table
                st.subheader("Summary")
                summary_table = pd.DataFrame(data)
                st.table(summary_table)

                st.subheader("Stargazer Details")
                st.write(f"**Everyone Who Starred You:** {', '.join(all_stargazers)}")
                st.write(f"**Genuine Stars By Others:** {', '.join(genuine_stargazers)}")
            else:
                st.warning("No repositories found for the given username.")
    else:
        st.error("Please provide both a GitHub Token and Username.")
