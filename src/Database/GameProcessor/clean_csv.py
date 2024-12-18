"""
File: read_csv.py

Description:
A program to read a given csv file from command line, 
parse and grab needed information to later be added to database

Authors:
Nick Creeley
Kyle Krebs

"""

import pandas as pd
import numpy as np
import os
import shutil
from process_games import add_game
from csv_to_database import transfer_plays_to_db


"""
process_csv: Processes the csv file

"""
def process_plays(csv_df: pd.DataFrame):
    # defining constraints of rows that we do not care about
    constraints = get_constraints(csv_df)
    
    # filter dataframe to fit the constraints
    filtered_df = csv_df[constraints]
    
    # final dataframe with important info
    final_df = pd.DataFrame(index=filtered_df.index, columns=['Home','Away', 'OffensivePossession', 'Outcome', 'ShotType', 'PrimaryPlayer', 'PrimaryPlayType', 'PrimaryDirection', 'PrimaryAction', 'SecondaryPlayer', 'SecondaryPlayType', 'SecondaryDirection', 'SecondaryAction'])
    final_df[:] = None

    # finds key information and puts in
    finds_opponent_site_and_conference(filtered_df, final_df) # Checked and done
    find_playoutcomes(filtered_df, final_df) 
    find_shottypes(filtered_df, final_df)
    find_playtype(filtered_df, final_df)
    find_offensive_team(filtered_df, final_df)
    find_players(filtered_df, final_df)
    find_playnumber(filtered_df, final_df)
    find_levelshot(filtered_df, final_df)
    find_year(filtered_df, final_df)

    
    final_df.fillna({'PrimaryPlayType':'N/A'}, inplace=True)
    final_df.fillna({'SecondaryPlayType':'N/A'}, inplace=True)
    final_df.fillna({'PrimaryAction':'N/A'}, inplace=True)
    final_df.fillna({'SecondaryAction':'N/A'}, inplace=True)
    final_df.fillna({'PrimaryDirection':'N/A'}, inplace=True)
    final_df.fillna({'SecondaryDirection':'N/A'}, inplace=True)

    final_df.replace('None', 'N/A', inplace=True)

    
    # print(final_df.isnull().sum())
    
    condition1 = final_df['Outcome'].isnull()
    condition2 = final_df['PrimaryPlayType'].isnull()
    
    conditions = condition1 | condition2

    filtered_rows = final_df.loc[conditions]
    
    # print(filtered_rows)
    
    # print('\n')
    
    return final_df


def find_conference(team):
    liberty_league = ['RIT', 'Bar', 'CU', 'HOB', 'IC', 'RPI', 'SKD', 'SLS', 'UNY', 'VC']
    empire8 = ['ALF', 'NAZ', 'SJC', 'UTI', 'Keu', 'SAG', 'Elm', 'HAR', 'HC', 'SGK', 'SUP', 'BRO']
    UAthleticAssociation = []
    sunyac = ['SNP', 'OST', 'ONE', 'PSC', 'BFS', 'SCD', 'FRE', 'SUN', 'SCK', 'Mor' ]

    if team in liberty_league:
        conference = 'Liberty League'
    elif team in empire8:
        conference = 'Empire 8'
    elif team in UAthleticAssociation:
        conference = 'University Athletic Association'
    elif team in sunyac:
        conference = 'SUNYAC'
    else:
        conference = 'UNKNOWN'
        
    return conference   


def finds_opponent_site_and_conference(df: pd.DataFrame, final_df: pd.DataFrame):
    # Checks to make sure 'Game' column exists
    if 'Game' not in df.columns:
        raise ValueError("The input DataFrame must contain a 'Game' column.")
    
    # Split 'Game' column values into 'Home' and 'Away' teams
    away_teams, home_teams = zip(*df['Game'].apply(lambda x: x.split('@') if '@' in x else ('Unknown', 'Unknown')))
    
    # Assign the split values to the final DataFrame
    final_df['Home'] = home_teams
    final_df['Away'] = away_teams

    # Create new columns for OffensiveConference and DefensiveConference
    final_df['OffensiveConference'] = final_df['Home'].apply(find_conference)
    final_df['DefensiveConference'] = final_df['Away'].apply(find_conference)


def find_offensive_team(df: pd.DataFrame, final_df: pd.DataFrame):
    final_df['OffensivePossession'] = df['Team']

