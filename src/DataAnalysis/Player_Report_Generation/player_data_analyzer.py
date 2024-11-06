import pandas as pd
import sys
import os
import json
from datetime import datetime
import math
from visual_generator import create_bar_chart

def analyze_player_performance(file, output_directory):
    """
    Analyzes player performance and categorizes insights.

    Args:
        file (str): Path to the player data CSV file.
        output_directory (str): Directory to save output files.

    Returns:
        dict: A dictionary containing categorized insights.
    """
    # Split player data by role
    primary_df, secondary_df, scorer_df, player_name = split_player_data_by_role(file)
    
    # Initialize insight lists for different categories
    insights = {
        "PNR_insights": [],
        "Cut_insights": [],
        "Handoff_insights": [],
        "Post_insights": [],
        "Spotup_insights": [],
        "Transition_insights": [],
        "Offscreen_insights": [],
        "Iso_insights": [],
        "Rollman_insights": []
    }
    
    # Process insights for primary, secondary, and scorer roles
    process_primary_stats(primary_df, player_name, insights, output_directory)
    # Merge secondary and scorer_df for spotup secondary function
    secondary_df = pd.concat([secondary_df, scorer_df], ignore_index=True)
    process_secondary_stats(secondary_df, player_name, insights, output_directory)
    process_scorer_stats(scorer_df, player_name, insights, output_directory)
    
    return insights
        
def split_player_data_by_role(file_name):
    # Extract the player's name from the file path (assumes format "PlayerName.csv")
    player_name = os.path.basename(file_name).replace('.csv', '').replace('_', ' ')

    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_name)

    # Filter rows where the player is the primary player
    primary_player_df = df[df['PrimaryPlayer'] == player_name]

    # Filter rows where the player is the secondary player
    secondary_player_df = df[df['SecondaryPlayer'] == player_name]

    # Filter rows where the player is the player (scorer)
    scorer_df = df[df['Player'] == player_name]

    return primary_player_df, secondary_player_df, scorer_df, player_name       

def write_insights_to_json(insights, output_file):
    """
    Writes the insights dictionary to a JSON file.

    Args:
        insights (dict): A dictionary containing categorized insights.
        output_file (str): The path to the output JSON file.
    """
    with open(output_file, 'w') as output:
        json.dump(insights, output, indent=4)
    print(f"Insights successfully written to {output_file}")

def process_primary_stats(df: pd.DataFrame, name, insights, output_directory):
    # Iterate through the types of insights
    for key in insights:
        if key == 'PNR_insights':  # PNR insights
            PNR_passer_stats(df, name, insights[key], output_directory)
        elif key == 'Iso_insights':  # Iso insights
            Iso_passer_stats(df, name, insights[key], output_directory)
        elif key == 'Post_insights':  # Post insights
            Post_passer_stats(df, name, insights[key], output_directory)

def PNR_passer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Calculates total passing proportion and efficiency for secondary plays out of a pick n roll
    total_passing_proport_csvs = ['twoplayer_pnr_cut_efficiency.csv', 'twoplayer_pnr_spotupsdrives_efficiency.csv', 'twoplayer_pnr_spotupsjumpers_efficiency.csv', 'player_rollman_efficiency.csv' ]
    filtered_df1 = df[(df['SourceFile'].isin(total_passing_proport_csvs)) & (df['PrimaryPlayer'] == name)]
    total_passing_proportion = find_play_proportions(filtered_df1, total_passing_proport_csvs)
    total_passing_proportion_dict = {
        'PNR - Cut': total_passing_proportion[0], 
        'PNR - Spotup Drive': total_passing_proportion[1],
        'PNR - Spotup Jumper': total_passing_proportion[2], 
        'PNR - Rollman': total_passing_proportion[3], 
        'Total Plays': total_passing_proportion[4]
    }
    
    filtered_df = df [ (df['SourceFile'] == 'twoplayer_pnr_cut_efficiency.csv') ]
    pnr_cut_efficiency = compute_grouped_statistics(filtered_df, 'PNR-->Cut.', 'PrimaryPlayer', 'PNR_Cut')
    
    filtered_df = df [ (df['SourceFile'] == 'twoplayer_pnr_spotupsdrives_efficiency.csv') ]
    pnr_sudrive_efficiency = compute_grouped_statistics(filtered_df, 'PNR-->SU Drive.', 'PrimaryPlayer', 'PNR_SpotupDrive')
    
    filtered_df = df [ (df['SourceFile'] == 'twoplayer_pnr_spotupsjumpers_efficiency.csv') ]
    pnr_sujumper_efficiency = compute_grouped_statistics(filtered_df, 'PNR-->SU Jumper.', 'PrimaryPlayer', 'PNR_SpotupJumper')
    
    filtered_df = df [ (df['SourceFile'] == 'player_rollman_efficiency.csv') ]
    pnr_rollman_efficiency = compute_grouped_statistics(filtered_df, 'PNR-->Rollman.', 'PrimaryPlayer', 'PNR_Rollman')
    
    
    # Creates PNR Pass -> Playtype Visual
    selected_keys = ['PNR - Cut', 'PNR - Spotup Drive', 'PNR - Spotup Jumper', 'PNR - Rollman']
    total_plays = total_passing_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_passing_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'PNR_PassPlayType_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=2,
        y_max=50,
        title='PNR Pass to Play Type Frequency',
        output_filename=output_file_path
    )
    
    total_passing_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all PNR secondary plays together.', 'PrimaryPlayer', 'PNR_Passer')
    
    # Extend the current insight list
    insight.extend([
        total_passing_proportion_dict, 
        total_passing_efficiency,
        pnr_cut_efficiency,
        pnr_sudrive_efficiency,
        pnr_sujumper_efficiency,
        pnr_rollman_efficiency
    ])
    
    # Additional insights for left, right, and high PNRs
    PNR_bhhigh_passer_stats(df, name, insight, output_directory)
    PNR_bhleft_passer_stats(df, name, insight, output_directory)
    PNR_bhright_passer_stats(df, name, insight, output_directory)

