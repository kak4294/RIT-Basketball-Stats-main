import pandas as pd
import sys
import os

#   Run in Terminal in order get all data seperated.
#   python seperate_player_data.py player_cut_basket_efficiency.csv player_cut_efficiency.csv player_cut_flash_efficiency.csv player_cut_screen_efficiency.csv player_handoffs_bhleft_dribble_efficiency.csv player_handoffs_bhleft_efficiency.csv player_handoffs_bhleft_stationary_efficiency.csv player_handoffs_bhright_dribble_efficiency.csv player_handoffs_bhright_efficiency.csv player_handoffs_bhright_stationary_efficiency.csv player_handoffs_dribble_efficiency.csv player_handoffs_efficiency.csv player_handoffs_stationary_efficiency.csv player_handoffs_top_dribble_efficiency.csv player_handoffs_top_efficiency.csv player_handoffs_top_stationary_efficiency.csv player_iso_efficiency.csv player_iso_left_efficiency.csv player_iso_right_efficiency.csv player_iso_top_efficiency.csv player_misc_efficiency.csv player_offscreens_curl_efficiency.csv player_offscreens_efficiency.csv player_offscreens_flare_efficiency.csv player_offscreens_leftshoulder_curl_efficiency.csv player_offscreens_leftshoulder_efficiency.csv player_offscreens_leftshoulder_straight_efficiency.csv player_offscreens_rightshoulder_curl_efficiency.csv player_offscreens_rightshoulder_efficiency.csv player_offscreens_rightshoulder_flare_efficiency.csv player_offscreens_rightshoulder_straight_efficiency.csv player_offscreens_straight_efficiency.csv player_pnr_bhhigh_efficiency.csv player_pnr_bhhigh_offpick_efficiency.csv player_pnr_bhhigh_rejectpick_efficiency.csv player_pnr_bhleft_efficiency.csv player_pnr_bhleft_offpick_efficiency.csv player_pnr_bhleft_rejectpick_efficiency.csv player_pnr_bhright_efficiency.csv player_pnr_bhright_offpick_efficiency.csv player_pnr_bhright_rejectpick_efficiency.csv player_pnr_efficiency.csv player_pnr_offpick_efficiency.csv player_pnr_rejectpick_efficiency.csv player_post_efficiency.csv player_post_faceup_efficiency.csv player_post_leftblock_efficiency.csv player_post_leftblock_faceup_efficiency.csv player_post_leftblock_leftshoulder_efficiency.csv player_post_leftblock_rightshoulder_efficiency.csv player_post_leftshoulder_efficiency.csv player_post_middle_efficiency.csv player_post_middle_faceup_efficiency.csv player_post_middle_leftshoulder_efficiency.csv player_post_middle_rightshoulder_efficiency.csv player_post_rightblock_efficiency.csv player_post_rightblock_faceup_efficiency.csv player_post_rightblock_leftshoulder_efficiency.csv player_post_rightblock_rightshoulder_efficiency.csv player_post_rightshoulder_efficiency.csv player_rollman_efficiency.csv player_rollman_leftdrive_efficiency.csv player_rollman_leftdrive_pop_efficiency.csv player_rollman_leftdrive_slip_efficiency.csv player_rollman_pop_efficiency.csv player_rollman_rightdrive_efficiency.csv player_rollman_rightdrive_pop_efficiency.csv player_rollman_rightdrive_slip_efficiency.csv player_rollman_roll_efficiency.csv player_rollman_slip_efficiency.csv player_spotup_drive_efficiency.csv player_spotup_efficiency.csv player_spotup_jumpshot_efficiency.csv player_spotup_leftdrive_efficiency.csv player_spotup_rightdrive_efficiency.csv player_spotup_straightdrive_efficiency.csv player_transition_bh_efficiency.csv player_transition_leakouts_efficiency.csv player_transition_leftwing_efficiency.csv player_transition_rightwing_efficiency.csv player_transition_trailer_efficiency.csv playerefficiency.csv playerefficiencyleft.csv playerefficiencyright.csv twoplayer_bhhigh_rollmanpops_efficiency.csv twoplayer_iso_cut_efficiency.csv twoplayer_iso_spotupdrives_efficiency.csv twoplayer_iso_spotupjumpers_efficiency.csv twoplayer_pnr_cut_efficiency.csv twoplayer_pnr_spotupdrives_efficiency.csv twoplayer_pnr_spotupsdrives_efficiency.csv twoplayer_pnr_spotupsjumpers_efficiency.csv twoplayer_pnrbhhigh_cuts_efficiency.csv twoplayer_pnrbhhigh_rollman_efficiency.csv twoplayer_pnrbhhigh_rollmanpops_efficiency.csv twoplayer_pnrbhhigh_rollmanrolls_efficiency.csv twoplayer_pnrbhhigh_rollmanslips_efficiency.csv twoplayer_pnrbhhigh_spotupdrives_efficiency.csv twoplayer_pnrbhhigh_spotupjumper_efficiency.csv twoplayer_pnrbhleft_cuts_efficiency.csv twoplayer_pnrbhleft_rollman_efficiency.csv twoplayer_pnrbhleft_rollmanpops_efficiency.csv twoplayer_pnrbhleft_rollmanrolls_efficiency.csv twoplayer_pnrbhleft_rollmanslips_efficiency.csv twoplayer_pnrbhleft_spotupdrives_efficiency.csv twoplayer_pnrbhleft_spotupjumper_efficiency.csv twoplayer_pnrbhright_cuts_efficiency.csv twoplayer_pnrbhright_rollman_efficiency.csv twoplayer_pnrbhright_rollmanpops_efficiency.csv twoplayer_pnrbhright_rollmanrolls_efficiency.csv twoplayer_pnrbhright_rollmanslips_efficiency.csv twoplayer_pnrbhright_spotupdrives_efficiency.csv twoplayer_pnrbhright_spotupjumper_efficiency.csv twoplayer_post_cut_efficiency.csv twoplayer_post_spotupdrive_efficiency.csv twoplayer_post_spotupjumper_efficiency.csv player_data

