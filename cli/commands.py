#!/usr/bin/env python3

""" Use this to execute commands to run either process. Recomemnded you use pipenv shell before executing."""
import click
import os
from NFL.NFLFanduel import run_nfl

@click.command()
@click.option('--week',default=17)
def fanduel_nfl(week):
    """Authenticate with fanduel and save cookies to the given store"""
    run_nfl()

if __name__ == '__main__':
    fanduel_nfl()