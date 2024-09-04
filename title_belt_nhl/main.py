import click

from .schedule import Schedule


@click.command()
@click.option("--team", default="VAN", required=True)
@click.option("--holder", "--belt-holder", default="PIT", required=True)
def cli(team, holder):
    click.echo(f"Calculating shortest path for {team} to challenge for the belt...")
    click.echo(f"The current belt holder is {holder}.")

    schedule = Schedule(team, holder)

    path = schedule.find_nearest_path([holder], holder)
    games = path.split("vs")

    click.echo("=============================================================")
    click.echo(f"CURRENT BELT HOLDER: {holder}")
    click.echo(f"{len(games)-1} GAMES UNTIL `{team}` HAS A SHOT AT THE BELT")
    click.echo(path)
