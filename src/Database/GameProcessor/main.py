import os
from clean_csv import run_clean_csv
from split_gamedata_by_team import split_row_by_team

if __name__ == '__main__':
    directory = "/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/raw/unsaved_games"
    for filename in os.listdir(directory):
        run_clean_csv(filename)
        print(f'{filename} was proccessed and added to database.\n')
    directory = '/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/cleaned/cleaned_game_csv/unprocessed_games.csv'
    split_row_by_team(directory)