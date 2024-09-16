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

def modify_2player_view(conn, view_name, play_numbers, secondary_play_numbers):
    """
    Modify an existing SQL view to add columns for counting turnovers and fouls.
    
    Args:
        conn: Database connection object
        view_name (str): The name of the view to modify.
        play_numbers (list of int): A list of play numbers to include in the modified view.
    """
    play_numbers_str = ', '.join(map(str, play_numbers))
    secondary_play_numbers_str = ', '.join(map(str, secondary_play_numbers))

    view_template = f"""
    CREATE OR REPLACE VIEW {view_name} AS
    SELECT 
        Player1 AS PrimaryPlayer,
        Player2 AS SecondaryPlayer,
        Team,
        SUM(TotalPlays) AS TotalPlays,
        SUM(Total3ptShots) AS Total3ptShots,
        SUM(Total3ptMakes) AS Total3ptMakes,
        (SUM(Total3ptMakes) / NULLIF(SUM(Total3ptShots), 0)) * 100 AS "3pt%",
        SUM(Total2ptShots) AS Total2ptShots,
        SUM(Total2ptMakes) AS Total2ptMakes,
        (SUM(Total2ptMakes) / NULLIF(SUM(Total2ptShots), 0)) * 100 AS "2pt%",
        SUM(TotalMidRangeShots) AS TotalMidRangeShots,
        SUM(TotalMidRangeMakes) AS TotalMidRangeMakes,
        (SUM(TotalMidRangeMakes) / NULLIF(SUM(TotalMidRangeShots), 0)) * 100 AS "MidRange%",
        (
            (SUM(Total2ptMakes) + (1.5 * SUM(Total3ptMakes))) / 
            NULLIF((SUM(Total2ptShots) + SUM(Total3ptShots)), 0)
        ) * 100 AS "EFG%",
        SUM(TurnoverCount) AS Turnover,  -- New column to count turnovers
        SUM(FoulCount) AS Foul           -- New column to count fouls
    FROM (
        SELECT 
            PrimaryPlayer AS Player1,
            SecondaryPlayer AS Player2,
            OffensivePossession AS Team,
            COUNT(*) AS TotalPlays,
            SUM(CASE WHEN Outcome IN ('3pmi', '3pma') THEN 1 ELSE 0 END) AS Total3ptShots,
            SUM(CASE WHEN Outcome = '3pMa' THEN 1 ELSE 0 END) AS Total3ptMakes,
            SUM(CASE WHEN (ShotLevel IN (1, 2, 3) AND Outcome NOT IN ('Turnover', 'Foul')) THEN 1 ELSE 0 END) AS Total2ptShots,        
            SUM(CASE WHEN (Outcome IN ('2pMa', 'And1') AND ShotLevel IN (1, 2, 3)) THEN 1 ELSE 0 END) AS Total2ptMakes,
            SUM(CASE WHEN ShotLevel IN (2, 3) THEN 1 ELSE 0 END) AS TotalMidRangeShots,
            SUM(CASE WHEN (ShotLevel IN (2, 3) AND Outcome IN ('And1', '2pMa')) THEN 1 ELSE 0 END) AS TotalMidRangeMakes,
            SUM(CASE WHEN Outcome = 'Turnover' THEN 1 ELSE 0 END) AS TurnoverCount,  -- New calculation for turnovers
            SUM(CASE WHEN Outcome = 'Foul' THEN 1 ELSE 0 END) AS FoulCount            -- New calculation for fouls
        FROM plays
        WHERE 
            PlayID IN ({play_numbers_str})
            AND SecondaryPlayID IN ({secondary_play_numbers_str})  -- Only include plays where PlayID is in the specified set
            AND PrimaryPlayer <> 'N/A'
            AND SecondaryPlayer <> 'N/A'
        GROUP BY 
            PrimaryPlayer, SecondaryPlayer, OffensivePossession
    ) AS CombinedStats
    GROUP BY 
        PrimaryPlayer, SecondaryPlayer, Team
    ORDER BY 
        TotalPlays DESC;
    """
    
    try:
        cur = conn.cursor()
        cur.execute(view_template)
        print(f"View '{view_name}' modified successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        
        
        
def modify_view(conn, view_name, play_numbers):
    """
    Modify an existing SQL view to add columns for counting turnovers and fouls.
    
    Args:
        conn: Database connection object
        view_name (str): The name of the view to modify.
        play_numbers (list of int): A list of play numbers to include in the modified view.
    """
    play_numbers_str = ', '.join(map(str, play_numbers))

    view_template = f"""
    CREATE OR REPLACE VIEW {view_name} AS
    SELECT 
        Player,
        Team,
        SUM(TotalPlays) AS TotalPlays,
        SUM(Total3ptShots) AS Total3ptShots,
        SUM(Total3ptMakes) AS Total3ptMakes,
        (SUM(Total3ptMakes) / NULLIF(SUM(Total3ptShots), 0)) * 100 AS "3pt%",
        SUM(Total2ptShots) AS Total2ptShots,
        SUM(Total2ptMakes) AS Total2ptMakes,
        (SUM(Total2ptMakes) / NULLIF(SUM(Total2ptShots), 0)) * 100 AS "2pt%",
        SUM(TotalMidRangeShots) AS TotalMidRangeShots,
        SUM(TotalMidRangeMakes) AS TotalMidRangeMakes,
        (SUM(TotalMidRangeMakes) / NULLIF(SUM(TotalMidRangeShots), 0)) * 100 AS "MidRange%",
        (
            (SUM(Total2ptMakes) + (1.5 * SUM(Total3ptMakes))) / 
            NULLIF((SUM(Total2ptShots) + SUM(Total3ptShots)), 0)
        ) * 100 AS "EFG%",
        SUM(TurnoverCount) AS Turnover,  -- New column to count turnovers
        SUM(FoulCount) AS Foul           -- New column to count fouls
    FROM (
        SELECT 
            PrimaryPlayer AS Player,
            OffensivePossession AS Team,
            COUNT(0) AS TotalPlays,
            SUM(CASE WHEN Outcome IN ('3pmi', '3pma') THEN 1 ELSE 0 END) AS Total3ptShots,
            SUM(CASE WHEN Outcome = '3pMa' THEN 1 ELSE 0 END) AS Total3ptMakes,
            SUM(CASE WHEN (ShotLevel IN (1, 2, 3) AND Outcome NOT IN ('Turnover', 'Foul')) THEN 1 ELSE 0 END) AS Total2ptShots,        
            SUM(CASE WHEN (Outcome IN ('2pMa', 'And1') AND ShotLevel IN (1, 2, 3)) THEN 1 ELSE 0 END) AS Total2ptMakes,
            SUM(CASE WHEN ShotLevel IN (2, 3) THEN 1 ELSE 0 END) AS TotalMidRangeShots,
            SUM(CASE WHEN (ShotLevel IN (2, 3) AND Outcome IN ('And1', '2pMa')) THEN 1 ELSE 0 END) AS TotalMidRangeMakes,
            SUM(CASE WHEN Outcome = 'Turnover' THEN 1 ELSE 0 END) AS TurnoverCount,  -- New calculation for turnovers
            SUM(CASE WHEN Outcome = 'Foul' THEN 1 ELSE 0 END) AS FoulCount            -- New calculation for fouls
        FROM plays
        WHERE 
            SecondaryPlayer = 'N/A' AND PlayID in ({play_numbers_str})
        GROUP BY 
            PrimaryPlayer, Team
        
        UNION ALL
        
        SELECT 
            SecondaryPlayer AS Player,
            OffensivePossession AS Team,
            COUNT(0) AS TotalPlays,
            SUM(CASE WHEN Outcome IN ('3pmi', '3pma') THEN 1 ELSE 0 END) AS Total3ptShots,
            SUM(CASE WHEN Outcome = '3pMa' THEN 1 ELSE 0 END) AS Total3ptMakes,
            SUM(CASE WHEN (ShotLevel IN (1, 2, 3) AND Outcome NOT IN ('Turnover', 'Foul')) THEN 1 ELSE 0 END) AS Total2ptShots,        
            SUM(CASE WHEN (Outcome IN ('2pMa', 'And1') AND ShotLevel IN (1, 2, 3)) THEN 1 ELSE 0 END) AS Total2ptMakes,
            SUM(CASE WHEN ShotLevel IN (2, 3) THEN 1 ELSE 0 END) AS TotalMidRangeShots,
            SUM(CASE WHEN (ShotLevel IN (2, 3) AND Outcome IN ('And1', '2pMa')) THEN 1 ELSE 0 END) AS TotalMidRangeMakes,
            SUM(CASE WHEN Outcome = 'Turnover' THEN 1 ELSE 0 END) AS TurnoverCount,  -- New calculation for turnovers
            SUM(CASE WHEN Outcome = 'Foul' THEN 1 ELSE 0 END) AS FoulCount            -- New calculation for fouls
            
        FROM plays
        WHERE 
            SecondaryPlayer <> 'N/A' AND SecondaryPlayID in ({play_numbers_str})
        GROUP BY 
            SecondaryPlayer, Team
    ) AS CombinedStats
    GROUP BY 
        Player, Team
    ORDER BY 
        TotalPlays DESC;
    """
    
    try:
        cur = conn.cursor()
        cur.execute(view_template)
        print(f"View '{view_name}' modified successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def main():
    conn = connect_to_db()
    if conn:
        try:
            # Get user input for view name and play numbers
            view_name = input("Enter the name of the view to modify: ")
            play_numbers_input = input("Enter a list of primary play numbers (comma-separated): ")
            secondary_play_numbers_input = input("Enter a list of secondary play numbers (comma-separated): ")

            # Convert input play numbers to a list of integers
            play_numbers = list(map(int, play_numbers_input.split(',')))
            secondary_play_numbers = list(map(int, secondary_play_numbers_input.split(',')))

            # Modify the view with the given name and play numbers
            modify_2player_view(conn, view_name, play_numbers, secondary_play_numbers)
            
            conn.commit()  # Commit after modifying the view
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()
    else:
        print("Failed to connect to the database")

if __name__ == "__main__":
    main()