def combine_and_split_player_data(file_list, output_directory):
    # Create an empty DataFrame to store the combined data
    combined_df = pd.DataFrame()

    # Process each file in the file list
    for file in file_list:
        try:
            # Correct the file name
            file = "efficiency_playdata/" + file
            
            # Load the CSV file into a DataFrame
            df = pd.read_csv(file)
            
            # Skip if the DataFrame is empty
            if df.empty:
                print(f"Skipping empty file: {file}")
                continue
            
            # Add a new column to the DataFrame with the name of the source file
            df['SourceFile'] = file.split('/')[-1]  # Extracting file name from the path
            
            # Concatenate the data from the current file with the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        except pd.errors.EmptyDataError:
            print(f"Error: {file} is empty or not formatted correctly. Skipping this file.")
        except FileNotFoundError:
            print(f"Error: {file} not found. Skipping this file.")
        except Exception as e:
            print(f"Unexpected error with file {file}: {e}. Skipping this file.")
            continue

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
            
    # After exporting, remove duplicates in all player CSV files in the output directory
    remove_duplicates_from_all_csvs(output_directory)


def export_player_data(team, player, group, output_directory):
    # Replace spaces and slashes in team and player names with underscores for directory and file naming
    team_directory = team.replace(' ', '_').replace('/', '_')
    player_filename = player.replace(' ', '_') + '.csv'
    
    # Construct the full path for the team's directory
    team_path = os.path.join(output_directory, team_directory)

    # Ensure the team's directory exists
    os.makedirs(team_path, exist_ok=True)  # Creates the directory if it doesn't exist
    
    # Construct the full path for the player's CSV file
    player_file_path = os.path.join(team_path, player_filename)
    
    # Append to the player's CSV file if it exists, otherwise create a new one
    if os.path.exists(player_file_path):
        group.to_csv(player_file_path, mode='a', header=False, index=False)
    else:
        group.to_csv(player_file_path, index=False)

    # print(f"Exported data for player {player} in team {team} to {player_file_path}")
    
    
# Function to remove duplicates from all CSV files in the output directory
def remove_duplicates_from_all_csvs(output_directory):
    # Traverse all subdirectories in the output directory
    for root, _, files in os.walk(output_directory):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                remove_duplicates_from_csv(file_path)


# Function to remove duplicate rows from a CSV file
def remove_duplicates_from_csv(file_path):
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Drop duplicate rows based on all columns
        df_cleaned = df.drop_duplicates()
        
        # Save the cleaned DataFrame back to the original file
        df_cleaned.to_csv(file_path, index=False)
        
        print(f"Duplicates removed and file saved at {file_path}")
    
    except pd.errors.EmptyDataError:
        print(f"Error: {file_path} is empty or not formatted correctly.")
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    except Exception as e:
        print(f"Unexpected error with file {file_path}: {e}")
    


if __name__ == "__main__":
    # Example usage: python seperate_player_data.py file1.csv file2.csv ... output_directory
    if len(sys.argv) < 3:
        print("Usage: python seperate_player_data.py <file1.csv> <file2.csv> ... <output_directory>")
        sys.exit(1)

    # List of input files
    file_list = sys.argv[1:-1]
    
    # Output directory for individual player files
    output_directory = sys.argv[-1] + "/"

    # Run the function
    combine_and_split_player_data(file_list, output_directory)