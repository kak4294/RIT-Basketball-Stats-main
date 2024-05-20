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
    # final dataframe with important info
    final_df = pd.DataFrame()

    # defining constraints of rows that we do not care about
    constraints = get_constraints(csv_df)
    
    # filter dataframe to fit the constraints
    filtered_df = csv_df[constraints]

    # finds key information and puts in
    finds_opponent_site(filtered_df, final_df) # Checked and done
    find_playoutcomes(filtered_df, final_df) 
    find_shottypes(filtered_df, final_df)
    
    # Counts and displays the value count of each shot type
    value_counts = final_df['ShotType'].value_counts(dropna=False)
    print(value_counts)
    print('\n')
    
    # Filter a df to show rows that aren't picking up the shottype.
    condition = final_df['ShotType'].isna()  
    none_df = final_df[condition]
    
    # Prints synergy string in form of list for rows that aren't picking up shottype
    # for index, row in none_df.iterrows():
        # synergy_list = row['Synergy String'].split(' > ')
        # print(synergy_list)
        # print('\n')

    # Print out the selected rows
    # print("Rows that meet the condition:")
    # print(none_df)
    #print('\n')
    
    print(final_df.head())
    print('\n')
    #find_playtype(filtered_df, final_df)



def finds_opponent_site(df: pd.DataFrame, final_df: pd.DataFrame):
    # Finds home and away teams
    away = df['Game'].str[:3]
    home = df['Game'].str[4:]
 
    
    # Finds the site and opponent of the game
    final_df['Site'] = np.where(home == 'RIT', 'Home', 'Away')
    final_df['Opponent'] = np.where(home == 'RIT', away, home)


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
    final_df['Synergy String'] = df['Synergy String']
    
    
def find_playtype():
    pass

def get_constraints(csv_df: pd.DataFrame):
    constraint1 = csv_df['Result'] != "No Violation"
    constraint2 = csv_df['Result'] != "Free Throw"
    constraint3 = csv_df['Result'] != "Run Offense"
    constraint4 = csv_df['Result'] != "Non Shooting Foul"
    constraint5 = csv_df['Result'] != "Kicked Ball"
    return constraint1 & constraint2 & constraint3 & constraint4 & constraint5


if __name__ == "__main__":
    
    #check that file is provided
    if len(sys.argv) < 2:
        print("Usage: python read_csv.py <csv file path_1> <csv file path_2>...")
        sys.exit()
    
    #process csv files given 
    for csv_file in sys.argv[1:]:
        #Process each csv path
        file_path = os.path.join('game_csv', csv_file)

        #turn csv into pandas dataframe
        df = pd.read_csv(file_path, index_col=False)
        
        print(df.head())

        process_plays(df)
     
