import rich_click as click

from title_belt_nhl.schedule import Schedule

team_option = click.option(
    "--team", default="VAN", required=True, help="Team abbrev. (ex: CHI)."
)
season_option = click.option(
    "--season",
    default=None,
    required=False,
    help="Defaults to current season if not specified. Example: 20242025.",
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
        for depth, match_list in enumerate(path_matches):
            click.echo(f"{depth}: {len(match_list)}")
            for match in match_list:
                on_path = "*" if match.on_shortest_path else ""
                click.echo(
                    f"\t{match.date_obj} | {match.belt_holder} -> {match} {on_path}"
                )


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
        path_matches = schedule.find_nearest_path_v2()
        if path_matches is None:
            click.echo(f"NO PATH FOUND FOR `{team}`")
        else:
            click.echo(f"{len(path_matches)} GAMES UNTIL `{team}` HAS A SHOT AT THE BELT")
            for match in path_matches:
                click.echo(f"\t{match.date_obj} | {match.belt_holder} -> {match}")
