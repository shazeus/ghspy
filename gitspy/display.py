"""Rich terminal display for GitSpy."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()


def print_header(username):
    console.print()
    console.print(
        Panel(
            f"[bold cyan]GitSpy[/] — scanning [bold yellow]@{username}[/]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()


def print_profile(data):
    table = Table(title="Profile", box=box.ROUNDED, border_style="blue")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Username", data["login"])
    table.add_row("Name", data["name"])
    table.add_row("Bio", data["bio"])
    table.add_row("Company", data["company"])
    table.add_row("Location", data["location"])
    table.add_row("Email", data["email"])
    table.add_row("Blog", data["blog"])
    table.add_row("Twitter", f"@{data['twitter']}" if data["twitter"] != "N/A" else "N/A")
    table.add_row("Repos", str(data["public_repos"]))
    table.add_row("Gists", str(data["public_gists"]))
    table.add_row("Followers", str(data["followers"]))
    table.add_row("Following", str(data["following"]))
    table.add_row("Created", data["created_at"][:10])
    table.add_row("Hireable", str(data["hireable"]) if data["hireable"] is not None else "N/A")
    table.add_row("Profile", data["profile"])

    console.print(table)
    console.print()


def print_emails(emails):
    if not emails:
        console.print("[dim]No emails found in commit history.[/]")
        console.print()
        return

    table = Table(title="Discovered Emails", box=box.ROUNDED, border_style="green")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Email", style="bold green")

    for i, email in enumerate(emails, 1):
        table.add_row(str(i), email)

    console.print(table)
    console.print()


def print_timezone(data):
    if data.get("confidence") == "none":
        console.print("[dim]Not enough commit data to estimate timezone.[/]")
        console.print()
        return

    confidence = data["confidence"]
    if confidence == "high":
        color = "green"
    elif confidence == "medium":
        color = "yellow"
    else:
        color = "red"

    console.print(
        Panel(
            f"[bold]{data['estimated_timezone']}[/]\n"
            f"Confidence: [{color}]{confidence}[/] ({data['total_commits_analyzed']} commits analyzed)\n"
            f"Peak hours (UTC): {', '.join(f'{h:02d}:00' for h in data['peak_hours_utc'])}",
            title="[bold]Timezone Estimate[/]",
            border_style="magenta",
            padding=(1, 2),
        )
    )
    console.print()

    if data.get("hour_distribution"):
        table = Table(title="Commit Hour Distribution (UTC)", box=box.SIMPLE)
        table.add_column("Hour", justify="right")
        table.add_column("Commits", justify="right")
        table.add_column("Graph")

        max_val = max(data["hour_distribution"].values()) if data["hour_distribution"] else 1
        for hour in range(24):
            count = data["hour_distribution"].get(hour, 0)
            if count > 0:
                bar_len = int(count / max_val * 25)
                bar = "█" * bar_len
                table.add_row(f"{hour:02d}:00", str(count), f"[cyan]{bar}[/]")

        console.print(table)
        console.print()


def print_activity(data):
    console.print(f"[bold]Activity Patterns[/] — {data['total_events']} events analyzed")
    if data.get("last_activity"):
        console.print(f"  Last activity: [green]{data['last_activity']}[/]")
    if data.get("streak"):
        console.print(f"  Current streak: [yellow]{data['streak']} day(s)[/]")
    console.print()

    if data["by_day"]:
        day_table = Table(title="Activity by Day", box=box.SIMPLE)
        day_table.add_column("Day", style="bold")
        day_table.add_column("Count", justify="right")
        day_table.add_column("Graph")

        max_day = max(data["by_day"].values()) if any(data["by_day"].values()) else 1
        for day, count in data["by_day"].items():
            bar_len = int(count / max_day * 20) if max_day > 0 else 0
            bar = "█" * bar_len
            day_table.add_row(day[:3], str(count), f"[cyan]{bar}[/]")

        console.print(day_table)
        console.print()

    if data["event_types"]:
        type_table = Table(title="Event Types", box=box.SIMPLE)
        type_table.add_column("Type", style="bold")
        type_table.add_column("Count", justify="right")

        for etype, count in data["event_types"].items():
            name = etype.replace("Event", "")
            type_table.add_row(name, str(count))

        console.print(type_table)
        console.print()


def print_tech_stack(data):
    console.print(
        f"[bold]Tech Stack[/] — {data['original_repos']} original repos, "
        f"{data['forked_repos']} forks"
    )
    console.print()

    if data["languages"]:
        table = Table(title="Languages", box=box.ROUNDED, border_style="magenta")
        table.add_column("Language", style="bold")
        table.add_column("Repos", justify="right")
        table.add_column("Graph")

        max_val = max(data["languages"].values()) if data["languages"] else 1
        colors = ["cyan", "green", "yellow", "red", "blue", "magenta"]
        for i, (lang, count) in enumerate(data["languages"].items()):
            color = colors[i % len(colors)]
            bar_len = int(count / max_val * 20)
            bar = "█" * bar_len
            table.add_row(lang, str(count), f"[{color}]{bar}[/]")

        console.print(table)
        console.print()

    if data["topics"]:
        topics_str = ", ".join(f"[dim]{t}[/]" for t in data["topics"])
        console.print(f"  Topics: {topics_str}")
        console.print()


def print_collaborators(data):
    if data["organizations"]:
        console.print(f"[bold]Organizations:[/] {', '.join(data['organizations'])}")
        console.print()

    if data["frequent_collaborators"]:
        table = Table(title="Frequent Collaborators", box=box.ROUNDED, border_style="yellow")
        table.add_column("User", style="bold")
        table.add_column("Interactions", justify="right")

        for user, count in data["frequent_collaborators"].items():
            table.add_row(f"@{user}", str(count))

        console.print(table)
        console.print()

    if data["following"]:
        console.print(f"[bold]Following ({data['following_count']}):[/] {', '.join(data['following'][:15])}")
        if data["following_count"] > 15:
            console.print(f"  [dim]... and {data['following_count'] - 15} more[/]")
        console.print()


def print_identities(data):
    if not data["identities"]:
        return

    table = Table(title="Commit Identities", box=box.ROUNDED, border_style="red")
    table.add_column("Email", style="bold")
    table.add_column("Names Used")
    table.add_column("Noreply?")

    for identity in data["identities"]:
        names = ", ".join(identity["names"])
        noreply = "[dim]yes[/]" if identity["is_noreply"] else "[yellow]no[/]"
        table.add_row(identity["email"], names, noreply)

    console.print(table)
    console.print(
        f"  [dim]{data['unique_emails']} unique email(s), "
        f"{data['unique_names']} unique name(s)[/]"
    )
    console.print()


def print_full_scan(report):
    print_profile(report["profile"])
    print_emails(report["emails"])
    print_timezone(report["timezone"])
    print_activity(report["activity"])
    print_tech_stack(report["tech_stack"])
    print_collaborators(report["collaborators"])
    print_identities(report["identities"])
