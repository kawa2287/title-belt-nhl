import click

from title_belt_nhl.schedule import Schedule

team_option = click.option(
    "--team", default="VAN", required=True, help="Team abbrev. (ex: CHI)."
)
season_option = click.option(
    "--season", default=None, required=False, help="Example: 20242025."
)


@click.group()
@team_option
@season_option
@click.pass_context
def cli(ctx, team, season):
    click.echo(f"Calculating shortest path for {team} to challenge for the belt...")

    schedule = Schedule(team, season)
    ctx.ensure_object(dict)
    ctx.obj["schedule"] = schedule


@cli.command()
@click.pass_context
def path(ctx):
    schedule: Schedule = ctx.obj["schedule"]
    team = schedule.team
    holder = schedule.belt_holder

    click.echo("=============================================================")
    click.echo(f"CURRENT SEASON: {schedule.get_season_pretty()}")
    click.echo(f"CURRENT BELT HOLDER: {holder}")

    if team == holder:
        click.echo(f"{team} ALREADY HAS THE BELT!")
    else:
        path_matches = schedule.find_nearest_path_games()
        click.echo(f"{len(path_matches)} GAMES UNTIL `{team}` HAS A SHOT AT THE BELT")
        for match in path_matches:
            click.echo(f"\t{match.date_obj} | {match.belt_holder} -> {match}")


@cli.command()
@click.pass_context
def path_alt(ctx):
    schedule: Schedule = ctx.obj["schedule"]
    team = schedule.team
    holder = schedule.belt_holder

    click.echo("=============================================================")
    click.echo(f"CURRENT SEASON: {schedule.get_season_pretty()}")
    click.echo(f"CURRENT BELT HOLDER: {holder}")

    if team == holder:
        click.echo(f"{team} ALREADY HAS THE BELT!")
    else:
        path = schedule.find_nearest_path_str([holder], holder)
        games = path.split("vs")
        click.echo(f"{len(games)-1} GAMES UNTIL `{team}` HAS A SHOT AT THE BELT")
        click.echo(path)
