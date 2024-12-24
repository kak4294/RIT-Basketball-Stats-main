import os
import csv
import pandas as pd
from csv_to_database import transfer_games_to_db

def split_row_by_team(input_file, team1, team2, date):
    # Configuration
    team1_col_name = 'Team1'
    team2_col_name = 'Team2'
    base_output_dir = '/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/cleaned/Teams'
    secondary_output = '/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/cleaned/cleaned_game_csv/processed_games.csv'
    
    # Read CSV using pandas
    df = pd.read_csv(input_file)
    
    df = df[ (df['Date'] == date) & (df['Team1'] == team1) & (df['Team2'] == team2)]
        
    # Get the column names for writing headers later
    fieldnames = df.columns.tolist()
    
    for _, row in df.iterrows():
        
        # Finds names of the teams
        team1_name = row[team1_col_name]
        team2_name = row[team2_col_name]
        
        # Clean names for files
        team1_name = team1_name.replace(' ', '_')
        team2_name = team2_name.replace(' ', '_')

        # Create a directory for the teams if it doesn't exist
        team1_dir = os.path.join(base_output_dir, team1_name)
        if not os.path.exists(team1_dir):
            os.makedirs(team1_dir)
        team2_dir = os.path.join(base_output_dir, team2_name)
        if not os.path.exists(team2_dir):
            os.makedirs(team2_dir)
        
        output_filename1 = team1_name + '.csv'
        output_filename2 = team2_name + '.csv'
        
        # Path to the output file for this team
        team1_file_path = os.path.join(team1_dir, output_filename1)
        team2_file_path = os.path.join(team2_dir, output_filename2)

        # Check if the files already exists to determine if we need headers
        file1_exists = os.path.isfile(team1_file_path)
        file2_exists = os.path.isfile(team2_file_path)
        file_games_exists = os.path.isfile(secondary_output)
        
        # Create the correct row to transport
        # Convert the row (a pandas Series) to a dict for writing
        row_team1_df, columns = create_row('team1', row, fieldnames)
        row_team2_df, columns = create_row('team2', row, fieldnames)
        
        # Convert Series to dictionary before writing to CSV
        row_team1_dict = row_team1_df.to_dict()
        row_team2_dict = row_team2_df.to_dict()
                
        # Open the team file in append mode for team 1
        if not row_exists(team1_file_path, row_team1_dict):  
            transfer_games_to_db(row_team1_dict) 
            with open(team1_file_path, 'a', newline='', encoding='utf-8') as team1_file:
                writer = csv.DictWriter(team1_file, fieldnames=columns)
                if not file1_exists:
                    writer.writeheader() 
                writer.writerow(row_team1_dict) 
            with open(secondary_output, 'a', newline='', encoding='utf-8') as all_games_file:
                writer = csv.DictWriter(all_games_file, fieldnames=columns)
                if not file_games_exists:
                    writer.writeheader() 
                writer.writerow(row_team1_dict)

        # Open the team file in append mode for team 2
        if not row_exists(team2_file_path, row_team2_dict):  
            transfer_games_to_db(row_team2_dict)
            with open(team2_file_path, 'a', newline='', encoding='utf-8') as team2_file:
                writer = csv.DictWriter(team2_file, fieldnames=columns)
                if not file2_exists:
                    writer.writeheader() 
                writer.writerow(row_team2_dict) 
            with open(secondary_output, 'a', newline='', encoding='utf-8') as all_games_file:
                writer = csv.DictWriter(all_games_file, fieldnames=columns)
                if not file_games_exists:
                    writer.writeheader() 
                writer.writerow(row_team2_dict)   
                
    print("Processing complete.")
    

def row_exists(file_path, row_dict):
    if os.path.exists(file_path):
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for existing_row in reader:
                # Convert every value in existing_row to a string (by putting in quotes)
                quoted_existing_row = {key: f'"{value}"' for key, value in existing_row.items()}
                
                # Compare quoted existing row with row_dict (which is already a dictionary of strings)
                if quoted_existing_row == {key: f'"{value}"' for key, value in row_dict.items()}:
                    return True  # Row already exists
    return False  # Row does not exist


