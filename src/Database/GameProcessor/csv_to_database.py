import csv
import os
import mysql.connector
from dotenv import load_dotenv
import pandas as pd
import sys
from mysql.connector import Error
import logging


# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('HOST')
DB_NAME = os.getenv('NAME')
DB_PORT = os.getenv('PORT')
DB_USER = os.getenv('USERNAME')
DB_PASS = os.getenv('PASSWORD')

def connect_to_db():
    """Connect to the MySQL database server"""
    conn = None
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def read_csv(file_path):
    """Read data from CSV file"""
    data = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            data.append(row)
    return data

def play_to_db(conn, data):
    try:
        cur = conn.cursor()
        for row in data:
            primary_playid = find_playid(cur, row[7], row[8], row[9])
            secondary_playid = find_playid(cur, row[11], row[12], row[13])
            home = row[1]
            away = row[2]
            shottype = row[5]
            outcome = row[4]
            offensive_possession = row[3]
            primary_player = row[6]
            secondary_player = row[10]
            playnumber = row[16]
            shotlevel = row[17]
            offensiveconference = row[14]
            defensiveconference = row[15]
            date = row[18]         
            insert_query = 'INSERT INTO plays (ShotType, Outcome, Home, Away, OffensivePossession, PlayID, PrimaryPlayer, SecondaryPlayID, SecondaryPlayer, PlayNumber, ShotLevel, DefensiveConference, OffensiveConference, Date)\
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cur.execute(insert_query, (shottype, outcome, home, away, offensive_possession, primary_playid, primary_player, secondary_playid, secondary_player, playnumber, shotlevel, defensiveconference, offensiveconference, date))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    
def game_to_db(conn, data):
    """
    Inserts data from a pandas DataFrame into the 'TeamGames' table in the database.
    
    Parameters:
    - conn: A MySQL database connection object.
    - data: A pandas DataFrame where each row represents a game data entry.
    """
    try:
        columns = data.columns.tolist()

        # Rename columns if necessary to match database schema
        if 'Differential' in columns and 'Diff' not in columns:
            data.rename(columns={'Differential': 'Diff'}, inplace=True)
            columns = data.columns.tolist()
            logging.info("Renamed 'Differential' column to 'Diff'.")

        # Fill NaN values with default (0)
        data_filled = data.fillna(0)
        logging.info("Filled NaN values with 0.")

        # Convert DataFrame to list of tuples for insertion
        processed_values = [tuple(row) for row in data_filled.values]

        if not processed_values:
            logging.info("No data to insert.")
            return

        # Prepare SQL statement
        columns_str = ', '.join([f'`{col}`' for col in columns])
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f'INSERT INTO TeamGames ({columns_str}) VALUES ({placeholders})'

        # Execute insertion
        with conn.cursor() as cursor:
            cursor.executemany(insert_query, processed_values)
            conn.commit()
            logging.info(f"Successfully inserted {cursor.rowcount} record(s) into the 'TeamGames' table.")
    except Error as err:
        logging.error(f"MySQL Error: {err}")
        conn.rollback()
    except Exception as e:
        logging.error(f'Unexpected Error: {e}')
    
def find_playid(cur, playtype, playdirection, playaction):
    try:
        select_query = "SELECT PlayID FROM PlayDescriptions\
                        WHERE PlayType = %s AND Direction = %s AND Play_Action = %s"
        cur.execute(select_query, (playtype, playdirection, playaction))
        result = cur.fetchone()
        cur.fetchall()
        return result[0] if result else None
    except mysql.connector.Error as e:
        print(f"Error: {e}")

 
def transfer_plays_to_db(file_path):
    conn = connect_to_db()
    if conn:
        try:
            data = read_csv(file_path)
            play_to_db(conn, data)
            conn.commit()  # Commit after all files are processed
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to the database")


def transfer_games_to_db(data_dict):
    conn = connect_to_db()
    if not conn:
        logging.error("Failed to connect to the database.")
        return
    
    try:
        # Determine the structure of the dictionary and convert to DataFrame
        if isinstance(data_dict, dict):
            # Assuming it's a single dictionary representing one game
            data = pd.DataFrame([data_dict])
            logging.info("Converted single dictionary to DataFrame.")
        elif isinstance(data_dict, list) and all(isinstance(item, dict) for item in data_dict):
            # If data_dict is a list of dictionaries
            data = pd.DataFrame(data_dict)
            logging.info("Converted list of dictionaries to DataFrame.")
        else:
            logging.error("Unsupported data_dict format. It should be a single dictionary or a list of dictionaries.")
            return

        game_to_db(conn, data)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()