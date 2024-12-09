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

def map_opponents(team_name):
  # Maps The result column values to their new outcome values
    if team_name == 'Bar':
        return 'Bard College'
    elif team_name == 'CU':
        return 'Clarkson'
    elif team_name == 'HOB':
        return 'Hobart'
    elif team_name == 'IC':
        return 'Ithaca'
    elif team_name == 'NAZ':
        return 'Nazareth'
    elif team_name == 'RPI':
        return 'RPI'
    elif team_name == 'SKD':
        return 'Skidmore'
    elif team_name == 'SJC':
        return 'St. John Fisher'
    elif team_name == 'SLS':
        return 'St. Lawrence'
    elif team_name == 'UNY':
        return 'Union College'
    elif team_name == 'VC':
        return 'Vassar'
    elif team_name == 'IC':
        return 'Wells'
    elif team_name == 'ASU':
        return 'Alfred State'
    elif team_name == 'Elm':
        return 'Elmira'
    elif team_name == 'GUB':
        return 'Gallaudent'
    elif team_name == 'ROY':
        return 'Rochester'
    elif team_name == 'WEL':
        return 'Wells'
    else:
        print(f'\nTeam Name: {team_name}\n')
        return None
 
def main():
    conn = connect_to_db()
    if conn:
        try:
            if len(sys.argv) < 2:
                print("Usage: python read_csv.py <csv file path_1> <csv file path_2>...")
                sys.exit()
            
            for csv_file in sys.argv[1:]:
                # Process each csv path
                csv_file = 'cleaned_' + csv_file
                file_path = os.path.join('/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/cleaned/cleaned_game_csv/RIT_clean_csv', csv_file)
                data = read_csv(file_path)
                insert_into_db(conn, data)
            
            conn.commit()  # Commit after all files are processed
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to the database")

if __name__ == "__main__":
    main()