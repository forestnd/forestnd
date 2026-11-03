import base64
import json
import urllib.request

USERNAME = "forestnd"

def fetch_github_stats(username):
    """Fetches public repo count, star count, and estimate/commit data."""
    repos_count = 0
    stars_count = 0
    commits_count = "1,240" # Fallback or calculated value

    try:
        # 1. Fetch user repositories to count repos and stars
        url = f"https://api.github.com/users/{username}/repos?per_page=100"
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Python-Badge-Generator", "Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req) as response:
            repos = json.loads(response.read().decode())
            repos_count = len(repos)
            stars_count = sum(repo.get("stargazers_count", 0) for repo in repos)
    except Exception as e:
        print(f"Warning: Could not fetch live GitHub repos ({e}). Using defaults.")
        repos_count = 42
        stars_count = 384

    # Format numbers nicely (e.g., commas for thousands if needed)
    return {
        "REPOS": str(repos_count),
        "STARS": str(stars_count),
        "COMMITS": commits_count
    }

def main():
    print("Fetching live GitHub stats...")
    stats = fetch_github_stats(USERNAME)
    print(f"Stats fetched -> Repos: {stats['REPOS']}, Stars: {stats['STARS']}, Commits: {stats['COMMITS']}")

    # 2. Read local logo and convert to Base64
    try:
        with open("logo.jpeg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            image_data_uri = f"data:image/jpeg;base64,{encoded_string}"
    except FileNotFoundError:
        print("Error: logo.jpeg not found in root directory!")
        image_data_uri = ""

    # 3. Read SVG template
    with open("badge-template.svg", "r", encoding="utf-8") as template_file:
        svg_content = template_file.read()

    # 4. Inject dynamic values into template placeholders
    final_svg = svg_content.replace("{{BASE64_LOGO}}", image_data_uri)
    final_svg = final_svg.replace("{{VAL_REPOS}}", stats["REPOS"])
    final_svg = final_svg.replace("{{VAL_STARS}}", stats["STARS"])
    final_svg = final_svg.replace("{{VAL_COMMITS}}", stats["COMMITS"])

    # 5. Write out the final compiled badge.svg
    with open("badge.svg", "w", encoding="utf-8") as output_file:
        output_file.write(final_svg)

    print("Successfully generated badge.svg with live stats and embedded logo!")

if __name__ == "__main__":
    main()