def find_year(df: pd.DataFrame, final_df: pd.DataFrame):
    
    dates = []
    
    for index, row in df.iterrows():
        date_list = row['Date'].split('/')
        
        date = None
        
        if int(date_list[0]) > 6:
            date = int(date_list[2]) + 1
        else:
            date = int(date_list[2])
            
        dates.append(date)
            
    final_df['Year'] = dates
        
def find_playoutcomes(df: pd.DataFrame, final_df: pd.DataFrame):
    # Maps The result column values to their new outcome values
    outcome_mapping = {
        'Foul': 'Foul',
        'Make 2 Pts': '2pMa',
        'Make 3 Pts': '3pMa',
        'Miss 2 Pts': '2pmi',
        'Miss 3 Pts': '3pmi',
        'Turnover': 'Turnover',
        '1 Pts': 'And1',
        '0 Pts': 'And1'
    }
    final_df['Outcome'] = df['Result'].map(outcome_mapping)

def find_shottypes(df: pd.DataFrame, final_df: pd.DataFrame):
    # Initialize an empty list to store shot types for each row
    shot_types = []

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Split the 'Synergy String' of the current row into a list based on delimiters
        synergy_list = row['Synergy String'].split(' > ')
            
        # Initialize shot type for the current row
        shot_type = None
            

        # Check for each shot type keyword in the synergy list
        if 'No Dribble Jumper' in synergy_list:
            shot_type = 'No Dribble Jumper'
        elif 'Dribble Jumper' in synergy_list:
            shot_type = 'Dribble Jumper'
        elif 'Drop Step' in synergy_list or 'To Drop Step' in synergy_list:
            shot_type = 'Drop Step'
        elif 'Hook Shot' in synergy_list or 'To Hook' in synergy_list:
            shot_type = 'Hook Shot'
        elif 'To Basket' in synergy_list or 'At Basket' in synergy_list or 'Rolls to Basket' in synergy_list or 'Cut' in synergy_list:
            shot_type = 'To Basket'
        elif 'Offensive Rebound' in synergy_list and 'Short' in synergy_list and 'Scoring Attempt' in synergy_list:
            shot_type = 'To Basket'
        elif 'Foul' in synergy_list or 'Turnover' in synergy_list or 'Shot Clock Violation':
            shot_type = 'N/A'
        else:
            print(synergy_list)

        # Append the shot type to the list for this row
        shot_types.append(shot_type)

    # Add the shot types list to the final DataFrame
    final_df['ShotType'] = shot_types
    
def find_players(df: pd.DataFrame, final_df: pd.DataFrame):
    
    primary_players = []
    secondary_players = []
    
    for index, row in df.iterrows():
        # Split the 'Player' column of the current row into a list based on delimiters
        synergy_list = row['Synergy String'].split(' > Ball Delivered > ')
    
        primary_play_list = synergy_list[0].split(' > ')
        primary_player = find_player_from_list(primary_play_list)
        
        secondary_play_list = None
        if len(synergy_list) > 1:
            secondary_play_list = synergy_list[1].split(' > ')
            secondary_player = find_player_from_list(secondary_play_list)
        else:
            secondary_player = 'N/A'
        
        # Append primary and secondary players to their respective lists
        primary_players.append(primary_player)
        secondary_players.append(secondary_player)
        
    # Add the lists as new columns in final_df
    final_df['PrimaryPlayer'] = primary_players
    final_df['SecondaryPlayer'] = secondary_players
        
def find_player_from_list(string_list):
    player_name_list = string_list[0].split(' ')
    name = ' '.join(player_name_list[1:])
    return name
    
