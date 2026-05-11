"""CLI interface for GitSpy."""

import json

import click
from rich.console import Console

from ghspy import __version__
from ghspy.github_api import GitHubClient
from ghspy.analyzer import UserAnalyzer
from ghspy import display

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="ghspy")
@click.option("--token", envvar="GITHUB_TOKEN", help="GitHub personal access token")
@click.pass_context
def cli(ctx, token):
    """GitSpy - GitHub OSINT tool for user reconnaissance."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = GitHubClient(token)


@cli.command()
@click.argument("username")
@click.option("--json-output", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def scan(ctx, username, as_json):
    """Full OSINT scan of a GitHub user."""
    analyzer = UserAnalyzer(ctx.obj["client"], username)

    if as_json:
        report = analyzer.full_scan()
        click.echo(json.dumps(report, indent=2, default=str))
        return

    display.print_header(username)
    with console.status(f"[cyan]Scanning @{username}...[/]"):
        report = analyzer.full_scan()
    display.print_full_scan(report)


@cli.command()
@click.argument("username")
@click.pass_context
def emails(ctx, username):
    """Extract email addresses from commit history."""
    analyzer = UserAnalyzer(ctx.obj["client"], username)
    display.print_header(username)
    with console.status("[cyan]Extracting emails from commits...[/]"):
        found = analyzer.extract_emails()
    display.print_emails(found)


@cli.command()
@click.argument("username")
@click.pass_context
def timezone(ctx, username):
    """Estimate timezone from commit timestamps."""
    analyzer = UserAnalyzer(ctx.obj["client"], username)
    display.print_header(username)
    with console.status("[cyan]Analyzing commit timestamps...[/]"):
        data = analyzer.estimate_timezone()
    display.print_timezone(data)


@cli.command()
@click.argument("username")
@click.pass_context
def activity(ctx, username):
    """Show activity patterns and heatmap."""
    analyzer = UserAnalyzer(ctx.obj["client"], username)
    display.print_header(username)
    with console.status("[cyan]Analyzing activity...[/]"):
        data = analyzer.activity_patterns()
    display.print_activity(data)


@cli.command()
@click.argument("username")
@click.pass_context
def collabs(ctx, username):
    """List frequent collaborators and organizations."""
    analyzer = UserAnalyzer(ctx.obj["client"], username)
    display.print_header(username)
    with console.status("[cyan]Finding collaborators...[/]"):
        data = analyzer.find_collaborators()
    display.print_collaborators(data)


@cli.command()
@click.argument("username")
@click.pass_context
def techstack(ctx, username):
    """Show technology stack from repositories."""
    analyzer = UserAnalyzer(ctx.obj["client"], username)
    display.print_header(username)
    data = analyzer.tech_stack()
    display.print_tech_stack(data)


@cli.command()
@click.argument("username")
@click.option("--format", "fmt", type=click.Choice(["json", "csv"]), default="json")
@click.option("--output", "-o", help="Output file path")
@click.pass_context
def export(ctx, username, fmt, output):
    """Export all findings to JSON or CSV."""
    analyzer = UserAnalyzer(ctx.obj["client"], username)

    with console.status(f"[cyan]Running full scan on @{username}...[/]"):
        report = analyzer.full_scan()

    if fmt == "json":
        content = json.dumps(report, indent=2, default=str)
        if output:
            with open(output, "w") as f:
                f.write(content)
            console.print(f"[green]Exported to {output}[/]")
        else:
            click.echo(content)

    elif fmt == "csv":
        import csv
        import io

        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["Category", "Key", "Value"])

        profile = report["profile"]
        for k, v in profile.items():
            writer.writerow(["profile", k, v])

        for email in report["emails"]:
            writer.writerow(["email", "address", email])

        tz = report["timezone"]
        for k, v in tz.items():
            if k != "hour_distribution":
                writer.writerow(["timezone", k, v])

        for lang, count in report["tech_stack"]["languages"].items():
            writer.writerow(["language", lang, count])

        content = out.getvalue()
        if output:
            with open(output, "w") as f:
                f.write(content)
            console.print(f"[green]Exported to {output}[/]")
        else:
            click.echo(content)


@cli.command(name="rate-limit")
@click.pass_context
def rate_limit(ctx):
    """Check GitHub API rate limit status."""
    client = ctx.obj["client"]
    data = client.get_rate_limit()
    core = data["resources"]["core"]

    console.print(f"\n[bold]GitHub API Rate Limit[/]")
    remaining = core["remaining"]
    limit = core["limit"]
    color = "green" if remaining > 100 else "red"
    console.print(f"  Remaining: [{color}]{remaining}[/] / {limit}")

    from datetime import datetime, timezone
    reset_time = datetime.fromtimestamp(core["reset"], tz=timezone.utc)
    console.print(f"  Resets at: {reset_time.strftime('%H:%M:%S UTC')}")
    if not client.token:
        console.print("  [yellow]Tip: Set GITHUB_TOKEN for 5000 req/hr instead of 60[/]")
    console.print()
