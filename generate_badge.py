import base64
import json
import os
import urllib.request

USERNAME = os.environ.get("GH_USERNAME")

def fetch_github_stats(username):
    """Fetches public repo count and star counts using GitHub's authenticated API."""
    repos_count = 0
    stars_count = 0
    total_contributions = 272  # Fallback baseline

    # Grab the GitHub token passed from the Action environment
    token = os.environ.get("GH_TOKEN")
    
    headers = {
        "User-Agent": "Python-Badge-Generator",
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        # Fetch repositories using the authenticated headers
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
        req = urllib.request.Request(repos_url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            repos = json.loads(response.read().decode())
            repos_count = len(repos)
            stars_count = sum(repo.get("stargazers_count", 0) for repo in repos)

    except Exception as e:
        print(f"Warning: Could not fetch authenticated GitHub API stats ({e}). Using defaults.")
        repos_count = 42
        stars_count = 384

    return {
        "REPOS": str(repos_count),
        "STARS": str(stars_count),
        "COMMITS": f"{total_contributions:,}"
    }

def img_convert(fiale_path):
    try:
        with open(fiale_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Error: {fiale_path} not found!")
        return ""
    


def main():
    print("Fetching live GitHub stats via Action environment...")
    stats = fetch_github_stats(USERNAME)
    print(f"Stats fetched -> Repos: {stats['REPOS']}, Stars: {stats['STARS']}, Contributions: {stats['COMMITS']}")

    # Read SVG template
    with open("badge-template.svg", "r", encoding="utf-8") as template_file:
        svg_content = template_file.read()

    # Inject values
    final_svg = svg_content.replace("{{BASE64_LOGO}}", img_convert("logo.jpeg"))
    final_svg = final_svg.replace("{{BASE64_FOOTER}}", img_convert("badge-footer.png"))
    final_svg = final_svg.replace("{{VAL_REPOS}}", stats["REPOS"])
    final_svg = final_svg.replace("{{VAL_STARS}}", stats["STARS"])
    final_svg = final_svg.replace("{{VAL_COMMITS}}", stats["COMMITS"])
    final_svg = final_svg.replace("{{VAL_USERNAME}}", USERNAME)

    # Save final badge.svg
    with open("badge.svg", "w", encoding="utf-8") as output_file:
        output_file.write(final_svg)

    print("Successfully generated badge.svg!")

if __name__ == "__main__":
    main()
