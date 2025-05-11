from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import gitingest

from tools.github import get_github_stats
from tools.leetcode import get_leetcode_stats
from tools.gfg import get_gfg_stats
# from tools.codeforces import get_codeforces_user_data

app = FastAPI(debug=False)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/github_stats/{username}")
def github_stats(username: str):
    return get_github_stats(username)


@app.get("/leetcode_stats/{username}")
def leetcode_stats(username: str):
    return get_leetcode_stats(username)


@app.get("/geeksforgeeks_stats/{username}")
def geeksforgeeks_stats(username: str):
    stats = get_gfg_stats(username)
    if "error" in stats:
        return {"status": "error", "data": stats["error"]}
    return {"status": "success", "data": stats}


@app.get("/repo_summary/")
def repo_summary(repo_url: str = Query(..., description="GitHub repository URL")):
    """
    Returns summary, tree, and README (as JSON if possible) for a GitHub repo.
    If estimated tokens <= 4k, also embed all code blocks in the README.
    """
    summary, tree, content = gitingest.ingest(repo_url)
    readme_json = None

    import re
    import json

    # Find README section in content (case-insensitive)
    readme_match = re.search(
        r"File:\s*README\.md\s*={16,}\s*(.*?)={16,}|File:\s*README\.md\s*-+\s*(.*?)(?:={16,}|$)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    readme_text = None
    if readme_match:
        readme_text = readme_match.group(1) or readme_match.group(2)
        readme_text = readme_text.strip() if readme_text else None

    token_match = re.search(r"Estimated tokens:\s*([\d\.]+)k", summary)
    estimated_tokens = None
    if token_match:
        try:
            estimated_tokens = float(token_match.group(1)) * 1000
        except Exception:
            estimated_tokens = None

    # If tokens <= 4000, extract all code blocks from content and append to README
    code_blocks = []
    if estimated_tokens is not None and estimated_tokens <= 4000:
        code_blocks = re.findall(r"```(?:[^\n]*)\n(.*?)```", content, re.DOTALL)

    if readme_text:
        try:
            readme_json = json.loads(readme_text)
        except Exception:
            readme_json = None

    
    if code_blocks and readme_text:
        if readme_json is not None:
            readme_json["code_blocks"] = code_blocks
        else:
            readme_text += "\n\n---\n\n" + "\n\n".join(
                [f"```python\n{cb}\n```" for cb in code_blocks]
            )

    return {
        "summary": summary,
        "tree": tree,
        "readme": readme_json if readme_json is not None else readme_text,
    }
