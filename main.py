import streamlit as st
import requests

def fetch_starred_repos(token, username):
    base_url = "https://api.github.com"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"{base_url}/users/{username}/starred"

    page = 1
    all_repos = []

    while True:
        response = requests.get(f"{url}?per_page=100&page={page}", headers=headers)
        if response.status_code != 200:
            st.error(f"Error: {response.status_code} - {response.json().get('message')}")
            break

        repos = response.json()
        if not repos:
            break

        # Exclude forked repositories
        non_forked_repos = [repo for repo in repos if not repo["fork"]]
        all_repos.extend(non_forked_repos)

        # Debug: Show current page progress
        st.write(f"Fetched page {page} with {len(non_forked_repos)} repos.")

        page += 1
        # Limit pages for testing
        if page > 5:  # Remove or increase this limit for real use
            st.warning("Stopping early for testing. Adjust the page limit.")
            break

    return all_repos

def fetch_stargazers(token, stargazers_url):
    headers = {"Authorization": f"Bearer {token}"}
    page = 1
    all_users = []

    while True:
        response = requests.get(f"{stargazers_url}?per_page=100&page={page}", headers=headers)
        if response.status_code != 200:
            st.warning(f"Stargazers fetch failed: {response.status_code}")
            break

        stargazers = response.json()
        if not stargazers:
            break

        all_users.extend([user["login"] for user in stargazers])

        page += 1
        # Limit stargazers for testing
        if page > 2:  # Adjust as needed
            st.warning("Stopping stargazers early for testing.")
            break

    return all_users

# Streamlit App
st.title("GitHub Starred Repositories Fetcher")

github_token = st.text_input("GitHub Token", type="password")
github_username = st.text_input("GitHub Username")

if st.button("Fetch Repositories"):
    if github_token and github_username:
        with st.spinner("Fetching repositories..."):
            repos = fetch_starred_repos(github_token, github_username)

            if repos:
                st.success(f"Fetched {len(repos)} non-forked repositories.")

                total_stars = 0
                genuine_stars = set()

                for repo in repos:
                    stargazers = fetch_stargazers(github_token, repo["stargazers_url"])
                    repo_name = repo["full_name"]
                    star_count = repo["stargazers_count"]

                    # Exclude stars by "0Armaan025"
                    stargazers = [user for user in stargazers if user != "0Armaan025"]

                    # Add unique stargazers
                    total_stars += star_count
                    genuine_stars.update(stargazers)

                    st.write(f"- **Repo:** {repo_name}")
                    st.write(f"  - Stars: {star_count}")
                    st.write(f"  - Genuine Stars: {len(set(stargazers))}")
    else:
        st.error("Please provide a GitHub Token and Username.")
