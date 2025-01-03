import os
import shutil
import sqlite3

import pandas as pd
import requests

DB_URL = "https://storage.googleapis.com/benchmarks-artifacts/travel-db/travel2.sqlite"
LOCAL_FILE = "travel2.sqlite"
# The backup lets us restart for each tutorial section
BACKUP_FILE = "travel2.backup.sqlite"


def download_db(overwrite=False):
    if overwrite or not os.path.exists(LOCAL_FILE):
        response = requests.get(DB_URL)
        response.raise_for_status()  # Ensure the request was successful
        with open(LOCAL_FILE, "wb") as f:
            f.write(response.content)
        # Backup - we will use this to "reset" our DB in each section
        shutil.copy(LOCAL_FILE, BACKUP_FILE)


def update_dates(file):
    """
    Convert the flights to present time for our tutorial
    """
    shutil.copy(BACKUP_FILE, file)
    conn = sqlite3.connect(file)

    # Get list of all tables in the SQLite database
    table_names = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    ).name.tolist()
    tables = {
        t: pd.read_sql(f"SELECT * from {t}", conn)
        for t in table_names
    }

    # Find the most recent flight departure time in the database
    example_time = pd.to_datetime(
        tables["flights"]["actual_departure"].replace("\\N", pd.NaT)
    ).max()
    current_time = pd.to_datetime("now").tz_localize(example_time.tz)

    # Compute diff, so will add this offset to all times
    offset = current_time - example_time

    # Add ofset to book_date
    tables["bookings"]["book_date"] = (
        pd.to_datetime(tables["bookings"]["book_date"].replace("\\N", pd.NaT), utc=True) + offset
    )

    # Add offset to times in the `flights` table
    datetime_columns = [
        "scheduled_departure",
        "scheduled_arrival",
        "actual_departure",
        "actual_arrival",
    ]
    for column in datetime_columns:
        tables["flights"][column] = (
            pd.to_datetime(tables["flights"][column].replace("\\N", pd.NaT)) + offset
        )

    # write back to the DB
    for table_name, df in tables.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()

    return file
