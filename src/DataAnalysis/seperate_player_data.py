import pandas as pd
import sys
import os

def combine_and_split_player_data(file_list, output_directory):
    # Create an empty DataFrame to store the combined data
    combined_df = pd.DataFrame()

    # Process each file in the file list
    for file in file_list:
        try:
            # Use the full path for each file
            file = os.path.join(output_directory, file)
            df = pd.read_csv(file)
            if df.empty:
                print(f"Skipping empty file: {file}")
                continue
            df['SourceFile'] = file.split('/')[-1]
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            
        except pd.errors.EmptyDataError:
            print(f"Error: {file} is empty or not formatted correctly. Skipping this file.")
        except FileNotFoundError:
            print(f"Error: {file} not found. Skipping this file.")
        except Exception as e:
            print(f"Unexpected error with file {file}: {e}. Skipping this file.")
            continue

    # Normalize data
    combined_df = combined_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Remove duplicates
    combined_df = combined_df.drop_duplicates()

    # Check for the presence of 'Player', 'PrimaryPlayer', and 'SecondaryPlayer' columns
    if 'Player' in combined_df.columns:
        player_column = 'Player'
        grouped_players = combined_df.groupby(['Team', player_column])
        
        # Export player data to respective CSV files for 'Player' column
        for (team, player), group in grouped_players:
            export_player_data(team, player, group, output_directory)
    
    # Check for the presence of 'PrimaryPlayer' and 'SecondaryPlayer'
    if 'PrimaryPlayer' in combined_df.columns and 'SecondaryPlayer' in combined_df.columns:
        # Process 'PrimaryPlayer' column
        primary_grouped = combined_df.groupby(['Team', 'PrimaryPlayer'])
        
        for (team, player), group in primary_grouped:
            export_player_data(team, player, group, output_directory)
        
        # Process 'SecondaryPlayer' column
        secondary_grouped = combined_df.groupby(['Team', 'SecondaryPlayer'])
        
        for (team, player), group in secondary_grouped:
            export_player_data(team, player, group, output_directory)


def export_player_data(team, player, df, output_directory):
    # Replace spaces and slashes in team and player names with underscores for directory and file naming
    team_directory = team.replace(' ', '_').replace('/', '_')
    player_filename = player.replace(' ', '_') + '.csv'
    
    # Construct the full path for the team's directory
    team_path = os.path.join(output_directory, team_directory)

    # Ensure the team's directory exists
    os.makedirs(team_path, exist_ok=True)  # Creates the directory if it doesn't exist
    
    # Construct the full path for the player's CSV file
    player_file_path = os.path.join(team_path, player_filename)
    
    # Check if the player's file exists
    if os.path.exists(player_file_path):
        # Read the existing data
        existing_df = pd.read_csv(player_file_path)
        # Combine existing data with new data
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        # Remove duplicates while preserving row order
        combined_df = combined_df.drop_duplicates()
    else:
        # If the file doesn't exist, use the new data
        combined_df = df
    
    # Write the combined DataFrame to the CSV file
    combined_df.to_csv(player_file_path, index=False)
    
    # print(f"Exported data for player {player} in team {team} to {player_file_path}")
    

if __name__ == "__main__":
    # Example usage: python seperate_player_data.py file1.csv file2.csv ... output_directory
    if len(sys.argv) < 3:
        print("Usage: python seperate_player_data.py <file1.csv> <file2.csv> ... <output_directory>")
        sys.exit(1)

    # List of input files
    file_list = sys.argv[1:-1]
    
    # Output directory for individual player files (absolute path)
    output_directory = "/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/cleaned/Teams/efficiency_playdata/"

    # Run the function
    combine_and_split_player_data(file_list, output_directory)
