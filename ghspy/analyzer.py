"""OSINT analysis logic for GitSpy."""

from collections import Counter, defaultdict
from datetime import datetime, timezone
import re


class UserAnalyzer:
    def __init__(self, client, username):
        self.client = client
        self.username = username
        self._user = None
        self._repos = None
        self._events = None

    @property
    def user(self):
        if self._user is None:
            self._user = self.client.get_user(self.username)
        return self._user

    @property
    def repos(self):
        if self._repos is None:
            self._repos = self.client.get_repos(self.username)
        return self._repos

    @property
    def events(self):
        if self._events is None:
            self._events = self.client.get_events(self.username)
        return self._events

    def profile_info(self):
        u = self.user
        return {
            "login": u["login"],
            "name": u.get("name") or "N/A",
            "bio": u.get("bio") or "N/A",
            "company": u.get("company") or "N/A",
            "location": u.get("location") or "N/A",
            "email": u.get("email") or "N/A",
            "blog": u.get("blog") or "N/A",
            "twitter": u.get("twitter_username") or "N/A",
            "public_repos": u["public_repos"],
            "public_gists": u["public_gists"],
            "followers": u["followers"],
            "following": u["following"],
            "created_at": u["created_at"],
            "updated_at": u["updated_at"],
            "avatar": u["avatar_url"],
            "profile": u["html_url"],
            "hireable": u.get("hireable"),
        }

    def extract_emails(self):
        emails = set()
        profile_email = self.user.get("email")
        if profile_email:
            emails.add(profile_email)

        for repo in self.repos[:10]:
            owner = repo["owner"]["login"]
            name = repo["name"]
            if repo.get("fork"):
                continue
            try:
                commits = self.client.get_repo_commits(owner, name, author=self.username, max_pages=1)
                for c in commits[:20]:
                    commit_data = c.get("commit", {})
                    author = commit_data.get("author", {})
                    committer = commit_data.get("committer", {})
                    if author.get("email") and not self._is_noreply(author["email"]):
                        emails.add(author["email"])
                    if committer.get("email") and not self._is_noreply(committer["email"]):
                        emails.add(committer["email"])
            except Exception:
                continue

        return sorted(emails)

    def _is_noreply(self, email):
        noreply_patterns = ["noreply", "users.noreply.github.com"]
        return any(p in email.lower() for p in noreply_patterns)

    def estimate_timezone(self):
        hours = []
        for repo in self.repos[:8]:
            if repo.get("fork"):
                continue
            try:
                commits = self.client.get_repo_commits(
                    repo["owner"]["login"], repo["name"],
                    author=self.username, max_pages=1
                )
                for c in commits[:30]:
                    date_str = c.get("commit", {}).get("author", {}).get("date", "")
                    if date_str:
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        hours.append(dt.hour)
            except Exception:
                continue

        if not hours:
            return {"estimated_utc_offset": None, "confidence": "none", "peak_hours_utc": []}

        hour_counts = Counter(hours)
        peak_hours = [h for h, _ in hour_counts.most_common(5)]

        avg_peak = sum(peak_hours) / len(peak_hours)
        if 6 <= avg_peak <= 10:
            offset = 0
            tz_guess = "UTC+0 (UK/Portugal/West Africa)"
        elif 10 < avg_peak <= 14:
            offset = -(avg_peak - 9)
            tz_guess = f"UTC{int(offset):+d} (US East / Americas)"
        elif 14 < avg_peak <= 18:
            offset = -(avg_peak - 9)
            tz_guess = f"UTC{int(offset):+d} (US West / Pacific)"
        elif avg_peak > 18 or avg_peak < 3:
            offset = 24 - avg_peak + 9 if avg_peak > 18 else 9 - avg_peak
            tz_guess = f"UTC+{int(offset)} (Asia / Eastern)"
        else:
            offset = 9 - avg_peak
            tz_guess = f"UTC+{int(offset):+d} (Europe)"

        total_commits = len(hours)
        if total_commits > 50:
            confidence = "high"
        elif total_commits > 20:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "estimated_timezone": tz_guess,
            "estimated_utc_offset": round(offset),
            "confidence": confidence,
            "total_commits_analyzed": total_commits,
            "peak_hours_utc": sorted(peak_hours),
            "hour_distribution": dict(sorted(hour_counts.items())),
        }

    def activity_patterns(self):
        hours = []
        days = []
        dates = []

        for event in self.events:
            date_str = event.get("created_at", "")
            if date_str:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                hours.append(dt.hour)
                days.append(dt.strftime("%A"))
                dates.append(dt.date())

        for repo in self.repos[:5]:
            if repo.get("fork"):
                continue
            try:
                commits = self.client.get_repo_commits(
                    repo["owner"]["login"], repo["name"],
                    author=self.username, max_pages=1
                )
                for c in commits[:20]:
                    date_str = c.get("commit", {}).get("author", {}).get("date", "")
                    if date_str:
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        hours.append(dt.hour)
                        days.append(dt.strftime("%A"))
                        dates.append(dt.date())
            except Exception:
                continue

        hour_counts = Counter(hours)
        day_counts = Counter(days)

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sorted_days = {d: day_counts.get(d, 0) for d in day_order}

        streak = 0
        if dates:
            unique_days = sorted(set(dates), reverse=True)
            streak = 1
            for i in range(1, len(unique_days)):
                if (unique_days[i - 1] - unique_days[i]).days == 1:
                    streak += 1
                else:
                    break

        event_types = Counter(e.get("type", "Unknown") for e in self.events)

        return {
            "total_events": len(self.events),
            "by_hour": dict(sorted(hour_counts.items())),
            "by_day": sorted_days,
            "streak": streak,
            "event_types": dict(event_types.most_common(10)),
            "first_activity": min(dates).isoformat() if dates else None,
            "last_activity": max(dates).isoformat() if dates else None,
        }

    def tech_stack(self):
        languages = Counter()
        topics = Counter()
        all_deps = set()

        for repo in self.repos:
            if repo.get("fork"):
                continue
            lang = repo.get("language")
            if lang:
                languages[lang] += 1
            for topic in repo.get("topics", []):
                topics[topic] += 1

        return {
            "languages": dict(languages.most_common(15)),
            "topics": dict(topics.most_common(20)),
            "total_repos": len(self.repos),
            "original_repos": sum(1 for r in self.repos if not r.get("fork")),
            "forked_repos": sum(1 for r in self.repos if r.get("fork")),
        }

    def find_collaborators(self):
        collaborators = Counter()

        for event in self.events:
            payload = event.get("payload", {})
            if event["type"] == "PullRequestEvent":
                pr = payload.get("pull_request", {})
                user = pr.get("user", {}).get("login")
                if user and user != self.username:
                    collaborators[user] += 1
                merged_by = pr.get("merged_by", {})
                if merged_by:
                    merger = merged_by.get("login")
                    if merger and merger != self.username:
                        collaborators[merger] += 1

            if event["type"] == "IssueCommentEvent":
                issue = payload.get("issue", {})
                user = issue.get("user", {}).get("login")
                if user and user != self.username:
                    collaborators[user] += 1

        orgs = self.client.get_orgs(self.username)
        org_names = [o["login"] for o in orgs]

        following = self.client.get_following(self.username)
        following_names = [f["login"] for f in following[:50]]

        return {
            "frequent_collaborators": dict(collaborators.most_common(15)),
            "organizations": org_names,
            "following": following_names[:20],
            "following_count": len(following),
        }

    def detect_alt_emails(self):
        email_to_names = defaultdict(set)
        name_to_emails = defaultdict(set)

        for repo in self.repos[:10]:
            if repo.get("fork"):
                continue
            try:
                commits = self.client.get_repo_commits(
                    repo["owner"]["login"], repo["name"],
                    author=self.username, max_pages=1,
                )
                for c in commits[:20]:
                    author = c.get("commit", {}).get("author", {})
                    name = author.get("name", "")
                    email = author.get("email", "")
                    if name and email:
                        email_to_names[email].add(name)
                        name_to_emails[name].add(email)
            except Exception:
                continue

        identities = []
        for email, names in email_to_names.items():
            identities.append({
                "email": email,
                "names": sorted(names),
                "is_noreply": self._is_noreply(email),
            })

        return {
            "identities": identities,
            "unique_emails": len(email_to_names),
            "unique_names": len(name_to_emails),
        }

    def full_scan(self):
        return {
            "profile": self.profile_info(),
            "emails": self.extract_emails(),
            "timezone": self.estimate_timezone(),
            "activity": self.activity_patterns(),
            "tech_stack": self.tech_stack(),
            "collaborators": self.find_collaborators(),
            "identities": self.detect_alt_emails(),
        }
