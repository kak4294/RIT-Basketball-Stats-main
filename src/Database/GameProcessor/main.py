import os
from clean_csv import run_clean_csv

if __name__ == '__main__':
    directory = "/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2024_25/raw/unsaved_games"
    for filename in os.listdir(directory):
        run_clean_csv(filename)
        print(f'{filename} was proccessed and added to database.\n')