def find_playtype(df: pd.DataFrame, final_df: pd.DataFrame):
    
    # iterates through rows in uncleaned dataframe
    for index, row in df.iterrows():
        # Split the 'Synergy String' of the current row into a list based on delimiters
        synergy_list = row['Synergy String'].split(' > Ball Delivered > ')
            
        for i in range(len(synergy_list)):
            play_list = synergy_list[i].split(' > ')
            if 'ISO' in play_list:
                process_iso(synergy_list[i], i, final_df, index)
            elif 'Spot-Up' in play_list:
                process_spot_ups(synergy_list[i], i, final_df, index)
            elif 'Hand Off' in play_list:
                process_hand_offs(synergy_list[i], i, final_df, index)
            elif 'Off Screen' in play_list:
                process_off_screens(synergy_list[i], i, final_df, index)
            elif 'Cut' in play_list:
                process_cuts(synergy_list[i], i, final_df, index)
            elif 'Post-Up' in play_list:
                process_postups(synergy_list[i], i, final_df, index)
            elif 'Transition' in play_list:
                process_transition(synergy_list[i], i, final_df, index)
            elif 'P&R Roll Man' in play_list:
                process_pnr_roll_man(synergy_list[i], i, final_df, index)
            elif 'P&R Ball Handler' in play_list:
                process_pnr(synergy_list[i], i, final_df, index)
            elif 'No Play Type' in play_list:
                final_df.at[index, 'PrimaryPlayType'] = 'Misc'

def find_playnumber(df: pd.DataFrame, final_df: pd.DataFrame):
    if '#' not in df.columns:
        raise ValueError("The input DataFrame must contain a '#' column.")
    
    final_df['PlayNumber'] = df['#']

def find_levelshot(df: pd.DataFrame, final_df: pd.DataFrame):
     # iterates through rows in uncleaned dataframe
    for index, row in df.iterrows():
        # Split the 'Synergy String' of the current row into a list based on delimiters
        synergy_string = row['Synergy String'].split(' > ')
        
        level_one_list = ['To Basket', 'At Basket', 'Rolls to Basket', 'Basket', 'Offensive Rebound', 
                          'Short', 'Make 2 Pts Foul', 'To Hook', 'Cut', 'To Drop Step', 'To Jumper', 
                          'To Up and Under', 'Post-Up']
            
        if 'Short to < 17\'' in synergy_string:
            final_df.at[index, 'ShotLevel'] = 2
        elif 'Medium/17\' to <3p' in synergy_string:
            final_df.at[index, 'ShotLevel'] = 3
        elif 'Long/3pt' in synergy_string:
            final_df.at[index, 'ShotLevel'] = 4
        else:
            final_df.at[index, 'ShotLevel'] = 1  

def process_cuts(playlist, playnumber, final_df: pd.DataFrame, idx):
    play_type = 'Cuts'
    if playnumber == 0:
        # Initialize the primary playtype and action
        final_df.at[idx, 'PrimaryPlayType'] = play_type
        action_column = 'PrimaryAction'
    else:
        # Initialize the secondary playtype and action
        final_df.at[idx, 'SecondaryPlayType'] = play_type
        action_column = 'SecondaryAction'
    
    # Determine the action
    if 'Basket' in playlist:
        final_df.at[idx, action_column] = 'Basket'
    elif 'Screen' in playlist:
        final_df.at[idx, action_column] = 'Screen'
    elif 'Flash' in playlist:
        final_df.at[idx, action_column] = 'Flash'
        
def process_transition(playlist, playnumber, final_df: pd.DataFrame, idx):
    play_type = 'Transition'
    action_column = 'PrimaryAction' if playnumber == 0 else 'SecondaryAction'
    playtype_column = 'PrimaryPlayType' if playnumber == 0 else 'SecondaryPlayType'
    
    # Initialize the play type
    final_df.at[idx, playtype_column] = play_type

    # Determine the play action
    if 'Ballhandler' in playlist:
        final_df.at[idx, action_column] = 'Ball Handler'
    elif 'Left Wing' in playlist:
        final_df.at[idx, action_column] = 'Left Wing'
    elif 'Right Wing' in playlist:
        final_df.at[idx, action_column] = 'Right Wing'
    elif 'Trailer' in playlist:
        final_df.at[idx, action_column] = 'Trailer'
    elif 'Leak Outs' in playlist:
        final_df.at[idx, action_column] = 'Leak Outs'
    elif 'First Middle' in playlist:
        final_df.at[idx, action_column] = 'First Middle'

def process_off_screens(playlist, playnumber, final_df: pd.DataFrame, idx):
    play_type = 'Off Screens'
    direction_column = 'PrimaryDirection' if playnumber == 0 else 'SecondaryDirection'
    action_column = 'PrimaryAction' if playnumber == 0 else 'SecondaryAction'
    playtype_column = 'PrimaryPlayType' if playnumber == 0 else 'SecondaryPlayType'
    
    # Initialize the play type
    final_df.at[idx, playtype_column] = play_type

    # Determine the direction
    if 'Top' in playlist:
        final_df.at[idx, direction_column] = 'Top'
    elif 'Right' in playlist:
        final_df.at[idx, direction_column] = 'Right'
    elif 'Left' in playlist:
        final_df.at[idx, direction_column] = 'Left'

    # Determine the action
    if 'Curl' in playlist:
        final_df.at[idx, action_column] = 'Curl'
    elif 'Straight' in playlist:
        final_df.at[idx, action_column] = 'Straight'
    elif 'Flare' in playlist:
        final_df.at[idx, action_column] = 'Flare'

