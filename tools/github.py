import requests
import os
from dotenv import load_dotenv 

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print(
        "Warning: GITHUB_TOKEN environment variable not set. API requests may be rate limited or fail."
    )

BASE_HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    BASE_HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"


def get_github_stats(username: str) -> dict | None:
    def get_github_user(username):
        """Fetch GitHub user data"""
        url = f"https://api.github.com/users/{username}"
        headers = BASE_HEADERS.copy() 
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching user data: Status code {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching user data: {e}")
            return None

    def get_user_repos(username):
        """Fetch repositories for a GitHub user"""
        url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
        headers = BASE_HEADERS.copy()
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error fetching user repos: Status code {response.status_code}")
                # Add response text for more detailed error diagnosis
                print(f"Response: {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching user repos: {e}")
            return []

    def get_repo_languages(username, repo_name):
        """Fetch languages used in a repository"""
        url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
        # Use BASE_HEADERS
        headers = BASE_HEADERS.copy()
        try:
            # Pass updated headers
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"Error fetching languages for repo {repo_name}: Status code {response.status_code}"
                )
                # Add response text for more detailed error diagnosis
                print(f"Response: {response.text}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching languages for repo {repo_name}: {e}")
            return {}

    def get_user_stats(username):
        """Fetch GitHub user stats"""
        user_data = get_github_user(username)
        if not user_data:
            print(
                f"Could not retrieve user data for {username}. Cannot generate stats."
            )
            return None

        repos = get_user_repos(username)
        processed_repos = []
        for repo in repos:
            repo_copy = repo.copy()
            languages = get_repo_languages(username, repo_copy["name"])
            repo_copy["languages"] = languages
            processed_repos.append(
                {
                    "name": repo.get("name"),
                    "full_name": repo.get("full_name"),
                    "html_url": repo.get("html_url"),
                    "description": repo.get("description"),
                    "fork": repo.get("fork"),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "pushed_at": repo.get("pushed_at"),
                    "stargazers_count": repo.get("stargazers_count"),
                    "watchers_count": repo.get("watchers_count"),
                    "language": repo.get("language"), # Primary language
                    "forks_count": repo.get("forks_count"),
                    "open_issues_count": repo.get("open_issues_count"),
                    # Get license name if license object exists, otherwise None
                    "license": repo.get("license", {}).get("name") if repo.get("license") else None,
                    "topics": repo.get("topics", []),
                    "languages": languages # Add the fetched languages breakdown
                }
            )

        stats = {
            "username": username,
            "followers": user_data["followers"],
            "following": user_data["following"],
            "public_repos": user_data["public_repos"],
            "repos": processed_repos,
        }
        return stats

    return get_user_stats(username)


if __name__ == "__main__":
    target_username = "nevrohelios"
    print(f"Fetching GitHub stats for {target_username}...")
    res = get_github_stats(target_username)

    import json
    from colorama import Fore
    print(
        Fore.GREEN + "GitHub stats fetched successfully!" + Fore.RESET
    )
    print(json.dumps(res, indent=4))
    with open("temp.json", "w") as f:
        json.dump(res, f, indent=4)