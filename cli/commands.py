#!/usr/bin/env python3

""" Use this to execute commands to run either process. Recomemnded you use pipenv shell before executing."""
import click
import os
import logging
import logging.config

from NFL.NFLFanduel import run_nfl

# Adding logger.
path = os.path.dirname(os.path.realpath(__file__))
logging.config.fileConfig(f"cli/logging.ini", disable_existing_loggers=False)

@click.command()
@click.option('--week',default=17)
@click.option(
    "--log-level",
    "-l",
    default="info",
    help="Indicate the level of logging requested. Default is WARNING",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
)
def fanduel_nfl(week, log_level):
    """Authenticate with fanduel and save cookies to the given store"""
    logs = logging.getLevelName(log_level.upper())
    logging.getLogger().setLevel(logs)
    run_nfl()

if __name__ == '__main__':
    fanduel_nfl()