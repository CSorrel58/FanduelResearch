import pandas as pd
from base import (
        google_drive_upload,
        clean_column,
        nba_url_creator,
        nba_url_scraper,
    )

def run_nba(day,month,year):
        day =day
        month=month
        year=year

        urls = []
        nba_url_creator(day,month,year,urls)

        rows = []
        nba_url_scraper(urls,rows)

        sample_frame = pd.DataFrame.from_records(rows).reset_index()