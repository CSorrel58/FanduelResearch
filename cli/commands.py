#!/usr/bin/env python3

"""
    Use this to execute commands to run either process. Recommended you use pipenv shell before executing.
    Example commands:
        NFL:
            cli/commands.py fanduel-nfl
        NBA
            cli/commands.py fanduel-nba
"""
import click
import os
import logging
import logging.config

from NFL.NFLFanduel import run_nfl
from NBA.NBAFanduel import run_nba

# Adding logger.
path = os.path.dirname(os.path.realpath(__file__))
logging.config.fileConfig(f"cli/logging.ini", disable_existing_loggers=False)

@click.group()
@click.option(
    "--log-level",
    "-l",
    default="info",
    help="Indicate the level of logging requested. Default is WARNING",
    type=click.Choice(["debug", "info", "warning", "error", "critical"]),
)
def scraper(log_level):
    logs = logging.getLevelName(log_level.upper())
    logging.getLogger().setLevel(logs)

@scraper.command("fanduel-nfl")
@click.option('--week',default=19)

def fanduel_nfl(week):
    """Go to Rotoguru for NFL from opening week through week number listed and scrape player data to a google sheet"""
    week = week
    run_nfl(week)

@scraper.command("fanduel-nba")
@click.option('--day',default=31)
@click.option('--month',default=12)
@click.option('--year',default=2021)

def fanduel_nba(day,month,year):
    """Go to RotoGuru for NBA from opening day through day listed and scrape player data to a given sheet"""
    day=day
    month=month
    year=year
    run_nba(day,month,year)

if __name__ == '__main__':
    scraper()