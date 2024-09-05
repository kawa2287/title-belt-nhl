import click

from title_belt_nhl.schedule import Schedule


@click.command()
@click.option("--team", default="VAN", required=True)
@click.option("--season", default=None, required=False)
def cli(team, season):
    click.echo(f"Calculating shortest path for {team} to challenge for the belt...")

    schedule = Schedule(team, season)
    holder = schedule.belt_holder

    path = schedule.find_nearest_path([holder], holder)
    games = path.split("vs")

    click.echo("=============================================================")
    click.echo(f"CURRENT SEASON: {schedule.season}")
    click.echo(f"CURRENT BELT HOLDER: {holder}")
    click.echo(f"{len(games)-1} GAMES UNTIL `{team}` HAS A SHOT AT THE BELT")
    click.echo(path)
