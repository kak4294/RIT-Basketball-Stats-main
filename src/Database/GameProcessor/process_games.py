import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

def update_score(row, new_df, one_or_two, team1, team2):
    """
    Updates the scores for Team1 or Team2 based on the play result.
    
    Parameters:
    - row: A row from the unprocessed DataFrame.
    - new_df: The game DataFrame to be updated.
    - one_or_two: Flag indicating which team to update (1 for Team1, else Team2).
    - team1: Name of Team1.
    - team2: Name of Team2.
    """
    # Initialize scores from the DataFrame   
    if one_or_two == 1:
        if row['Result'] == 'Make 2 Pts':
            new_df.at[0, 'T1Pts'] += 2
        elif row['Result'] == 'Make 3 Pts':
            new_df.at[0, 'T1Pts'] += 3
        elif row['Result'] == 'Free Throw':
            if isinstance(row['Synergy Tags'], str):
                if 'FTM' in row['Synergy Tags']:
                    new_df.at[0, 'T1Pts'] += 1
            else:
                print(f"{team1} vs {team2}: Free Throw at Play #{row['#']} not accounted for.")
                return True
        elif row['Result'] in ['1 Pts', '0 Pts']:
            if isinstance(row['Synergy Tags'], str):
                if '3FGM' in row['Synergy Tags']:
                    new_df.at[0, 'T1Pts'] += 3
                elif '2FGM' in row['Synergy Tags']:
                    new_df.at[0, 'T1Pts'] += 2
            else:
                print(f"{team1} vs {team2}: And 1 at Play #{row['#']} not accounted for.")
                return True
    else:
        if row['Result'] == 'Make 2 Pts':
            new_df.at[0, 'T2Pts'] += 2
        elif row['Result'] == 'Make 3 Pts':
            new_df.at[0, 'T2Pts'] += 3
        elif row['Result'] == 'Free Throw':
            if isinstance(row['Synergy Tags'], str):
                if 'FTM' in row['Synergy Tags']:
                    new_df.at[0, 'T2Pts'] += 1
            else:
                print(f"{team1} vs {team2}: Free Throw at Play #{row['#']} not accounted for.")
                return True
        elif row['Result'] in ['1 Pts', '0 Pts']:
            if isinstance(row['Synergy Tags'], str):
                if '3FGM' in row['Synergy Tags']:
                    new_df.at[0, 'T2Pts'] += 3
                elif '2FGM' in row['Synergy Tags']:
                    new_df.at[0, 'T2Pts'] += 2
            else:
                print(f"{team1} vs {team2}: And 1 at Play #{row['#']} not accounted for.")
                return True
    return False

