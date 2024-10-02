import click

from title_belt_nhl.schedule import Schedule


@click.command()
@click.option("--team", default="VAN", required=True, help="Team abbrev. (ex: CHI).")
@click.option("--season", default=None, required=False, help="Example: 20242025.")
def cli(team, season):
    click.echo(f"Calculating shortest path for {team} to challenge for the belt...")

    schedule = Schedule(team, season)
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