def process_hand_offs(playlist, playnumber, final_df: pd.DataFrame, idx):
    play_type = 'Hand Offs'
    direction_column = 'PrimaryDirection' if playnumber == 0 else 'SecondaryDirection'
    action_column = 'PrimaryAction' if playnumber == 0 else 'SecondaryAction'
    playtype_column = 'PrimaryPlayType' if playnumber == 0 else 'SecondaryPlayType'
    
    # Initialize the play type
    final_df.at[idx, playtype_column] = play_type

    # Determine the direction
    if 'Top' in playlist:
        final_df.at[idx, direction_column] = 'Top'
    elif 'Right' in playlist:
        final_df.at[idx, direction_column] = 'Right'
    elif 'Left' in playlist:
        final_df.at[idx, direction_column] = 'Left'

    # Determine the action
    if 'Dribble' in playlist:
        final_df.at[idx, action_column] = 'Dribble'
    elif 'Stationary' in playlist:
        final_df.at[idx, action_column] = 'Stationary'
        
def process_pnr_roll_man(playlist, playnumber, final_df: pd.DataFrame, idx):
    play_type = 'P&R Roll Man'
    direction_column = 'PrimaryDirection' if playnumber == 0 else 'SecondaryDirection'
    action_column = 'PrimaryAction' if playnumber == 0 else 'SecondaryAction'
    playtype_column = 'PrimaryPlayType' if playnumber == 0 else 'SecondaryPlayType'
    
    # Initialize the play type
    final_df.at[idx, playtype_column] = play_type

    # Determine the direction
    if 'Drives Left' in playlist:
        final_df.at[idx, direction_column] = 'Left'
    elif 'Drives Right' in playlist:
        final_df.at[idx, direction_column] = 'Right'

    # Determine the action
    if 'Pick and Pops' in playlist:
        final_df.at[idx, action_column] = 'Pop'
    elif 'Rolls to Basket' in playlist:
        final_df.at[idx, action_column] = 'Roll'
    elif 'Slips the Pick' in playlist:
        final_df.at[idx, action_column] = 'Slips'

def process_spot_ups(playlist, playnumber, final_df: pd.DataFrame, idx):
    play_type = 'Spot Ups'
    direction_column = 'PrimaryDirection' if playnumber == 0 else 'SecondaryDirection'
    action_column = 'PrimaryAction' if playnumber == 0 else 'SecondaryAction'
    playtype_column = 'PrimaryPlayType' if playnumber == 0 else 'SecondaryPlayType'
    
    # Initialize the play type
    final_df.at[idx, playtype_column] = play_type

    # Initialize the action to None
    action = None

    # Determine the direction and set action to 'Drive' if a direction is found
    if 'Drives Left' in playlist:
        final_df.at[idx, direction_column] = 'Left'
        action = 'Drive'
    elif 'Drives Right' in playlist:
        final_df.at[idx, direction_column] = 'Right'
        action = 'Drive'
    elif 'Drives Straight' in playlist:
        final_df.at[idx, direction_column] = 'Straight'
        action = 'Drive'

    # Determine the action if not already set to 'Drive'
    if 'No Dribble Jumper' in playlist:
        action = 'Shot'

    # Set the action column in the DataFrame
    if action is not None:
        final_df.at[idx, action_column] = action
                  
