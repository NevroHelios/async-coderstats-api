from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


# @app.get("/codeforces_stats/{username}")
# def codeforces_stats(username: str):
#     stats = get_codeforces_user_data(username)
#     if "error" in stats:
#         return {"status": "error", "message": stats["error"]}
#     return {"status": "success", "data": stats}