def create_row(team, row: pd.Series, df_columns):
    columns = ['Team', 'Opponent', 'Team_Pts', 'Opponent_Pts', 'TotalPts', 'Differential', 
               'T1_CutPlays', 'T1_Cut2PA', 'T1_Cut2PM', 'T1_Cut2P%', 'T1_CutTO', 'T1_CutFouls', 
               
               'T1_PnrPlays', 'T1_Pnr3PA', 'T1_Pnr3PM', 'T1_Pnr3P%', 'T1_Pnr2PA', 'T1_Pnr2PM', 'T1_Pnr2P%', 'T1_PnrMiA','T1_PnrMiM', 
               'T1_PnrMi%', 'T1_PnrEFG%', 'T1_PnrTO', 'T1_PnrFouls', 
               
               'T1_PostPlays','T1_Post2PA', 'T1_Post2PM', 'T1_Post2P%', 'T1_PostTO', 'T1_PostFouls', 
               
               'T1_RollPlays', 'T1_Roll3PA', 'T1_Roll3PM', 'T1_Roll3P%', 'T1_Roll2PA', 'T1_Roll2PM', 'T1_Roll2P%', 'T1_RollMiA',
               'T1_RollMiM', 'T1_RollMi%', 'T1_RollEFG%', 'T1_RollTO', 'T1_RollFouls', 
               
               'T1_SUShotPlays', 'T1_SUShot3PA', 'T1_SUShot3PM', 'T1_SUShot3P%', 'T1_SUShotMiA','T1_SUShotMiM', 'T1_SUShotMi%', 
               'T1_SUShotTO', 'T1_SUShotFouls', 
               
               'T1_SUDrivePlays', 'T1_SUDriveMiA', 'T1_SUDriveMiM', 'T1_SUDriveMi%', 'T1_SUDrive2PA', 'T1_SUDrive2PM', 'T1_SUDrive2P%', 
               'T1_SUDriveTO', 'T1_SUDriveFouls',
               
               'T1_IsoPlays', 'T1_Iso3PA', 'T1_Iso3PM', 'T1_Iso3P%', 'T1_Iso2PA', 'T1_Iso2PM', 'T1_Iso2P%', 'T1_IsoMiA','T1_IsoMiM', 
               'T1_IsoMi%', 'T1_IsoEFG%', 'T1_IsoTO', 'T1_IsoFouls',
               
               'T1_TransitionPlays', 'T1_Transition3PA', 'T1_Transition3PM', 'T1_Transition3P%', 
               'T1_Transition2PA', 'T1_Transition2PM', 'T1_Transition2P%', 'T1_TransitionMiA','T1_TransitionMiM', 
               'T1_TransitionMi%', 'T1_TransitionEFG%', 'T1_TransitionTO', 'T1_TransitionFouls', 
               
               'T1_OfscPlays', 'T1_Ofsc3PA', 'T1_Ofsc3PM', 'T1_Ofsc3P%', 'T1_Ofsc2PA', 'T1_Ofsc2PM', 'T1_Ofsc2P%', 'T1_OfscMiA','T1_OfscMiM', 
               'T1_OfscMi%', 'T1_OfscEFG%', 'T1_OfscTO', 'T1_OfscFouls', 
               
               'T1_HaOfPlays', 'T1_HaOf3PA', 'T1_HaOf3PM', 'T1_HaOf3P%', 'T1_HaOf2PA', 'T1_HaOf2PM', 'T1_HaOf2P%', 'T1_HaOfMiA',
               'T1_HaOfMiM', 'T1_HaOfMi%', 'T1_HaOfEFG%', 'T1_HaOfTO', 'T1_HaOfFouls',
               
               
               'T2_CutPlays', 'T2_Cut2PA', 'T2_Cut2PM', 'T2_Cut2P%', 'T2_CutTO', 'T2_CutFouls', 

               'T2_PnrPlays', 'T2_Pnr3PA', 'T2_Pnr3PM', 'T2_Pnr3P%', 'T2_Pnr2PA', 'T2_Pnr2PM', 
               'T2_Pnr2P%', 'T2_PnrMiA', 'T2_PnrMiM', 'T2_PnrMi%', 'T2_PnrEFG%', 'T2_PnrTO', 
               'T2_PnrFouls', 
               
               'T2_PostPlays', 'T2_Post2PA', 'T2_Post2PM', 'T2_Post2P%', 'T2_PostTO', 'T2_PostFouls', 

               'T2_RollPlays', 'T2_Roll3PA', 'T2_Roll3PM', 'T2_Roll3P%', 'T2_Roll2PA', 
               'T2_Roll2PM', 'T2_Roll2P%', 'T2_RollMiA', 'T2_RollMiM', 'T2_RollMi%', 
               'T2_RollEFG%', 'T2_RollTO', 'T2_RollFouls', 

               'T2_SUShotPlays', 'T2_SUShot3PA', 'T2_SUShot3PM', 'T2_SUShot3P%', 
               'T2_SUShotMiA', 'T2_SUShotMiM', 'T2_SUShotMi%', 'T2_SUShotTO', 
               'T2_SUShotFouls', 

               'T2_SUDrivePlays', 'T2_SUDriveMiA', 'T2_SUDriveMiM', 'T2_SUDriveMi%', 'T2_SUDrive2PA', 
               'T2_SUDrive2PM', 'T2_SUDrive2P%', 'T2_SUDriveTO', 'T2_SUDriveFouls',

               'T2_IsoPlays', 'T2_Iso3PA', 'T2_Iso3PM', 'T2_Iso3P%', 'T2_Iso2PA', 
               'T2_Iso2PM', 'T2_Iso2P%', 'T2_IsoMiA', 'T2_IsoMiM', 'T2_IsoMi%', 
               'T2_IsoEFG%', 'T2_IsoTO', 'T2_IsoFouls',

               'T2_TransitionPlays', 'T2_Transition3PA', 
               'T2_Transition3PM', 'T2_Transition3P%', 'T2_Transition2PA', 
               'T2_Transition2PM', 'T2_Transition2P%', 'T2_TransitionMiA', 
               'T2_TransitionMiM', 'T2_TransitionMi%', 'T2_TransitionEFG%', 
               'T2_TransitionTO', 'T2_TransitionFouls', 

               'T2_OfscPlays', 'T2_Ofsc3PA', 'T2_Ofsc3PM', 'T2_Ofsc3P%', 
               'T2_Ofsc2PA', 'T2_Ofsc2PM', 'T2_Ofsc2P%', 'T2_OfscMiA', 
               'T2_OfscMiM', 'T2_OfscMi%', 'T2_OfscEFG%', 'T2_OfscTO', 
               'T2_OfscFouls', 

               'T2_HaOfPlays', 'T2_HaOf3PA', 'T2_HaOf3PM', 'T2_HaOf3P%', 
               'T2_HaOf2PA', 'T2_HaOf2PM', 'T2_HaOf2P%', 'T2_HaOfMiA', 
               'T2_HaOfMiM', 'T2_HaOfMi%', 'T2_HaOfEFG%', 'T2_HaOfTO', 'T2_HaOfFouls',
               
               'Date'
            ]
    
    updated_columns = [col.replace('T1', 'O') for col in columns]
    updated_columns = [col.replace('T2', 'D') for col in updated_columns]
    
    # Initialize team_df as a Series with updated_columns as its index
    team_df = pd.Series(index=updated_columns)
    
    # Case: Team 1 being explored
    if team == 'team1':
        team_df['Team'] = row['Team1']
        team_df['Opponent'] = row['Team2']
        team_df['Team_Pts'] = row['T1Pts']
        team_df['Opponent_Pts'] = row['T2Pts']
        team_df['TotalPts'] = row['T1Pts'] + row['T2Pts']
        team_df['Differential'] = row['T1Pts'] - row['T2Pts']
        team_df['Date'] = row['Date']
        
        for i in range(6, len(df_columns)):
            column_name = df_columns[i]
            if 'T1' in column_name:
                new_key = column_name.replace('T1', 'O')
                team_df[new_key] = row[column_name]
            elif 'T2' in column_name:
                new_key = column_name.replace('T2', 'D')
                team_df[new_key] = row[column_name]
        
        return team_df, updated_columns
    
    # Case: Team 2 being explored
    team_df['Team'] = row['Team2']
    team_df['Opponent'] = row['Team1']
    team_df['Team_Pts'] = row['T2Pts']
    team_df['Opponent_Pts'] = row['T1Pts']
    team_df['TotalPts'] = row['T2Pts'] + row['T1Pts']
    team_df['Differential'] = row['T2Pts'] - row['T1Pts']
    team_df['Date'] = row['Date']
    
    for i in range(6, len(df_columns)):
        column_name = df_columns[i]
        if 'T1' in column_name:
            new_key = column_name.replace('T1', 'D')
            team_df[new_key] = row[column_name]
        elif 'T2' in column_name:
            new_key = column_name.replace('T2', 'O')
            team_df[new_key] = row[column_name]
    
    return team_df, updated_columns
        
     
if __name__ == '__main__':
    split_row_by_team('/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/src/Database/GameProcessor/sample_processed_games.csv')
   