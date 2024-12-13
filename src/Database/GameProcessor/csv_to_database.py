import csv
import os
import mysql.connector
from dotenv import load_dotenv
import sys

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

def insert_into_db(conn, data):
    try:
        cur = conn.cursor()
        for row in data:
            primary_playid = find_playid(cur, row[6], row[7], row[8])
            secondary_playid = find_playid(cur, row[10], row[11], row[12])
            home = row[0]
            away = row[1]
            shottype = row[4]
            outcome = row[3]
            offensive_possession = row[2]
            primary_player = row[5]
            secondary_player = row[9]
            playnumber = row[15]
            shotlevel = row[16]
            offensiveconference = row[13]
            defensiveconference = row[14]
            year = row[17]
            
            insert_query = 'INSERT INTO plays (ShotType, Outcome, Home, Away, OffensivePossession, PlayID, PrimaryPlayer, SecondaryPlayID, SecondaryPlayer, PlayNumber, ShotLevel, DefensiveConference, OffensiveConference, Year)\
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            cur.execute(insert_query, (shottype, outcome, home, away, offensive_possession, primary_playid, primary_player, secondary_playid, secondary_player, playnumber, shotlevel, defensiveconference, offensiveconference, year))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    
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
            insert_into_db(conn, data)
            conn.commit()  # Commit after all files are processed
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to the database")
