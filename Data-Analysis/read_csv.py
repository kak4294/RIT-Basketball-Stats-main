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
import sys
import os


"""
process_csv: Processes the csv file

"""
def process_plays(csv_df: pd.DataFrame):
    # defining constraints of rows that we do not care about
    constraints = get_constraints(csv_df)
    
    # filter dataframe to fit the constraints
    filtered_df = csv_df[constraints]
    
    # final dataframe with important info
    final_df = pd.DataFrame(index=filtered_df.index, columns=['Site', 'PossesionType', 'Opponent', 'Outcome', 'ShotType', 'PrimaryPlayType', 'PrimaryDirection', 'PrimaryAction', 'SecondaryPlayType', 'SecondaryDirection', 'SecondaryAction'])
    final_df[:] = None

    print(final_df.head())

    # finds key information and puts in
    finds_opponent_site(filtered_df, final_df) # Checked and done
    find_playoutcomes(filtered_df, final_df) 
    find_shottypes(filtered_df, final_df)
    find_playtype(filtered_df, final_df)
    find_offense_defense(filtered_df, final_df)
    
    final_df['PrimaryDirection'].fillna('N/A', inplace=True)
    final_df['PrimaryAction'].fillna('N/A', inplace=True)
    final_df['SecondaryPlayType'].fillna('N/A', inplace=True)
    final_df['SecondaryDirection'].fillna('N/A', inplace=True)
    final_df['SecondaryAction'].fillna('N/A', inplace=True)
    
    pd.set_option('display.max_columns', None)
    print(final_df.isnull().sum())
    print('\n')
    
    return final_df


def finds_opponent_site(df: pd.DataFrame, final_df: pd.DataFrame):
    # Finds home and away teams
    away = df['Game'].apply(lambda x: x[:3] if len(x) == 7 else x[:2])
    home = df['Game'].apply(lambda x: x[4:] if len(x) == 7 else x[3:])
    
    # Finds the site and opponent of the game
    final_df['Site'] = np.where(home == 'RIT', 'Home', 'Away')
    final_df['Opponent'] = np.where(home == 'RIT', away, home)

def find_offense_defense(df: pd.DataFrame, final_df: pd.DataFrame):
    final_df['PossesionType'] = np.where(df['Team'] == 'Rochester Institute of Technology Tigers', 'Offense', 'Defense')
    

def find_playoutcomes(df: pd.DataFrame, final_df: pd.DataFrame):
    # Maps The result column values to their new outcome values
    outcome_mapping = {
        'Foul': 'Foul',
        'Make 2 Pts': '2pMa',
        'Make 3 Pts': '3pMa',
        'Miss 2 Pts': '2pmi',
        'Miss 3 Pts': '3pmi',
        'Turnover': 'Turnover',
        '1 Pts': 'And1'
    }
    final_df['Outcome'] = df['Result'].map(outcome_mapping)


def find_shottypes(df: pd.DataFrame, final_df: pd.DataFrame):
    # Initialize an empty list to store shot types for each row
    shot_types = []

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Split the 'Synergy String' of the current row into a list based on delimiters
        synergy_list = row['Synergy String'].split(' > ')

        #if (row == 8 or row == 55 or row == 63 or row == 76):
        #    print
            
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
    #final_df['Synergy String'] = df['Synergy String']
    
    
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
    elif 'Dribble Move' in playlist:
        final_df.at[idx, action_column] = 'Dribble Move'
            
        

def get_constraints(csv_df: pd.DataFrame):
    constraint1 = csv_df['Result'] != "No Violation"
    constraint2 = csv_df['Result'] != "Free Throw"
    constraint3 = csv_df['Result'] != "Run Offense"
    constraint4 = csv_df['Result'] != "Non Shooting Foul"
    constraint5 = csv_df['Result'] != "Kicked Ball"
    constraint6 = csv_df['Synergy String'].str.contains('Offensive Rebound')
    return constraint1 & constraint2 & constraint3 & constraint4 & constraint5 & ~constraint6


if __name__ == "__main__":
    
    #check that file is provided
    if len(sys.argv) < 2:
        print("Usage: python read_csv.py <csv file path_1> <csv file path_2>...")
        sys.exit()
    
    #process csv files given 
    for csv_file in sys.argv[1:]:
        #Process each csv path
        file_path = os.path.join('Data-Analysis/game_csv', csv_file)

        #turn csv into pandas dataframe
        df = pd.read_csv(file_path, index_col=False)
        
        print(df.head())

        final_df = process_plays(df)
        file_name = 'cleaned_' + csv_file
        final_df.to_csv('Data-Analysis/RIT_clean_csv/' + file_name, encoding='utf-8', index=False)
     