def process_game(unprocessed_df: pd.DataFrame, processed_df: pd.DataFrame):
    """
    Processes the game by updating statistics based on unprocessed and processed DataFrames.
    
    Parameters:
    - unprocessed_df: DataFrame containing unprocessed game plays.
    - processed_df: DataFrame containing processed game plays.
    
    Returns:
    - game_df: Updated game statistics DataFrame.
    """
    columns = ['Team1', 'Team2', 'T1Pts', 'T2Pts', 'TotalPts', 'Differential', 
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
    
    processed_df = processed_df.reset_index(drop=True)

    # Identify unique teams
    unique_teams = processed_df['OffensivePossession'].unique().tolist()
    if len(unique_teams) < 2:
        print("Error: Less than two unique teams found in 'OffensivePossession'.")
        return None
    team1 = unique_teams[0]
    team2 = unique_teams[1]

    # Initialize game_df with a single row containing team names and zeros for all stats
    initial_data = [team1, team2] + [0] * (len(columns) - 2)
    game_df = pd.DataFrame([initial_data], columns=columns)

    play_not_counted = False

    for _, row in unprocessed_df.iterrows():
        # Update points
        if team1 == row['Team']: 
            not_accounted = update_score(row, game_df, 1, team1, team2)
        else:
            not_accounted = update_score(row, game_df, 0, team1, team2)
            
        if not_accounted:
            play_not_counted = True
            
    # Update total points and differential
    game_df.at[0, 'TotalPts'] = game_df.at[0, 'T1Pts'] + game_df.at[0, 'T2Pts']
    game_df.at[0, 'Differential'] = game_df.at[0, 'T1Pts'] - game_df.at[0, 'T2Pts']
    
    # Update the date of the game
    game_df.at[0, 'Date'] = processed_df.at[0, 'Date']

    for _, row in processed_df.iterrows():        
        # Flag to check which team to update
        team1_update = team1 == row['OffensivePossession']
        
        play_processed = False
        key = row['SecondaryPlayType']
        second_key = row['SecondaryAction']

        # Process based on secondary play types
        if key == 'Cuts': 
            update_cut(team1_update, row, game_df)
            play_processed = True
        elif key == 'Spot Ups' and second_key == 'Shot': 
            update_shot(team1_update, row, game_df)
            play_processed = True
        elif key == 'Spot Ups' and second_key == 'Drive':
            update_drive(team1_update, row, game_df)
            play_processed = True
        elif key == 'P&R Roll Man':  
            update_roll(team1_update, row, game_df)
            play_processed = True

        # If secondary play was not processed, process based on primary play types
        if not play_processed:
            key = row['PrimaryPlayType']
            second_key = row['PrimaryAction']
            
            if key == "PNR": 
                update_pnr(team1_update, row, game_df)
            elif key == 'Iso':
                update_iso(team1_update, row, game_df)
            elif key == 'Post': 
                update_post(team1_update, row, game_df)
            elif key == 'Cuts': 
                update_cut(team1_update, row, game_df)
            elif key == 'Spot Ups' and second_key == 'Shot': 
                update_shot(team1_update, row, game_df)
            elif key == 'Spot Ups' and second_key == 'Drive':
                update_drive(team1_update, row, game_df)
            elif key == 'Off Screens':
                update_offscreen(team1_update, row, game_df)
            elif key == 'Hand Offs':  
                update_handoff(team1_update, row, game_df)
            elif key == 'Transition':  
                update_transition(team1_update, row, game_df)
                
    game_df[game_df.select_dtypes(include=['float']).columns] = game_df.select_dtypes(include=['float']).round(2)
    
    return game_df, play_not_counted

def update_pnr(t1vt2, line, df: pd.DataFrame):
    """
    Updates pick and roll statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_PnrPlays', 'T1_Pnr3PA', 'T1_Pnr3PM', 'T1_Pnr3P%', 
                             'T1_Pnr2PA', 'T1_Pnr2PM', 'T1_Pnr2P%', 'T1_PnrMiA',
                             'T1_PnrMiM', 'T1_PnrMi%', 'T1_PnrEFG%', 'T1_PnrTO', 
                             'T1_PnrFouls']
    else:
        processed_columns = ['T2_PnrPlays', 'T2_Pnr3PA', 'T2_Pnr3PM', 'T2_Pnr3P%', 
                             'T2_Pnr2PA', 'T2_Pnr2PM', 'T2_Pnr2P%', 'T2_PnrMiA', 
                             'T2_PnrMiM', 'T2_PnrMi%', 'T2_PnrEFG%', 'T2_PnrTO', 
                             'T2_PnrFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
    
    # Handle outcomes
    outcome = line['Outcome']
    shot_level = line.get('ShotLevel', 1)  # Default to 1 if not present
    
    if outcome == '2pMa':
        df.at[0, processed_columns[5]] += 1  # Makes
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[8]] += 1  # Makes
            df.at[0, processed_columns[7]] += 1  # Attempts
            
    elif outcome == '2pmi':
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[7]] += 1  # Makes

    elif outcome == '3pMa':
        df.at[0, processed_columns[2]] += 1  # Makes
        df.at[0, processed_columns[1]] += 1  # Attempts

    elif outcome == '3pmi':
        df.at[0, processed_columns[1]] += 1  # Attempts
        
    elif outcome == 'Turnover':
        df.at[0, processed_columns[11]] += 1  # Turnovers
        
    elif outcome == 'Foul':
        df.at[0, processed_columns[12]] += 1  # Fouls
        
    elif outcome == 'And1':
        if shot_level == 4:
            df.at[0, processed_columns[2]] += 1  # Makes
            df.at[0, processed_columns[1]] += 1  # Attempts

        else:
            df.at[0, processed_columns[5]] += 1  # Makes
            df.at[0, processed_columns[4]] += 1  # Attempts

            if shot_level != 1: 
                df.at[0, processed_columns[8]] += 1  # Makes
                df.at[0, processed_columns[7]] += 1  # Attempts
                
    # Update shot percentages
    makes_two = df.at[0, 'T1_Pnr2PM'] if t1vt2 else df.at[0, 'T2_Pnr2PM']
    attempts_two = df.at[0, 'T1_Pnr2PA'] if t1vt2 else df.at[0, 'T2_Pnr2PA']
    makes_three = df.at[0, 'T1_Pnr3PM'] if t1vt2 else df.at[0, 'T2_Pnr3PM']
    attempts_three = df.at[0, 'T1_Pnr3PA'] if t1vt2 else df.at[0, 'T2_Pnr3PA']
    makes_mid = df.at[0, 'T1_PnrMiM'] if t1vt2 else df.at[0, 'T2_PnrMiM']
    attempts_mid = df.at[0, 'T1_PnrMiA'] if t1vt2 else df.at[0, 'T2_PnrMiA']
    
    if attempts_two > 0:
        df.at[0, processed_columns[6]] = update_shot_percent(makes_two, attempts_two)
    if attempts_three > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes_three, attempts_three)
    if attempts_mid > 0:
        df.at[0, processed_columns[9]] = update_shot_percent(makes_mid, attempts_mid)
    
    # Update EFG%
    total_efg = update_EFGpercent(makes_two, attempts_two, makes_three, attempts_three)
    df.at[0, processed_columns[10]] = total_efg

def update_cut(t1vt2, line, df: pd.DataFrame):
    """
    Updates cut statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_CutPlays', 'T1_Cut2PA', 'T1_Cut2PM', 'T1_Cut2P%', 'T1_CutTO', 'T1_CutFouls']
    else:
        processed_columns = ['T2_CutPlays', 'T2_Cut2PA', 'T2_Cut2PM', 'T2_Cut2P%', 'T2_CutTO', 'T2_CutFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
        
    # Handle outcomes
    outcome = line['Outcome']
    if outcome == '2pMa':
        df.at[0, processed_columns[1]] += 1  # Makes
        df.at[0, processed_columns[2]] += 1  # Attempts
    elif outcome == '2pmi':
        df.at[0, processed_columns[2]] += 1  # Attempts
    elif outcome == 'Turnover':
        df.at[0, processed_columns[4]] += 1  # Turnovers
    elif outcome == 'Foul':
        df.at[0, processed_columns[5]] += 1  # Fouls
    elif outcome == 'And1':
        df.at[0, processed_columns[1]] += 1  # Makes
        df.at[0, processed_columns[2]] += 1  # Attempts
    
    # Update shot percentages
    makes = df.at[0, processed_columns[1]]
    attempts = df.at[0, processed_columns[2]]
    if attempts > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes, attempts)

def update_post(t1vt2, line, df: pd.DataFrame):
    """
    Updates post statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_PostPlays','T1_Post2PA', 'T1_Post2PM', 'T1_Post2P%', 'T1_PostTO', 'T1_PostFouls']
    else:
        processed_columns = ['T2_PostPlays', 'T2_Post2PA', 'T2_Post2PM', 'T2_Post2P%', 'T2_PostTO', 'T2_PostFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
        
    # Handle outcomes
    outcome = line['Outcome']
    if outcome == '2pMa':
        df.at[0, processed_columns[2]] += 1  # Makes
        df.at[0, processed_columns[1]] += 1  # Attempts
    elif outcome == '2pmi':
        df.at[0, processed_columns[1]] += 1  # Attempts
    elif outcome == 'Turnover':
        df.at[0, processed_columns[4]] += 1  # Turnovers
    elif outcome == 'Foul':
        df.at[0, processed_columns[5]] += 1  # Fouls
    elif outcome == 'And1':
        df.at[0, processed_columns[2]] += 1  # Makes
        df.at[0, processed_columns[1]] += 1  # Attempts
    
    # Update shot percentages
    makes = df.at[0, processed_columns[2]]
    attempts = df.at[0, processed_columns[1]]
    if attempts > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes, attempts)

def update_roll(t1vt2, line, df: pd.DataFrame):
    """
    Updates roll statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_RollPlays', 'T1_Roll3PA', 'T1_Roll3PM', 'T1_Roll3P%', 'T1_Roll2PA', 'T1_Roll2PM', 
                             'T1_Roll2P%', 'T1_RollMiA', 'T1_RollMiM', 'T1_RollMi%', 'T1_RollEFG%', 'T1_RollTO', 
                             'T1_RollFouls']
    else:
        processed_columns = ['T2_RollPlays', 'T2_Roll3PA', 'T2_Roll3PM', 'T2_Roll3P%', 'T2_Roll2PA', 'T2_Roll2PM', 
                             'T2_Roll2P%', 'T2_RollMiA', 'T2_RollMiM', 'T2_RollMi%', 'T2_RollEFG%', 'T2_RollTO', 
                             'T2_RollFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
        
    # Handle outcomes
    outcome = line['Outcome']
    shot_level = line.get('ShotLevel', 1)
    
    if outcome == '2pMa':
        df.at[0, processed_columns[5]] += 1  # Makes
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[8]] += 1  # Makes
            df.at[0, processed_columns[7]] += 1  # Attempts
    elif outcome == '2pmi':
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[7]] += 1  # Makes
    elif outcome == '3pMa':
        df.at[0, processed_columns[2]] += 1  # Makes
        df.at[0, processed_columns[1]] += 1  # Attempts
    elif outcome == '3pmi':
        df.at[0, processed_columns[1]] += 1  # Attempts
    elif outcome == 'Turnover':
        df.at[0, processed_columns[11]] += 1  # Turnovers
    elif outcome == 'Foul':
        df.at[0, processed_columns[12]] += 1  # Fouls
    elif outcome == 'And1':
        if shot_level == 4:
            df.at[0, processed_columns[2]] += 1  # Makes
            df.at[0, processed_columns[1]] += 1  # Attempts
        else:
            df.at[0, processed_columns[5]] += 1  # Makes
            df.at[0, processed_columns[4]] += 1  # Attempts
            if shot_level != 1:
                df.at[0, processed_columns[8]] += 1  # Makes
                df.at[0, processed_columns[7]] += 1  # Attempts
                
    
    # Update shot percentages
    makes_two = df.at[0, 'T1_Roll2PM'] if t1vt2 else df.at[0, 'T2_Roll2PM']
    attempts_two = df.at[0, 'T1_Roll2PA'] if t1vt2 else df.at[0, 'T2_Roll2PA']
    makes_three = df.at[0, 'T1_Roll3PM'] if t1vt2 else df.at[0, 'T2_Roll3PM']
    attempts_three = df.at[0, 'T1_Roll3PA'] if t1vt2 else df.at[0, 'T2_Roll3PA']
    makes_mid = df.at[0, 'T1_RollMiA'] if t1vt2 else df.at[0, 'T2_RollMiA']
    attempts_mid = df.at[0, 'T1_RollMiM'] if t1vt2 else df.at[0, 'T2_RollMiM']
    
    if attempts_two > 0:
        df.at[0, processed_columns[6]] = update_shot_percent(makes_two, attempts_two)
    if attempts_three > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes_three, attempts_three)
    if attempts_mid > 0:
        df.at[0, processed_columns[9]] = update_shot_percent(makes_mid, attempts_mid)
    
    # Update EFG%
    total_efg = update_EFGpercent(makes_two, attempts_two, makes_three, attempts_three)
    df.at[0, processed_columns[10]] = total_efg

