import pandas as pd
import sys
import os

#   Run in Terminal in order get all data seperated.
#   python seperate_team_offense_data.py player_cut_basket_efficiency.csv player_cut_efficiency.csv player_cut_flash_efficiency.csv player_cut_screen_efficiency.csv player_handoffs_bhleft_dribble_efficiency.csv player_handoffs_bhleft_efficiency.csv player_handoffs_bhleft_stationary_efficiency.csv player_handoffs_bhright_dribble_efficiency.csv player_handoffs_bhright_efficiency.csv player_handoffs_bhright_stationary_efficiency.csv player_handoffs_dribble_efficiency.csv player_handoffs_efficiency.csv player_handoffs_stationary_efficiency.csv player_handoffs_top_dribble_efficiency.csv player_handoffs_top_efficiency.csv player_handoffs_top_stationary_efficiency.csv player_iso_efficiency.csv player_iso_left_efficiency.csv player_iso_right_efficiency.csv player_iso_top_efficiency.csv player_misc_efficiency.csv player_offscreens_curl_efficiency.csv player_offscreens_efficiency.csv player_offscreens_flare_efficiency.csv player_offscreens_leftshoulder_curl_efficiency.csv player_offscreens_leftshoulder_efficiency.csv player_offscreens_leftshoulder_straight_efficiency.csv player_offscreens_rightshoulder_curl_efficiency.csv player_offscreens_rightshoulder_efficiency.csv player_offscreens_rightshoulder_flare_efficiency.csv player_offscreens_rightshoulder_straight_efficiency.csv player_offscreens_straight_efficiency.csv player_pnr_bhhigh_efficiency.csv player_pnr_bhhigh_offpick_efficiency.csv player_pnr_bhhigh_rejectpick_efficiency.csv player_pnr_bhleft_efficiency.csv player_pnr_bhleft_offpick_efficiency.csv player_pnr_bhleft_rejectpick_efficiency.csv player_pnr_bhright_efficiency.csv player_pnr_bhright_offpick_efficiency.csv player_pnr_bhright_rejectpick_efficiency.csv player_pnr_efficiency.csv player_pnr_offpick_efficiency.csv player_pnr_rejectpick_efficiency.csv player_post_efficiency.csv player_post_faceup_efficiency.csv player_post_leftblock_efficiency.csv player_post_leftblock_faceup_efficiency.csv player_post_leftblock_leftshoulder_efficiency.csv player_post_leftblock_rightshoulder_efficiency.csv player_post_leftshoulder_efficiency.csv player_post_middle_efficiency.csv player_post_middle_faceup_efficiency.csv player_post_middle_leftshoulder_efficiency.csv player_post_middle_rightshoulder_efficiency.csv player_post_rightblock_efficiency.csv player_post_rightblock_faceup_efficiency.csv player_post_rightblock_leftshoulder_efficiency.csv player_post_rightblock_rightshoulder_efficiency.csv player_post_rightshoulder_efficiency.csv player_rollman_efficiency.csv player_rollman_leftdrive_efficiency.csv player_rollman_leftdrive_pop_efficiency.csv player_rollman_leftdrive_slip_efficiency.csv player_rollman_pop_efficiency.csv player_rollman_rightdrive_efficiency.csv player_rollman_rightdrive_pop_efficiency.csv player_rollman_rightdrive_slip_efficiency.csv player_rollman_roll_efficiency.csv player_rollman_slip_efficiency.csv player_spotup_drive_efficiency.csv player_spotup_efficiency.csv player_spotup_jumpshot_efficiency.csv player_spotup_leftdrive_efficiency.csv player_spotup_rightdrive_efficiency.csv player_spotup_straightdrive_efficiency.csv player_transition_bh_efficiency.csv player_transition_leakouts_efficiency.csv player_transition_leftwing_efficiency.csv player_transition_rightwing_efficiency.csv player_transition_trailer_efficiency.csv playerefficiency.csv playerefficiencyleft.csv playerefficiencyright.csv twoplayer_bhhigh_rollmanpops_efficiency.csv twoplayer_iso_cut_efficiency.csv twoplayer_iso_spotupdrives_efficiency.csv twoplayer_iso_spotupjumpers_efficiency.csv twoplayer_pnr_cut_efficiency.csv twoplayer_pnr_spotupdrives_efficiency.csv twoplayer_pnr_spotupsdrives_efficiency.csv twoplayer_pnr_spotupsjumpers_efficiency.csv twoplayer_pnrbhhigh_cuts_efficiency.csv twoplayer_pnrbhhigh_rollman_efficiency.csv twoplayer_pnrbhhigh_rollmanpops_efficiency.csv twoplayer_pnrbhhigh_rollmanrolls_efficiency.csv twoplayer_pnrbhhigh_rollmanslips_efficiency.csv twoplayer_pnrbhhigh_spotupdrives_efficiency.csv twoplayer_pnrbhhigh_spotupjumper_efficiency.csv twoplayer_pnrbhleft_cuts_efficiency.csv twoplayer_pnrbhleft_rollman_efficiency.csv twoplayer_pnrbhleft_rollmanpops_efficiency.csv twoplayer_pnrbhleft_rollmanrolls_efficiency.csv twoplayer_pnrbhleft_rollmanslips_efficiency.csv twoplayer_pnrbhleft_spotupdrives_efficiency.csv twoplayer_pnrbhleft_spotupjumper_efficiency.csv twoplayer_pnrbhright_cuts_efficiency.csv twoplayer_pnrbhright_rollman_efficiency.csv twoplayer_pnrbhright_rollmanpops_efficiency.csv twoplayer_pnrbhright_rollmanrolls_efficiency.csv twoplayer_pnrbhright_rollmanslips_efficiency.csv twoplayer_pnrbhright_spotupdrives_efficiency.csv twoplayer_pnrbhright_spotupjumper_efficiency.csv twoplayer_post_cut_efficiency.csv twoplayer_post_spotupdrive_efficiency.csv twoplayer_post_spotupjumper_efficiency.csv team_offense_data

