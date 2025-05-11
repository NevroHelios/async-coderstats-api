# Async CoderStats API

This project provides a FastAPI backend to fetch and aggregate user statistics from various coding platforms and analyze GitHub repositories.

## Challenge:

Developers and recruiters often need to gather programming-related statistics and information about a user or a project from multiple sources. Manually collecting this data from different platforms like GitHub, LeetCode, GeeksforGeeks, and Codeforces, or analyzing repository structures and content can be time-consuming and inefficient.

## Solution:

This API offers a centralized solution by providing specific endpoints to:
*   Fetch user statistics from GitHub, LeetCode, GeeksforGeeks, and Codeforces.
*   Retrieve a summary, file tree, and content (including code blocks for smaller repositories) of a given GitHub repository.

This simplifies data aggregation and provides a structured way to access this information programmatically.

## Tech:

*   **Backend Framework:** FastAPI
*   **Language:** Python
*   **HTTP Requests:** `requests` library
*   **Web Scraping (for Codeforces):** `BeautifulSoup4`
*   **Repository Analysis:** `gitingest` 
*   **Development Server:** Uvicorn (managed via `uv`)

## Result:

A robust and easy-to-use API that serves as a single point of access for:
*   Consolidated user profiles from popular coding platforms.
*   Quick insights into GitHub repository structure, summary, and code.

This can be valuable for portfolio websites, developer dashboards, recruitment tools, or any application requiring programmatic access to coding-related data.

## Development Server

For Windows:
```bash
uv run uvicorn main:app
```

With custom host/port:
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

```
GET /github_stats/{username}
GET /leetcode_stats/{username}
GET /geeksforgeeks_stats/{username}
GET /repo_summary/?repo_url={repository_url}
```