def update_shot(t1vt2, line, df: pd.DataFrame):
    """
    Updates shot statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_SUShotPlays', 'T1_SUShot3PA', 'T1_SUShot3PM', 'T1_SUShot3P%', 
                             'T1_SUShotMiA', 'T1_SUShotMiM', 'T1_SUShotMi%', 
                             'T1_SUShotTO', 'T1_SUShotFouls']
    else:
        processed_columns = ['T2_SUShotPlays', 'T2_SUShot3PA', 'T2_SUShot3PM', 'T2_SUShot3P%', 
                             'T2_SUShotMiA', 'T2_SUShotMiM', 'T2_SUShotMi%', 
                             'T2_SUShotTO', 'T2_SUShotFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
        
    # Handle outcomes
    outcome = line['Outcome']
    shot_level = line.get('ShotLevel', 1)
    
    if outcome == '2pMa':
        df.at[0, processed_columns[5]] += 1  # Makes
        df.at[0, processed_columns[4]] += 1  # Attempts
    elif outcome == '2pmi':
        df.at[0, processed_columns[4]] += 1  # Attempts
    elif outcome == '3pMa':
        df.at[0, processed_columns[2]] += 1  # Makes
        df.at[0, processed_columns[1]] += 1  # Attempts
    elif outcome == '3pmi':
        df.at[0, processed_columns[1]] += 1  # Attempts
    elif outcome == 'Turnover':
        df.at[0, processed_columns[7]] += 1  # Turnovers
    elif outcome == 'Foul':
        df.at[0, processed_columns[8]] += 1  # Fouls
    elif outcome == 'And1':
        if shot_level == 4:
            df.at[0, processed_columns[2]] += 1  # Makes
            df.at[0, processed_columns[1]] += 1  # Attempts
        else:
            df.at[0, processed_columns[5]] += 1  # Makes
            df.at[0, processed_columns[4]] += 1  # Attempts
    
    # Update shot percentages
    makes_three = df.at[0, 'T1_SUShot3PM'] if t1vt2 else df.at[0, 'T2_SUShot3PM']
    attempts_three = df.at[0, 'T1_SUShot3PA'] if t1vt2 else df.at[0, 'T2_SUShot3PA']
    makes_mid = df.at[0, 'T1_SUShotMiM'] if t1vt2 else df.at[0, 'T2_SUShotMiM']
    attempts_mid = df.at[0, 'T1_SUShotMiA'] if t1vt2 else df.at[0, 'T2_SUShotMiA']
    
    if attempts_mid > 0:
        df.at[0, processed_columns[6]] = update_shot_percent(makes_mid, attempts_mid)
    if attempts_three > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes_three, attempts_three)

def update_drive(t1vt2, line, df: pd.DataFrame):
    """
    Updates drive statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_SUDrivePlays', 'T1_SUDriveMiA', 'T1_SUDriveMiM', 'T1_SUDriveMi%', 
                             'T1_SUDrive2PA', 'T1_SUDrive2PM', 'T1_SUDrive2P%', 
                             'T1_SUDriveTO', 'T1_SUDriveFouls']
    else:
        processed_columns = ['T2_SUDrivePlays', 'T2_SUDriveMiA', 'T2_SUDriveMiM', 'T2_SUDriveMi%', 
                             'T2_SUDrive2PA', 'T2_SUDrive2PM', 'T2_SUDrive2P%', 
                             'T2_SUDriveTO', 'T2_SUDriveFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
        
    # Handle outcomes
    outcome = line['Outcome']
    shot_level = line.get('ShotLevel', 1)
    
    if outcome == '2pMa':
        df.at[0, processed_columns[5]] += 1  # Makes
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[2]] += 1  # Makes
            df.at[0, processed_columns[1]] += 1  # Attempts
    elif outcome == '2pmi':
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[1]] += 1  # Attempts
    elif outcome == 'Turnover':
        df.at[0, processed_columns[7]] += 1  # Turnovers 
    elif outcome == 'Foul':
        df.at[0, processed_columns[8]] += 1  # Fouls 
    elif outcome == 'And1':
        if shot_level != 1:
            df.at[0, processed_columns[5]] += 1  # Makes
            df.at[0, processed_columns[4]] += 1  # Attempts
            df.at[0, processed_columns[2]] += 1  # Makes
            df.at[0, processed_columns[1]] += 1  # Attempts
        else:
            df.at[0, processed_columns[5]] += 1  # Makes
            df.at[0, processed_columns[4]] += 1  # Attempts
    
    # Update shot percentages
    makes_two = df.at[0, 'T1_SUDrive2PM'] if t1vt2 else df.at[0, 'T2_SUDrive2PM']
    attempts_two = df.at[0, 'T1_SUDrive2PA'] if t1vt2 else df.at[0, 'T2_SUDrive2PA']
    makes_mid = df.at[0, 'T1_SUDriveMiM'] if t1vt2 else df.at[0, 'T2_SUDriveMiM']
    attempts_mid = df.at[0, 'T1_SUDriveMiA'] if t1vt2 else df.at[0, 'T2_SUDriveMiA']
    
    if attempts_two > 0:
        df.at[0, processed_columns[6]] = update_shot_percent(makes_two, attempts_two)
    if attempts_mid > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes_mid, attempts_mid)