def combine_and_split_team_data(file_list, output_directory, input_directory):
    # Create an empty DataFrame to store the combined data
    combined_df = pd.DataFrame()

    # Process each file in the file list
    for file in file_list:
        try:
            # Use the full path for each file
            file_path = os.path.join(input_directory, file)
            df = pd.read_csv(file_path)
            if df.empty:
                print(f"Skipping empty file: {file_path}")
                continue
            df['SourceFile'] = os.path.basename(file_path)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            
        except pd.errors.EmptyDataError:
            print(f"Error: {file_path} is empty or not formatted correctly. Skipping this file.")
        except FileNotFoundError:
            print(f"Error: {file_path} not found. Skipping this file.")
        except Exception as e:
            print(f"Unexpected error with file {file_path}: {e}. Skipping this file.")
            continue

    # Normalize data: Strip whitespace from string columns
    combined_df = combined_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Remove duplicate rows
    combined_df = combined_df.drop_duplicates()

    # Check for the presence of 'Team' column
    if 'Team' not in combined_df.columns:
        print("Error: 'Team' column not found in the combined data.")
        sys.exit(1)

    # Group the data by 'Team'
    grouped_teams = combined_df.groupby('Team')

    # Export each team's data to a separate CSV file
    for team, group in grouped_teams:
        export_team_data(team, group, output_directory)

def export_team_data(team, df, output_directory):
    # Replace spaces and slashes in team names with underscores for file naming
    safe_team_name = team.replace(' ', '_').replace('/', '_')
    team_filename = f"{safe_team_name}.csv"
    
    # Construct the full path for the team's CSV file
    team_file_path = os.path.join(output_directory, team_filename)
    
    # Check if the team's file exists
    if os.path.exists(team_file_path):
        # Read the existing data
        existing_df = pd.read_csv(team_file_path)
        # Combine existing data with new data
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        # Remove duplicates while preserving row order
        combined_df = combined_df.drop_duplicates()
    else:
        # If the file doesn't exist, use the new data
        combined_df = df
    
    # Write the combined DataFrame to the CSV file
    combined_df.to_csv(team_file_path, index=False)
    
    print(f"Exported data for team '{team}' to {team_file_path}")

if __name__ == "__main__":
    # Example usage: python separate_team_data.py file1.csv file2.csv ... output_directory
    if len(sys.argv) < 3:
        print("Usage: python separate_team_data.py <file1.csv> <file2.csv> ... <output_directory>")
        sys.exit(1)

    # List of input files
    file_list = sys.argv[1:-1]
    
    # Output directory for individual team files (absolute path)
    output_directory = "/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/cleaned/Teams/team_offense_data/"
    
    # Input Directory
    input_directory = "/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/cleaned/Teams/efficiency_playdata/"

    # Optional: Verify that the output directory exists
    if not os.path.isdir(input_directory):
        print(f"Error: The output directory '{input_directory}' does not exist.")
        sys.exit(1)

    # Run the function
    combine_and_split_team_data(file_list, output_directory, input_directory)