def process_pnr(playlist, playnumber, final_df: pd.DataFrame, idx):
    play_type = 'PNR'
    direction_column = 'PrimaryDirection' if playnumber == 0 else 'SecondaryDirection'
    action_column = 'PrimaryAction' if playnumber == 0 else 'SecondaryAction'
    playtype_column = 'PrimaryPlayType' if playnumber == 0 else 'SecondaryPlayType'
    
    # Initialize the play type
    final_df.at[idx, playtype_column] = play_type

    # Initialize the action to None
    action = None

    # Determine the direction
    if 'Left P&R' in playlist:
        final_df.at[idx, direction_column] = 'Left'
    elif 'Right P&R' in playlist:
        final_df.at[idx, direction_column] = 'Right'
    elif 'High P&R' in playlist:
        final_df.at[idx, direction_column] = 'High'

    # Determine the action
    if 'Dribbles Off Pick' in playlist or 'Dribble Off Pick' in playlist:
        action = 'Off'
    elif 'Go Away from Pick' in playlist:
        action = 'Away'

    # Set the action column in the DataFrame
    #if action is not None:
    final_df.at[idx, action_column] = action
        
def process_iso(playlist, playnumber, final_df: pd.DataFrame, idx):
    play_type = 'Iso'
    direction_column = 'PrimaryDirection' if playnumber == 0 else 'SecondaryDirection'
    playtype_column = 'PrimaryPlayType' if playnumber == 0 else 'SecondaryPlayType'
    
    # Initialize the play type
    final_df.at[idx, playtype_column] = play_type

    # Determine the direction
    if 'Top' in playlist:
        final_df.at[idx, direction_column] = 'Top'
    elif 'Right' in playlist:
        final_df.at[idx, direction_column] = 'Right'
    elif 'Left' in playlist:
        final_df.at[idx, direction_column] = 'Left'
        
def process_postups(playlist, playnumber, final_df: pd.DataFrame, idx):
    play_type = 'Post'
    direction_column = 'PrimaryDirection' if playnumber == 0 else 'SecondaryDirection'
    action_column = 'PrimaryAction' if playnumber == 0 else 'SecondaryAction'
    playtype_column = 'PrimaryPlayType' if playnumber == 0 else 'SecondaryPlayType'
    
    # Initialize the play type
    final_df.at[idx, playtype_column] = play_type

    # Determine the direction
    if 'Flash Middle' in playlist:
        final_df.at[idx, direction_column] = 'Middle'
    elif 'Right Block' in playlist:
        final_df.at[idx, direction_column] = 'Right'
    elif 'Left Block' in playlist:
        final_df.at[idx, direction_column] = 'Left'

    # Determine the action
    if 'Face-up' in playlist:
        final_df.at[idx, action_column] = 'Face Up'
    elif 'Left Shoulder' in playlist:
        final_df.at[idx, action_column] = 'Left Shoulder'
    elif 'Right Shoulder' in playlist:
        final_df.at[idx, action_column] = 'Right Shoulder'
    elif 'Dribble Move' in playlist:
        final_df.at[idx, action_column] = 'Dribble'
            
        
def get_constraints(csv_df: pd.DataFrame):
    constraint1 = csv_df['Result'] != "No Violation"
    constraint2 = csv_df['Result'] != "Free Throw"
    constraint3 = csv_df['Result'] != "Run Offense"
    constraint4 = csv_df['Result'] != "Non Shooting Foul"
    constraint5 = csv_df['Result'] != "Kicked Ball"
    constraint6 = csv_df['Result'] != "Shot Clock Violation"
    constraint7 = csv_df['Result'] != "8 Sec Violation"
    constraint8 = csv_df['Result'] != "Out of Bound 5 Sec Violation"
    return constraint1 & constraint2 & constraint3 & constraint4 & constraint5 & constraint6 & constraint7 & constraint8


def run_clean_csv(csv_file):
    #Process csv path
    raw_file_path = os.path.join('/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/raw/unsaved_games', csv_file)
    
    # Creates a cleaned version of game data
    raw_df = pd.read_csv(raw_file_path, index_col=False)
    final_df = process_plays(raw_df)
    
    # Aggregates all team data together from one specific game and puts into csv file
    add_game(raw_df, final_df)
    
    # Creates a new file with clean play data into seperate folder
    file_name = 'cleaned_' + csv_file
    cleaned_file_path = os.path.join('/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/cleaned/cleaned_game_csv/cleaned_csv', file_name)
    final_df.to_csv(cleaned_file_path, encoding='utf-8', index=False)
    
    # Transfers each play into actual database
    transfer_plays_to_db(cleaned_file_path)
    
    # Moves files to a saved location once they are in the database
    source = os.path.join("/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/raw/unsaved_games", csv_file)
    destination = os.path.join("/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/raw/saved_games", csv_file)
    shutil.move(source, destination)

     
