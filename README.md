# GitSpy

GitHub OSINT tool — extract intelligence from any GitHub user profile. Discover emails, estimate timezones, map tech stacks, find collaborators, and analyze activity patterns, all from your terminal.

## Install

```bash
pip install gitspy
```

## Quick Start

```bash
# Full OSINT scan of any GitHub user
gitspy scan torvalds

# Extract emails from commit history
gitspy emails dhh

# Estimate someone's timezone
gitspy timezone antirez

# See what languages and tools they use
gitspy techstack shazeus
```

## Commands

| Command | Description |
|---------|-------------|
| `gitspy scan <user>` | Full OSINT scan — profile, emails, timezone, activity, tech stack, collaborators |
| `gitspy emails <user>` | Extract email addresses from commit history |
| `gitspy timezone <user>` | Estimate timezone from commit hour patterns |
| `gitspy activity <user>` | Show activity patterns — peak hours, days, streaks, event types |
| `gitspy techstack <user>` | Map languages, topics, and repo stats |
| `gitspy collabs <user>` | Find frequent collaborators and organizations |
| `gitspy export <user>` | Export all findings to JSON or CSV |
| `gitspy rate-limit` | Check GitHub API rate limit status |

## What It Finds

### Email Discovery
Scans commit history across repos to find email addresses. Filters out GitHub noreply addresses and highlights real ones.

### Timezone Estimation
Analyzes commit timestamps to estimate the user's timezone. Shows confidence level (high/medium/low) based on sample size and a full hour-by-hour distribution chart.

### Activity Patterns
- Activity by day of week (bar chart)
- Event type breakdown (Push, PR, Issue, etc.)
- Current activity streak
- First and last activity dates

### Tech Stack
- Languages ranked by repo count
- Repository topics
- Original vs forked repo ratio

### Collaborator Discovery
- Frequent collaborators from PR and issue interactions
- Organization memberships
- Following list

### Identity Mapping
Cross-references commit emails and author names to map out identities and detect alt accounts or name changes.

## Options

```bash
# Export as JSON
gitspy scan user --json-output

# Export to file
gitspy export user --format json --output report.json
gitspy export user --format csv --output report.csv

# Use a GitHub token for higher rate limits
gitspy --token ghp_xxxx scan user

# Or set as environment variable
export GITHUB_TOKEN=ghp_xxxx
```

## GitHub API Rate Limits

Without a token: **60 requests/hour**. With a token: **5,000 requests/hour**.

A full scan uses ~20-50 requests depending on the user's repo count. Set `GITHUB_TOKEN` for best results.

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Generate one at [github.com/settings/tokens](https://github.com/settings/tokens) — no special scopes needed for public data.

## Examples

```bash
# Quick email lookup
gitspy emails octocat

# Check when someone is usually online
gitspy timezone gvanrossum

# See what a user is working with
gitspy techstack shazeus

# Full scan with JSON export
gitspy scan torvalds --json-output | jq '.emails'

# Export everything to a file
gitspy export antirez --format json -o antirez-report.json
```

## Disclaimer

This tool only accesses **publicly available data** through the GitHub API. It does not bypass any access controls or scrape private information. Use responsibly and in accordance with GitHub's Terms of Service.

## Requirements

- Python 3.8+
- Works on Linux, macOS, and Windows

## License

MIT