def update_iso(t1vt2, line, df: pd.DataFrame):
    """
    Updates isolation statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_IsoPlays', 'T1_Iso3PA', 'T1_Iso3PM', 'T1_Iso3P%', 
                             'T1_Iso2PA', 'T1_Iso2PM', 'T1_Iso2P%', 'T1_IsoMiA',
                             'T1_IsoMiM', 'T1_IsoMi%', 'T1_IsoEFG%', 'T1_IsoTO', 'T1_IsoFouls']
    else:
        processed_columns = ['T2_IsoPlays', 'T2_Iso3PA', 'T2_Iso3PM', 'T2_Iso3P%', 
                             'T2_Iso2PA', 'T2_Iso2PM', 'T2_Iso2P%', 'T2_IsoMiA', 
                             'T2_IsoMiM', 'T2_IsoMi%', 'T2_IsoEFG%', 'T2_IsoTO', 'T2_IsoFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
        
    # Handle outcomes
    outcome = line['Outcome']
    shot_level = line.get('ShotLevel', 1)
    
    if outcome == '2pMa':
        df.at[0, processed_columns[5]] += 1  # Makes
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[8]] += 1  # Makes
            df.at[0, processed_columns[7]] += 1  # Attempts
            
    elif outcome == '2pmi':
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[7]] += 1  # Makes

    elif outcome == '3pMa':
        df.at[0, processed_columns[2]] += 1  # Makes
        df.at[0, processed_columns[1]] += 1  # Attempts

    elif outcome == '3pmi':
        df.at[0, processed_columns[1]] += 1  # Attempts
        
    elif outcome == 'Turnover':
        df.at[0, processed_columns[11]] += 1  # Turnovers
        
    elif outcome == 'Foul':
        df.at[0, processed_columns[12]] += 1  # Fouls
        
    elif outcome == 'And1':
        if shot_level == 4:
            df.at[0, processed_columns[2]] += 1  # Makes
            df.at[0, processed_columns[1]] += 1  # Attempts

        else:
            df.at[0, processed_columns[5]] += 1  # Makes
            df.at[0, processed_columns[4]] += 1  # Attempts

            if shot_level != 1: 
                df.at[0, processed_columns[8]] += 1  # Makes
                df.at[0, processed_columns[7]] += 1  # Attempts
    
    # Update shot percentages
    makes_two = df.at[0, 'T1_Iso2PM'] if t1vt2 else df.at[0, 'T2_Iso2PM']
    attempts_two = df.at[0, 'T1_Iso2PA'] if t1vt2 else df.at[0, 'T2_Iso2PA']
    makes_three = df.at[0, 'T1_Iso3PM'] if t1vt2 else df.at[0, 'T2_Iso3PM']
    attempts_three = df.at[0, 'T1_Iso3PA'] if t1vt2 else df.at[0, 'T2_Iso3PA']
    makes_mid = df.at[0, 'T1_IsoMiM'] if t1vt2 else df.at[0, 'T2_IsoMiM']
    attempts_mid = df.at[0, 'T1_IsoMiA'] if t1vt2 else df.at[0, 'T2_IsoMiA']

    if attempts_two > 0:
        df.at[0, processed_columns[6]] = update_shot_percent(makes_two, attempts_two)
    if attempts_three > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes_three, attempts_three)
    if attempts_mid > 0:
        df.at[0, processed_columns[9]] = update_shot_percent(makes_mid, attempts_mid)
    
    # Update EFG%
    total_efg = update_EFGpercent(makes_two, attempts_two, makes_three, attempts_three)
    df.at[0, processed_columns[10]] = total_efg

def update_transition(t1vt2, line, df: pd.DataFrame):
    """
    Updates transition statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_TransitionPlays', 'T1_Transition3PA', 'T1_Transition3PM', 'T1_Transition3P%', 
                             'T1_Transition2PA', 'T1_Transition2PM', 'T1_Transition2P%', 'T1_TransitionMiA',
                             'T1_TransitionMiM', 'T1_TransitionMi%', 'T1_TransitionEFG%', 'T1_TransitionTO', 
                             'T1_TransitionFouls']
    else:
        processed_columns = ['T2_TransitionPlays', 'T2_Transition3PA', 'T2_Transition3PM', 'T2_Transition3P%', 
                             'T2_Transition2PA', 'T2_Transition2PM', 'T2_Transition2P%', 'T2_TransitionMiA', 
                             'T2_TransitionMiM', 'T2_TransitionMi%', 'T2_TransitionEFG%', 'T2_TransitionTO', 
                             'T2_TransitionFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
        
    # Handle outcomes
    outcome = line['Outcome']
    shot_level = line.get('ShotLevel', 1)
    
    if outcome == '2pMa':
        df.at[0, processed_columns[5]] += 1  # Makes
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[8]] += 1  # Makes
            df.at[0, processed_columns[7]] += 1  # Attempts
            
    elif outcome == '2pmi':
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[7]] += 1  # Makes

    elif outcome == '3pMa':
        df.at[0, processed_columns[2]] += 1  # Makes
        df.at[0, processed_columns[1]] += 1  # Attempts

    elif outcome == '3pmi':
        df.at[0, processed_columns[1]] += 1  # Attempts
        
    elif outcome == 'Turnover':
        df.at[0, processed_columns[11]] += 1  # Turnovers
        
    elif outcome == 'Foul':
        df.at[0, processed_columns[12]] += 1  # Fouls
        
    elif outcome == 'And1':
        if shot_level == 4:
            df.at[0, processed_columns[2]] += 1  # Makes
            df.at[0, processed_columns[1]] += 1  # Attempts

        else:
            df.at[0, processed_columns[5]] += 1  # Makes
            df.at[0, processed_columns[4]] += 1  # Attempts

            if shot_level != 1: 
                df.at[0, processed_columns[8]] += 1  # Makes
                df.at[0, processed_columns[7]] += 1  # Attempts
    
    # Update shot percentages
    makes_two = df.at[0, 'T1_Transition2PM'] if t1vt2 else df.at[0, 'T2_Transition2PM']
    attempts_two = df.at[0, 'T1_Transition2PA'] if t1vt2 else df.at[0, 'T2_Transition2PA']
    makes_three = df.at[0, 'T1_Transition3PM'] if t1vt2 else df.at[0, 'T2_Transition3PM']
    attempts_three = df.at[0, 'T1_Transition3PA'] if t1vt2 else df.at[0, 'T2_Transition3PA']
    makes_mid = df.at[0, 'T1_TransitionMiM'] if t1vt2 else df.at[0, 'T2_TransitionMiM']
    attempts_mid = df.at[0, 'T1_TransitionMiA'] if t1vt2 else df.at[0, 'T2_TransitionMiA']

    if attempts_two > 0:
        df.at[0, processed_columns[6]] = update_shot_percent(makes_two, attempts_two)
    if attempts_three > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes_three, attempts_three)
    if attempts_mid > 0:
        df.at[0, processed_columns[9]] = update_shot_percent(makes_mid, attempts_mid)
    
    # Update EFG%
    total_efg = update_EFGpercent(makes_two, attempts_two, makes_three, attempts_three)
    df.at[0, processed_columns[10]] = total_efg

