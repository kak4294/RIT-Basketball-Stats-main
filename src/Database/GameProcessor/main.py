import os
from clean_csv import run_clean_csv
from split_gamedata_by_team import split_row_by_team
from csv_to_database import transfer_games_to_db
from csv_to_database import transfer_plays_to_db
from process_games import df_to_csv_file
import shutil


if __name__ == '__main__':
    directory = "/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/raw/unsaved_games"
    for filename in os.listdir(directory):
        # Handles .DS_Store
        if 'DS_Store' in filename:
            continue 
        
        # Cleans csv and creates a copy
        final_df, team1, team2, date, play_not_counted, t1score, t2score, game_df = run_clean_csv(filename)
        
        if play_not_counted:
            output = input(f'Check score for {team1} vs {team2} on {date}\n\
                Does this score look correct\n\
                {team1}: {t1score}\n\
                {team2}: {t2score}\n\
                [ y/n ]: ')
            if output == 'n':
                print('Okay input new scores')
                t1score = input(f'{team1}: ')
                t2score = input(f'{team2}: ')
        
        # Updates scores if neccesary and moves to unprocessed games csv file
        df_to_csv_file(game_df, t1score, t2score)
                
        # Creates a new file with clean play data into seperate folder
        clean_file_name = 'cleaned_' + filename
        cleaned_file_path = os.path.join('/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/cleaned/cleaned_game_csv/game_csv', clean_file_name)
        final_df.to_csv(cleaned_file_path, encoding='utf-8', index=False)
        
        # Transfers play-by-play statistics into actual database
        transfer_plays_to_db(cleaned_file_path)
        
        # Adds team stats to database
        split_directory = '/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/cleaned/cleaned_game_csv/unprocessed_games.csv'
        split_row_by_team(split_directory, team1, team2, date)
        
        # Moves files to a saved location once they are in the database
        source = os.path.join("/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/raw/unsaved_games", filename)
        destination = os.path.join("/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/raw/saved_games", filename)
        shutil.move(source, destination)
        print(f'{filename} was proccessed and added to database.\n')