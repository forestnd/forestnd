import os
import time
import requests
import base64
from datetime import datetime


TOKEN = os.environ.get("GH_TOKEN")
API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
}

def get_user_info():
    response = requests.get(f"{API}/user", headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_all_repositories():
    repositories = []
    page = 1

    while True:
        response = requests.get(
            f"{API}/user/repos",
            headers=HEADERS,
            params={
                "visibility": "all",
                "affiliation": "owner,collaborator,organization_member",
                "per_page": 100,
                "page": page,
            },
        )
        response.raise_for_status()

        batch = response.json()
        if not batch:
            break

        repositories.extend(batch)
        page += 1

    return repositories


def get_commit_activity(owner, repo):
    url = f"{API}/repos/{owner}/{repo}/stats/commit_activity"

    while True:
        response = requests.get(url, headers=HEADERS)

        # GitHub may still be calculating repository statistics.
        if response.status_code == 202:
            time.sleep(2)
            continue

        response.raise_for_status()

        if response.status_code == 204:
            return []

        return response.json()

def img_convert(fiale_path):
    try:
        with open(fiale_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Error: {fiale_path} not found!")
        return ""

repositories = get_all_repositories()
user_info = get_user_info()
account_stats = {
    "public_repos": 0,
    "private_repos": 0,
    "commits": 0
}
print("Fetching account stats...")
for repository in repositories:
    owner = repository["owner"]["login"]
    name = repository["name"]
    activity = get_commit_activity(owner, name)
    yearly_commit_count = sum(week["total"] for week in activity)
    if name == owner:
        print(f"Skipping repository: {owner}/{name} Commits: {yearly_commit_count} (same as owner)")
        continue
    if repository["fork"]:
        print(f"Skipping repository: {owner}/{name} Commits: {yearly_commit_count} (forked)")
        continue
    if repository["visibility"] == "private":
        print(f"Skipping repository: {owner}/{name} Commits: {yearly_commit_count} (private)")
        account_stats["private_repos"] += 1
    else:
        account_stats["public_repos"] += 1
        print(f"Repository: {owner}/{name}, Yearly Commits: {yearly_commit_count} (public)")    
    account_stats["commits"] += yearly_commit_count

print("Writing final SVG...")
with open("badge-template.svg", "r", encoding="utf-8") as template_file:
    svg_content = template_file.read()

if os.path.exists("logo.jpeg"):
    final_svg = svg_content.replace("{{BASE64_LOGO}}", img_convert("logo.jpeg"))
else:
    with open("/tmp/avatar.jpeg", "wb") as out_file:
        for chunk in requests.get(user_info["avatar_url"], stream=True).iter_content(chunk_size=1024):
            if chunk:
                out_file.write(chunk)
    final_svg = svg_content.replace("{{BASE64_LOGO}}", img_convert("/tmp/avatar.jpeg"))
final_svg = final_svg.replace("{{BASE64_FOOTER}}", img_convert("badge-footer.png"))
final_svg = final_svg.replace("{{VAL_REPOS}}", str(account_stats["public_repos"] + account_stats["private_repos"]))
final_svg = final_svg.replace("{{VAL_REPOS_PUBLIC}}", str(account_stats["public_repos"]))
final_svg = final_svg.replace("{{VAL_REPOS_PRIVATE}}", str(account_stats["private_repos"]))
final_svg = final_svg.replace("{{VAL_COMMITS}}", str(account_stats["commits"]))
final_svg = final_svg.replace("{{VAL_USERNAME}}", user_info["login"])
final_svg = final_svg.replace("{{VAL_USER_JOINED}}", datetime.strptime(user_info["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d %b %Y"))

# Save final badge.svg
with open("badge.svg", "w", encoding="utf-8") as output_file:
    output_file.write(final_svg)

print("Successfully generated badge.svg!")
print("-" * 10)
print("Total Repositories:", account_stats["public_repos"] + account_stats["private_repos"])
print("Public Repositories:", account_stats["public_repos"])
print("Private Repositories:", account_stats["private_repos"])
print("Total Commits:", account_stats["commits"])