import pandas as pd
import numpy as np
import sys
import os

def process_score(df):
    # Intialize Score dictionary and filter dataframe
    score_dict = {}
    team_score_df = df[['Result', 'Team', 'Synergy Tags']]
    
    # Seperates teams in order to track score of games
    unique_teams = df['Team'].unique()
    team1 = unique_teams[0]
    team2 = unique_teams[1]
    
    # Intializes score
    team1_score = 0
    team2_score = 0
    
    for idx, row in team_score_df.iterrows():
        
        if row['Result'] == 'Make 2 Pts':
            if row['Team'] == team1:
                team1_score += 2
            else:
                team2_score += 2
                
        if row['Result'] == 'Make 3 Pts':
            if row['Team'] == team1:
                team1_score += 3
            else:
                team2_score += 3
                
        if row['Result'] == 'Free Throw':
            if 'FTM' in row['Synergy Tags']:
                if row['Team'] == team1:
                    team1_score += 1
                else:
                    team2_score += 1
                    
        if row['Result'] == '1 Pts' or row['Result'] == '0 Pts':
            if '3FGM' in row['Synergy Tags']:
                if row['Team'] == team1:
                    team1_score += 3
                else:
                    team2_score += 3
            elif '2FGM' in row['Synergy Tags']:
                if row['Team'] == team1:
                    team1_score += 2
                else:
                    team2_score += 2 
                    
    score_dict[team1] = team1_score
    score_dict[team2] = team2_score
    
    print(f'{team1}: {team1_score}\n')        
    print(f'{team2}: {team2_score}\n')      
    
    return score_dict    
    

if __name__ == "__main__":
    #check that file is provided
    if len(sys.argv) < 2:
        print("Usage: python read_csv.py <csv file path_1> <csv file path_2>...")
        sys.exit()
    
    #process csv files given 
    for csv_file in sys.argv[1:]:
        #Process each csv path
        file_path = os.path.join('/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/raw/unsaved_games', csv_file)

        #turn csv into pandas dataframe
        df = pd.read_csv(file_path, index_col=False)
        
        # Finds team names and score of game
        team_score_dict = process_score(df)
     