<p align="center">
  <h1 align="center">GhSpy</h1>
  <p align="center">GitHub OSINT tool — extract intelligence from any GitHub user profile.</p>
  <p align="center">
    <a href="https://pypi.org/project/ghspy/"><img src="https://img.shields.io/pypi/v/ghspy?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/ghspy/"><img src="https://img.shields.io/pypi/pyversions/ghspy" alt="Python"></a>
    <a href="https://github.com/shazeus/ghspy/blob/main/LICENSE"><img src="https://img.shields.io/github/license/shazeus/ghspy" alt="License"></a>
    <a href="https://github.com/shazeus/ghspy/stargazers"><img src="https://img.shields.io/github/stars/shazeus/ghspy?style=social" alt="Stars"></a>
  </p>
</p>

---

Discover emails, estimate timezones, map tech stacks, find collaborators, and analyze activity patterns — all from your terminal. GhSpy uses the public GitHub API to gather open-source intelligence on any GitHub user.

- **Email Discovery** — extract real email addresses from commit history
- **Timezone Estimation** — estimate location from commit hour patterns
- **Activity Analysis** — peak hours, active days, contribution streaks
- **Tech Stack Mapping** — languages, topics, original vs forked repos
- **Collaborator Detection** — frequent interactions, orgs, following
- **Identity Mapping** — cross-reference commit emails and author names

## Installation

```bash
pip install ghspy
```

Requires Python 3.8+. Works on Linux, macOS, and Windows.

## Usage

```bash
# Full OSINT scan
ghspy scan torvalds

# Extract emails from commit history
ghspy emails dhh

# Estimate timezone
ghspy timezone antirez

# Activity patterns
ghspy activity shazeus

# Tech stack
ghspy techstack gvanrossum

# Collaborators & organizations
ghspy collabs octocat

# Export to JSON
ghspy export torvalds --format json -o report.json

# Export to CSV
ghspy export torvalds --format csv -o report.csv
```

## Commands

| Command | Description |
|---------|-------------|
| `ghspy scan <user>` | Full OSINT scan with all modules |
| `ghspy emails <user>` | Extract emails from commit history |
| `ghspy timezone <user>` | Estimate timezone from commit patterns |
| `ghspy activity <user>` | Activity breakdown by hour, day, and event type |
| `ghspy techstack <user>` | Languages, topics, and repo statistics |
| `ghspy collabs <user>` | Collaborators, organizations, and following |
| `ghspy export <user>` | Export findings to JSON or CSV |
| `ghspy rate-limit` | Check GitHub API rate limit |

## Configuration

### GitHub Token

Without a token you get **60 requests/hour**. With a token you get **5,000 requests/hour**. A full scan uses 20–50 requests depending on the user's repo count.

```bash
# Set as environment variable (recommended)
export GITHUB_TOKEN=ghp_your_token_here

# Or pass directly
ghspy --token ghp_xxxx scan torvalds
```

Generate a token at [github.com/settings/tokens](https://github.com/settings/tokens) — no special scopes needed for public data.

### JSON Output

Every command supports `--json-output` for piping to other tools:

```bash
ghspy scan user --json-output | jq '.emails'
ghspy scan user --json-output | jq '.timezone.estimated_timezone'
```

## How It Works

GhSpy queries the public GitHub REST API to collect:

1. **User profile** — public info, bio, location, social links
2. **Repositories** — languages, topics, fork status, activity dates
3. **Commit history** — author emails, timestamps, committer info
4. **Public events** — pushes, PRs, issues, comments
5. **Social graph** — followers, following, organizations

All data is publicly available through GitHub's API. No authentication bypass or scraping is involved.

## Disclaimer

This tool only accesses **publicly available data** through the official GitHub API. It does not bypass access controls, scrape private information, or violate GitHub's Terms of Service. Use responsibly.

## License

[MIT](LICENSE)