def update_offscreen(t1vt2, line, df: pd.DataFrame):
    """
    Updates offscreen statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_OfscPlays', 'T1_Ofsc3PA', 'T1_Ofsc3PM', 'T1_Ofsc3P%', 
                             'T1_Ofsc2PA', 'T1_Ofsc2PM', 'T1_Ofsc2P%', 'T1_OfscMiA',
                             'T1_OfscMiM', 'T1_OfscMi%', 'T1_OfscEFG%', 'T1_OfscTO', 
                             'T1_OfscFouls']
    else:
        processed_columns = ['T2_OfscPlays', 'T2_Ofsc3PA', 'T2_Ofsc3PM', 'T2_Ofsc3P%', 
                             'T2_Ofsc2PA', 'T2_Ofsc2PM', 'T2_Ofsc2P%', 'T2_OfscMiA', 
                             'T2_OfscMiM', 'T2_OfscMi%', 'T2_OfscEFG%', 'T2_OfscTO', 
                             'T2_OfscFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
    
    # Handle outcomes
    outcome = line['Outcome']
    shot_level = line.get('ShotLevel', 1)
    
    if outcome == '2pMa':
        df.at[0, processed_columns[5]] += 1  # Makes
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[8]] += 1  # Makes
            df.at[0, processed_columns[7]] += 1  # Attempts
            
    elif outcome == '2pmi':
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[7]] += 1  # Makes

    elif outcome == '3pMa':
        df.at[0, processed_columns[2]] += 1  # Makes
        df.at[0, processed_columns[1]] += 1  # Attempts

    elif outcome == '3pmi':
        df.at[0, processed_columns[1]] += 1  # Attempts
        
    elif outcome == 'Turnover':
        df.at[0, processed_columns[11]] += 1  # Turnovers
        
    elif outcome == 'Foul':
        df.at[0, processed_columns[12]] += 1  # Fouls
        
    elif outcome == 'And1':
        if shot_level == 4:
            df.at[0, processed_columns[2]] += 1  # Makes
            df.at[0, processed_columns[1]] += 1  # Attempts

        else:
            df.at[0, processed_columns[5]] += 1  # Makes
            df.at[0, processed_columns[4]] += 1  # Attempts

            if shot_level != 1: 
                df.at[0, processed_columns[8]] += 1  # Makes
                df.at[0, processed_columns[7]] += 1  # Attempts
    
    # Update shot percentages
    makes_two = df.at[0, 'T1_Ofsc2PM'] if t1vt2 else df.at[0, 'T2_Ofsc2PM']
    attempts_two = df.at[0, 'T1_Ofsc2PA'] if t1vt2 else df.at[0, 'T2_Ofsc2PA']
    makes_three = df.at[0, 'T1_Ofsc3PM'] if t1vt2 else df.at[0, 'T2_Ofsc3PM']
    attempts_three = df.at[0, 'T1_Ofsc3PA'] if t1vt2 else df.at[0, 'T2_Ofsc3PA']
    makes_mid = df.at[0, 'T1_OfscMiM'] if t1vt2 else df.at[0, 'T2_OfscMiM']
    attempts_mid = df.at[0, 'T1_OfscMiA'] if t1vt2 else df.at[0, 'T2_OfscMiA']

    if attempts_two > 0:
        df.at[0, processed_columns[6]] = update_shot_percent(makes_two, attempts_two)
    if attempts_three > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes_three, attempts_three)
    if attempts_mid > 0:
        df.at[0, processed_columns[9]] = update_shot_percent(makes_mid, attempts_mid)
    
    # Update EFG%
    total_efg = update_EFGpercent(makes_two, attempts_two, makes_three, attempts_three)
    df.at[0, processed_columns[10]] = total_efg

def update_handoff(t1vt2, line, df: pd.DataFrame):
    """
    Updates handoff statistics for a team.
    
    Parameters:
    - t1vt2: Boolean flag indicating which team to update.
    - line: A row from the processed DataFrame.
    - df: The game DataFrame to be updated.
    """
    if t1vt2:
        processed_columns = ['T1_HaOfPlays', 'T1_HaOf3PA', 'T1_HaOf3PM', 'T1_HaOf3P%', 
                             'T1_HaOf2PA', 'T1_HaOf2PM', 'T1_HaOf2P%', 'T1_HaOfMiA',
                             'T1_HaOfMiM', 'T1_HaOfMi%', 'T1_HaOfEFG%', 'T1_HaOfTO', 
                             'T1_HaOfFouls']
    else:
        processed_columns = ['T2_HaOfPlays', 'T2_HaOf3PA', 'T2_HaOf3PM', 'T2_HaOf3P%', 
                             'T2_HaOf2PA', 'T2_HaOf2PM', 'T2_HaOf2P%', 'T2_HaOfMiA', 
                             'T2_HaOfMiM', 'T2_HaOfMi%', 'T2_HaOfEFG%', 'T2_HaOfTO', 
                             'T2_HaOfFouls']
        
    # Increment plays
    df.at[0, processed_columns[0]] += 1
    
    # Handle outcomes
    outcome = line['Outcome']
    shot_level = line.get('ShotLevel', 1)
    
    if outcome == '2pMa':
        df.at[0, processed_columns[5]] += 1  # Makes
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[8]] += 1  # Makes
            df.at[0, processed_columns[7]] += 1  # Attempts
            
    elif outcome == '2pmi':
        df.at[0, processed_columns[4]] += 1  # Attempts
        if shot_level != 1:
            df.at[0, processed_columns[7]] += 1  # Makes

    elif outcome == '3pMa':
        df.at[0, processed_columns[2]] += 1  # Makes
        df.at[0, processed_columns[1]] += 1  # Attempts

    elif outcome == '3pmi':
        df.at[0, processed_columns[1]] += 1  # Attempts
        
    elif outcome == 'Turnover':
        df.at[0, processed_columns[11]] += 1  # Turnovers
        
    elif outcome == 'Foul':
        df.at[0, processed_columns[12]] += 1  # Fouls
        
    elif outcome == 'And1':
        if shot_level == 4:
            df.at[0, processed_columns[2]] += 1  # Makes
            df.at[0, processed_columns[1]] += 1  # Attempts

        else:
            df.at[0, processed_columns[5]] += 1  # Makes
            df.at[0, processed_columns[4]] += 1  # Attempts

            if shot_level != 1: 
                df.at[0, processed_columns[8]] += 1  # Makes
                df.at[0, processed_columns[7]] += 1  # Attempts
    
    # Update shot percentages
    makes_two = df.at[0, 'T1_HaOf2PM'] if t1vt2 else df.at[0, 'T2_HaOf2PM']
    attempts_two = df.at[0, 'T1_HaOf2PA'] if t1vt2 else df.at[0, 'T2_HaOf2PA']
    makes_three = df.at[0, 'T1_HaOf3PM'] if t1vt2 else df.at[0, 'T2_HaOf3PM']
    attempts_three = df.at[0, 'T1_HaOf3PA'] if t1vt2 else df.at[0, 'T2_HaOf3PA']
    makes_mid = df.at[0, 'T1_HaOfMiM'] if t1vt2 else df.at[0, 'T2_HaOfMiM']
    attempts_mid = df.at[0, 'T1_HaOfMiA'] if t1vt2 else df.at[0, 'T2_HaOfMiA']
    
    if attempts_two > 0:
        df.at[0, processed_columns[6]] = update_shot_percent(makes_two, attempts_two)
    if attempts_three > 0:
        df.at[0, processed_columns[3]] = update_shot_percent(makes_three, attempts_three)
    if attempts_mid > 0:
        df.at[0, processed_columns[9]] = update_shot_percent(makes_mid, attempts_mid)
    
    # Update EFG%
    total_efg = update_EFGpercent(makes_two, attempts_two, makes_three, attempts_three)
    df.at[0, processed_columns[10]] = total_efg

def update_shot_percent(makes, attempts):
    """
    Calculates and returns the shot percentage.
    
    Parameters:
    - makes: Number of made shots.
    - attempts: Number of shot attempts.
    
    Returns:
    - shot_percentage: Calculated shot percentage rounded to two decimals.
    """
    if attempts == 0:
        return None
    shot_percentage = makes / attempts
    shot_percentage = round(shot_percentage, 2)
    return shot_percentage

def update_EFGpercent(makes_two, attempts_two, makes_three, attempts_three):
    """
    Calculates and returns the Effective Field Goal (EFG) percentage.
    
    Parameters:
    - makes_two: Number of made 2-point shots.
    - attempts_two: Number of attempted 2-point shots.
    - makes_three: Number of made 3-point shots.
    - attempts_three: Number of attempted 3-point shots.
    
    Returns:
    - efg: Calculated EFG percentage.
    """
    total_attempts = attempts_two + attempts_three
    if total_attempts == 0:
        return None
    efg = (makes_two + (1.5 * makes_three)) / total_attempts
    efg = round(efg, 2)
    return efg


def add_game(csv_file: pd.DataFrame, processed_plays: pd.DataFrame):
    """
    Adds a game's statistics to the CSV file.
    
    Parameters:
    - csv_file: DataFrame containing the unprocessed game plays.
    - processed_plays: DataFrame containing the processed game plays.
    """
    if csv_file is None or processed_plays is None:
        print("Error: 'csv_file' and 'processed_plays' must be provided.")
        return

    # Process stats for the game   
    game_df, play_not_counted = process_game(csv_file, processed_plays)
    game_df.replace("", 0.00, inplace=True)
    
    if game_df is None:
        print("Error in processing game. Exiting.")
        return
    
    return game_df, play_not_counted
    
    
def df_to_csv_file(game_df: pd.DataFrame, t1score, t2score):
    
    # Update score statistics if needed... ['Team1', 'Team2', 'T1Pts', 'T2Pts', 'TotalPts', 'Differential']
    game_df.at[0, 'T1Pts'] = int(t1score)
    game_df.at[0, 'T2Pts'] = int(t2score)
    game_df.at[0, 'TotalPts'] = int(t1score) + int(t2score)
    game_df.at[0, 'Differential'] = int(t1score) - int(t2score)
    
    # Define the CSV path
    csv_path = Path('/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/cleaned/cleaned_game_csv/unprocessed_games.csv')

    # Ensure the parent directory exists
    if not csv_path.parent.exists():
        try:
            csv_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"Directory '{csv_path.parent}' created.")
        except Exception as e:
            print(f"An error occurred while creating the directory: {e}")
            return  # Exit the function if directory creation fails

    # Check if the CSV file exists
    if not csv_path.is_file():
        try:
            # Create the CSV file with headers
            game_df.to_csv(csv_path, index=False)
            print(f"File 'all_proccessed_games.csv' created with headers and first game data.")
        except Exception as e:
            print(f"An error occurred while creating the CSV file: {e}")
    else:
        try:
            # Append the new game data without writing the headers
            game_df.to_csv(csv_path, mode='a', header=False, index=False)
        except Exception as e:
            print(f"An error occurred while appending to the CSV file: {e}")
            