def PNR_bhhigh_passer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Calculates proportion and efficiency for various PNR plays (cutters, spot-up drivers, rollman, etc.)
    
    # Cutters off high pick n roll
    bhhighpassing_cut_csv = ['twoplayer_pnrbhhigh_cuts_efficiency.csv']
    filtered_df5 = df[(df['SourceFile'].isin(bhhighpassing_cut_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_cut_player_proportion = find_player_proportions(filtered_df5, bhhighpassing_cut_csv, 'SecondaryPlayer')
    player_dict = {}
    for player in bhhighpassing_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df5, bhhighpassing_cut_csv, player, bhhighpassing_cut_player_proportion[player], 'SecondaryPlayer' )
        bhhighpassing_cut_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
    outer_dict1 = {'BHHighPNRCuts': bhhighpassing_cut_player_proportion}
    insight.extend([outer_dict1])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassHighCutsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH High to Cuts By Cutter',
        output_filename=output_file_path
    )

    # Spot-up drivers off high pick n roll
    bhhighpassing_spotupdrives_csv = ['twoplayer_pnrbhhigh_spotupdrives_efficiency.csv']
    filtered_df6 = df[(df['SourceFile'].isin(bhhighpassing_spotupdrives_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_spotupdrives_player_proportion = find_player_proportions(filtered_df6, bhhighpassing_spotupdrives_csv, 'SecondaryPlayer')
    player_dict = {}
    
    for player in bhhighpassing_spotupdrives_player_proportion:
        player_data = find_player_efficiency(filtered_df6, bhhighpassing_spotupdrives_csv, player, bhhighpassing_spotupdrives_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_spotupdrives_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict2 = {'BHHighPNRSpotupDrives': bhhighpassing_spotupdrives_player_proportion}
    insight.extend([outer_dict2])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassHighDrivesPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH High to Spot Up Drives By Shooter',
        output_filename=output_file_path
    )

    # Spot-up shooters off high pick n roll
    bhhighpassing_spotupjumpers_csv = ['twoplayer_pnrbhhigh_spotupjumper_efficiency.csv']
    filtered_df7 = df[(df['SourceFile'].isin(bhhighpassing_spotupjumpers_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_spotupjumpers_player_proportion = find_player_proportions(filtered_df7, bhhighpassing_spotupjumpers_csv, 'SecondaryPlayer')

    player_dict = {}
    for player in bhhighpassing_spotupjumpers_player_proportion:
        player_data = find_player_efficiency(filtered_df7, bhhighpassing_spotupjumpers_csv, player, bhhighpassing_spotupjumpers_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_spotupjumpers_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict3 = {'BHHighPNRSpotupJumpers': bhhighpassing_spotupjumpers_player_proportion}
    insight.extend([outer_dict3])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassHighShotsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH High to Spot Up Shots By Shooter',
        output_filename=output_file_path
    )
    

    # Rollman rolling off high pick n roll
    bhhighpassing_rollmanrolls_csv = ['twoplayer_pnrbhhigh_rollmanrolls_efficiency.csv']
    filtered_df8 = df[(df['SourceFile'].isin(bhhighpassing_rollmanrolls_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_rollmanrolls_player_proportion = find_player_proportions(filtered_df8, bhhighpassing_rollmanrolls_csv, 'SecondaryPlayer')

    player_dict = {}
    for player in bhhighpassing_rollmanrolls_player_proportion:
        player_data = find_player_efficiency(filtered_df8, bhhighpassing_rollmanrolls_csv, player, bhhighpassing_rollmanrolls_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_rollmanrolls_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict4 = {'BHHighPNRRollmanRolls': bhhighpassing_rollmanrolls_player_proportion}
    insight.extend([outer_dict4])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassHighRollsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH High to Rollman Rolling By Shooter',
        output_filename=output_file_path
    )

    # Rollman slips off high pick n roll
    bhhighpassing_rollmanslips_csv = ['twoplayer_pnrbhhigh_rollmanslips_efficiency.csv']
    filtered_df9 = df[(df['SourceFile'].isin(bhhighpassing_rollmanslips_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_rollmanslips_player_proportion = find_player_proportions(filtered_df9, bhhighpassing_rollmanslips_csv, 'SecondaryPlayer')

    player_dict = {}
    for player in bhhighpassing_rollmanslips_player_proportion:
        player_data = find_player_efficiency(filtered_df9, bhhighpassing_rollmanslips_csv, player, bhhighpassing_rollmanslips_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_rollmanslips_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict5 = {'BHHighPNRRollmanSlips': bhhighpassing_rollmanslips_player_proportion}
    insight.extend([outer_dict5])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassHighSlipsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH High to Rollman Slipping By Shooter',
        output_filename=output_file_path
    )

    # Rollman pops off high pick n roll
    bhhighpassing_rollmanpops_csv = ['twoplayer_pnrbhhigh_rollmanpops_efficiency.csv']
    filtered_df10 = df[(df['SourceFile'].isin(bhhighpassing_rollmanpops_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_rollmanpops_player_proportion = find_player_proportions(filtered_df10, bhhighpassing_rollmanpops_csv, 'SecondaryPlayer')

    player_dict = {}
    for player in bhhighpassing_rollmanpops_player_proportion:
        player_data = find_player_efficiency(filtered_df10, bhhighpassing_rollmanpops_csv, player, bhhighpassing_rollmanpops_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_rollmanpops_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict6 = {'BHHighPNRRollmanPops': bhhighpassing_rollmanpops_player_proportion}
    insight.extend([outer_dict6])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassHighPopsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH High to Rollman Popping By Shooter',
        output_filename=output_file_path
    )

def PNR_bhleft_passer_stats(df: pd.DataFrame, name, insight, output_directory):  
    # Calculates proportion and efficiency of a player hitting a specific second player (cutter) off of a high pick n roll
    pnrpasser_cut_csv = ['twoplayer_pnrbhleft_cuts_efficiency.csv']
    filtered_df1 = df[(df['SourceFile'].isin(pnrpasser_cut_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_cut_player_proportion = find_player_proportions(filtered_df1, pnrpasser_cut_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df1, pnrpasser_cut_csv, player, pnrpasser_cut_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_cut_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict1 = {'BHLeftPNRCuts': pnrpasser_cut_player_proportion}
    insight.extend([outer_dict1])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassLeftCutsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Left to Cuts by Cutter',
        output_filename=output_file_path
    )

    # Spot up drivers
    pnrpasser_spotupdrives_csv = ['twoplayer_pnrbhleft_spotupdrives_efficiency.csv']
    filtered_df2 = df[(df['SourceFile'].isin(pnrpasser_spotupdrives_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_spotupdrives_player_proportion = find_player_proportions(filtered_df2, pnrpasser_spotupdrives_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_spotupdrives_player_proportion:
        player_data = find_player_efficiency(filtered_df2, pnrpasser_spotupdrives_csv, player, pnrpasser_spotupdrives_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_spotupdrives_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict2 = {'BHLeftPNRSpotupDrives': pnrpasser_spotupdrives_player_proportion}
    insight.extend([outer_dict2])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassLeftDrivesPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Left to Spot Up Drives by Shooter',
        output_filename=output_file_path
    )

    # Spot up jumpers
    pnrpasser_spotupjumper_csv = ['twoplayer_pnrbhleft_spotupjumper_efficiency.csv']
    filtered_df3 = df[(df['SourceFile'].isin(pnrpasser_spotupjumper_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_spotupjumper_player_proportion = find_player_proportions(filtered_df3, pnrpasser_spotupjumper_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_spotupjumper_player_proportion:
        player_data = find_player_efficiency(filtered_df3, pnrpasser_spotupjumper_csv, player, pnrpasser_spotupjumper_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_spotupjumper_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict3 = {'BHLeftPNRSpotupJumpers': pnrpasser_spotupjumper_player_proportion}
    insight.extend([outer_dict3])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassLeftShotsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Left to Spot Up Jumper by Shooter',
        output_filename=output_file_path
    )

    # Rollman rolls
    pnrpasser_rollmanrolls_csv = ['twoplayer_pnrbhleft_rollmanrolls_efficiency.csv']
    filtered_df4 = df[(df['SourceFile'].isin(pnrpasser_rollmanrolls_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanrolls_player_proportion = find_player_proportions(filtered_df4, pnrpasser_rollmanrolls_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_rollmanrolls_player_proportion:
        player_data = find_player_efficiency(filtered_df4, pnrpasser_rollmanrolls_csv, player, pnrpasser_rollmanrolls_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanrolls_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict4 = {'BHLeftPNRRollmanRolls': pnrpasser_rollmanrolls_player_proportion}
    insight.extend([outer_dict4])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassLeftRollsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Left to Rollman Rolling by Shooter',
        output_filename=output_file_path
    )

    # Rollman slips
    pnrpasser_rollmanslips_csv = ['twoplayer_pnrbhleft_rollmanslips_efficiency.csv']
    filtered_df5 = df[(df['SourceFile'].isin(pnrpasser_rollmanslips_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanslips_player_proportion = find_player_proportions(filtered_df5, pnrpasser_rollmanslips_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_rollmanslips_player_proportion:
        player_data = find_player_efficiency(filtered_df5, pnrpasser_rollmanrolls_csv, player, pnrpasser_rollmanslips_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanslips_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict5 = {'BHLeftPNRRollmanSlips': pnrpasser_rollmanslips_player_proportion}
    insight.extend([outer_dict5])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassLeftSlipsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Left to Rollman Slips by Rollman',
        output_filename=output_file_path
    )

    # Rollman pops
    pnrpasser_rollmanpops_csv = ['twoplayer_pnrbhleft_rollmanpops_efficiency.csv']
    filtered_df6 = df[(df['SourceFile'].isin(pnrpasser_rollmanpops_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanpops_player_proportion = find_player_proportions(filtered_df6, pnrpasser_rollmanpops_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_rollmanpops_player_proportion:
        player_data = find_player_efficiency(filtered_df6, pnrpasser_rollmanpops_csv, player, pnrpasser_rollmanpops_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanpops_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict6 = {'BHLeftPNRRollmanPops': pnrpasser_rollmanpops_player_proportion}
    insight.extend([outer_dict6])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassLeftPopsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Left to Rollman Popping by Shooter',
        output_filename=output_file_path
    )

def PNR_bhright_passer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Calculates proportion and efficiency of a player hitting a specific second player (cutter) off of a high pick n roll
    pnrpasser_cut_csv = ['twoplayer_pnrbhright_cuts_efficiency.csv']
    filtered_df1 = df[(df['SourceFile'].isin(pnrpasser_cut_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_cut_player_proportion = find_player_proportions(filtered_df1, pnrpasser_cut_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df1, pnrpasser_cut_csv, player, pnrpasser_cut_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_cut_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict1 = {'BHRightPNRCuts': pnrpasser_cut_player_proportion}
    insight.extend([outer_dict1])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassRightCutsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Right to Cuts by Cutter',
        output_filename=output_file_path
    )

    # Spot up drivers
    pnrpasser_spotupdrives_csv = ['twoplayer_pnrbhright_spotupdrives_efficiency.csv']
    filtered_df2 = df[(df['SourceFile'].isin(pnrpasser_spotupdrives_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_spotupdrives_player_proportion = find_player_proportions(filtered_df2, pnrpasser_spotupdrives_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_spotupdrives_player_proportion:
        player_data = find_player_efficiency(filtered_df2, pnrpasser_spotupdrives_csv, player, pnrpasser_spotupdrives_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_spotupdrives_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict2 = {'BHRightPNRSpotupDrives': pnrpasser_spotupdrives_player_proportion}
    insight.extend([outer_dict2])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassRightDrivesPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Right to Spot Up Drives by Shooter',
        output_filename=output_file_path
    )

    # Spot up jumpers
    pnrpasser_spotupjumper_csv = ['twoplayer_pnrbhright_spotupjumper_efficiency.csv']
    filtered_df3 = df[(df['SourceFile'].isin(pnrpasser_spotupjumper_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_spotupjumper_player_proportion = find_player_proportions(filtered_df3, pnrpasser_spotupjumper_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_spotupjumper_player_proportion:
        player_data = find_player_efficiency(filtered_df3, pnrpasser_spotupjumper_csv, player, pnrpasser_spotupjumper_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_spotupjumper_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict3 = {'BHRightPNRSpotupJumpers': pnrpasser_spotupjumper_player_proportion}
    insight.extend([outer_dict3])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassRightShotsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Right to Spot Up Jumpers by Shooter',
        output_filename=output_file_path
    )

    # Rollman rolls
    pnrpasser_rollmanrolls_csv = ['twoplayer_pnrbhright_rollmanrolls_efficiency.csv']
    filtered_df4 = df[(df['SourceFile'].isin(pnrpasser_rollmanrolls_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanrolls_player_proportion = find_player_proportions(filtered_df4, pnrpasser_rollmanrolls_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_rollmanrolls_player_proportion:
        player_data = find_player_efficiency(filtered_df4, pnrpasser_rollmanrolls_csv, player, pnrpasser_rollmanrolls_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanrolls_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict4 = {'BHRightPNRRollmanRolls': pnrpasser_rollmanrolls_player_proportion}
    insight.extend([outer_dict4])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassRightRollsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Right to Rollman Rolling by Shooter',
        output_filename=output_file_path
    )

    # Rollman slips
    pnrpasser_rollmanslips_csv = ['twoplayer_pnrbhright_rollmanslips_efficiency.csv']
    filtered_df5 = df[(df['SourceFile'].isin(pnrpasser_rollmanslips_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanslips_player_proportion = find_player_proportions(filtered_df5, pnrpasser_rollmanslips_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_rollmanslips_player_proportion:
        player_data = find_player_efficiency(filtered_df5, pnrpasser_rollmanrolls_csv, player, pnrpasser_rollmanslips_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanslips_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict5 = {'BHRightPNRRollmanSlips': pnrpasser_rollmanslips_player_proportion}
    insight.extend([outer_dict5])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassRightSlipsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Right to Rollman Slipping by Shooter',
        output_filename=output_file_path
    )

    # Rollman pops
    pnrpasser_rollmanpops_csv = ['twoplayer_pnrbhright_rollmanpops_efficiency.csv']
    filtered_df6 = df[(df['SourceFile'].isin(pnrpasser_rollmanpops_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanpops_player_proportion = find_player_proportions(filtered_df6, pnrpasser_rollmanpops_csv, 'SecondaryPlayer')
    
    player_dict = {}
    for player in pnrpasser_rollmanpops_player_proportion:
        player_data = find_player_efficiency(filtered_df6, pnrpasser_rollmanpops_csv, player, pnrpasser_rollmanpops_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanpops_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict6 = {'BHRightPNRRollmanPops': pnrpasser_rollmanpops_player_proportion}
    insight.extend([outer_dict6])
    
    output_file_path = os.path.join(output_directory, 'PNR_PassRightPopsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=2,
        y_max=15,
        title='BH Right to Rollman Popping by Shooter',
        output_filename=output_file_path
    )

def Iso_passer_stats(df: pd.DataFrame, name, insight, output_directory):
    total_passing_proport_csvs = ['twoplayer_iso_cut_efficiency.csv', 
                                'twoplayer_iso_spotupdrives_efficiency.csv', 
                                'twoplayer_iso_spotupjumpers_efficiency.csv']
    filtered_df0 = df[(df['SourceFile'].isin(total_passing_proport_csvs)) & (df['PrimaryPlayer'] == name)]
    total_passing_proportion = find_play_proportions(filtered_df0, total_passing_proport_csvs)
    total_passing_proportion_dict = {
        'Pass ISO Cut': total_passing_proportion[0], 
        'Pass ISO Spotup Drive': total_passing_proportion[1],
        'Pass ISO Spotup Jumper': total_passing_proportion[2],  
        'Total Plays': total_passing_proportion[3]
    }
    total_passing_efficiency = compute_grouped_statistics(filtered_df0, 'Efficiency for all ISO secondary plays together.', 'PrimaryPlayer', 'Total_Iso_Passer')

    # Calculates proportion and efficiency of a player hitting a specific second player (cutter) off of an isolation play
    isopasser_cut_csv = ['twoplayer_iso_cut_efficiency.csv']
    filtered_df1 = df[(df['SourceFile'].isin(isopasser_cut_csv)) & (df['PrimaryPlayer'] == name)]
    isopasser_cut_player_proportion = find_player_proportions(filtered_df1, isopasser_cut_csv, 'SecondaryPlayer')
    for player in isopasser_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df1, isopasser_cut_csv, player, isopasser_cut_player_proportion[player], 'SecondaryPlayer')
        isopasser_cut_player_proportion[player] = player_data

    # Calculates proportion and efficiency of a player hitting a specific second player (spot up shooter) off of an isolation play
    isopasser_spotupdrives_csv = ['twoplayer_iso_spotupdrives_efficiency.csv']
    filtered_df2 = df[(df['SourceFile'].isin(isopasser_spotupdrives_csv)) & (df['PrimaryPlayer'] == name)]
    isopasser_spotupdrives_player_proportion = find_player_proportions(filtered_df2, isopasser_spotupdrives_csv, 'SecondaryPlayer')
    for player in isopasser_spotupdrives_player_proportion:
        player_data = find_player_efficiency(filtered_df2, isopasser_spotupdrives_csv, player, isopasser_spotupdrives_player_proportion[player], 'SecondaryPlayer')
        isopasser_spotupdrives_player_proportion[player] = player_data

    # Calculates proportion and efficiency of a player hitting a specific second player (spot up jumper) off of an isolation play
    isopasser_spotupjumper_csv = ['twoplayer_iso_spotupjumpers_efficiency.csv']
    filtered_df3 = df[(df['SourceFile'].isin(isopasser_spotupjumper_csv)) & (df['PrimaryPlayer'] == name)]
    isopasser_spotupjumper_player_proportion = find_player_proportions(filtered_df3, isopasser_spotupjumper_csv, 'SecondaryPlayer')
    for player in isopasser_spotupjumper_player_proportion:
        player_data = find_player_efficiency(filtered_df3, isopasser_spotupjumper_csv, player, isopasser_spotupjumper_player_proportion[player], 'SecondaryPlayer')
        isopasser_spotupjumper_player_proportion[player] = player_data
        
    insight.extend([
        total_passing_proportion_dict,
        total_passing_efficiency,
        isopasser_cut_player_proportion,
        isopasser_spotupdrives_player_proportion,
        isopasser_spotupjumper_player_proportion
    ])

def Post_passer_stats(df: pd.DataFrame, name, insight, output_directory):
    total_passing_proport_csvs = ['twoplayer_post_cut_efficiency.csv', 
                                'twoplayer_post_spotupdrives_efficiency.csv', 
                                'twoplayer_post_spotupjumper_efficiency.csv']
    filtered_df0 = df[(df['SourceFile'].isin(total_passing_proport_csvs)) & (df['PrimaryPlayer'] == name)]
    total_passing_proportion = find_play_proportions(filtered_df0, total_passing_proport_csvs)
    total_passing_proportion_dict = {
        'Post - Cut': total_passing_proportion[0], 
        'Post - Spotup Drive': total_passing_proportion[1],
        'Post - Spotup Jumper': total_passing_proportion[2],  
        'Total Plays': total_passing_proportion[3]
    }
    total_passing_efficiency = compute_grouped_statistics(filtered_df0, 'Efficiency for all POST secondary plays together.', 'PrimaryPlayer', 'Total_Post_Passer')

    # Creates Post Pass -> Playtype Visual
    selected_keys = ['Post - Cut', 'Post - Spotup Drive', 'Post - Spotup Jumper']
    total_plays = total_passing_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_passing_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'Post_PassPlayType_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=3,
        y_max=50,
        title='Post Pass to Play Type Frequency',
        output_filename=output_file_path
    )


    postpasser_cut_csv = ['twoplayer_post_cut_efficiency.csv']
    filtered_df1 = df[(df['SourceFile'].isin(postpasser_cut_csv)) & (df['PrimaryPlayer'] == name)]
    postpasser_cut_player_proportion = find_player_proportions(filtered_df1, postpasser_cut_csv, 'SecondaryPlayer')
    player_dict = {}
    for player in postpasser_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df1, postpasser_cut_csv, player, postpasser_cut_player_proportion[player], 'SecondaryPlayer')
        postpasser_cut_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
        
    outer_dict1 = {'PostCut': postpasser_cut_player_proportion}
        
    output_file_path = os.path.join(output_directory, 'Post_PassCutsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=3,
        y_max=25,
        title='Post Pass to Cut by Cutters',
        output_filename=output_file_path
    ) 
        

    postpasser_spotupdrives_csv = ['twoplayer_post_spotupdrives_efficiency.csv']
    filtered_df2 = df[(df['SourceFile'].isin(postpasser_spotupdrives_csv)) & (df['PrimaryPlayer'] == name)]
    postpasser_spotupdrives_player_proportion = find_player_proportions(filtered_df2, postpasser_spotupdrives_csv, 'SecondaryPlayer')
    player_dict = {}
    for player in postpasser_spotupdrives_player_proportion:
        player_data = find_player_efficiency(filtered_df2, postpasser_spotupdrives_csv, player, postpasser_spotupdrives_player_proportion[player], 'SecondaryPlayer')
        postpasser_spotupdrives_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
        
    outer_dict2 = {'PostSpotupDrives': postpasser_spotupdrives_player_proportion}    
    
    output_file_path = os.path.join(output_directory, 'Post_PassDrivesPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=3,
        y_max=25,
        title='Post Pass to Spot Up Drives by Shooter',
        output_filename=output_file_path
    ) 
        

    postpasser_spotupjumper_csv = ['twoplayer_post_spotupjumper_efficiency.csv']
    filtered_df3 = df[(df['SourceFile'].isin(postpasser_spotupjumper_csv)) & (df['PrimaryPlayer'] == name)]
    postpasser_spotupjumper_player_proportion = find_player_proportions(filtered_df3, postpasser_spotupjumper_csv, 'SecondaryPlayer')
    player_dict = {}
    for player in postpasser_spotupjumper_player_proportion:
        player_data = find_player_efficiency(filtered_df3, postpasser_spotupjumper_csv, player, postpasser_spotupjumper_player_proportion[player], 'SecondaryPlayer')
        postpasser_spotupjumper_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
        
    outer_dict3 = {'PostSpotupJumper': postpasser_spotupjumper_player_proportion}
    
    output_file_path = os.path.join(output_directory, 'Post_PassShotsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=3,
        y_max=25,
        title='Post Pass to Spot Up Jumpers by Shooter',
        output_filename=output_file_path
    ) 
        
    
    insight.extend([
        total_passing_proportion_dict,
        total_passing_efficiency,
        outer_dict1,
        outer_dict2,
        outer_dict3
    ])    
    
    
def process_secondary_stats(df: pd.DataFrame, name, insights, output_directory):
    for key in insights:
        if key == 'Rollman_insights':  # Rollman insights
            Rollman_secondary_stats(df, name, insights[key], output_directory)
        elif key == 'Cut_insights':  # Cut insights
            Cut_secondary_stats(df, name, insights[key], output_directory)
        elif key == 'Spotup_insights':  # Spotup insights
            Spotup_secondary_stats(df, name, insights[key], output_directory)

def Rollman_secondary_stats(df: pd.DataFrame, name, insight, output_directory):
    
    # Calculates total proportion and efficiency for Rollman plays
    filtered_df = df [ (df['SourceFile'] == 'player_rollman_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_rollman_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Total Efficiency', 'SecondaryPlayer', 'Rollman_Total')


    # Calculates proportion / efficiency for rollman Slips vs Rolls vs Pops
    total_rollman_type_proport_csvs = ['player_rollman_slip_efficiency.csv', 'player_rollman_roll_efficiency.csv',
                                    'player_rollman_pop_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_rollman_type_proport_csvs) & (df['SecondaryPlayer'] == name) ]
    total_rollman_type_proportion = find_play_proportions(filtered_df, total_rollman_type_proport_csvs)
    total_rollman_type_proportion_dict = {'Rollman Slip' : total_rollman_type_proportion[0], 'Rollman Roll': total_rollman_type_proportion[1],
                                        'Rollman Pop': total_rollman_type_proportion[2], 'Total Plays': total_rollman_type_proportion[3] }

    selected_keys = ['Rollman Slip', 'Rollman Roll', 'Rollman Pop']
    total_plays = total_rollman_type_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_rollman_type_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'Rollman_PlayType_Freq.png')
    create_bar_chart(
        data_dict=data_to_plot,
        section=4,
        y_max=50,
        title='Rollman Play Type Frequency',
        output_filename=output_file_path
    )


    filtered_df = df [ (df['SourceFile'] == 'player_rollman_slip_efficiency.csv')  & (df['SecondaryPlayer'] == name) ]
    total_slip_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Slip', 'SecondaryPlayer', 'Rollman_Slip')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_roll_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_roll_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Roll', 'SecondaryPlayer', 'Rollman_Roll')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_pop_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_pop_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Pop', 'SecondaryPlayer', 'Rollman_Pop')
    
    
    # Calculates proportion / efficiency for Left Drives vs Right Drives for SLIPS
    total_rollman_direction_proport_csvs = ['player_rollman_leftdrive_slip_efficiency.csv', 'player_rollman_rightdrive_slip_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_rollman_direction_proport_csvs) & (df['SecondaryPlayer'] == name) ]
    total_rollman_direction_proportion = find_play_proportions(filtered_df, total_rollman_direction_proport_csvs)
    total_rollman_direction_proportion_dict = {'Rollman Slip - Left' : total_rollman_direction_proportion[0], 'Rollman Slip - Right': total_rollman_direction_proportion[1],
                                            'Total Plays': total_rollman_direction_proportion[2] }
    total_rollman_direction_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all Rollman drive plays together.', 'SecondaryPlayer', 'Rollman_Slip_Drive')

    selected_keys = ['Rollman Slip - Left', 'Rollman Slip - Right']
    total_plays = total_rollman_direction_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_rollman_direction_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'Rollman_SlipDirection_Freq.png')
    create_bar_chart(
        data_dict=data_to_plot,
        section=4,
        y_max=15,
        title='Rollman Slip - Drive Direction Frequency',
        output_filename=output_file_path
    )
    

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_leftdrive_slip_efficiency.csv')  & (df['SecondaryPlayer'] == name) ]
    total_slip_left_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Slip --> Left', 'SecondaryPlayer', 'Rollman Slip_Left_Drive')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_rightdrive_slip_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_slip_right_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Slip --> Right', 'SecondaryPlayer', 'Rollman Slip_Right_Drive')


    # Calculates proportion / efficiency for Left Drives vs Right Drives for POPS
    total_rollman_direction_pop_proport_csvs = ['player_rollman_leftdrive_pop_efficiency.csv', 'player_rollman_rightdrive_pop_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_rollman_direction_pop_proport_csvs) & (df['SecondaryPlayer'] == name) ]
    total_rollman_direction_pop_proportion = find_play_proportions(filtered_df, total_rollman_direction_pop_proport_csvs)
    total_rollman_direction_pop_proportion_dict = {'Rollman Pop - Left' : total_rollman_direction_pop_proportion[0], 'Rollman Pop - Right': total_rollman_direction_pop_proportion[1],
                                            'Total Plays': total_rollman_direction_pop_proportion[2] }
    total_rollman_direction_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all Rollman drive plays together off of Pops.', 'SecondaryPlayer', 'Rollman_Pop_Drive')

    selected_keys = ['Rollman Pop - Left', 'Rollman Pop - Right']
    total_plays = total_rollman_direction_pop_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_rollman_direction_pop_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'Rollman_PopDirection_Freq.png')
    create_bar_chart(
        data_dict=data_to_plot,
        section=4,
        y_max=15,
        title='Rollman Pop - Drive Direction Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_leftdrive_pop_efficiency.csv')  & (df['SecondaryPlayer'] == name) ]
    total_pop_left_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Pop --> Left', 'SecondaryPlayer', 'Rollman_Pop_Left')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_rightdrive_pop_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_pop_right_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Pop --> Right', 'SecondaryPlayer', 'Rollman_Pop_Right')


    # Calculates proportion and efficiency of rollman based on which player passed them the ball
    rollman_player_csv = ['player_rollman_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(rollman_player_csv)) & (df['SecondaryPlayer'] == name)]
    rollman_player_proportion = find_player_proportions(filtered_df, rollman_player_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in rollman_player_proportion:
        player_data = find_player_efficiency(filtered_df, rollman_player_csv, player, rollman_player_proportion[player], 'PrimaryPlayer' )
        rollman_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict1 = {'PNR_to_Rollman': rollman_player_proportion}
    
    output_file_path = os.path.join(output_directory, 'Rollman_AllPlayTypePlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=4,
        y_max=25,
        title='Rollman Efficiency By Passer',
        output_filename=output_file_path
    )

    rollman_slip_player_csv = ['player_rollman_slip_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(rollman_slip_player_csv)) & (df['SecondaryPlayer'] == name)]
    rollman_slip_player_proportion = find_player_proportions(filtered_df, rollman_slip_player_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in rollman_slip_player_proportion:
        player_data = find_player_efficiency(filtered_df, rollman_slip_player_csv, player, rollman_slip_player_proportion[player], 'PrimaryPlayer' )
        rollman_slip_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict2 = {'PNR_to_RollmanSlip': rollman_slip_player_proportion}
    
    output_file_path = os.path.join(output_directory, 'Rollman_SlipPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=4,
        y_max=25,
        title='Rollman Slip Frequency By Passer',
        output_filename=output_file_path
    )


    rollman_pop_player_csv = ['player_rollman_pop_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(rollman_pop_player_csv)) & (df['SecondaryPlayer'] == name)]
    rollman_pop_player_proportion = find_player_proportions(filtered_df, rollman_pop_player_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in rollman_pop_player_proportion:
        player_data = find_player_efficiency(filtered_df, rollman_pop_player_csv, player, rollman_pop_player_proportion[player], 'PrimaryPlayer' )
        rollman_pop_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict3 = {'PNR_to_RollmanPop': rollman_pop_player_proportion}
    
    output_file_path = os.path.join(output_directory, 'Rollman_PopPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=4,
        y_max=25,
        title='Rollman Pop Frequency By Passer',
        output_filename=output_file_path
    )


    rollman_roll_player_csv = ['player_rollman_roll_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(rollman_roll_player_csv)) & (df['SecondaryPlayer'] == name)]
    rollman_roll_player_proportion_dict = find_player_proportions(filtered_df, rollman_roll_player_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in rollman_roll_player_proportion_dict:
        player_data = find_player_efficiency(filtered_df, rollman_roll_player_csv, player, rollman_roll_player_proportion_dict[player], 'PrimaryPlayer' )
        rollman_roll_player_proportion_dict[player] = player_data
        player_dict[player] = player_data['TotalPlays']

    outer_dict4 = {'PNR_to_RollmanRoll': rollman_roll_player_proportion_dict}
    
    output_file_path = os.path.join(output_directory, 'Rollman_RollPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=4,
        y_max=25,
        title='Rollman Roll Frequency By Passer',
        output_filename=output_file_path
    )
    
    insight.extend([
        total_rollman_efficiency,
        total_rollman_type_proportion_dict,
        total_slip_efficiency,
        total_roll_efficiency,
        total_pop_efficiency,
        total_rollman_direction_proportion_dict,
        total_rollman_direction_efficiency,
        total_slip_left_efficiency,
        total_slip_right_efficiency,
        total_rollman_direction_pop_proportion_dict,
        total_pop_left_efficiency,
        total_pop_right_efficiency,
        outer_dict1,
        outer_dict2,
        outer_dict3,
        outer_dict4
    ])

def Cut_secondary_stats(df: pd.DataFrame, name, insight, output_directory):
    # Finds total efficiency for ALL secondary cutter plays
    second_cut_csvs = ['twoplayer_iso_cut_efficiency.csv', 'twoplayer_pnr_cut_efficiency.csv', 'twoplayer_post_cut_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(second_cut_csvs)) & (df['SecondaryPlayer'] == name) ]
    total_cut_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all secondary cutter plays.', 'SecondaryPlayer', 'Playtype_Cutter')

    # Calculates total proportion and efficiency of each type of play leading to a cutter shot. Including unknown passers. 
    total_cut_proport_csvs = ['twoplayer_iso_cut_efficiency.csv', 'twoplayer_pnr_cut_efficiency.csv', 'twoplayer_post_cut_efficiency.csv', ]
    filtered_df = df [ (df['SourceFile'].isin(total_cut_proport_csvs)) & (df['SecondaryPlayer'] == name)  ]
    total_cut_proportion = find_play_proportions(filtered_df, total_cut_proport_csvs)

    unknown_passer_csv = ['player_cut_efficiency.csv']
    unknown_passer_df = df [ (df['SourceFile'].isin(unknown_passer_csv)) & (df['Player'] == name) ]
    total_unknown_proportion = find_play_proportions(unknown_passer_df, unknown_passer_csv)

    if total_unknown_proportion[1] == 0:
        percent_known_passer = 1
    else: 
        percent_known_passer = float(total_cut_proportion[3]) / float(total_unknown_proportion[1])
    percent_unknown_passer = 1 - percent_known_passer
    total_cut_proportion_dict = {'Iso --> Cut' : (total_cut_proportion[0] * percent_known_passer), 'PNR --> Cut': (total_cut_proportion[1] * percent_known_passer),
                                'Post --> Cut': (total_cut_proportion[2] * percent_known_passer), 'Unknown --> Cut': percent_unknown_passer,
                                'Total Plays': total_unknown_proportion[1] }

    iso_cut_efficiency_csv = ['twoplayer_iso_cut_efficiency.csv']
    iso_cut_efficiency_df = df [ (df['SourceFile'].isin(iso_cut_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    iso_cut_efficiency = compute_grouped_statistics(iso_cut_efficiency_df, 'Efficiency for all Isos leading to secondary cutter plays.', 'SecondaryPlayer', 'Iso_Cutter')
    iso_cut_player_proportion = find_player_proportions(iso_cut_efficiency_df, iso_cut_efficiency_csv, 'PrimaryPlayer')
    for player in iso_cut_player_proportion:
        player_data = find_player_efficiency(iso_cut_efficiency_df, iso_cut_efficiency_csv, player, iso_cut_player_proportion[player], 'PrimaryPlayer')
        iso_cut_player_proportion[player] = player_data

    pnr_cut_efficiency_csv = ['twoplayer_pnr_cut_efficiency.csv']
    pnr_cut_efficiency_df = df [ (df['SourceFile'].isin(pnr_cut_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnr_cut_efficiency = compute_grouped_statistics(pnr_cut_efficiency_df, 'Efficiency for all PNRs leading to secondary cutter plays.', 'SecondaryPlayer', 'PNR_Cutter')
    pnr_cut_player_proportion = find_player_proportions(pnr_cut_efficiency_df, pnr_cut_efficiency_csv, 'PrimaryPlayer')
    for player in pnr_cut_player_proportion:
        player_data = find_player_efficiency(pnr_cut_efficiency_df, pnr_cut_efficiency_csv, player, pnr_cut_player_proportion[player], 'PrimaryPlayer')
        pnr_cut_player_proportion[player] = player_data

    post_cut_efficiency_csv = ['twoplayer_post_cut_efficiency.csv']
    post_cut_efficiency_df = df [ (df['SourceFile'].isin(post_cut_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    post_cut_efficiency = compute_grouped_statistics(post_cut_efficiency_df, 'Efficiency for all Post ups leading to secondary cutter plays.', 'SecondaryPlayer', 'PostUps_Cutter')
    post_cut_player_proportion = find_player_proportions(post_cut_efficiency_df, post_cut_efficiency_csv, 'PrimaryPlayer')
    for player in post_cut_player_proportion:
        player_data = find_player_efficiency(post_cut_efficiency_df, post_cut_efficiency_csv, player, post_cut_player_proportion[player], 'PrimaryPlayer')
        post_cut_player_proportion[player] = player_data
        
        
    insight.extend([
        total_cut_efficiency,
        total_cut_proportion_dict,
        iso_cut_efficiency,
        pnr_cut_efficiency,
        post_cut_efficiency
    ])

def Spotup_secondary_stats(df: pd.DataFrame, name, insight, output_directory):
    # Finds total efficiency for ALL secondary cutter plays
    second_spotup_csvs = ['twoplayer_iso_spotupdrives_efficiency.csv', 'twoplayer_iso_spotupjumpers_efficiency.csv', 
                    'twoplayer_pnr_spotupdrives_efficiency.csv', 'twoplayer_pnr_spotupsjumpers_efficiency.csv',
                    'twoplayer_post_spotupdrive_efficiency.csv', 'twoplayer_post_spotupjumper_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(second_spotup_csvs)) & (df['SecondaryPlayer'] == name) ]
    total_spotup_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all secondary Spot Up plays.', 'SecondaryPlayer', 'Playtype_SpotUps')


    # Calculates total proportion and efficiency of each type of play leading to a spot up drive. Including unknown passers.
    total_spotupdrives_proport_csvs = ['twoplayer_iso_spotupdrives_efficiency.csv', 'twoplayer_pnr_spotupdrives_efficiency.csv', 'twoplayer_post_spotupdrive_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(total_spotupdrives_proport_csvs)) & (df['SecondaryPlayer'] == name)  ]
    total_spotupdrives_proportion = find_play_proportions(filtered_df, total_spotupdrives_proport_csvs)
    total_secondary_spotupdrives_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency Secondary SU Drives', 'SecondaryPlayer', 'Secondary_SU_Drives_Total')

    unknown_passer_csv = ['player_spotup_drive_efficiency.csv']
    unknown_passer_df = df [ (df['Player'] == name) & (df['SourceFile'].isin(unknown_passer_csv)) ]
    total_unknown_proportion = find_play_proportions(unknown_passer_df, unknown_passer_csv)
    total_unknown_sudrives_efficiency = compute_grouped_statistics(unknown_passer_df, 'Unknown Stats', 'Player', 'SU_Drives_Total' )

    percent_known_passer = (total_secondary_spotupdrives_efficiency['Secondary_SU_Drives_Total']['TotalPlays']) / (total_unknown_sudrives_efficiency['SU_Drives_Total']['TotalPlays'])
    percent_unknown_passer = 1 - percent_known_passer


    total_spotupdrives_proportion_dict = {'Iso - SU Drives' : (total_spotupdrives_proportion[0] * percent_known_passer), 
                                        'PNR - SU Drives': (total_spotupdrives_proportion[1] * percent_known_passer),
                                        'Post - SU Drives': (total_spotupdrives_proportion[2] * percent_known_passer), 
                                        'Unknown - SU Drives': percent_unknown_passer,
                                        'Total Plays': total_unknown_sudrives_efficiency['SU_Drives_Total']['TotalPlays']
                                        }
    
    selected_keys = ['Iso - SU Drives', 'PNR - SU Drives', 'Post - SU Drives', 'Unknown - SU Drives']
    total_plays = total_spotupdrives_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_spotupdrives_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'SpotUp_PlayTypeDrives_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=5,
        y_max=50,
        title='Play Type to Spot Up Drive Frequency',
        output_filename=output_file_path
    )
    

    # Calculates total proportion and efficiency of each type of play leading to a spot up jumpers. Including unknown passers.
    total_spotupjumpers_proport_csvs = ['twoplayer_iso_spotupjumpers_efficiency.csv', 'twoplayer_pnr_spotupsjumpers_efficiency.csv','twoplayer_post_spotupjumper_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(total_spotupjumpers_proport_csvs)) & (df['SecondaryPlayer'] == name)  ]
    total_spotupjumpers_proportion = find_play_proportions(filtered_df, total_spotupjumpers_proport_csvs)

    unknown_passer_csv = ['player_spotup_jumpshot_efficiency.csv']
    unknown_passer_df = df [ (df['SourceFile'].isin(unknown_passer_csv)) & (df['Player'] == name) ]
    total_unknown_proportion = find_play_proportions(unknown_passer_df, unknown_passer_csv)

    if total_unknown_proportion[1] == 0:
        percent_known_passer = 1
    else: 
        percent_known_passer = float(total_spotupjumpers_proportion[3]) / float(total_unknown_proportion[1])
    percent_unknown_passer = 1 - percent_known_passer
    total_spotupjumpers_proportion_dict = {'Iso - SU Jumpers' : (total_spotupjumpers_proportion[0] * percent_known_passer), 
                                        'PNR - SU Jumpers': (total_spotupjumpers_proportion[1] * percent_known_passer),
                                        'Post - SU Jumpers': (total_spotupjumpers_proportion[2] * percent_known_passer), 
                                        'Unknown - SU Jumpers': percent_unknown_passer,
                                        'Total Plays': total_unknown_proportion[1] 
                                        }
    
    selected_keys = ['Iso - SU Jumpers', 'PNR - SU Jumpers', 'Post - SU Jumpers', 'Unknown - SU Jumpers']
    total_plays = total_spotupjumpers_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_spotupjumpers_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'SpotUp_PlayTypeShots_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=5,
        y_max=50,
        title='Play Type to Spot Up Jumper Frequency',
        output_filename=output_file_path
    )

    iso_spotupdrives_efficiency_csv = ['twoplayer_iso_spotupdrives_efficiency.csv']
    iso_spotupdrives_efficiency_df = df [ (df['SourceFile'].isin(iso_spotupdrives_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    iso_spotupdrives_efficiency = compute_grouped_statistics(iso_spotupdrives_efficiency_df, 'Efficiency for all Isos leading to secondary Spot up drives plays.', 'SecondaryPlayer', 'Iso_SpotUpDrives')
    iso_spotupdrives_player_proportion = find_player_proportions(iso_spotupdrives_efficiency_df, iso_spotupdrives_efficiency_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in iso_spotupdrives_player_proportion:
        player_data = find_player_efficiency(iso_spotupdrives_efficiency_df, iso_spotupdrives_efficiency_csv, player, iso_spotupdrives_player_proportion[player], 'PrimaryPlayer')
        iso_spotupdrives_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
        
    outer_dict0 = {'Iso_to_SpotupDrives': iso_spotupdrives_player_proportion}

        
    output_file_path = os.path.join(output_directory, 'SpotUp_IsoDrivesPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=5,
        y_max=25,
        title='Iso to Spot Up Drive By Passer',
        output_filename=output_file_path
    )
    

    iso_spotupjumpers_efficiency_csv = ['twoplayer_iso_spotupjumpers_efficiency.csv']
    iso_spotupjumpers_efficiency_df = df [ (df['SourceFile'].isin(iso_spotupjumpers_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    iso_spotupjumpers_efficiency = compute_grouped_statistics(iso_spotupjumpers_efficiency_df, 'Efficiency for all Isos leading to secondary Spot up jumpers plays.', 'SecondaryPlayer', 'Iso_SpotUpJumpers')
    iso_spotupjumpers_player_proportion = find_player_proportions(iso_spotupjumpers_efficiency_df, iso_spotupjumpers_efficiency_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in iso_spotupjumpers_player_proportion:
        player_data = find_player_efficiency(iso_spotupjumpers_efficiency_df, iso_spotupjumpers_efficiency_csv, player, iso_spotupjumpers_player_proportion[player], 'PrimaryPlayer')
        iso_spotupjumpers_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
        
    outer_dict1 = {'Iso_to_SpotupJumpers': iso_spotupjumpers_player_proportion}
        
    output_file_path = os.path.join(output_directory, 'SpotUp_IsoShotsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=5,
        y_max=25,
        title='Iso to Spot Up Jumper By Passer',
        output_filename=output_file_path
    )


    pnr_spotupsdrives_efficiency_csv = ['twoplayer_pnr_spotupsdrives_efficiency.csv']
    pnr_spotupdrives_efficiency_df = df [ (df['SourceFile'].isin(pnr_spotupsdrives_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnr_spotupdrives_efficiency = compute_grouped_statistics(pnr_spotupdrives_efficiency_df, 'Efficiency for all PNRs leading to secondary Spot up drives plays.', 'SecondaryPlayer', 'PNR_SpotUpDrives')
    pnr_spotupdrives_player_proportion = find_player_proportions(pnr_spotupdrives_efficiency_df, pnr_spotupsdrives_efficiency_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in pnr_spotupdrives_player_proportion:
        player_data = find_player_efficiency(pnr_spotupdrives_efficiency_df, pnr_spotupsdrives_efficiency_csv, player, pnr_spotupdrives_player_proportion[player], 'PrimaryPlayer')
        pnr_spotupdrives_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
        
    outer_dict2 = {'PNR_to_SpotupDrives': pnr_spotupdrives_player_proportion}

        
    output_file_path = os.path.join(output_directory, 'SpotUp_PnrDrivesPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=5,
        y_max=25,
        title='PNR to Spot Up Drives By Passer',
        output_filename=output_file_path
    )

    pnr_spotupjumpers_efficiency_csv = ['twoplayer_pnr_spotupsjumpers_efficiency.csv']
    pnr_spotupjumpers_efficiency_df = df [ (df['SourceFile'].isin(pnr_spotupjumpers_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnr_spotupjumpers_efficiency = compute_grouped_statistics(pnr_spotupjumpers_efficiency_df, 'Efficiency for all PNRs leading to secondary Spot up jumpers plays.', 'SecondaryPlayer', 'PNR_SpotUpJumpers')
    pnr_spotupjumpers_player_proportion = find_player_proportions(pnr_spotupjumpers_efficiency_df, pnr_spotupjumpers_efficiency_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in pnr_spotupjumpers_player_proportion:
        player_data = find_player_efficiency(pnr_spotupjumpers_efficiency_df, pnr_spotupjumpers_efficiency_csv, player, pnr_spotupjumpers_player_proportion[player], 'PrimaryPlayer')
        pnr_spotupjumpers_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
        
    outer_dict3 = {'PNR_to_SpotupJumpers': pnr_spotupjumpers_player_proportion}

        
    output_file_path = os.path.join(output_directory, 'SpotUp_PNRShotsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=5,
        y_max=25,
        title='PNR to Spot Up Jumpers By Passer',
        output_filename=output_file_path
    )


    post_spotupdrives_efficiency_csv = ['twoplayer_post_spotupdrive_efficiency.csv']
    post_spotupdrives_efficiency_df = df [ (df['SourceFile'].isin(post_spotupdrives_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    post_spotupdrives_efficiency = compute_grouped_statistics(post_spotupdrives_efficiency_df, 'Efficiency for all Post plays leading to secondary Spot up drives plays.', 'SecondaryPlayer', 'Post_SpotUpDrives')
    post_spotupdrives_player_proportion = find_player_proportions(post_spotupdrives_efficiency_df, post_spotupdrives_efficiency_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in post_spotupdrives_player_proportion:
        player_data = find_player_efficiency(post_spotupdrives_efficiency_df, post_spotupdrives_efficiency_csv, player, post_spotupdrives_player_proportion[player], 'PrimaryPlayer')
        post_spotupdrives_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
        
    outer_dict4 = {'Post_to_SpotupDrives': post_spotupdrives_player_proportion}

        
    output_file_path = os.path.join(output_directory, 'SpotUp_PostDrivesPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=5,
        y_max=25,
        title='Post to Spot Up Drives By Passer',
        output_filename=output_file_path
    )


    post_spotupjumpers_efficiency_csv = ['twoplayer_post_spotupjumper_efficiency.csv']
    post_spotupjumpers_efficiency_df = df [ (df['SourceFile'].isin(post_spotupjumpers_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    post_spotupjumpers_efficiency = compute_grouped_statistics(post_spotupjumpers_efficiency_df, 'Efficiency for all Post plays leading to secondary Spot up jumpers plays.', 'SecondaryPlayer', 'Post_SpotUpJumpers')
    post_spotupjumpers_player_proportion = find_player_proportions(post_spotupjumpers_efficiency_df, post_spotupjumpers_efficiency_csv, 'PrimaryPlayer')
    player_dict = {}
    for player in post_spotupjumpers_player_proportion:
        player_data = find_player_efficiency(post_spotupjumpers_efficiency_df, post_spotupjumpers_efficiency_csv, player, post_spotupjumpers_player_proportion[player], 'PrimaryPlayer')
        post_spotupjumpers_player_proportion[player] = player_data
        player_dict[player] = player_data['TotalPlays']
  
    outer_dict5 = {'Post_to_SpotupJumpers': post_spotupjumpers_player_proportion}

    output_file_path = os.path.join(output_directory, 'SpotUp_PostShotsPlayer_Freq.png')
    create_bar_chart(
        data_dict=player_dict,
        section=5,
        y_max=25,
        title='Post to Spot Up Jumpers By Passer',
        output_filename=output_file_path
    )
    

    insight.extend([
        total_spotup_efficiency,
        total_spotupdrives_proportion_dict,
        total_spotupjumpers_proportion_dict,
        iso_spotupdrives_efficiency,
        outer_dict0,
        iso_spotupjumpers_efficiency,
        outer_dict1,
        pnr_spotupdrives_efficiency,
        outer_dict2,
        pnr_spotupjumpers_efficiency,
        outer_dict3,
        post_spotupdrives_efficiency,
        outer_dict4,
        post_spotupjumpers_efficiency,
        outer_dict5,
    ])


def process_scorer_stats(df: pd.DataFrame, name, insights, output_directory):
    for key in insights:
        if key == "PNR_insights":  # PNR insights
            PNR_scorer_stats(df, name, insights[key], output_directory)
        elif key == 'Iso_insights':  # Iso insights
            Iso_scorer_stats(df, name, insights[key], output_directory)
        elif key == 'Post_insights':  # Post insights
            Post_scorer_stats(df, name, insights[key], output_directory)
        elif key == 'Cut_insights':  # Cut insights
            Cut_scorer_stats(df, name, insights[key], output_directory)
        elif key == 'Spotup_insights':  # Spotup insights
            Spotup_scorer_stats(df, name, insights[key], output_directory)
        elif key == 'Transition_insights':  # Transition insights
            Transition_scorer_stats(df, name, insights[key], output_directory)
        elif key == 'Offscreen_insights':  # Offscreen insights
            Offscreen_scorer_stats(df, name, insights[key], output_directory)
        elif key == 'Handoff_insights':  # Handoff insights
            Handoff_scorer_stats(df, name, insights[key], output_directory)

def PNR_scorer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Finds total efficiency for ALL PNR scorer plays
    filtered_df1 = df[(df['SourceFile'] == 'player_pnr_efficiency.csv')]
    total_pnr_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all PNR scorer plays together.', 'Player', 'PNR_Scorer')

    # Calculate total proportion and efficiency for REJECTING vs GOING OFF screens
    total_pnr_proport_csvs = ['player_pnr_offpick_efficiency.csv', 'player_pnr_rejectpick_efficiency.csv']
    filtered_df2 = df[df['SourceFile'].isin(total_pnr_proport_csvs)]
    total_pnr_proportion = find_play_proportions(filtered_df2, total_pnr_proport_csvs)
    total_pnr_proportion_dict = {'PNR Accept': total_pnr_proportion[0], 
                                 'PNR Reject': total_pnr_proportion[1],
                                 'Total Plays': total_pnr_proportion[2]}
    
    selected_keys = ['PNR Accept', 'PNR Reject']
    total_plays = total_pnr_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_pnr_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'PNR_Usage_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=2,
        y_max=100,
        title='PNR Usage Frequency',
        output_filename=output_file_path
    )

    filtered_df2_offpick = df[(df['SourceFile'] == 'player_pnr_offpick_efficiency.csv')]
    total_pnr_offpick_efficiency = compute_grouped_statistics(filtered_df2_offpick, 'Efficiency for all PNR scorers going OFF screens.', 'Player', 'PNR_Off')

    filtered_df2_rejectpick = df[(df['SourceFile'] == 'player_pnr_rejectpick_efficiency.csv')]
    total_pnr_reject_efficiency = compute_grouped_statistics(filtered_df2_rejectpick, 'Efficiency for all PNR scorers REJECTING screens.', 'Player', 'PNR_Reject')

    # Calculate total proportion and efficiency for High vs Left vs Right screens
    total_pnr_direction_proport_csvs = ['player_pnr_bhhigh_efficiency.csv', 'player_pnr_bhleft_efficiency.csv', 'player_pnr_bhright_efficiency.csv']
    filtered_df3 = df[df['SourceFile'].isin(total_pnr_direction_proport_csvs)]
    total_pnr_direction_proportion = find_play_proportions(filtered_df3, total_pnr_direction_proport_csvs)
    total_pnr_direction_proportion_dict = {'PNR High': total_pnr_direction_proportion[0], 
                                           'PNR Left': total_pnr_direction_proportion[1], 
                                           'PNR Right': total_pnr_direction_proportion[2], 
                                           'Total Plays': total_pnr_direction_proportion[3]}
    
    selected_keys = ['PNR High', 'PNR Left', 'PNR Right']
    total_plays = total_pnr_direction_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_pnr_direction_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'PNR_DirectionLocation_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=2,
        y_max=50,
        title='PNR Direction/Location Frequency',
        output_filename=output_file_path
    )

    filtered_df3_high = df[(df['SourceFile'] == 'player_pnr_bhhigh_efficiency.csv')]
    total_pnr_bhhigh_efficiency = compute_grouped_statistics(filtered_df3_high, 'Efficiency for all PNR scorers on HIGH screens.', 'Player', 'PNR_High')

    filtered_df3_left = df[(df['SourceFile'] == 'player_pnr_bhleft_efficiency.csv')]
    total_pnr_bhleft_efficiency = compute_grouped_statistics(filtered_df3_left, 'Efficiency for all PNR scorers on LEFT screens.', 'Player', 'PNR_Left')

    filtered_df3_right = df[(df['SourceFile'] == 'player_pnr_bhright_efficiency.csv')]
    total_pnr_bhright_efficiency = compute_grouped_statistics(filtered_df3_right, 'Efficiency for all PNR scorers on RIGHT screens.', 'Player', 'PNR_Right')

    # Calculate total proportion and efficiency for BH High --> Rejecting Screens
    filtered_df_bhhigh_reject = df[(df['SourceFile'] == 'player_pnr_bhhigh_rejectpick_efficiency.csv')]
    total_pnr_bhhigh_rejectpick_efficiency = compute_grouped_statistics(filtered_df_bhhigh_reject, 'Efficiency for HIGH PNR scorer REJECTING screens.', 'Player', 'PNR_High_Reject')
    bhhigh_reject_total = 0
    if 'PNR_High_Reject' in total_pnr_bhhigh_rejectpick_efficiency.keys():
        bhhigh_reject_total = total_pnr_bhhigh_rejectpick_efficiency['PNR_High_Reject']['TotalPlays']

    # Calculate total proportion and efficiency for BH High --> OFF Screens
    filtered_df_bhhigh_offpick = df[(df['SourceFile'] == 'player_pnr_bhhigh_offpick_efficiency.csv')]
    total_pnr_bhhigh_offpick_efficiency = compute_grouped_statistics(filtered_df_bhhigh_offpick, 'Efficiency for HIGH PNR scorer going OFF screens.', 'Player', 'PNR_High_Off')
    bhhigh_off_total = 0
    if 'PNR_High_Off' in total_pnr_bhhigh_offpick_efficiency.keys():
        bhhigh_off_total = total_pnr_bhhigh_offpick_efficiency['PNR_High_Off']['TotalPlays']


    # Calculate total proportion and efficiency for BH Left --> Rejecting Screens
    filtered_df_bhleft_reject = df[(df['SourceFile'] == 'player_pnr_bhleft_rejectpick_efficiency.csv')]
    total_pnr_bhleft_rejectpick_efficiency = compute_grouped_statistics(filtered_df_bhleft_reject, 'Efficiency for LEFT PNR scorer REJECTING screens.', 'Player', 'PNR_Left_Reject')
    bhleft_reject_total = 0
    if 'PNR_Left_Reject' in total_pnr_bhleft_rejectpick_efficiency.keys():
        bhleft_reject_total = total_pnr_bhleft_rejectpick_efficiency['PNR_Left_Reject']['TotalPlays']


    # Calculate total proportion and efficiency for BH Left --> OFF Screens
    filtered_df_bhleft_offpick = df[(df['SourceFile'] == 'player_pnr_bhleft_offpick_efficiency.csv')]
    total_pnr_bhleft_offpick_efficiency = compute_grouped_statistics(filtered_df_bhleft_offpick, 'Efficiency for LEFT PNR scorer going OFF screens.', 'Player', 'PNR_Left_Off')
    bhleft_off_total = 0
    if 'PNR_Left_Off' in total_pnr_bhleft_offpick_efficiency.keys():
        bhleft_off_total = total_pnr_bhleft_offpick_efficiency['PNR_Left_Off']['TotalPlays']


    # Calculate total proportion and efficiency for BH Right --> Rejecting Screens
    filtered_df_bhright_reject = df[(df['SourceFile'] == 'player_pnr_bhright_rejectpick_efficiency.csv')]
    total_pnr_bhright_rejectpick_efficiency = compute_grouped_statistics(filtered_df_bhright_reject, 'Efficiency for RIGHT PNR scorer REJECTING screens.', 'Player', 'PNR_Right_Reject')
    bhright_reject_total = 0
    if 'PNR_Right_Reject' in total_pnr_bhright_rejectpick_efficiency.keys():
        bhright_reject_total = total_pnr_bhright_rejectpick_efficiency['PNR_Right_Reject']['TotalPlays']


    # Calculate total proportion and efficiency for BH Right --> OFF Screens
    filtered_df_bhright_offpick = df[(df['SourceFile'] == 'player_pnr_bhright_offpick_efficiency.csv')]
    total_pnr_bhright_offpick_efficiency = compute_grouped_statistics(filtered_df_bhright_offpick, 'Efficiency for RIGHT PNR scorer going OFF screens.', 'Player', 'PNR_Right_Off')
    bhright_off_total = 0
    if 'PNR_Right_Off' in total_pnr_bhright_offpick_efficiency.keys():
        bhright_off_total = total_pnr_bhright_offpick_efficiency['PNR_Right_Off']['TotalPlays']

    combo_dict = {'High-Off': bhhigh_off_total, 'High-Reject': bhhigh_reject_total,
                  'Left-Off': bhleft_off_total, 'Left-Reject': bhleft_reject_total,
                  'Right-Off': bhright_off_total, 'Right-Reject': bhright_reject_total}
    output_file_path = os.path.join(output_directory, 'PNR_Combination_Freq.png')
    
    create_bar_chart(
        data_dict=combo_dict,
        section=2,
        y_max=50,
        title='PNR Combination Frequency',
        output_filename=output_file_path
    )


    # Append all calculated insights to the insight list
    insight.extend([
        total_pnr_efficiency, 
        total_pnr_proportion_dict, 
        total_pnr_offpick_efficiency, 
        total_pnr_reject_efficiency, 
        total_pnr_direction_proportion_dict, 
        total_pnr_bhhigh_efficiency, 
        total_pnr_bhleft_efficiency, 
        total_pnr_bhright_efficiency, 
        total_pnr_bhhigh_rejectpick_efficiency, 
        total_pnr_bhhigh_offpick_efficiency, 
        total_pnr_bhleft_rejectpick_efficiency, 
        total_pnr_bhleft_offpick_efficiency, 
        total_pnr_bhright_rejectpick_efficiency, 
        total_pnr_bhright_offpick_efficiency
    ])

def Iso_scorer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Finds total efficiency for ALL Iso scorer plays
    filtered_df1 = df [ (df['SourceFile'] == 'player_iso_efficiency.csv') ]
    total_iso_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all Iso scorer plays together.', 'Player', 'Iso_Scorer')


    # Calculates total proportion and efficiency for going Left vs Right vs Straight screens
    total_iso_proport_csvs = ['player_iso_left_efficiency.csv', 'player_iso_right_efficiency.csv', 'player_iso_top_efficiency.csv']
    filtered_df2 = df [ df['SourceFile'].isin(total_iso_proport_csvs) ]
    total_iso_proportion = find_play_proportions(filtered_df2, total_iso_proport_csvs)
    total_iso_proportion_dict = {'Iso Left' : total_iso_proportion[0], 'Iso Right': total_iso_proportion[1],
                                'Iso Top': total_iso_proportion[2], 'Total Plays': total_iso_proportion[3], }
    
    selected_keys = ['Iso Left', 'Iso Right', 'Iso Top']
    total_plays = total_iso_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_iso_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'IsoDirectionLocation_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=8,
        y_max=25,
        title='Iso Direction / Location Frequency',
        output_filename=output_file_path
    )

    filtered_df2 = df [ (df['SourceFile'] == 'player_iso_left_efficiency.csv') ]
    total_iso_left_efficiency = compute_grouped_statistics(filtered_df2, 'Efficiency for all Iso scorers going Left.', 'Player', 'Iso_Left')

    filtered_df2 = df [ (df['SourceFile'] == 'player_iso_right_efficiency.csv') ]
    total_iso_right_efficiency = compute_grouped_statistics(filtered_df2, 'Efficiency for all Iso scorers going Right.', 'Player', 'Iso_Right')

    filtered_df2 = df [ (df['SourceFile'] == 'player_iso_top_efficiency.csv') ]
    total_iso_top_efficiency = compute_grouped_statistics(filtered_df2, 'Efficiency for all Iso scorers from Top.', 'Player', 'Iso_Top')

    insight.extend([
        total_iso_efficiency,
        total_iso_proportion_dict,
        total_iso_left_efficiency,
        total_iso_right_efficiency,
        total_iso_top_efficiency
    ])

def Post_scorer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Finds total efficiency for ALL Post scorer plays
    filtered_df1 = df [ (df['SourceFile'] == 'player_post_efficiency.csv') ]
    total_post_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all Post scorer plays together.', 'Player', 'Post_Scorer')

    # Calculates total proportion and efficiency for starting on Left block vs Right block vs Middle
    total_post_proport_csvs = ['player_post_leftblock_efficiency.csv', 'player_post_rightblock_efficiency.csv', 'player_post_middle_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_post_proport_csvs) ]
    total_post_block_proportion = find_play_proportions(filtered_df, total_post_proport_csvs)
    total_post_block_proportion_dict = {'Post Left Block' : total_post_block_proportion[0], 'Post Right Block': total_post_block_proportion[1],
                                'Post Middle': total_post_block_proportion[2], 'Total Plays': total_post_block_proportion[3], }

    selected_keys = ['Post Left Block', 'Post Right Block', 'Post Middle']
    total_plays = total_post_block_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_post_block_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'Post_Location_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=3,
        y_max=50,
        title='Post Location Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_post_leftblock_efficiency.csv') ]
    total_post_leftblock_efficiency = compute_grouped_statistics(filtered_df, 'Post Left Block.', 'Player', 'Post_LeftBlock')

    filtered_df = df [ (df['SourceFile'] == 'player_post_rightblock_efficiency.csv') ]
    total_post_rightblock_efficiency = compute_grouped_statistics(filtered_df, 'Post Right Block', 'Player', 'Post_RightBlock')

    filtered_df = df [ (df['SourceFile'] == 'player_post_middle_efficiency.csv') ]
    total_post_middle_efficiency = compute_grouped_statistics(filtered_df, 'Post Middle', 'Player', 'Post_Middle')


    # Calculates total proportion and efficiency for shooting off Left shoulder vs Right shoulder vs Facing up
    total_post_proport_csvs = ['player_post_leftshoulder_efficiency.csv', 'player_post_rightshoulder_efficiency.csv', 'player_post_faceup_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_post_proport_csvs) ]
    total_post_shoulder_proportion = find_play_proportions(filtered_df, total_post_proport_csvs)
    total_post_shoulder_proportion_dict = {'Post Left Shoulder' : total_post_shoulder_proportion[0], 'Post Right Shoulder': total_post_shoulder_proportion[1],
                                'Post Face Up': total_post_shoulder_proportion[2], 'Total Plays': total_post_shoulder_proportion[3] }
    
    selected_keys = ['Post Left Shoulder', 'Post Right Shoulder', 'Post Face Up']
    total_plays = total_post_shoulder_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_post_shoulder_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'Post_ShotType_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=3,
        y_max=50,
        title='Post Shot Type Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_post_leftshoulder_efficiency.csv') ]
    post_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Left shoulder', 'Player', 'Post_LeftShoulder')

    filtered_df = df [ (df['SourceFile'] == 'player_post_rightshoulder_efficiency.csv') ]
    post_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Right shoulder', 'Player', 'Post_RightShoulder')

    filtered_df = df [ (df['SourceFile'] == 'player_post_faceup_efficiency.csv') ]
    post_faceup_efficiency = compute_grouped_statistics(filtered_df, 'Post Face Up', 'Player', 'Post_Faceup')
    
    
    # Calculates the combinations of post plays
    filtered_df = df[(df['SourceFile'] == 'player_post_leftblock_faceup_efficiency.csv')]
    leftblock_faceup_efficiency = compute_grouped_statistics(filtered_df, 'Post Left Block --> Faceup', 'Player', 'Post_LeftBlock_Faceup')
    leftblock_faceup_total = 0
    for key in leftblock_faceup_efficiency:
        if 'Post_LeftBlock_Faceup' == key:
            leftblock_faceup_total = leftblock_faceup_efficiency['Post_LeftBlock_Faceup']['TotalPlays']

    filtered_df = df[(df['SourceFile'] == 'player_post_leftblock_leftshoulder_efficiency.csv')]
    leftblock_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Left Block --> Left Shoulder', 'Player', 'Post_LeftBlock_LeftShoulder')
    leftblock_leftshoulder_total = 0
    for key in leftblock_leftshoulder_efficiency:
        if 'Post_LeftBlock_LeftShoulder' == key:
            leftblock_leftshoulder_total = leftblock_leftshoulder_efficiency['Post_LeftBlock_LeftShoulder']['TotalPlays']

    filtered_df = df[(df['SourceFile'] == 'player_post_leftblock_rightshoulder_efficiency.csv')]
    leftblock_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Left Block --> Right Shoulder', 'Player', 'Post_LeftBlock_RightShoulder' )
    leftblock_rightshoulder_total = 0
    for key in leftblock_rightshoulder_efficiency:
        if 'Post_LeftBlock_RightShoulder'== key:
            leftblock_rightshoulder_total = leftblock_rightshoulder_efficiency['Post_LeftBlock_RightShoulder']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_faceup_efficiency.csv')]
    rightblock_faceup_efficiency = compute_grouped_statistics(filtered_df, 'Post Right Block --> Faceup', 'Player', 'Post_RightBlock_Faceup')
    rightblock_faceup_total = 0
    for key in rightblock_faceup_efficiency:
        if 'Post_RightBlock_Faceup'== key:
            rightblock_faceup_total = rightblock_faceup_efficiency['Post_RightBlock_Faceup']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_leftshoulder_efficiency.csv')]
    rightblock_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Right Block --> Left Shoulder', 'Player', 'Post_RightBlock_LeftShoulder')
    rightblock_leftshoulder_total = 0
    for key in rightblock_leftshoulder_efficiency:
        if 'Post_RightBlock_LeftShoulder'== key:
            rightblock_leftshoulder_total = rightblock_leftshoulder_efficiency['Post_RightBlock_LeftShoulder']["TotalPlays"]
    

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_rightshoulder_efficiency.csv')]
    rightblock_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Right Block --> Right Shoulder', 'Player', 'Post_RightBlock_RightShoulder')
    rightblock_rightshoulder_total = 0
    for key in rightblock_rightshoulder_efficiency:
        if 'Post_RightBlock_RightShoulder'== key:
            rightblock_rightshoulder_total = rightblock_rightshoulder_efficiency['Post_RightBlock_RightShoulder']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_middle_faceup_efficiency.csv')]
    middle_faceup_efficiency = compute_grouped_statistics(filtered_df, 'Post Middle --> Faceup', 'Player', 'Post_Middle_Faceup')
    middle_faceup_total = 0
    for key in middle_faceup_efficiency:
        if 'Post_Middle_Faceup'== key:
            middle_faceup_total = middle_faceup_efficiency['Post_Middle_Faceup']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_middle_leftshoulder_efficiency.csv')]
    middle_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Middle --> Left Shoulder', 'Player', 'Post_Middle_LeftShoulder')
    middle_leftshoulder_total = 0
    for key in middle_leftshoulder_efficiency:
        if 'Post_Middle_LeftShoulder'== key:
            middle_leftshoulder_total = middle_leftshoulder_efficiency['Post_Middle_LeftShoulder']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_middle_rightshoulder_efficiency.csv')]
    middle_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Middle --> Right Shoulder', 'Player', 'Post_Middle_RightShoulder')
    middle_rightshoulder_total = 0
    for key in middle_rightshoulder_efficiency:
        if 'Post_Middle_RightShoulder'== key:
            middle_rightshoulder_total = middle_rightshoulder_efficiency['Post_Middle_RightShoulder']["TotalPlays"]
        
    combo_dict = {'LeftBlock - FaceUp': leftblock_faceup_total, 'LeftBlock - LeftShoulder': leftblock_leftshoulder_total, 'LeftBlock - RightShoulder': leftblock_rightshoulder_total,
                  'RightBlock - FaceUp': rightblock_faceup_total, 'RightBlock - LeftShoulder': rightblock_leftshoulder_total, 'RightBlock - RightShoulder': rightblock_rightshoulder_total,
                  'Middle - FaceUp': middle_faceup_total, 'Middle - LeftShoulder': middle_leftshoulder_total, 'Middle - RightShoulder': middle_rightshoulder_total}
    output_file_path = os.path.join(output_directory, 'Post_Combination_Freq.png')
        
    create_bar_chart(
        data_dict=combo_dict,
        section=3,
        y_max=25,
        title='Post Combination Frequency',
        output_filename=output_file_path
    )

    insight.extend([
        total_post_efficiency,
        total_post_block_proportion_dict,
        total_post_leftblock_efficiency,
        total_post_rightblock_efficiency,
        total_post_middle_efficiency,
        total_post_shoulder_proportion_dict,
        post_leftshoulder_efficiency,
        post_rightshoulder_efficiency,
        post_faceup_efficiency,
        leftblock_faceup_efficiency,
        leftblock_leftshoulder_efficiency,
        leftblock_rightshoulder_efficiency,
        rightblock_faceup_efficiency,
        rightblock_leftshoulder_efficiency,
        rightblock_rightshoulder_efficiency,
        middle_faceup_efficiency,
        middle_leftshoulder_efficiency,
        middle_rightshoulder_efficiency
    ])

def Cut_scorer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Finds total efficiency for ALL Cutter scorer plays
    filtered_df = df [ (df['SourceFile'] == 'player_cut_efficiency.csv') ]
    total_cut_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all cutting scorer plays together.', 'Player', 'Cut_Scorer')

    # Calculates total proportion and efficiency for Basket vs Flash vs Screen cuts
    total_cut_proport_csvs = ['player_cut_basket_efficiency.csv', 'player_cut_flash_efficiency.csv', 'player_cut_screen_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_cut_proport_csvs) ]
    total_cut_proportion = find_play_proportions(filtered_df, total_cut_proport_csvs)
    total_cut_proportion_dict = {'Basket Cut' : total_cut_proportion[0], 'Flash Cut': total_cut_proportion[1],
                                'Screen Cut': total_cut_proportion[2], 'Total Plays': total_cut_proportion[3], }
    
    selected_keys = ['Basket Cut', 'Flash Cut', 'Screen Cut']
    total_plays = total_cut_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_cut_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'Cut_Type_Freq.png')
    
    # Call create_bar_chart with the corrected arguments
    create_bar_chart(
        data_dict=data_to_plot,
        section=1,
        y_max=50,
        title='Cut Type Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_cut_basket_efficiency.csv') ]
    total_cut_basket_efficiency = compute_grouped_statistics(filtered_df, 'Basket Cut', 'Player', 'Basket_Cuts')

    filtered_df = df [ (df['SourceFile'] == 'player_cut_flash_efficiency.csv') ]
    total_cut_flash_efficiency = compute_grouped_statistics(filtered_df, 'Flash Cut', 'Player', 'Flash_Cuts')

    filtered_df = df [ (df['SourceFile'] == 'player_cut_screen_efficiency.csv') ]
    total_cut_screen_efficiency = compute_grouped_statistics(filtered_df, 'Screen Cut', 'Player', 'Screen_Cuts')
    
    insight.extend([
        total_cut_efficiency,
        [total_cut_proportion_dict],
        total_cut_basket_efficiency,
        total_cut_flash_efficiency,
        total_cut_screen_efficiency
    ])

def Spotup_scorer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Finds total efficiency for ALL Spotup scorer plays
    filtered_df = df [ (df['SourceFile'] == 'player_spotup_efficiency.csv') ]
    total_spotup_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all Spotup scorer plays together.', 'Player', 'SpotUp_Scorer')

    # Calculates total proportion and efficiency for starting on Jumpers vs Drives
    total_spotup_proport_csvs = ['player_spotup_jumpshot_efficiency.csv', 'player_spotup_leftdrive_efficiency.csv', 'player_spotup_rightdrive_efficiency.csv', 'player_spotup_straightdrive_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_spotup_proport_csvs) ]
    total_spotup_proportion = find_play_proportions(filtered_df, total_spotup_proport_csvs)
    total_spotup_proportion_dict = {'Jumpshot' : total_spotup_proportion[0], 'Drive': total_spotup_proportion[1] + total_spotup_proportion[2] + total_spotup_proportion[3],
                                    'Total Plays': total_spotup_proportion[4], }
    
    selected_keys = ['Jumpshot', 'Drive']
    total_plays = total_spotup_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_spotup_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'SpotUp_PlayType_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=5,
        y_max=50,
        title='Spot Up Play Type Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_spotup_jumpshot_efficiency.csv') ]
    total_spotup_jumpshot_efficiency = compute_grouped_statistics(filtered_df, 'Jumpshot', 'Player', 'SpotUp_Jumper')

    total_drive_csvs = ['player_spotup_leftdrive_efficiency.csv', 'player_spotup_rightdrive_efficiency.csv', 'player_spotup_straightdrive_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(total_drive_csvs))]
    total_spotup_drive_efficiency = compute_grouped_statistics(filtered_df, 'Drives', 'Player', 'SpotUp_Drive')


    filtered_df = df [ (df['SourceFile'] == 'player_spotup_leftdrive_efficiency.csv') ]
    total_spotup_leftdrive_efficiency = compute_grouped_statistics(filtered_df, 'Left Drive', 'Player', 'SpotUp_LeftDrive')
    total_spotup_leftdrive_total = 0
    if 'SpotUp_LeftDrive' in total_spotup_leftdrive_efficiency.keys():
        total_spotup_leftdrive_total = total_spotup_leftdrive_efficiency['SpotUp_LeftDrive']['TotalPlays']
    

    filtered_df = df [ (df['SourceFile'] == 'player_spotup_rightdrive_efficiency.csv') ]
    total_spotup_rightdrive_efficiency = compute_grouped_statistics(filtered_df, 'Right Drive', 'Player', 'SpotUp_RightDrive')
    total_spotup_rightdrive_total = 0
    if 'SpotUp_RightDrive' in total_spotup_rightdrive_efficiency.keys():
        total_spotup_rightdrive_total = total_spotup_rightdrive_efficiency['SpotUp_RightDrive']['TotalPlays']
   

    filtered_df = df [ (df['SourceFile'] == 'player_spotup_straightdrive_efficiency.csv') ]
    total_spotup_straightdrive_efficiency = compute_grouped_statistics(filtered_df, 'Straight Drive', 'Player', 'SpotUp_StraightDrive')
    total_spotup_straightdrive_total = 0
    if 'SpotUp_StraightDrive' in total_spotup_straightdrive_efficiency.keys():
        total_spotup_straightdrive_total = total_spotup_straightdrive_efficiency['SpotUp_StraightDrive']['TotalPlays']

    combo_dict = {'Left': total_spotup_leftdrive_total,
                  'Right': total_spotup_rightdrive_total,
                  'Straight': total_spotup_straightdrive_total}
    output_file_path = os.path.join(output_directory, 'SpotUp_DriveDirection_Freq.png')
    create_bar_chart(
        data_dict=combo_dict,
        section=5,
        y_max=50,
        title='Spot Up Drive Direction Frequency',
        output_filename=output_file_path
    )


    insight.extend([total_spotup_efficiency,
                total_spotup_proportion_dict,
                total_spotup_jumpshot_efficiency,
                total_spotup_drive_efficiency,
                total_spotup_leftdrive_efficiency,
                total_spotup_rightdrive_efficiency,
                total_spotup_straightdrive_efficiency
                ])

def Transition_scorer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Calculates total proportion and efficiency for Transition plays
    total_transition_proport_csvs = ['player_transition_bh_efficiency.csv', 'player_transition_leakouts_efficiency.csv', 
                                    'player_transition_leftwing_efficiency.csv', 'player_transition_rightwing_efficiency.csv', 'player_transition_trailer_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_transition_proport_csvs) ]
    total_transition_proportion = find_play_proportions(filtered_df, total_transition_proport_csvs)
    total_transition_proportion_dict = {'Ball Handler' : total_transition_proportion[0], 'Leakouts': total_transition_proportion[1],
                                        'Leftwing': total_transition_proportion[2], 'Rightwing' : total_transition_proportion[3], 
                                        'Trailer': total_transition_proportion[4], 'Total Plays': total_transition_proportion[5] }
    total_transition_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all transition scorer plays together.', 'Player', 'Transition_Scorer')

    selected_keys = ['Ball Handler', 'Leakouts', 'Leftwing', 'Rightwing', 'Trailer' ]
    total_plays = total_transition_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_transition_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'Transition_Type_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=9,
        y_max=50,
        title='Transition Type Frequency',
        output_filename=output_file_path
    )


    filtered_df = df [ (df['SourceFile'] == 'player_transition_bh_efficiency.csv') ]
    total_transition_bh_efficiency = compute_grouped_statistics(filtered_df, 'Transition BH', 'Player', 'Transition_BH')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_leakouts_efficiency.csv') ]
    total_transition_leakouts_efficiency = compute_grouped_statistics(filtered_df, 'Transition Leakouts', 'Player', 'Transition_Leakouts')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_leftwing_efficiency.csv') ]
    total_transition_leftwing_efficiency = compute_grouped_statistics(filtered_df, 'Transition Left Wing', 'Player', 'Transition_LeftWing')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_rightwing_efficiency.csv') ]
    total_transition_rightwing_efficiency = compute_grouped_statistics(filtered_df, 'Transition Right Wing', 'Player', 'Transition_RightWing')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_trailer_efficiency.csv') ]
    total_transition_trailer_efficiency = compute_grouped_statistics(filtered_df, 'Transition Trailer', 'Player', 'Transition_Trailer')

    insight.extend([
        total_transition_proportion_dict,
        total_transition_efficiency,
        total_transition_bh_efficiency,
        total_transition_leakouts_efficiency,
        total_transition_leftwing_efficiency,
        total_transition_rightwing_efficiency,
        total_transition_trailer_efficiency
    ])

def Offscreen_scorer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Finds total efficiency for ALL Off Screen scorer plays
    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_efficiency.csv') ]
    total_offscreens_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all Off Screen scorer plays together.', 'Player', 'OffScreen_Scorer')

    # Calculates total proportion and efficiency for handoffs going Left vs Right vs Top
    total_offscreens_proport_csvs = ['player_offscreens_leftshoulder_efficiency.csv', 'player_offscreens_rightshoulder_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_offscreens_proport_csvs) ]
    total_offscreens_proportion = find_play_proportions(filtered_df, total_offscreens_proport_csvs)
    total_offscreens_proportion_dict = {'Off Screen Left Shoulder' : total_offscreens_proportion[0], 'Off Screen Right Shoulder': total_offscreens_proportion[1],
                                'Total Plays': total_offscreens_proportion[2] }
    
    selected_keys = ['Off Screen Left Shoulder', 'Off Screen Right Shoulder']
    total_plays = total_offscreens_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_offscreens_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'OffScreen_Shoulder_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=6,
        y_max=50,
        title='Off Screen Running Off Shoulder Frequency',
        output_filename=output_file_path
    )
    

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_efficiency.csv') ]
    total_offscreens_left_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Left', 'Player', 'OffScreen_LeftShoulder')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_efficiency.csv') ]
    total_offscreens_right_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Right', 'Player', 'OffScreen_RightShoulder')

    # Calculates total proportion and efficiency for Flares vs Straight vs Curls
    total_offscreens_type_proport_csvs = ['player_offscreens_flare_efficiency.csv', 'player_offscreens_straight_efficiency.csv', 'player_offscreens_curl_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_offscreens_type_proport_csvs) ]
    total_offscreens_type_proportion = find_play_proportions(filtered_df, total_offscreens_type_proport_csvs)
    total_offscreens_type_proportion_dict = {'Flare' : total_offscreens_type_proportion[0], 'Straight': total_offscreens_type_proportion[1],
                                        'Curl': total_offscreens_type_proportion[2], 'Total Plays': total_offscreens_type_proportion[3] }
        
    selected_keys = ['Flare', 'Straight', 'Curl']
    total_plays = total_offscreens_type_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_offscreens_type_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'OffScreen_Type_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=6,
        y_max=50,
        title='Off Screen Type Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_flare_efficiency.csv') ]
    total_offscreens_flare_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Flare', 'Player', 'Flare')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_straight_efficiency.csv') ]
    total_offscreens_straight_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Straight', 'Player', 'Straight')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_curl_efficiency.csv') ]
    total_offscreens_curl_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Curl', 'Player', 'Curl')

    # Calculates total proportion and efficiency for combinations of direction and type of off screen
    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_flare_efficiency.csv') ]
    total_offscreens_left_flare_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Left --> Flare', 'Player', 'LeftShoulder_Flare')
    offscreens_left_flare_total = 0
    if 'LeftShoulder_Flare' in total_offscreens_left_flare_efficiency.keys():
        offscreens_left_flare_total = total_offscreens_left_flare_efficiency['LeftShoulder_Flare']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_straight_efficiency.csv') ]
    total_offscreens_left_straight_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Left --> Straight', 'Player', 'LeftShoulder_Straight')
    offscreens_left_straight_total = 0
    if 'LeftShoulder_Straight' in total_offscreens_left_straight_efficiency.keys():
        offscreens_left_straight_total = total_offscreens_left_straight_efficiency['LeftShoulder_Straight']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_curl_efficiency.csv') ]
    total_offscreens_left_curl_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Left --> Curl', 'Player', 'LeftShoulder_Curl')
    offscreens_left_curl_total = 0
    if 'LeftShoulder_Curl' in total_offscreens_left_curl_efficiency.keys():
        offscreens_left_curl_total = total_offscreens_left_curl_efficiency['LeftShoulder_Curl']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_flare_efficiency.csv') ]
    total_offscreens_right_flare_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Right --> Flare', 'Player', 'RightShoulder_Flare')
    offscreens_right_flare_total = 0
    if 'RightShoulder_Flare' in total_offscreens_right_flare_efficiency.keys():
        offscreens_right_flare_total = total_offscreens_right_flare_efficiency['RightShoulder_Flare']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_straight_efficiency.csv') ]
    total_offscreens_right_straight_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Right --> Straight', 'Player', 'RightShoulder_Straight')
    offscreens_right_straight_total = 0
    if 'RightShoulder_Straight' in total_offscreens_right_straight_efficiency.keys():
        offscreens_right_straight_total = total_offscreens_right_straight_efficiency['RightShoulder_Straight']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_curl_efficiency.csv') ]
    total_offscreens_right_curl_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Right --> Curl', 'Player', 'RightShoulder_Curl')
    offscreens_right_curl_total = 0
    if 'RightShoulder_Curl' in total_offscreens_right_curl_efficiency.keys():
        offscreens_right_curl_total = total_offscreens_right_curl_efficiency['RightShoulder_Curl']['TotalPlays']
    
    
    combo_dict = {'Left Shoulder - Flare': offscreens_left_flare_total, 'Left Shoulder - Straight': offscreens_left_straight_total, 'Left Shoulder': offscreens_left_curl_total,
                  'Right Shoulder - Flare': offscreens_right_flare_total, 'Right Shoulder - Straight': offscreens_right_straight_total, 'Right Shoulder': offscreens_right_curl_total}
    output_file_path = os.path.join(output_directory, 'OffScreen_Combination_Freq.png')
    create_bar_chart(
        data_dict=combo_dict,
        section=6,
        y_max=25,
        title='Off Screen Combination Frequency',
        output_filename=output_file_path
    )

    insight.extend([
        total_offscreens_efficiency,
        total_offscreens_proportion_dict,
        total_offscreens_left_efficiency,
        total_offscreens_right_efficiency,
        total_offscreens_flare_efficiency,
        total_offscreens_straight_efficiency,
        total_offscreens_curl_efficiency,
        total_offscreens_left_flare_efficiency,
        total_offscreens_left_straight_efficiency,
        total_offscreens_left_curl_efficiency,
        total_offscreens_right_flare_efficiency,
        total_offscreens_right_straight_efficiency,
        total_offscreens_right_curl_efficiency
    ])
    
def Handoff_scorer_stats(df: pd.DataFrame, name, insight, output_directory):
    # Finds total efficiency for ALL Handoff scorer plays
    filtered_df1 = df [ (df['SourceFile'] == 'player_handoffs_efficiency.csv') ]
    total_handoffs_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all Handoff scorer plays together.', 'Player', 'Handoff_Scorer')

    # Calculates total proportion and efficiency for handoffs going Left vs Right vs Top
    total_handoffs_proport_csvs = ['player_handoffs_bhleft_efficiency.csv', 'player_handoffs_bhright_efficiency.csv', 'player_handoffs_top_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_handoffs_proport_csvs) ]
    total_handoffs_proportion = find_play_proportions(filtered_df, total_handoffs_proport_csvs)
    total_handoffs_proportion_dict = {'Handoff Left' : total_handoffs_proportion[0], 'Handoff Right': total_handoffs_proportion[1],
                                'Handoff from Top': total_handoffs_proportion[2], 'Total Plays': total_handoffs_proportion[3], }

    selected_keys = ['Handoff Left', 'Handoff Right', 'Handoff from Top']
    total_plays = total_handoffs_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_handoffs_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'HandOff_Direction_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=7,
        y_max=50,
        title='Hand Off Directio Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhleft_efficiency.csv') ]
    total_handoffs_left_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Left', 'Player', 'BHLeft')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhright_efficiency.csv') ]
    total_handoffs_right_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Right', 'Player', 'BHRight')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_top_efficiency.csv') ]
    total_handoffs_top_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Top', 'Player', 'BHTop')
    
    
    # Calculates total proportion and efficiency of Dribble handoffs vs Stationary Handoffs
    total_handoffs_type_proport_csvs = ['player_handoffs_stationary_efficiency.csv', 'player_handoffs_dribble_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_handoffs_type_proport_csvs) ]
    total_handoffs_type_proportion = find_play_proportions(filtered_df, total_handoffs_type_proport_csvs)
    total_handoffs_type_proportion_dict = {'Handoffs Stationary' : total_handoffs_type_proportion[0], 'Handoffs Dribble': total_handoffs_type_proportion[1],
                                'Total Plays': total_handoffs_type_proportion[2], }
    
    selected_keys = ['Handoffs Stationary', 'Handoffs Dribble']
    total_plays = total_handoffs_type_proportion_dict['Total Plays']
    data_to_plot = {
        key: int(total_handoffs_type_proportion_dict[key] * total_plays)
        for key in selected_keys
    }
    output_file_path = os.path.join(output_directory, 'HandOff_Type_Freq.png')
    
    create_bar_chart(
        data_dict=data_to_plot,
        section=7,
        y_max=50,
        title='Hand Off Type Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_stationary_efficiency.csv') ]
    total_handoffs_stationary_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Stationary', 'Player', 'Stationary')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_dribble_efficiency.csv') ]
    total_handoffs_dribble_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Dribble', 'Player', 'Dribble')
    
    
    # Calculates combinations  of type of handoff and direction
    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhleft_stationary_efficiency.csv') ]
    total_handoffs_stationary_left_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Left --> Stationary', 'Player', 'Left_Stationary')
    handoffs_stationary_left_total = 0
    if 'Left_Stationary' in total_handoffs_stationary_left_efficiency.keys():
        handoffs_stationary_left_total = total_handoffs_stationary_left_efficiency['Left_Stationary']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhright_stationary_efficiency.csv') ]
    total_handoffs_stationary_right_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Right --> Stationary', 'Player', 'Right_Stationary')
    handoffs_stationary_right_total = 0
    if 'Right_Stationary' in total_handoffs_stationary_right_efficiency.keys():
        handoffs_stationary_right_total =total_handoffs_stationary_right_efficiency['Right_Stationary']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_top_stationary_efficiency.csv') ]
    total_handoffs_stationary_top_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Top --> Stationary', 'Player', 'Top_Stationary')
    handoffs_stationary_top_total = 0
    if 'Top_Stationary' in total_handoffs_stationary_top_efficiency.keys():
        handoffs_stationary_top_total = total_handoffs_stationary_top_efficiency['Top_Stationary']['TotalPlays']


    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhleft_dribble_efficiency.csv') ]
    total_handoffs_dribble_left_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Left --> Dribble', 'Player', 'Left_Dribble')
    handoffs_dribble_left_total = 0
    if 'Left_Dribble' in total_handoffs_dribble_left_efficiency.keys():
        handoffs_dribble_left_total = total_handoffs_dribble_left_efficiency['Left_Dribble']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhright_dribble_efficiency.csv') ]
    total_handoffs_dribble_right_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Right --> Dribble', 'Player', 'Right_Dribble')
    handoffs_dribble_right_total = 0
    if 'Right_Dribble' in total_handoffs_dribble_right_efficiency.keys():
        handoffs_dribble_right_total = total_handoffs_dribble_right_efficiency['Right_Dribble']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_top_dribble_efficiency.csv') ]
    total_handoffs_dribble_top_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Top --> Dribble', 'Player', 'Top_Dribble')
    handoffs_dribble_top_total = 0
    if 'Top_Dribble' in total_handoffs_dribble_top_efficiency.keys():
        handoffs_dribble_top_total = total_handoffs_dribble_top_efficiency['Top_Dribble']['TotalPlays']
        
    combo_dict = {'Stationary - Left': handoffs_stationary_left_total, 'Stationary - Right': handoffs_stationary_right_total, 'Stationary - Top': handoffs_stationary_top_total,
                  'Dribble - Left': handoffs_dribble_left_total, 'Stationary - Right': handoffs_dribble_right_total, 'Stationary - Top': handoffs_dribble_top_total}
    output_file_path = os.path.join(output_directory, 'HandOff_Combination_Freq.png')
    create_bar_chart(
        data_dict=combo_dict,
        section=7,
        y_max=25,
        title='Hand Off Combination Frequency',
        output_filename=output_file_path
    )

    insight.extend([
        total_handoffs_efficiency,
        total_handoffs_proportion_dict, 
        total_handoffs_left_efficiency, 
        total_handoffs_right_efficiency, 
        total_handoffs_top_efficiency,
        total_handoffs_type_proportion_dict, 
        total_handoffs_stationary_efficiency, 
        total_handoffs_dribble_efficiency, 
        total_handoffs_stationary_left_efficiency, 
        total_handoffs_stationary_right_efficiency, 
        total_handoffs_stationary_top_efficiency, 
        total_handoffs_dribble_left_efficiency, 
        total_handoffs_dribble_right_efficiency, 
        total_handoffs_dribble_top_efficiency
])


def compute_grouped_statistics(df, statdescription, playertype, key):
    """
    Groups efficiency statistics by 'PrimaryPlayer' and returns a dictionary with the aggregated statistics.

    :param df: Input DataFrame containing basketball statistics data.
    :param statdescription: Description for the statistics. 
    :return: Dictionary with grouped statistics, grouped by 'PrimaryPlayer'.
    """

    # Group by 'PrimaryPlayer' and aggregate statistics
    grouped_stats = df.groupby(playertype).agg({
        'TotalPlays': 'sum',
        'Total3ptShots': 'sum',
        'Total3ptMakes': 'sum',
        '3pt%': 'mean',
        'Total2ptShots': 'sum',
        'Total2ptMakes': 'sum',
        '2pt%': 'mean',
        'TotalMidRangeShots': 'sum',
        'TotalMidRangeMakes': 'sum',
        'MidRange%': 'mean',
        'EFG%': 'mean',
        'Turnover': 'sum',
        'Foul': 'sum'
    }).reset_index()

    # Initialize a dictionary to store the results for each player
    stats_dict = {}

    # Loop through the rows of the grouped statistics DataFrame
    for _, row in grouped_stats.iterrows():
        three_perc = float(row['3pt%'])
        two_perc = float(row['2pt%'])
        midrange_perc = float(row['MidRange%'])
                           
        if int(row['Total3ptShots']) != 0:
            three_perc = float( (row['Total3ptMakes'] / row['Total3ptShots']) * 100 )
        if int(row['Total2ptShots']) != 0:
            two_perc = float( (row['Total2ptMakes'] / row['Total2ptShots']) * 100 )
        if int(row['TotalMidRangeShots']) != 0:
            midrange_perc = float( (row['TotalMidRangeMakes'] / row['TotalMidRangeShots']) * 100 )
        
        stats_dict[key] = {
            'StatDescription': statdescription,
            'TotalPlays': int(row['TotalPlays']),
            'Total3ptShots': int(row['Total3ptShots']),
            'Total3ptMakes': int(row['Total3ptMakes']),
            '3pt%': three_perc,
            'Total2ptShots': int(row['Total2ptShots']),
            'Total2ptMakes': int(row['Total2ptMakes']),
            '2pt%': two_perc,
            'TotalMidRangeShots': int(row['TotalMidRangeShots']),
            'TotalMidRangeMakes': int(row['TotalMidRangeMakes']),
            'MidRange%': midrange_perc,
            'EFG%': float(row['EFG%']),
            'Turnover': int(row['Turnover']),
            'Foul': int(row['Foul'])
        }

    return stats_dict

def find_play_proportions(df, sourcefile_list):
    """
    Finds the total play proportions based on the given 'SourceFile' value lists.

    :param df: Input DataFrame containing the data.
    :param sourcefile_list: List containing 'SourceFile' values.
    :return: List of proportions of total plays for each 'SourceFile' value.
    """
    total_plays_all = 0
    play_totals = []

    # Calculate the total plays for each 'SourceFile' value
    for sourcefile in sourcefile_list:
        filtered_df = df[df['SourceFile'] == sourcefile]
        if filtered_df.empty:
            play_totals.append(0)
            continue
        total_plays = filtered_df['TotalPlays'].sum()
        play_totals.append(total_plays)
        total_plays_all += total_plays

    # Calculate the proportions for each 'SourceFile'
    proportions = [float(total) / float(total_plays_all) if total_plays_all > 0 else 0 for total in play_totals]

    # Convert total_plays_all to native int before appending
    proportions.append(int(total_plays_all))

    return proportions

def find_player_proportions(df, sourcefile, player_col):
    """
    Calculates the proportion of total plays each SecondaryPlayer was involved in and rounds it to 2 decimal places.

    :param df: Input DataFrame containing 'SecondaryPlayer' and 'TotalPlays' columns.
    :return: Dictionary where keys are 'SecondaryPlayer' and values are their proportion of total plays (rounded to 2 decimal places).
    """
    player_dict = {}
    total_plays = 0

    if df.empty:
        return player_dict

    filtered_df = df[df['SourceFile'].isin(sourcefile)]

    if filtered_df.empty:
        return player_dict

    # Aggregate plays for each player
    grouped = filtered_df.groupby(player_col)['TotalPlays'].sum().reset_index()

    for _, row in grouped.iterrows():
        player = row[player_col]
        plays = row['TotalPlays']
        player_dict[player] = plays
        total_plays += plays

    # Convert counts to proportions
    for player in player_dict:
        player_dict[player] = round(float(player_dict[player]) / float(total_plays), 2)

    return player_dict

def find_player_efficiency(df, sourcefile, player, proportion, playertype):
    """
    Finds player efficiency statistics based on a specific 'SourceFile' and 'SecondaryPlayer'.

    :param df: Input DataFrame containing basketball statistics data.
    :param sourcefile: Specific value to filter by in the 'SourceFile' column.
    :param secondaryplayer: Specific secondary player to filter by in the 'SecondaryPlayer' column.
    :param proportion: Proportion of plays involving the player.
    :return: Dictionary with the player's efficiency statistics and the play proportion.
    """

    # Filter the DataFrame where 'SourceFile' matches and 'SecondaryPlayer' matches
    filtered_df = df[(df['SourceFile'].isin(sourcefile)) & (df[playertype] == player)]

    # If no data is found, return an empty dictionary
    if filtered_df.empty:
        return {}

    # Group data and aggregate statistics (should return only one row since we filtered specifically)
    grouped_stats = filtered_df.agg({
        'TotalPlays': 'sum',
        'Total3ptShots': 'sum',
        'Total3ptMakes': 'sum',
        '3pt%': 'mean',
        'Total2ptShots': 'sum',
        'Total2ptMakes': 'sum',
        '2pt%': 'mean',
        'TotalMidRangeShots': 'sum',
        'TotalMidRangeMakes': 'sum',
        'MidRange%': 'mean',
        'EFG%': 'mean',
        'Turnover': 'sum',
        'Foul': 'sum'
    })

    three_perc = float(grouped_stats['3pt%'])
    two_perc = float(grouped_stats['2pt%'])
    midrange_perc = float(grouped_stats['MidRange%'])
                        
    if int(grouped_stats['Total3ptShots']) != 0:
        three_perc = float( (grouped_stats['Total3ptMakes'] / grouped_stats['Total3ptShots']) * 100 )
    if int(grouped_stats['Total2ptShots']) != 0:
        two_perc = float( (grouped_stats['Total2ptMakes'] / grouped_stats['Total2ptShots']) * 100 )
    if int(grouped_stats['TotalMidRangeShots']) != 0:
        midrange_perc = float( (grouped_stats['TotalMidRangeMakes'] / grouped_stats['TotalMidRangeShots']) * 100 )

    # Create a dictionary with the aggregated statistics
    stats_dict = {
        'Player': player_name,
        'TotalPlays': int(grouped_stats['TotalPlays']),
        'Total3ptShots': int(grouped_stats['Total3ptShots']),
        'Total3ptMakes': int(grouped_stats['Total3ptMakes']),
        '3pt%': three_perc,
        'Total2ptShots': int(grouped_stats['Total2ptShots']),
        'Total2ptMakes': int(grouped_stats['Total2ptMakes']),
        '2pt%': two_perc,
        'TotalMidRangeShots': int(grouped_stats['TotalMidRangeShots']),
        'TotalMidRangeMakes': int(grouped_stats['TotalMidRangeMakes']),
        'MidRange%': midrange_perc,
        'EFG%': float(grouped_stats['EFG%']),
        'Turnover': int(grouped_stats['Turnover']),
        'Foul': int(grouped_stats['Foul']),
        'playproportion': proportion  # Add play proportion to the dictionary
    }

    return stats_dict

    
def replace_nan_and_round_percentages(obj):
    """
    Recursively traverse the input object, replacing NaN values with '-'
    and rounding numeric values to two decimal places for keys containing '%'.
    
    Args:
        obj (dict or list or other): The input data structure.
        
    Returns:
        The processed data structure with NaNs replaced and percentages rounded.
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            if '%' in key:
                # Handle keys containing '%'
                if isinstance(value, float):
                    if math.isnan(value):
                        new_dict[key] = '-'
                    else:
                        new_dict[key] = round(value, 2)
                elif isinstance(value, str):
                    if value.strip().lower() == 'nan':
                        new_dict[key] = '-'
                    else:
                        try:
                            # Attempt to convert to float and round
                            numeric_value = float(value)
                            new_dict[key] = round(numeric_value, 2)
                        except ValueError:
                            # If conversion fails, retain original value
                            new_dict[key] = value
                elif isinstance(value, int):
                    # Convert integer to float and round
                    new_dict[key] = round(float(value), 2)
                elif isinstance(value, (dict, list)):
                    # Recursively process nested structures
                    new_dict[key] = replace_nan_and_round_percentages(value)
                else:
                    # For other types, retain original value
                    new_dict[key] = value
            else:
                # Handle keys not containing '%'
                if isinstance(value, float):
                    if math.isnan(value):
                        new_dict[key] = '-'
                    else:
                        new_dict[key] = value
                elif isinstance(value, str):
                    if value.strip().lower() == 'nan':
                        new_dict[key] = '-'
                    else:
                        new_dict[key] = value
                elif isinstance(value, (dict, list)):
                    # Recursively process nested structures
                    new_dict[key] = replace_nan_and_round_percentages(value)
                else:
                    new_dict[key] = value
        return new_dict
    elif isinstance(obj, list):
        return [replace_nan_and_round_percentages(item) for item in obj]
    else:
        # For non-dict and non-list items, handle NaN replacements if necessary
        if isinstance(obj, float):
            if math.isnan(obj):
                return '-'
            else:
                return obj
        elif isinstance(obj, str):
            if obj.strip().lower() == 'nan':
                return '-'
            else:
                return obj
        else:
            return obj

def write_insights_to_json(insights, output_file):
    """
    Process the insights data by replacing NaN values and rounding percentages,
    then write the cleaned data to a JSON file.
    """
    # Clean the data
    clean_insights = replace_nan_and_round_percentages(insights)
    
    # Write to JSON file with indentation for readability
    with open(output_file, 'w') as f:
        json.dump(clean_insights, f, indent=4)

    
if __name__ == "__main__":
    # Example usage: python player_data_analyzer.py file1.csv file2.csv ... output_directory
    if len(sys.argv) < 2:
        print("Usage: python player_data_analyzer.py <player_file.csv> <output_directory>")
        sys.exit(1)

    # Extract command-line arguments
    player_file = os.path.join("/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/cleaned/Teams/player_data/Rochester_Institute_of_Technology_Tigers/", sys.argv[1])
    output_directory = "/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/cleaned/reports/"


    print(f"Processing Player File: {player_file}")
    
    base_filename = os.path.basename(player_file)  # Extracts 'firstname_lastname.csv'
    name_part = os.path.splitext(base_filename)[0]  # Removes '.csv' -> 'firstname_lastname'
    player_name = name_part.replace('_', '-')  # 'firstname-lastname'
    
    # 2. Get the current date
    current_datetime = datetime.now()
    month = current_datetime.strftime("%m")
    day = current_datetime.strftime("%d")
    year = current_datetime.strftime("%Y")
        
    # 3. Create the folder name
    foldername = f"{player_name}-{month}-{day}-{year}"
    
    player_output_folder = os.path.join(output_directory, foldername)
    os.makedirs(player_output_folder, exist_ok=True)
    
    image_output_folder = os.path.join(player_output_folder, 'images')
    os.makedirs(image_output_folder, exist_ok=True)
    
    # Run the function
    insights = analyze_player_performance(player_file, image_output_folder)
    
    # Specify the path for the output insights JSON file
    output_insights_file = os.path.join(player_output_folder, 'insights_4.json')

    # Write the insights to the JSON file
    write_insights_to_json(insights, output_insights_file)
