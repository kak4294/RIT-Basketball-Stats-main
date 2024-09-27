import pandas as pd
import sys
import os

def analyze_player_performance(file_list):
    # Load the CSV file into a DataFrame
    for file in file_list:
        # Split player data by role
        primary_df, secondary_df, scorer_df, player_name = split_player_data_by_role(file)
        
        # Initialize insight lists for different categories
        PNR_insights = []
        Cut_insights = []
        Handoff_insights = []
        Post_insights = []
        Spotup_insights = []
        Transition_insights = []
        Offscreen_insights = []
        Iso_insights = []
        Rollman_insights = []
        
        # Combine all insights into a single list
        insights = [PNR_insights, Cut_insights, Handoff_insights, Post_insights, 
                    Spotup_insights, Transition_insights, Offscreen_insights, 
                    Iso_insights, Rollman_insights]
        
        # Process insights for primary, secondary, and scorer roles
        process_primary_stats(primary_df, player_name, insights)
        process_secondary_stats(secondary_df, player_name, insights)
        process_scorer_stats(scorer_df, player_name, insights)
        
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


def process_primary_stats(df: pd.DataFrame, name, insights):
    # Iterate through the types of insights
    for i in range(8):
        if i == 0:  # PNR insights
            PNR_passer_stats(df, name, insights[i])
        elif i == 7:  # Iso insights
            Iso_passer_stats(df, name, insights[i])
        elif i == 3:  # Post insights
            Post_passer_stats(df, name, insights[i])

def PNR_passer_stats(df: pd.DataFrame, name, insight):
    # Calculates total passing proportion and efficiency for secondary plays out of a pick n roll
    total_passing_proport_csvs = ['twoplayer_pnr_cut_efficiency.csv', 'twoplayer_pnr_spotupsdrives_efficiency.csv', 'twoplayer_pnr_spotupsjumpers_efficiency.csv', 'player_rollman_efficiency.csv' ]
    filtered_df1 = df[(df['SourceFile'].isin(total_passing_proport_csvs)) & (df['PrimaryPlayer'] == name)]
    total_passing_proportion = find_play_proportions(filtered_df1, total_passing_proport_csvs)
    
    total_passing_proportion_dict = {
        'Pass PNR Cut': total_passing_proportion[0], 
        'Pass PNR Spotup Drive': total_passing_proportion[1],
        'Pass PNR Spotup Jumper': total_passing_proportion[2], 
        'Pass PNR Rollman': total_passing_proportion[3], 
        'Total Plays': total_passing_proportion[4]
    }
    total_passing_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all PNR secondary plays together.', 'PrimaryPlayer')
    
    # Extend the current insight list
    insight.extend([
        total_passing_proportion_dict, 
        total_passing_efficiency])
    
    # Additional insights for left, right, and high PNRs
    PNR_bhhigh_passer_stats(df, name, insight)
    PNR_bhleft_passer_stats(df, name, insight)
    PNR_bhright_passer_stats(df, name, insight)

def PNR_bhhigh_passer_stats(df: pd.DataFrame, name, insight):
    # Calculates proportion and efficiency for various PNR plays (cutters, spot-up drivers, rollman, etc.)
    
    # Cutters off high pick n roll
    bhhighpassing_cut_csv = ['twoplayer_pnrbhhigh_cuts_efficiency.csv']
    filtered_df5 = df[(df['SourceFile'].isin(bhhighpassing_cut_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_cut_player_proportion = find_player_proportions(filtered_df5, bhhighpassing_cut_csv, 'SecondaryPlayer')
    
    for player in bhhighpassing_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df5, bhhighpassing_cut_csv, player, bhhighpassing_cut_player_proportion[player], 'SecondaryPlayer' )
        bhhighpassing_cut_player_proportion[player] = player_data

    outer_dict1 = {'BH High PNR --> Cuts': bhhighpassing_cut_player_proportion}
    insight.extend([outer_dict1])

    # Spot-up drivers off high pick n roll
    bhhighpassing_spotupdrives_csv = ['twoplayer_pnrbhhigh_spotupdrives_efficiency.csv']
    filtered_df6 = df[(df['SourceFile'].isin(bhhighpassing_spotupdrives_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_spotupdrives_player_proportion = find_player_proportions(filtered_df6, bhhighpassing_spotupdrives_csv, 'SecondaryPlayer')

    for player in bhhighpassing_spotupdrives_player_proportion:
        player_data = find_player_efficiency(filtered_df6, bhhighpassing_spotupdrives_csv, player, bhhighpassing_spotupdrives_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_spotupdrives_player_proportion[player] = player_data

    outer_dict2 = {'BH High PNR --> Spotup Drives': bhhighpassing_spotupdrives_player_proportion}
    insight.extend([outer_dict2])

    # Spot-up shooters off high pick n roll
    bhhighpassing_spotupjumpers_csv = ['twoplayer_pnrbhhigh_spotupjumper_efficiency.csv']
    filtered_df7 = df[(df['SourceFile'].isin(bhhighpassing_spotupjumpers_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_spotupjumpers_player_proportion = find_player_proportions(filtered_df7, bhhighpassing_spotupjumpers_csv, 'SecondaryPlayer')

    for player in bhhighpassing_spotupjumpers_player_proportion:
        player_data = find_player_efficiency(filtered_df7, bhhighpassing_spotupjumpers_csv, player, bhhighpassing_spotupjumpers_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_spotupjumpers_player_proportion[player] = player_data

    outer_dict3 = {'BH High PNR --> Spotup Jumpers': bhhighpassing_spotupjumpers_player_proportion}
    insight.extend([outer_dict3])

    # Rollman rolling off high pick n roll
    bhhighpassing_rollmanrolls_csv = ['twoplayer_pnrbhhigh_rollmanrolls_efficiency.csv']
    filtered_df8 = df[(df['SourceFile'].isin(bhhighpassing_rollmanrolls_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_rollmanrolls_player_proportion = find_player_proportions(filtered_df8, bhhighpassing_rollmanrolls_csv, 'SecondaryPlayer')

    for player in bhhighpassing_rollmanrolls_player_proportion:
        player_data = find_player_efficiency(filtered_df8, bhhighpassing_rollmanrolls_csv, player, bhhighpassing_rollmanrolls_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_rollmanrolls_player_proportion[player] = player_data

    outer_dict4 = {'BH High PNR --> Rollman Rolls': bhhighpassing_rollmanrolls_player_proportion}
    insight.extend([outer_dict4])

    # Rollman slips off high pick n roll
    bhhighpassing_rollmanslips_csv = ['twoplayer_pnrbhhigh_rollmanslips_efficiency.csv']
    filtered_df9 = df[(df['SourceFile'].isin(bhhighpassing_rollmanslips_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_rollmanslips_player_proportion = find_player_proportions(filtered_df9, bhhighpassing_rollmanslips_csv, 'SecondaryPlayer')

    for player in bhhighpassing_rollmanslips_player_proportion:
        player_data = find_player_efficiency(filtered_df9, bhhighpassing_rollmanslips_csv, player, bhhighpassing_rollmanslips_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_rollmanslips_player_proportion[player] = player_data

    outer_dict5 = {'BH High PNR --> Rollman Slips': bhhighpassing_rollmanslips_player_proportion}
    insight.extend([outer_dict5])

    # Rollman pops off high pick n roll
    bhhighpassing_rollmanpops_csv = ['twoplayer_pnrbhhigh_rollmanpops_efficiency.csv']
    filtered_df10 = df[(df['SourceFile'].isin(bhhighpassing_rollmanpops_csv)) & (df['PrimaryPlayer'] == name)]
    bhhighpassing_rollmanpops_player_proportion = find_player_proportions(filtered_df10, bhhighpassing_rollmanpops_csv, 'SecondaryPlayer')

    for player in bhhighpassing_rollmanpops_player_proportion:
        player_data = find_player_efficiency(filtered_df10, bhhighpassing_rollmanpops_csv, player, bhhighpassing_rollmanpops_player_proportion[player], 'SecondaryPlayer')
        bhhighpassing_rollmanpops_player_proportion[player] = player_data

    outer_dict6 = {'BH High PNR --> Rollman Pops': bhhighpassing_rollmanpops_player_proportion}
    insight.extend([outer_dict6])

def PNR_bhleft_passer_stats(df: pd.DataFrame, name, insight):  
    # Calculates proportion and efficiency of a player hitting a specific second player (cutter) off of a high pick n roll
    pnrpasser_cut_csv = ['twoplayer_pnrbhleft_cuts_efficiency.csv']
    filtered_df1 = df[(df['SourceFile'].isin(pnrpasser_cut_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_cut_player_proportion = find_player_proportions(filtered_df1, pnrpasser_cut_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df1, pnrpasser_cut_csv, player, pnrpasser_cut_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_cut_player_proportion[player] = player_data

    outer_dict1 = {'BH Left PNR --> Cuts': pnrpasser_cut_player_proportion}
    insight.extend([outer_dict1])

    # Spot up drivers
    pnrpasser_spotupdrives_csv = ['twoplayer_pnrbhleft_spotupdrives_efficiency.csv']
    filtered_df2 = df[(df['SourceFile'].isin(pnrpasser_spotupdrives_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_spotupdrives_player_proportion = find_player_proportions(filtered_df2, pnrpasser_spotupdrives_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_spotupdrives_player_proportion:
        player_data = find_player_efficiency(filtered_df2, pnrpasser_spotupdrives_csv, player, pnrpasser_spotupdrives_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_spotupdrives_player_proportion[player] = player_data

    outer_dict2 = {'BH Left PNR --> Spotup Drives': pnrpasser_spotupdrives_player_proportion}
    insight.extend([outer_dict2])

    # Spot up jumpers
    pnrpasser_spotupjumper_csv = ['twoplayer_pnrbhleft_spotupjumper_efficiency.csv']
    filtered_df3 = df[(df['SourceFile'].isin(pnrpasser_spotupjumper_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_spotupjumper_player_proportion = find_player_proportions(filtered_df3, pnrpasser_spotupjumper_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_spotupjumper_player_proportion:
        player_data = find_player_efficiency(filtered_df3, pnrpasser_spotupjumper_csv, player, pnrpasser_spotupjumper_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_spotupjumper_player_proportion[player] = player_data

    outer_dict3 = {'BH Left PNR --> Spotup Jumpers': pnrpasser_spotupjumper_player_proportion}
    insight.extend([outer_dict3])

    # Rollman rolls
    pnrpasser_rollmanrolls_csv = ['twoplayer_pnrbhleft_rollmanrolls_efficiency.csv']
    filtered_df4 = df[(df['SourceFile'].isin(pnrpasser_rollmanrolls_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanrolls_player_proportion = find_player_proportions(filtered_df4, pnrpasser_rollmanrolls_csv)
    
    for player in pnrpasser_rollmanrolls_player_proportion:
        player_data = find_player_efficiency(filtered_df4, pnrpasser_rollmanrolls_csv, player, pnrpasser_rollmanrolls_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanrolls_player_proportion[player] = player_data

    outer_dict4 = {'BH Left PNR --> Rollman Rolls': pnrpasser_rollmanrolls_player_proportion}
    insight.extend([outer_dict4])

    # Rollman slips
    pnrpasser_rollmanslips_csv = ['twoplayer_pnrbhleft_rollmanslips_efficiency.csv']
    filtered_df5 = df[(df['SourceFile'].isin(pnrpasser_rollmanslips_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanslips_player_proportion = find_player_proportions(filtered_df5, pnrpasser_rollmanslips_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_rollmanslips_player_proportion:
        player_data = find_player_efficiency(filtered_df5, pnrpasser_rollmanrolls_csv, player, pnrpasser_rollmanslips_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanslips_player_proportion[player] = player_data

    outer_dict5 = {'BH Left PNR --> Rollman Slips': pnrpasser_rollmanslips_player_proportion}
    insight.extend([outer_dict5])

    # Rollman pops
    pnrpasser_rollmanpops_csv = ['twoplayer_pnrbhleft_rollmanpops_efficiency.csv']
    filtered_df6 = df[(df['SourceFile'] == pnrpasser_rollmanpops_csv) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanpops_player_proportion = find_player_proportions(filtered_df6, pnrpasser_rollmanpops_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_rollmanpops_player_proportion:
        player_data = find_player_efficiency(filtered_df6, pnrpasser_rollmanpops_csv, player, pnrpasser_rollmanpops_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanpops_player_proportion[player] = player_data

    outer_dict6 = {'BH Left PNR --> Rollman Pops': pnrpasser_rollmanpops_player_proportion}
    insight.extend([outer_dict6])

def PNR_bhright_passer_stats(df: pd.DataFrame, name, insight):
    # Calculates proportion and efficiency of a player hitting a specific second player (cutter) off of a high pick n roll
    pnrpasser_cut_csv = ['twoplayer_pnrbhright_cuts_efficiency.csv']
    filtered_df1 = df[(df['SourceFile'].isin(pnrpasser_cut_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_cut_player_proportion = find_player_proportions(filtered_df1, pnrpasser_cut_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df1, pnrpasser_cut_csv, player, pnrpasser_cut_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_cut_player_proportion[player] = player_data

    outer_dict1 = {'BH Right PNR --> Cuts': pnrpasser_cut_player_proportion}
    insight.extend([outer_dict1])

    # Spot up drivers
    pnrpasser_spotupdrives_csv = ['twoplayer_pnrbhright_spotupdrives_efficiency.csv']
    filtered_df2 = df[(df['SourceFile'].isin(pnrpasser_spotupdrives_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_spotupdrives_player_proportion = find_player_proportions(filtered_df2, pnrpasser_spotupdrives_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_spotupdrives_player_proportion:
        player_data = find_player_efficiency(filtered_df2, pnrpasser_spotupdrives_csv, player, pnrpasser_spotupdrives_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_spotupdrives_player_proportion[player] = player_data

    outer_dict2 = {'BH Right PNR --> Spotup Drives': pnrpasser_spotupdrives_player_proportion}
    insight.extend([outer_dict2])

    # Spot up jumpers
    pnrpasser_spotupjumper_csv = ['twoplayer_pnrbhright_spotupjumper_efficiency.csv']
    filtered_df3 = df[(df['SourceFile'].isin(pnrpasser_spotupjumper_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_spotupjumper_player_proportion = find_player_proportions(filtered_df3, pnrpasser_spotupjumper_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_spotupjumper_player_proportion:
        player_data = find_player_efficiency(filtered_df3, pnrpasser_spotupjumper_csv, player, pnrpasser_spotupjumper_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_spotupjumper_player_proportion[player] = player_data

    outer_dict3 = {'BH Right PNR --> Spotup Jumpers': pnrpasser_spotupjumper_player_proportion}
    insight.extend([outer_dict3])

    # Rollman rolls
    pnrpasser_rollmanrolls_csv = ['twoplayer_pnrbhright_rollmanrolls_efficiency.csv']
    filtered_df4 = df[(df['SourceFile'].isin(pnrpasser_rollmanrolls_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanrolls_player_proportion = find_player_proportions(filtered_df4, pnrpasser_rollmanrolls_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_rollmanrolls_player_proportion:
        player_data = find_player_efficiency(filtered_df4, pnrpasser_rollmanrolls_csv, player, pnrpasser_rollmanrolls_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanrolls_player_proportion[player] = player_data

    outer_dict4 = {'BH Right PNR --> Rollman Rolls': pnrpasser_rollmanrolls_player_proportion}
    insight.extend([outer_dict4])

    # Rollman slips
    pnrpasser_rollmanslips_csv = ['twoplayer_pnrbhright_rollmanslips_efficiency.csv']
    filtered_df5 = df[(df['SourceFile'].isin(pnrpasser_rollmanslips_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanslips_player_proportion = find_player_proportions(filtered_df5, pnrpasser_rollmanslips_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_rollmanslips_player_proportion:
        player_data = find_player_efficiency(filtered_df5, pnrpasser_rollmanrolls_csv, player, pnrpasser_rollmanslips_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanslips_player_proportion[player] = player_data

    outer_dict5 = {'BH Right PNR --> Rollman Slips': pnrpasser_rollmanslips_player_proportion}
    insight.extend([outer_dict5])

    # Rollman pops
    pnrpasser_rollmanpops_csv = ['twoplayer_pnrbhright_rollmanpops_efficiency.csv']
    filtered_df6 = df[(df['SourceFile'].isin(pnrpasser_rollmanpops_csv)) & (df['PrimaryPlayer'] == name)]
    pnrpasser_rollmanpops_player_proportion = find_player_proportions(filtered_df6, pnrpasser_rollmanpops_csv, 'SecondaryPlayer')
    
    for player in pnrpasser_rollmanpops_player_proportion:
        player_data = find_player_efficiency(filtered_df6, pnrpasser_rollmanpops_csv, player, pnrpasser_rollmanpops_player_proportion[player], 'SecondaryPlayer')
        pnrpasser_rollmanpops_player_proportion[player] = player_data

    outer_dict6 = {'BH Right PNR --> Rollman Pops': pnrpasser_rollmanpops_player_proportion}
    insight.extend([outer_dict6])

def Iso_passer_stats(df: pd.DataFrame, name, insight):
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
    total_passing_efficiency = compute_grouped_statistics(filtered_df0, 'Efficiency for all ISO secondary plays together.', 'PrimaryPlayer')

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

def Post_passer_stats(df: pd.DataFrame, name, insight):
    total_passing_proport_csvs = ['twoplayer_post_cut_efficiency.csv', 
                                'twoplayer_post_spotupdrives_efficiency.csv', 
                                'twoplayer_post_spotupjumper_efficiency.csv']
    filtered_df0 = df[(df['SourceFile'].isin(total_passing_proport_csvs)) & (df['PrimaryPlayer'] == name)]
    total_passing_proportion = find_play_proportions(filtered_df0, total_passing_proport_csvs)
    total_passing_proportion_dict = {
        'Pass POST Cut': total_passing_proportion[0], 
        'Pass POST Spotup Drive': total_passing_proportion[1],
        'Pass POST Spotup Jumper': total_passing_proportion[2],  
        'Total Plays': total_passing_proportion[3]
    }
    total_passing_efficiency = compute_grouped_statistics(filtered_df0, 'Efficiency for all POST secondary plays together.', 'PrimaryPlayer')


    postpasser_cut_csv = ['twoplayer_post_cut_efficiency.csv']
    filtered_df1 = df[(df['SourceFile'].isin(postpasser_cut_csv)) & (df['PrimaryPlayer'] == name)]
    postpasser_cut_player_proportion = find_player_proportions(filtered_df1, postpasser_cut_csv, 'SecondaryPlayer')
    for player in postpasser_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df1, postpasser_cut_csv, player, postpasser_cut_player_proportion[player], 'SecondaryPlayer')
        postpasser_cut_player_proportion[player] = player_data

    postpasser_spotupdrives_csv = ['twoplayer_post_spotupdrives_efficiency.csv']
    filtered_df2 = df[(df['SourceFile'].isin(postpasser_spotupdrives_csv)) & (df['PrimaryPlayer'] == name)]
    postpasser_spotupdrives_player_proportion = find_player_proportions(filtered_df2, postpasser_spotupdrives_csv, 'SecondaryPlayer')
    for player in postpasser_spotupdrives_player_proportion:
        player_data = find_player_efficiency(filtered_df2, postpasser_spotupdrives_csv, player, postpasser_spotupdrives_player_proportion[player], 'SecondaryPlayer')
        postpasser_spotupdrives_player_proportion[player] = player_data

    postpasser_spotupjumper_csv = ['twoplayer_post_spotupjumpers_efficiency.csv']
    filtered_df3 = df[(df['SourceFile'].isin(postpasser_spotupjumper_csv)) & (df['PrimaryPlayer'] == name)]
    postpasser_spotupjumper_player_proportion = find_player_proportions(filtered_df3, postpasser_spotupjumper_csv, 'SecondaryPlayer')
    for player in postpasser_spotupjumper_player_proportion:
        player_data = find_player_efficiency(filtered_df3, postpasser_spotupjumper_csv, player, postpasser_spotupjumper_player_proportion[player], 'SecondaryPlayer')
        postpasser_spotupjumper_player_proportion[player] = player_data
    
    insight.extend([
        total_passing_proportion_dict,
        total_passing_efficiency,
        postpasser_cut_player_proportion,
        postpasser_spotupdrives_player_proportion,
        postpasser_spotupjumper_player_proportion
    ])    
    
    
    
def process_secondary_stats(df: pd.DataFrame, name, insights):
    for i in range(8):
        insight = insights[i]
        if i == 8:  # Rollman insights
            Rollman_secondary_stats(df, name, insight)
        elif i == 1:  # Cut insights
            Cut_secondary_stats(df, name, insight)
        elif i == 4:  # Spotup insights
            Spotup_secondary_stats(df, name, insight)

def Rollman_secondary_stats(df: pd.DataFrame, name, insight):
    
    # Calculates total proportion and efficiency for Rollman plays
    filtered_df = df [ (df['SourceFile'] == 'player_rollman_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_rollman_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Total Efficiency', 'SecondaryPlayer')


    # Calculates proportion / efficiency for rollman Slips vs Rolls vs Pops
    total_rollman_type_proport_csvs = ['player_rollman_slip_efficiency.csv', 'player_rollman_roll_efficiency.csv',
                                    'player_rollman_pop_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_rollman_type_proport_csvs) & (df['SecondaryPlayer'] == name) ]
    total_rollman_type_proportion = find_play_proportions(filtered_df, total_rollman_type_proport_csvs)
    total_rollman_type_proportion_dict = {'Rollman Slip%' : total_rollman_type_proportion[0], 'Rollman Roll%': total_rollman_type_proportion[1],
                                        'Rollman Pop%': total_rollman_type_proportion[2], 'Total Plays': total_rollman_type_proportion[3] }
    total_rollman_type_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all Rollman scorer plays together.', 'SecondaryPlayer')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_slip_efficiency.csv')  & (df['SecondaryPlayer'] == name) ]
    total_slip_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Slip', 'SecondaryPlayer')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_roll_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_roll_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Roll', 'SecondaryPlayer')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_pop_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_pop_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Pop', 'SecondaryPlayer')
    
    
    # Calculates proportion / efficiency for Left Drives vs Right Drives for SLIPS
    total_rollman_direction_proport_csvs = ['player_rollman_leftdrive_slip_efficiency.csv', 'player_rollman_rightdrive_slip_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_rollman_direction_proport_csvs) & (df['SecondaryPlayer'] == name) ]
    total_rollman_direction_proportion = find_play_proportions(filtered_df, total_rollman_direction_proport_csvs)
    total_rollman_direction_proportion_dict = {'Rollman Slip --> Left%' : total_rollman_direction_proportion[0], 'Rollman Slip --> Right%': total_rollman_direction_proportion[1],
                                            'Total Plays': total_rollman_direction_proportion[2] }
    total_rollman_direction_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all Rollman drive plays together.', 'SecondaryPlayer')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_leftdrive_slip_efficiency.csv')  & (df['SecondaryPlayer'] == name) ]
    total_slip_left_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Slip --> Left', 'SecondaryPlayer')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_rightdrive_slip_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_slip_right_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Slip --> Right', 'SecondaryPlayer')


    # Calculates proportion / efficiency for Left Drives vs Right Drives for POPS
    total_rollman_direction_pop_proport_csvs = ['player_rollman_leftdrive_pop_efficiency.csv', 'player_rollman_rightdrive_pop_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_rollman_direction_pop_proport_csvs) & (df['SecondaryPlayer'] == name) ]
    total_rollman_direction_pop_proportion = find_play_proportions(filtered_df, total_rollman_direction_pop_proport_csvs)
    total_rollman_direction_pop_proportion_dict = {'Rollman Pop --> Left%' : total_rollman_direction_pop_proportion[0], 'Rollman Pop --> Right%': total_rollman_direction_pop_proportion[1],
                                            'Total Plays': total_rollman_direction_pop_proportion[2] }
    total_rollman_direction_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all Rollman drive plays together off of Pops.', 'SecondaryPlayer')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_leftdrive_pop_efficiency.csv')  & (df['SecondaryPlayer'] == name) ]
    total_pop_left_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Pop --> Left', 'SecondaryPlayer')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_rightdrive_pop_efficiency.csv') & (df['SecondaryPlayer'] == name) ]
    total_pop_right_efficiency = compute_grouped_statistics(filtered_df, 'Rollman Pop --> Right', 'SecondaryPlayer')


    # Calculates proportion and efficiency of rollman based on which player passed them the ball
    rollman_player_csv = 'player_rollman_efficiency.csv'
    filtered_df = df [ (df['SourceFile'] == rollman_player_csv) & (df['SecondaryPlayer'] == name)]
    rollman_player_proportion = find_player_proportions(filtered_df, rollman_player_csv, 'PrimaryPlayer')
    for player in rollman_player_proportion:
        player_data = find_player_efficiency(filtered_df, rollman_player_csv, player, rollman_player_proportion[player], 'PrimaryPlayer' )
        rollman_player_proportion[player] = player_data

    outer_dict1 = {'PNR --> Rollman': rollman_player_proportion}


    rollman_slip_player_csv = 'player_rollman_slip_efficiency.csv'
    filtered_df = df [ (df['SourceFile'] == rollman_slip_player_csv) & (df['SecondaryPlayer'] == name)]
    rollman_slip_player_proportion = find_player_proportions(filtered_df, rollman_slip_player_csv, 'PrimaryPlayer')
    for player in rollman_slip_player_proportion:
        player_data = find_player_efficiency(filtered_df, rollman_slip_player_csv, player, rollman_slip_player_proportion[player], 'PrimaryPlayer' )
        rollman_slip_player_proportion[player] = player_data

    outer_dict2 = {'PNR --> Rollman Slip': rollman_slip_player_proportion}


    rollman_pop_player_csv = 'player_rollman_pop_efficiency.csv'
    filtered_df = df [ (df['SourceFile'] == rollman_pop_player_csv) & (df['SecondaryPlayer'] == name)]
    rollman_pop_player_proportion = find_player_proportions(filtered_df, rollman_pop_player_csv, 'PrimaryPlayer')
    for player in rollman_pop_player_proportion:
        player_data = find_player_efficiency(filtered_df, rollman_pop_player_csv, player, rollman_pop_player_proportion[player], 'PrimaryPlayer' )
        rollman_pop_player_proportion[player] = player_data

    outer_dict3 = {'PNR --> Rollman Pop': rollman_pop_player_proportion}


    rollman_roll_player_csv = 'player_rollman_roll_efficiency.csv'
    filtered_df = df [ (df['SourceFile'] == rollman_roll_player_csv) & (df['SecondaryPlayer'] == name)]
    rollman_roll_player_proportion_dict = find_player_proportions(filtered_df, rollman_roll_player_csv, 'PrimaryPlayer')
    for player in rollman_roll_player_proportion_dict:
        player_data = find_player_efficiency(filtered_df, rollman_roll_player_csv, player, rollman_roll_player_proportion_dict[player], 'PrimaryPlayer' )
        rollman_roll_player_proportion_dict[player] = player_data

    outer_dict4 = {'PNR --> Rollman Roll': rollman_roll_player_proportion_dict}
    
    insight.extend([
        total_rollman_efficiency,
        total_rollman_type_proportion_dict,
        total_rollman_type_efficiency,
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

def Cut_secondary_stats(df: pd.DataFrame, name, insight):
    # Finds total efficiency for ALL secondary cutter plays
    second_cut_csvs = ['twoplayer_iso_cut_efficiency.csv', 'twoplayer_pnr_cut_efficiency.csv', 'twoplayer_post_cut_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(second_cut_csvs)) & (df['SecondaryPlayer'] == name) ]
    total_cut_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all secondary cutter plays.', 'SecondaryPlayer')

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
    iso_cut_efficiency = compute_grouped_statistics(iso_cut_efficiency_df, 'Efficiency for all Isos leading to secondary cutter plays.', 'SecondaryPlayer')
    iso_cut_player_proportion = find_player_proportions(iso_cut_efficiency_df, iso_cut_efficiency_csv, 'PrimaryPlayer')
    for player in iso_cut_player_proportion:
        player_data = find_player_efficiency(iso_cut_efficiency_df, iso_cut_efficiency_csv, player, iso_cut_player_proportion[player], 'PrimaryPlayer')
        iso_cut_player_proportion[player] = player_data

    pnr_cut_efficiency_csv = ['twoplayer_pnr_cut_efficiency.csv']
    pnr_cut_efficiency_df = df [ (df['SourceFile'].isin(pnr_cut_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnr_cut_efficiency = compute_grouped_statistics(pnr_cut_efficiency_df, 'Efficiency for all PNRs leading to secondary cutter plays.', 'SecondaryPlayer')
    pnr_cut_player_proportion = find_player_proportions(pnr_cut_efficiency_df, pnr_cut_efficiency_csv, 'PrimaryPlayer')
    for player in pnr_cut_player_proportion:
        player_data = find_player_efficiency(pnr_cut_efficiency_df, pnr_cut_efficiency_csv, player, pnr_cut_player_proportion[player], 'PrimaryPlayer')
        pnr_cut_player_proportion[player] = player_data

    post_cut_efficiency_csv = ['twoplayer_post_cut_efficiency.csv']
    post_cut_efficiency_df = df [ (df['SourceFile'].isin(post_cut_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    post_cut_efficiency = compute_grouped_statistics(post_cut_efficiency_df, 'Efficiency for all Post ups leading to secondary cutter plays.', 'SecondaryPlayer')
    post_cut_player_proportion = find_player_proportions(post_cut_efficiency_df, post_cut_efficiency_csv, 'PrimaryPlayer')
    for player in post_cut_player_proportion:
        player_data = find_player_efficiency(post_cut_efficiency_df, post_cut_efficiency_csv, player, post_cut_player_proportion[player], 'PrimaryPlayer')
        post_cut_player_proportion[player] = player_data
        
    # Calculates total proportion and efficiency of all directions in PNR leading to a cut.
    total_pnr_direction_proport_csvs = ['twoplayer_pnrbhhigh_cuts_efficiency.csv', 'twoplayer_pnrbhright_cuts_efficiency', 'twoplayer_pnrbhright_cuts_efficiency.csv', ]
    filtered_df = df [ (df['SourceFile'].isin(total_pnr_direction_proport_csvs)) & (df['SecondaryPlayer'] == name)  ]
    total_pnr_direction_proportion = find_play_proportions(filtered_df, total_cut_proport_csvs)
    total_pnr_direction_proportion_dict = {'High PNR --> Cut' : total_cut_proportion[0] , 'Right PNR --> Cut': total_cut_proportion[1],
                                'Left PNR --> Cut': total_cut_proportion[2] , 'Total Plays': total_cut_proportion[3] }


    pnrbhhigh_cut_efficiency_csv = ['twoplayer_pnrbhhigh_cuts_efficiency.csv']
    pnrbhhigh_cut_efficiency_df = df [ (df['SourceFile'].isin(pnrbhhigh_cut_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnrbhhigh_cut_efficiency = compute_grouped_statistics(pnrbhhigh_cut_efficiency_df, 'Efficiency for all High PNRs leading to secondary cutter plays.', 'SecondaryPlayer')
    pnrbhhigh_cut_player_proportion = find_player_proportions(pnrbhhigh_cut_efficiency_df, pnrbhhigh_cut_efficiency_csv, 'PrimaryPlayer')
    for player in pnrbhhigh_cut_player_proportion:
        player_data = find_player_efficiency(pnrbhhigh_cut_efficiency_df, pnrbhhigh_cut_efficiency_csv, player, pnrbhhigh_cut_player_proportion[player], 'PrimaryPlayer')
        pnrbhhigh_cut_player_proportion[player] = player_data


    pnrbhright_cut_efficiency_csv = ['twoplayer_pnrbhright_cuts_efficiency.csv']
    pnrbhright_cut_efficiency_df = df [ (df['SourceFile'].isin(pnrbhright_cut_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnrbhright_cut_efficiency = compute_grouped_statistics(pnrbhright_cut_efficiency_df, 'Efficiency for all Right PNRs leading to secondary cutter plays.', 'SecondaryPlayer')
    pnrbhright_cut_player_proportion = find_player_proportions(pnrbhright_cut_efficiency_df, pnrbhright_cut_efficiency_csv, 'PrimaryPlayer')
    for player in pnrbhright_cut_player_proportion:
        player_data = find_player_efficiency(pnrbhright_cut_efficiency_df, pnrbhright_cut_efficiency_csv, player, pnrbhright_cut_player_proportion[player], 'PrimaryPlayer')
        pnrbhright_cut_player_proportion[player] = player_data


    pnrbhleft_cut_efficiency_csv = ['twoplayer_pnrbhleft_cuts_efficiency.csv']
    pnrbhleft_cut_efficiency_df = df [ (df['SourceFile'].isin(pnrbhleft_cut_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnrbhleft_cut_efficiency = compute_grouped_statistics(pnrbhleft_cut_efficiency_df, 'Efficiency for all Left PNRs leading to secondary cutter plays.', 'SecondaryPlayer')
    pnrbhleft_cut_player_proportion = find_player_proportions(pnrbhleft_cut_efficiency_df, pnrbhleft_cut_efficiency_csv, 'PrimaryPlayer')
    for player in pnrbhleft_cut_player_proportion:
        player_data = find_player_efficiency(pnrbhleft_cut_efficiency_df, pnrbhleft_cut_efficiency_csv, player, pnrbhleft_cut_player_proportion[player], 'PrimaryPlayer')
        pnrbhleft_cut_player_proportion[player] = player_data
        
        
    insight.extend([
        total_cut_efficiency,
        total_cut_proportion_dict,
        iso_cut_efficiency,
        pnr_cut_efficiency,
        post_cut_efficiency,
        total_pnr_direction_proportion,
        total_pnr_direction_proportion_dict,
        pnrbhhigh_cut_efficiency,
        pnrbhright_cut_efficiency,
        pnrbhleft_cut_efficiency
    ])

def Spotup_secondary_stats(df: pd.DataFrame, name, insight):
    # Finds total efficiency for ALL secondary cutter plays
    second_spotup_csvs = ['twoplayer_iso_spotupdrives_efficiency.csv', 'twoplayer_iso_spotupjumpers_efficiency.csv', 
                    'twoplayer_pnr_spotupdrives_efficiency.csv', 'twoplayer_pnr_spotupsjumpers_efficiency.csv',
                    'twoplayer_post_spotupdrive_efficiency.csv', 'twoplayer_post_spotupjumper_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(second_spotup_csvs)) & (df['SecondaryPlayer'] == name) ]
    total_spotup_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all secondary Spot Up plays.', 'SecondaryPlayer')

    # Calculates total proportion and efficiency of each type of play leading to a spot up drive. Including unknown passers.
    total_spotupdrives_proport_csvs = ['twoplayer_iso_spotupdrives_efficiency.csv', 'twoplayer_pnr_spotupdrives_efficiency.csv', 'twoplayer_post_spotupdrive_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(total_spotupdrives_proport_csvs)) & (df['SecondaryPlayer'] == name)  ]
    total_spotupdrives_proportion = find_play_proportions(filtered_df, total_spotupdrives_proport_csvs)

    unknown_passer_csv = ['player_spotup_drive_efficiency.csv']
    unknown_passer_df = df [ (df['SourceFile'].isin(unknown_passer_csv)) & (df['Player'] == name) ]
    total_unknown_proportion = find_play_proportions(unknown_passer_df, unknown_passer_csv)

    if total_unknown_proportion[1] == 0:
        percent_known_passer = 1
    else: 
        percent_known_passer = float(total_spotupdrives_proportion[3]) / float(total_unknown_proportion[1])
    percent_unknown_passer = 1 - percent_known_passer
    total_spotupdrives_proportion_dict = {'Iso --> Spot Up Drives' : (total_spotupdrives_proportion[0] * percent_known_passer), 
                                        'PNR --> Spot Up Drives': (total_spotupdrives_proportion[1] * percent_known_passer),
                                        'Post --> Spot Up Drives': (total_spotupdrives_proportion[2] * percent_known_passer), 
                                        'Unknown --> Spot Up Drives': percent_unknown_passer,
                                        'Total Plays': total_unknown_proportion[1] 
                                        }

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
    total_spotupjumpers_proportion_dict = {'Iso --> Spot Up Jumpers' : (total_spotupjumpers_proportion[0] * percent_known_passer), 
                                        'PNR --> Spot Up Jumpers': (total_spotupjumpers_proportion[1] * percent_known_passer),
                                        'Post --> Spot Up Jumpers': (total_spotupjumpers_proportion[2] * percent_known_passer), 
                                        'Unknown --> Spot Up Jumpers': percent_unknown_passer,
                                        'Total Plays': total_unknown_proportion[1] 
                                        }

    iso_spotupdrives_efficiency_csv = ['twoplayer_iso_spotupdrives_efficiency.csv']
    iso_spotupdrives_efficiency_df = df [ (df['SourceFile'].isin(iso_spotupdrives_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    iso_spotupdrives_efficiency = compute_grouped_statistics(iso_spotupdrives_efficiency_df, 'Efficiency for all Isos leading to secondary Spot up drives plays.', 'SecondaryPlayer')
    iso_spotupdrives_player_proportion = find_player_proportions(iso_spotupdrives_efficiency_df, iso_spotupdrives_efficiency_csv, 'PrimaryPlayer')
    for player in iso_spotupdrives_player_proportion:
        player_data = find_player_efficiency(iso_spotupdrives_efficiency_df, iso_spotupdrives_efficiency_csv, player, iso_spotupdrives_player_proportion[player], 'PrimaryPlayer')
        iso_spotupdrives_player_proportion[player] = player_data

    iso_spotupjumpers_efficiency_csv = ['twoplayer_iso_spotupjumpers_efficiency.csv']
    iso_spotupjumpers_efficiency_df = df [ (df['SourceFile'].isin(iso_spotupjumpers_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    iso_spotupjumpers_efficiency = compute_grouped_statistics(iso_spotupjumpers_efficiency_df, 'Efficiency for all Isos leading to secondary Spot up jumpers plays.', 'SecondaryPlayer')
    iso_spotupjumpers_player_proportion = find_player_proportions(iso_spotupjumpers_efficiency_df, iso_spotupjumpers_efficiency_csv, 'PrimaryPlayer')
    for player in iso_spotupjumpers_player_proportion:
        player_data = find_player_efficiency(iso_spotupjumpers_efficiency_df, iso_spotupjumpers_efficiency_csv, player, iso_spotupjumpers_player_proportion[player], 'PrimaryPlayer')
        iso_spotupjumpers_player_proportion[player] = player_data


    pnr_spotupsdrives_efficiency_csv = ['twoplayer_pnr_spotupsdrives_efficiency.csv']
    pnr_spotupdrives_efficiency_df = df [ (df['SourceFile'].isin(pnr_spotupsdrives_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnr_spotupdrives_efficiency = compute_grouped_statistics(pnr_spotupdrives_efficiency_df, 'Efficiency for all PNRs leading to secondary Spot up drives plays.', 'SecondaryPlayer')
    pnr_spotupdrives_player_proportion = find_player_proportions(pnr_spotupdrives_efficiency_df, pnr_spotupsdrives_efficiency_csv, 'PrimaryPlayer')
    for player in pnr_spotupdrives_player_proportion:
        player_data = find_player_efficiency(pnr_spotupdrives_efficiency_df, pnr_spotupsdrives_efficiency_csv, player, pnr_spotupdrives_player_proportion[player], 'PrimaryPlayer')
        pnr_spotupdrives_player_proportion[player] = player_data

    pnr_spotupjumpers_efficiency_csv = ['twoplayer_pnr_spotupsjumpers_efficiency.csv']
    pnr_spotupjumpers_efficiency_df = df [ (df['SourceFile'].isin(pnr_spotupjumpers_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnr_spotupjumpers_efficiency = compute_grouped_statistics(pnr_spotupjumpers_efficiency_df, 'Efficiency for all PNRs leading to secondary Spot up jumpers plays.', 'SecondaryPlayer')
    pnr_spotupjumpers_player_proportion = find_player_proportions(pnr_spotupjumpers_efficiency_df, pnr_spotupjumpers_efficiency_csv, 'PrimaryPlayer')
    for player in pnr_spotupjumpers_player_proportion:
        player_data = find_player_efficiency(pnr_spotupjumpers_efficiency_df, pnr_spotupjumpers_efficiency_csv, player, pnr_spotupjumpers_player_proportion[player], 'PrimaryPlayer')
        pnr_spotupjumpers_player_proportion[player] = player_data


    post_spotupdrives_efficiency_csv = ['twoplayer_post_spotupdrive_efficiency.csv']
    post_spotupdrives_efficiency_df = df [ (df['SourceFile'].isin(post_spotupdrives_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    post_spotupdrives_efficiency = compute_grouped_statistics(post_spotupdrives_efficiency_df, 'Efficiency for all Post plays leading to secondary Spot up drives plays.', 'SecondaryPlayer')
    post_spotupdrives_player_proportion = find_player_proportions(post_spotupdrives_efficiency_df, post_spotupdrives_efficiency_csv, 'PrimaryPlayer')
    for player in post_spotupdrives_player_proportion:
        player_data = find_player_efficiency(post_spotupdrives_efficiency_df, post_spotupdrives_efficiency_csv, player, post_spotupdrives_player_proportion[player], 'PrimaryPlayer')
        post_spotupdrives_player_proportion[player] = player_data

    post_spotupjumpers_efficiency_csv = ['twoplayer_post_spotupjumper_efficiency.csv']
    post_spotupjumpers_efficiency_df = df [ (df['SourceFile'].isin(post_spotupjumpers_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    post_spotupjumpers_efficiency = compute_grouped_statistics(post_spotupjumpers_efficiency_df, 'Efficiency for all Post plays leading to secondary Spot up jumpers plays.', 'SecondaryPlayer')
    post_spotupjumpers_player_proportion = find_player_proportions(post_spotupjumpers_efficiency_df, post_spotupjumpers_efficiency_csv, 'PrimaryPlayer')
    for player in post_spotupjumpers_player_proportion:
        player_data = find_player_efficiency(post_spotupjumpers_efficiency_df, post_spotupjumpers_efficiency_csv, player, post_spotupjumpers_player_proportion[player], 'PrimaryPlayer')
        post_spotupjumpers_player_proportion[player] = player_data
        
    
    # Calculates total proportion and efficiency of all directions in PNR leading to a spotupdrives.
    total_pnr_drives_direction_proport_csvs = ['twoplayer_pnrbhhigh_spotupdrives_efficiency.csv', 'twoplayer_pnrbhright_spotupdrives_efficiency', 'twoplayer_pnrbhright_spotupdrives_efficiency.csv', ]
    filtered_df = df [ (df['SourceFile'].isin(total_pnr_drives_direction_proport_csvs)) & (df['SecondaryPlayer'] == name)  ]
    total_pnr_drives_direction_proportion = find_play_proportions(filtered_df, total_pnr_drives_direction_proport_csvs)
    total_pnr_drives_direction_proportion_dict = {'High PNR --> Spotupdrives' : total_pnr_drives_direction_proportion[0] , 'Right PNR --> Spotupdrives': total_pnr_drives_direction_proportion[1],
                                'Left PNR --> Spotupdrives': total_pnr_drives_direction_proportion[2] , 'Total Plays': total_pnr_drives_direction_proportion[3] }


    pnrbhhigh_spotupdrives_efficiency_csv = ['twoplayer_pnrbhhigh_spotupdrives_efficiency.csv']
    pnrbhhigh_spotupdrives_efficiency_df = df [ (df['SourceFile'].isin(pnrbhhigh_spotupdrives_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnrbhhigh_spotupdrives_efficiency = compute_grouped_statistics(pnrbhhigh_spotupdrives_efficiency_df, 'Efficiency for all High PNRs leading to secondary spotupdrives plays.', 'SecondaryPlayer')
    pnrbhhigh_spotupdrives_player_proportion = find_player_proportions(pnrbhhigh_spotupdrives_efficiency_df, pnrbhhigh_spotupdrives_efficiency_csv, 'PrimaryPlayer')
    for player in pnrbhhigh_spotupdrives_player_proportion:
        player_data = find_player_efficiency(pnrbhhigh_spotupdrives_efficiency_df, pnrbhhigh_spotupdrives_efficiency_csv, player, pnrbhhigh_spotupdrives_player_proportion[player], 'PrimaryPlayer')
        pnrbhhigh_spotupdrives_player_proportion[player] = player_data


    pnrbhright_spotupdrives_efficiency_csv = ['twoplayer_pnrbhright_spotupdrives_efficiency.csv']
    pnrbhright_spotupdrives_efficiency_df = df [ (df['SourceFile'].isin(pnrbhright_spotupdrives_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnrbhright_spotupdrives_efficiency = compute_grouped_statistics(pnrbhright_spotupdrives_efficiency_df, 'Efficiency for all Right PNRs leading to secondary spotupdrives plays.', 'SecondaryPlayer')
    pnrbhright_spotupdrives_player_proportion = find_player_proportions(pnrbhright_spotupdrives_efficiency_df, pnrbhright_spotupdrives_efficiency_csv, 'PrimaryPlayer')
    for player in pnrbhright_spotupdrives_player_proportion:
        player_data = find_player_efficiency(pnrbhright_spotupdrives_efficiency_df, pnrbhright_spotupdrives_efficiency_csv, player, pnrbhright_spotupdrives_player_proportion[player], 'PrimaryPlayer')
        pnrbhright_spotupdrives_player_proportion[player] = player_data


    pnrbhleft_spotupdrives_efficiency_csv = ['twoplayer_pnrbhleft_spotupdrives_efficiency.csv']
    pnrbhleft_spotupdrives_efficiency_df = df [ (df['SourceFile'].isin(pnrbhleft_spotupdrives_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnrbhleft_spotupdrives_efficiency = compute_grouped_statistics(pnrbhleft_spotupdrives_efficiency_df, 'Efficiency for all Left PNRs leading to secondary spotupdrives plays.', 'SecondaryPlayer')
    pnrbhleft_spotupdrives_player_proportion = find_player_proportions(pnrbhleft_spotupdrives_efficiency_df, pnrbhleft_spotupdrives_efficiency_csv, 'PrimaryPlayer')
    for player in pnrbhleft_spotupdrives_player_proportion:
        player_data = find_player_efficiency(pnrbhleft_spotupdrives_efficiency_df, pnrbhleft_spotupdrives_efficiency_csv, player, pnrbhleft_spotupdrives_player_proportion[player], 'PrimaryPlayer')
        pnrbhleft_spotupdrives_player_proportion[player] = player_data



    # Calculates total proportion and efficiency of all directions in PNR leading to a spotupjumper.
    total_pnr_jumpers_direction_proport_csvs = ['twoplayer_pnrbhhigh_spotupjumper_efficiency.csv', 'twoplayer_pnrbhright_spotupjumper_efficiency', 'twoplayer_pnrbhleft_spotupjumper_efficiency.csv', ]
    filtered_df = df [ (df['SourceFile'].isin(total_pnr_jumpers_direction_proport_csvs)) & (df['SecondaryPlayer'] == name)  ]
    total_pnr_jumpers_direction_proportion = find_play_proportions(filtered_df, total_pnr_jumpers_direction_proport_csvs)
    total_pnr_jumpers_direction_proportion_dict = {'High PNR --> Spotupjumpers' : total_pnr_jumpers_direction_proportion[0] , 'Right PNR --> Spotupjumpers': total_pnr_jumpers_direction_proportion[1],
                                'Left PNR --> Spotupjumpers': total_pnr_jumpers_direction_proportion[2] , 'Total Plays': total_pnr_jumpers_direction_proportion[3] }



    pnrbhhigh_spotupjumper_efficiency_csv = ['twoplayer_pnrbhhigh_spotupjumper_efficiency.csv']
    pnrbhhigh_spotupjumper_efficiency_df = df [ (df['SourceFile'].isin(pnrbhhigh_spotupjumper_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnrbhhigh_spotupjumper_efficiency = compute_grouped_statistics(pnrbhhigh_spotupjumper_efficiency_df, 'Efficiency for all High PNRs leading to secondary spotupjumper plays.', 'SecondaryPlayer')
    pnrbhhigh_spotupjumper_player_proportion = find_player_proportions(pnrbhhigh_spotupjumper_efficiency_df, pnrbhhigh_spotupjumper_efficiency_csv, 'PrimaryPlayer')
    for player in pnrbhhigh_spotupjumper_player_proportion:
        player_data = find_player_efficiency(pnrbhhigh_spotupjumper_efficiency_df, pnrbhhigh_spotupjumper_efficiency_csv, player, pnrbhhigh_spotupjumper_player_proportion[player], 'PrimaryPlayer')
        pnrbhhigh_spotupjumper_player_proportion[player] = player_data


    pnrbhright_spotupjumper_efficiency_csv = ['twoplayer_pnrbhright_spotupjumpers_efficiency.csv']
    pnrbhright_spotupjumper_efficiency_df = df [ (df['SourceFile'].isin(pnrbhright_spotupjumper_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnrbhright_spotupjumper_efficiency = compute_grouped_statistics(pnrbhright_spotupjumper_efficiency_df, 'Efficiency for all Right PNRs leading to secondary spotupjumper plays.', 'SecondaryPlayer')
    pnrbhright_spotupjumper_player_proportion = find_player_proportions(pnrbhright_spotupjumper_efficiency_df, pnrbhright_spotupjumper_efficiency_csv, 'PrimaryPlayer')
    for player in pnrbhright_spotupjumper_player_proportion:
        player_data = find_player_efficiency(pnrbhright_spotupjumper_efficiency_df, pnrbhright_spotupjumper_efficiency_csv, player, pnrbhright_spotupjumper_player_proportion[player], 'PrimaryPlayer')
        pnrbhright_spotupjumper_player_proportion[player] = player_data


    pnrbhleft_spotupjumper_efficiency_csv = ['twoplayer_pnrbhleft_spotupjumper_efficiency.csv']
    pnrbhleft_spotupjumper_efficiency_df = df [ (df['SourceFile'].isin(pnrbhleft_spotupjumper_efficiency_csv)) & (df['SecondaryPlayer'] == name) ]
    pnrbhleft_spotupjumper_efficiency = compute_grouped_statistics(pnrbhleft_spotupjumper_efficiency_df, 'Efficiency for all Left PNRs leading to secondary spotupjumper plays.', 'SecondaryPlayer')
    pnrbhleft_spotupjumper_player_proportion = find_player_proportions(pnrbhleft_spotupjumper_efficiency_df, pnrbhleft_spotupjumper_efficiency_csv, 'PrimaryPlayer')
    for player in pnrbhleft_spotupjumper_player_proportion:
        player_data = find_player_efficiency(pnrbhleft_spotupjumper_efficiency_df, pnrbhleft_spotupjumper_efficiency_csv, player, pnrbhleft_spotupjumper_player_proportion[player], 'PrimaryPlayer')
        pnrbhleft_spotupjumper_player_proportion[player] = player_data


    insight.extend([
        total_spotup_efficiency,
        total_spotupdrives_proportion_dict,
        total_spotupjumpers_proportion_dict,
        iso_spotupdrives_efficiency,
        iso_spotupdrives_player_proportion,
        iso_spotupjumpers_efficiency,
        iso_spotupjumpers_player_proportion,
        pnr_spotupdrives_efficiency,
        pnr_spotupdrives_player_proportion,
        pnr_spotupjumpers_efficiency,
        pnr_spotupjumpers_player_proportion,
        post_spotupdrives_efficiency,
        post_spotupdrives_player_proportion,
        post_spotupjumpers_efficiency,
        post_spotupjumpers_player_proportion,
        total_pnr_drives_direction_proportion_dict,
        pnrbhhigh_spotupdrives_efficiency,
        pnrbhhigh_spotupdrives_player_proportion,
        pnrbhright_spotupdrives_efficiency,
        pnrbhright_spotupdrives_player_proportion,
        pnrbhleft_spotupdrives_efficiency,
        pnrbhleft_spotupdrives_player_proportion,
        total_pnr_jumpers_direction_proportion_dict,
        pnrbhhigh_spotupjumper_efficiency,
        pnrbhhigh_spotupjumper_player_proportion,
        pnrbhright_spotupjumper_efficiency,
        pnrbhright_spotupjumper_player_proportion,
        pnrbhleft_spotupjumper_efficiency,
        pnrbhleft_spotupjumper_player_proportion,
    ])


def process_scorer_stats(df: pd.DataFrame, name, insights):
    for i in range(8):
        insight = insights[i]
        if i == 0:  # PNR insights
            PNR_scorer_stats(df, name, insight)
        elif i == 7:  # Iso insights
            Iso_scorer_stats(df, name, insight)
        elif i == 3:  # Post insights
            Post_scorer_stats(df, name, insight)
        elif i == 1:  # Cut insights
            Cut_scorer_stats(df, name, insight)
        elif i == 4:  # Spotup insights
            Spotup_scorer_stats(df, name, insight)
        elif i == 5:  # Transition insights
            Transition_scorer_stats(df, name, insight)
        elif i == 6:  # Offscreen insights
            Offscreen_scorer_stats(df, name, insight)
        elif i == 2:  # Handoff insights
            Handoff_scorer_stats(df, name, insight)

def PNR_scorer_stats(df: pd.DataFrame, name, insight):
    # Finds total efficiency for ALL PNR scorer plays
    filtered_df1 = df[(df['SourceFile'] == 'player_pnr_efficiency.csv')]
    total_pnr_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all PNR scorer plays together.', 'Player')

    # Calculate total proportion and efficiency for REJECTING vs GOING OFF screens
    total_pnr_proport_csvs = ['player_pnr_offpick_efficiency.csv', 'player_pnr_rejectpick_efficiency.csv']
    filtered_df2 = df[df['SourceFile'].isin(total_pnr_proport_csvs)]
    total_pnr_proportion = find_play_proportions(filtered_df2, total_pnr_proport_csvs)
    total_pnr_proportion_dict = {'PNR Player goes OFF screen': total_pnr_proportion[0], 
                                 'PNR Player REJECTS screen': total_pnr_proportion[1],
                                 'Total Plays': total_pnr_proportion[2]}

    filtered_df2_offpick = df[(df['SourceFile'] == 'player_pnr_offpick_efficiency.csv')]
    total_pnr_offpick_efficiency = compute_grouped_statistics(filtered_df2_offpick, 'Efficiency for all PNR scorers going OFF screens.', 'Player')

    filtered_df2_rejectpick = df[(df['SourceFile'] == 'player_pnr_rejectpick_efficiency.csv')]
    total_pnr_reject_efficiency = compute_grouped_statistics(filtered_df2_rejectpick, 'Efficiency for all PNR scorers REJECTING screens.', 'Player')

    # Calculate total proportion and efficiency for High vs Left vs Right screens
    total_pnr_direction_proport_csvs = ['player_pnr_bhhigh_efficiency.csv', 'player_pnr_bhleft_efficiency.csv', 'player_pnr_bhright_efficiency.csv']
    filtered_df3 = df[df['SourceFile'].isin(total_pnr_direction_proport_csvs)]
    total_pnr_direction_proportion = find_play_proportions(filtered_df3, total_pnr_direction_proport_csvs)
    total_pnr_direction_proportion_dict = {'PNR Player HIGH': total_pnr_direction_proportion[0], 
                                           'PNR Player LEFT': total_pnr_direction_proportion[1], 
                                           'PNR Player RIGHT': total_pnr_direction_proportion[2], 
                                           'Total Plays': total_pnr_direction_proportion[3]}

    filtered_df3_high = df[(df['SourceFile'] == 'player_pnr_bhhigh_efficiency.csv')]
    total_pnr_bhhigh_efficiency = compute_grouped_statistics(filtered_df3_high, 'Efficiency for all PNR scorers on HIGH screens.', 'Player')

    filtered_df3_left = df[(df['SourceFile'] == 'player_pnr_bhleft_efficiency.csv')]
    total_pnr_bhleft_efficiency = compute_grouped_statistics(filtered_df3_left, 'Efficiency for all PNR scorers on LEFT screens.', 'Player')

    filtered_df3_right = df[(df['SourceFile'] == 'player_pnr_bhright_efficiency.csv')]
    total_pnr_bhright_efficiency = compute_grouped_statistics(filtered_df3_right, 'Efficiency for all PNR scorers on RIGHT screens.', 'Player')

    # Calculate total proportion and efficiency for BH High --> Rejecting Screens
    filtered_df_bhhigh_reject = df[(df['SourceFile'] == 'player_pnr_bhhigh_rejectpick_efficiency.csv')]
    total_pnr_bhhigh_rejectpick_efficiency = compute_grouped_statistics(filtered_df_bhhigh_reject, 'Efficiency for HIGH PNR scorer REJECTING screens.', 'Player')

    # Calculate total proportion and efficiency for BH High --> OFF Screens
    filtered_df_bhhigh_offpick = df[(df['SourceFile'] == 'player_pnr_bhhigh_offpick_efficiency.csv')]
    total_pnr_bhhigh_offpick_efficiency = compute_grouped_statistics(filtered_df_bhhigh_offpick, 'Efficiency for HIGH PNR scorer going OFF screens.', 'Player')

    # Calculate total proportion and efficiency for BH Left --> Rejecting Screens
    filtered_df_bhleft_reject = df[(df['SourceFile'] == 'player_pnr_bhleft_rejectpick_efficiency.csv')]
    total_pnr_bhleft_rejectpick_efficiency = compute_grouped_statistics(filtered_df_bhleft_reject, 'Efficiency for LEFT PNR scorer REJECTING screens.', 'Player')

    # Calculate total proportion and efficiency for BH Left --> OFF Screens
    filtered_df_bhleft_offpick = df[(df['SourceFile'] == 'player_pnr_bhleft_offpick_efficiency.csv')]
    total_pnr_bhleft_offpick_efficiency = compute_grouped_statistics(filtered_df_bhleft_offpick, 'Efficiency for LEFT PNR scorer going OFF screens.', 'Player')

    # Calculate total proportion and efficiency for BH Right --> Rejecting Screens
    filtered_df_bhright_reject = df[(df['SourceFile'] == 'player_pnr_bhright_rejectpick_efficiency.csv')]
    total_pnr_bhright_rejectpick_efficiency = compute_grouped_statistics(filtered_df_bhright_reject, 'Efficiency for RIGHT PNR scorer REJECTING screens.', 'Player')

    # Calculate total proportion and efficiency for BH Right --> OFF Screens
    filtered_df_bhright_offpick = df[(df['SourceFile'] == 'player_pnr_bhright_offpick_efficiency.csv')]
    total_pnr_bhright_offpick_efficiency = compute_grouped_statistics(filtered_df_bhright_offpick, 'Efficiency for RIGHT PNR scorer going OFF screens.', 'Player')

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

def Iso_scorer_stats(df: pd.DataFrame, name, insight):
    # Finds total efficiency for ALL Iso scorer plays
    filtered_df1 = df [ (df['SourceFile'] == 'player_iso_efficiency.csv') ]
    total_iso_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all Iso scorer plays together.', 'Player')


    # Calculates total proportion and efficiency for going Left vs Right vs Straight screens
    total_iso_proport_csvs = ['player_iso_left_efficiency.csv', 'player_iso_right_efficiency.csv', 'player_iso_top_efficiency.csv']
    filtered_df2 = df [ df['SourceFile'].isin(total_iso_proport_csvs) ]
    total_iso_proportion = find_play_proportions(filtered_df2, total_iso_proport_csvs)
    total_iso_proportion_dict = {'Iso Player goes Left' : total_iso_proportion[0], 'Iso Player goes Right': total_iso_proportion[1],
                                'Iso Player from Top': total_iso_proportion[2], 'Total Plays': total_iso_proportion[3], }

    filtered_df2 = df [ (df['SourceFile'] == 'player_iso_left_efficiency.csv') ]
    total_iso_left_efficiency = compute_grouped_statistics(filtered_df2, 'Efficiency for all Iso scorers going Left.', 'Player')

    filtered_df2 = df [ (df['SourceFile'] == 'player_iso_right_efficiency.csv') ]
    total_iso_right_efficiency = compute_grouped_statistics(filtered_df2, 'Efficiency for all Iso scorers going Right.', 'Player')

    filtered_df2 = df [ (df['SourceFile'] == 'player_iso_top_efficiency.csv') ]
    total_iso_top_efficiency = compute_grouped_statistics(filtered_df2, 'Efficiency for all Iso scorers from Top.', 'Player')

    insight.extend([
        total_iso_efficiency,
        total_iso_proportion_dict,
        total_iso_left_efficiency,
        total_iso_right_efficiency,
        total_iso_top_efficiency
    ])

def Post_scorer_stats(df: pd.DataFrame, name, insight):
    # Finds total efficiency for ALL Post scorer plays
    filtered_df1 = df [ (df['SourceFile'] == 'player_post_efficiency.csv') ]
    total_post_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all Post scorer plays together.', 'Player')

    # Calculates total proportion and efficiency for starting on Left block vs Right block vs Middle
    total_post_proport_csvs = ['player_post_leftblock_efficiency.csv', 'player_post_rightblock_efficiency.csv', 'player_post_middle_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_post_proport_csvs) ]
    total_post_block_proportion = find_play_proportions(filtered_df, total_post_proport_csvs)
    total_post_block_proportion_dict = {'Post player from Left block' : total_post_block_proportion[0], 'Post player from Right block': total_post_block_proportion[1],
                                'Post player from Middle': total_post_block_proportion[2], 'Total Plays': total_post_block_proportion[3], }

    filtered_df = df [ (df['SourceFile'] == 'player_post_leftblock_efficiency.csv') ]
    total_post_leftblock_efficiency = compute_grouped_statistics(filtered_df, 'Post Left Block.', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_post_rightblock_efficiency.csv') ]
    total_post_rightblock_efficiency = compute_grouped_statistics(filtered_df, 'Post Right Block', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_post_middle_efficiency.csv') ]
    total_post_middle_efficiency = compute_grouped_statistics(filtered_df, 'Post Middle', 'Player')


    # Calculates total proportion and efficiency for shooting off Left shoulder vs Right shoulder vs Facing up
    total_post_proport_csvs = ['player_post_leftshoulder_efficiency.csv', 'player_post_rightshoulder_efficiency.csv', 'player_post_faceup_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_post_proport_csvs) ]
    total_post_shoulder_proportion = find_play_proportions(filtered_df, total_post_proport_csvs)
    total_post_shoulder_proportion_dict = {'Post Left shoulder' : total_post_shoulder_proportion[0], 'Post Right shoulder': total_post_shoulder_proportion[1],
                                'Post Face Up': total_post_shoulder_proportion[2], 'Total Plays': total_post_shoulder_proportion[3] }

    filtered_df = df [ (df['SourceFile'] == 'player_post_leftshoulder_efficiency.csv') ]
    post_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Left shoulder', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_post_rightshoulder_efficiency.csv') ]
    post_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Right shoulder', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_post_faceup_efficiency.csv') ]
    post_faceup_efficiency = compute_grouped_statistics(filtered_df, 'Post Face Up', 'Player')
    
    
    # Calculates the combinations of post plays
    filtered_df = df[(df['SourceFile'] == 'player_post_leftblock_faceup_efficiency.csv')]
    leftblock_faceup_efficiency = compute_grouped_statistics(filtered_df, 'Post Left Block --> Faceup', 'Player')

    filtered_df = df[(df['SourceFile'] == 'player_post_leftblock_leftshoulder_efficiency.csv')]
    leftblock_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Left Block --> Left Shoulder', 'Player')

    filtered_df = df[(df['SourceFile'] == 'player_post_leftblock_rightshoulder_efficiency.csv')]
    leftblock_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Left Block --> Right Shoulder', 'Player')

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_faceup_efficiency.csv')]
    rightblock_faceup_efficiency = compute_grouped_statistics(filtered_df, 'Post Right Block --> Faceup', 'Player')

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_leftshoulder_efficiency.csv')]
    rightblock_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Right Block --> Left Shoulder', 'Player')

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_rightshoulder_efficiency.csv')]
    rightblock_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Right Block --> Right Shoulder', 'Player')

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_faceup_efficiency.csv')]
    middle_faceup_efficiency = compute_grouped_statistics(filtered_df, 'Post Middle --> Faceup', 'Player')

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_leftshoulder_efficiency.csv')]
    middle_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Middle --> Left Shoulder', 'Player')

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_rightshoulder_efficiency.csv')]
    middle_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'Post Middle --> Right Shoulder', 'Player')

    insight.extend({
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
    })

def Cut_scorer_stats(df: pd.DataFrame, name, insight):
    # Finds total efficiency for ALL Cutter scorer plays
    filtered_df = df [ (df['SourceFile'] == 'player_cut_efficiency.csv') ]
    total_cut_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all cutting scorer plays together.', 'Player')

    # Calculates total proportion and efficiency for Basket vs Flash vs Screen cuts
    total_cut_proport_csvs = ['player_cut_basket_efficiency.csv', 'player_cut_flash_efficiency.csv', 'player_cut_screen_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_cut_proport_csvs) ]
    total_cut_proportion = find_play_proportions(filtered_df, total_cut_proport_csvs)
    total_cut_proportion_dict = {'Basket Cut' : total_cut_proportion[0], 'Flash Cut': total_cut_proportion[1],
                                'Screen Cut': total_cut_proportion[2], 'Total Plays': total_cut_proportion[3], }

    filtered_df = df [ (df['SourceFile'] == 'player_cut_basket_efficiency.csv') ]
    total_cut_basket_efficiency = compute_grouped_statistics(filtered_df, 'Basket Cut', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_cut_flash_efficiency.csv') ]
    total_cut_flash_efficiency = compute_grouped_statistics(filtered_df, 'Flash Cut', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_cut_screen_efficiency.csv') ]
    total_cut_screen_efficiency = compute_grouped_statistics(filtered_df, 'Screen Cut', 'Player')
    
    insight.extend({
        total_cut_efficiency,
        total_cut_proportion_dict,
        total_cut_basket_efficiency,
        total_cut_flash_efficiency,
        total_cut_screen_efficiency
    })

def Spotup_scorer_stats(df: pd.DataFrame, name, insight):
    # Finds total efficiency for ALL Spotup scorer plays
    filtered_df = df [ (df['SourceFile'] == 'player_spotup_efficiency.csv') ]
    total_spotup_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all Spotup scorer plays together.', 'Player')

    # Calculates total proportion and efficiency for starting on Jumpers vs Drives
    total_spotup_proport_csvs = ['player_spotup_jumpshot_efficiency.csv', 'player_spotup_leftdrive_efficiency.csv', 'player_spotup_rightdrive_efficiency.csv', 'player_spotup_straightdrive_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_spotup_proport_csvs) ]
    total_spotup_proportion = find_play_proportions(filtered_df, total_spotup_proport_csvs)
    total_spotup_proportion_dict = {'Jumpshot' : total_spotup_proportion[0], 'Drive': total_spotup_proportion[1] + total_spotup_proportion[2] + total_spotup_proportion[3],
                                    'Total Plays': total_spotup_proportion[4], }

    filtered_df = df [ (df['SourceFile'] == 'player_spotup_jumpshot_efficiency.csv') ]
    total_spotup_jumpshot_efficiency = compute_grouped_statistics(filtered_df, 'Jumpshot', 'Player')

    total_drive_csvs = ['player_spotup_leftdrive_efficiency.csv', 'player_spotup_rightdrive_efficiency.csv', 'player_spotup_straightdrive_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(total_drive_csvs))]
    total_spotup_drive_efficiency = compute_grouped_statistics(filtered_df, 'Drives', 'Player')


    filtered_df = df [ (df['SourceFile'] == 'player_spotup_leftdrive_efficiency.csv') ]
    total_spotup_leftdrive_efficiency = compute_grouped_statistics(filtered_df, 'Left Drive', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_spotup_rightdrive_efficiency.csv') ]
    total_spotup_rightdrive_efficiency = compute_grouped_statistics(filtered_df, 'Right Drive', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_spotup_straightdrive_efficiency.csv') ]
    total_spotup_straightdrive_efficiency = compute_grouped_statistics(filtered_df, 'Straight Drive', 'Player')

    insight.extend([total_spotup_efficiency,
                total_spotup_proportion_dict,
                total_spotup_jumpshot_efficiency,
                total_spotup_drive_efficiency,
                total_spotup_leftdrive_efficiency,
                total_spotup_rightdrive_efficiency,
                total_spotup_straightdrive_efficiency
                ])

def Transition_scorer_stats(df: pd.DataFrame, name, insight):
    # Calculates total proportion and efficiency for Transition plays
    total_transition_proport_csvs = ['player_transition_bh_efficiency.csv', 'player_transition_leakouts_efficiency.csv', 
                                    'player_transition_leftwing_efficiency.csv', 'player_transition_rightwing_efficiency.csv', 'player_transition_trailer_efficiency']
    filtered_df = df [ df['SourceFile'].isin(total_transition_proport_csvs) ]
    total_transition_proportion = find_play_proportions(filtered_df, total_transition_proport_csvs)
    total_transition_proportion_dict = {'Transition BH %' : total_transition_proportion[0], 'Transition Leakouts%': total_transition_proportion[1],
                                        'Transition Leftwing': total_transition_proportion[2], 'Transition Rightwing' : total_transition_proportion[3], 
                                        'Transition Trailer': total_transition_proportion[4], 'Total Plays': total_transition_proportion[5] }
    total_transition_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all transition scorer plays together.', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_bh_efficiency.csv') ]
    total_transition_bh_efficiency = compute_grouped_statistics(filtered_df, 'Transition BH', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_leakouts_efficiency.csv') ]
    total_transition_leakouts_efficiency = compute_grouped_statistics(filtered_df, 'Transition Leakouts', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_leftwing_efficiency.csv') ]
    total_transition_leftwing_efficiency = compute_grouped_statistics(filtered_df, 'Transition Left Wing', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_rightwing_efficiency.csv') ]
    total_transition_rightwing_efficiency = compute_grouped_statistics(filtered_df, 'Transition Right Wing', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_trailer_efficiency.csv') ]
    total_transition_trailer_efficiency = compute_grouped_statistics(filtered_df, 'Transition Trailer', 'Player')

    insight.extend([
        total_transition_proportion_dict,
        total_transition_efficiency,
        total_transition_bh_efficiency,
        total_transition_leakouts_efficiency,
        total_transition_leftwing_efficiency,
        total_transition_rightwing_efficiency,
        total_transition_trailer_efficiency
    ])

def Offscreen_scorer_stats(df: pd.DataFrame, name, insight):
    # Finds total efficiency for ALL Off Screen scorer plays
    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_efficiency.csv') ]
    total_offscreens_efficiency = compute_grouped_statistics(filtered_df, 'Efficiency for all Off Screen scorer plays together.', 'Player')

    # Calculates total proportion and efficiency for handoffs going Left vs Right vs Top
    total_offscreens_proport_csvs = ['player_offscreens_leftshoulder_efficiency.csv', 'player_offscreens_rightshoulder_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_offscreens_proport_csvs) ]
    total_offscreens_proportion = find_play_proportions(filtered_df, total_offscreens_proport_csvs)
    total_offscreens_proportion_dict = {'Off Screen Shooter running off Left Shoulder' : total_offscreens_proportion[0], 'Off Screen Shooter running off Right Shoulder': total_offscreens_proportion[1],
                                'Total Plays': total_offscreens_proportion[2] }

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_efficiency.csv') ]
    total_offscreens_left_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Left', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_efficiency.csv') ]
    total_offscreens_right_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Right', 'Player')

    # Calculates total proportion and efficiency for Flares vs Straight vs Curls
    total_offscreens_type_proport_csvs = ['player_offscreens_flare_efficiency.csv', 'player_offscreens_straight_efficiency.csv', 'player_offscreens_curl_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_offscreens_type_proport_csvs) ]
    total_offscreens_type_proportion = find_play_proportions(filtered_df, total_offscreens_type_proport_csvs)
    total_offscreens_type_proportion_dict = {'Shooter running off a Flare' : total_offscreens_type_proportion[0], 'Shooter running straight off a screen': total_offscreens_type_proportion[1],
                                        'Shooter curling off screen': total_offscreens_type_proportion[2], 'Total Plays': total_offscreens_type_proportion[3] }

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_flare_efficiency.csv') ]
    total_offscreens_flare_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Flare', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_straight_efficiency.csv') ]
    total_offscreens_straight_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Straight', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_curl_efficiency.csv') ]
    total_offscreens_curl_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Curl', 'Player')

    # Calculates total proportion and efficiency for combinations of direction and type of off screen
    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_flare_efficiency.csv') ]
    total_offscreens_left_flare_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Left --> Flare', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_straight_efficiency.csv') ]
    total_offscreens_left_straight_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Left --> Straight', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_curl_efficiency.csv') ]
    total_offscreens_left_curl_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Left --> Curl', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_flare_efficiency.csv') ]
    total_offscreens_right_flare_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Right --> Flare', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_straight_efficiency.csv') ]
    total_offscreens_right_straight_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Right --> Straight', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_curl_efficiency.csv') ]
    total_offscreens_right_curl_efficiency = compute_grouped_statistics(filtered_df, 'Off Screens Right --> Curl', 'Player')

    insight.extend([
        total_offscreens_efficiency,
        total_offscreens_proportion_dict,
        total_offscreens_left_efficiency,
        total_offscreens_right_efficiency,
        total_offscreens_type_proportion_dict,
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
    
def Handoff_scorer_stats(df: pd.DataFrame, name, insight):
    # Finds total efficiency for ALL Handoff scorer plays
    filtered_df1 = df [ (df['SourceFile'] == 'player_handoffs_efficiency.csv') ]
    total_handoffs_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all Handoff scorer plays together.', 'Player')

    # Calculates total proportion and efficiency for handoffs going Left vs Right vs Top
    total_handoffs_proport_csvs = ['player_handoffs_bhleft_efficiency.csv', 'player_handoffs_bhright_efficiency.csv', 'player_handoffs_top_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_handoffs_proport_csvs) ]
    total_handoffs_proportion = find_play_proportions(filtered_df, total_handoffs_proport_csvs)
    total_handoffs_proportion_dict = {'Handoff shooter going Left' : total_handoffs_proportion[0], 'Handoff shooter going Right': total_handoffs_proportion[1],
                                'Handoff shooter from Top': total_handoffs_proportion[2], 'Total Plays': total_handoffs_proportion[3], }

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhleft_efficiency.csv') ]
    total_handoffs_left_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Left', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhright_efficiency.csv') ]
    total_handoffs_right_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Right', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_top_efficiency.csv') ]
    total_handoffs_top_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Top', 'Player')
    
    
    # Calculates total proportion and efficiency of Dribble handoffs vs Stationary Handoffs
    total_handoffs_type_proport_csvs = ['player_handoffs_stationary_efficiency.csv', 'player_handoffs_dribble_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_handoffs_type_proport_csvs) ]
    total_handoffs_type_proportion = find_play_proportions(filtered_df, total_handoffs_type_proport_csvs)
    total_handoffs_type_proportion_dict = {'Handoffs Stationary' : total_handoffs_type_proportion[0], 'Handoffs Dribble': total_handoffs_type_proportion[1],
                                'Total Plays': total_handoffs_type_proportion[2], }

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_stationary_efficiency.csv') ]
    total_handoffs_stationary_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Stationary', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_dribble_efficiency.csv') ]
    total_handoffs_dribble_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Dribble', 'Player')
    
    
    # Calculates combinations  of type of handoff and direction
    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhleft_stationary_efficiency.csv') ]
    total_handoffs_stationary_left_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Left --> Stationary', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhright_stationary_efficiency.csv') ]
    total_handoffs_stationary_right_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Right --> Stationary', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_top_stationary_efficiency.csv') ]
    total_handoffs_stationary_top_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Top --> Stationary', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhleft_dribble_efficiency.csv') ]
    total_handoffs_dribble_left_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Left --> Dribble', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhright_dribble_efficiency.csv') ]
    total_handoffs_dribble_right_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Right --> Dribble', 'Player')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_top_dribble_efficiency.csv') ]
    total_handoffs_dribble_top_efficiency = compute_grouped_statistics(filtered_df, 'Handoffs Top --> Dribble', 'Player')

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


def compute_grouped_statistics(df, statdescription, playertype):
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
        stats_dict[row[playertype]] = {
            'StatDescription': statdescription,
            'TotalPlays': row['TotalPlays'],
            'Total3ptShots': row['Total3ptShots'],
            'Total3ptMakes': row['Total3ptMakes'],
            '3pt%': row['3pt%'],
            'Total2ptShots': row['Total2ptShots'],
            'Total2ptMakes': row['Total2ptMakes'],
            '2pt%': row['2pt%'],
            'TotalMidRangeShots': row['TotalMidRangeShots'],
            'TotalMidRangeMakes': row['TotalMidRangeMakes'],
            'MidRange%': row['MidRange%'],
            'EFG%': row['EFG%'],
            'Turnover': row['Turnover'],
            'Foul': row['Foul']
        }

    return stats_dict

def find_play_proportions(df, sourcefile_list):
    """
    Finds the total play proportions based on the given 'SourceFile' value lists.

    :param df: Input DataFrame containing the data.
    :param sourcefile_lists: Variable number of lists containing 'SourceFile' values.
    :return: List of proportions of total plays for each list of 'SourceFile' values.
    """
    total_plays_all = 0
    play_totals = []

    # Calculate the total plays for each list of 'SourceFile' values
    for sourcefile in sourcefile_list:
        filtered_df = df[ df['SourceFile'] == sourcefile ]
        if filtered_df.empty:
            play_totals.append(0)
            continue
        total_plays = filtered_df['TotalPlays'].sum()
        play_totals.append(total_plays)
        total_plays_all += total_plays

    # Calculate the proportions for each Sourcefile
    proportions = [total / total_plays_all if total_plays_all > 0 else 0 for total in play_totals]

    proportions.append(total_plays_all)

    return proportions

def find_player_proportions(df, sourcefile, player_col):
    """
    Calculates the proportion of total plays each SecondaryPlayer was involved in and rounds it to 2 decimal places.

    :param df: Input DataFrame containing 'SecondaryPlayer' and 'TotalPlays' columns.
    :return: Dictionary where keys are 'SecondaryPlayer' and values are their proportion of total plays (rounded to 2 decimal places).
    """
    # Initialize an empty dictionary to store the total plays for each secondary player
    player_dict = {}
    total_plays = 0

    if df.empty:
      return player_dict

    filtered_df = df[df['SourceFile'] == sourcefile]

    if filtered_df.empty:
        return player_dict

    # Loop through each row in the DataFrame
    for _, row in filtered_df.iterrows():
        player = row[player_col]
        plays = row['TotalPlays']

        # If the player is already in the dictionary, add the current plays to their total
        if player in player_dict:
            continue
        else:
            # Otherwise, set the initial plays value for the player
            player_dict[player] = plays
            total_plays += plays

    # Adjust the values to be proportions between 0 and 1 and round to 2 decimal places
    for player in player_dict:
        player_dict[player] = round(player_dict[player] / total_plays, 2)



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
    filtered_df = df[(df['SourceFile'] == sourcefile) & (df[playertype] == player)]

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

    # Create a dictionary with the aggregated statistics
    stats_dict = {
        'TotalPlays': grouped_stats['TotalPlays'],
        'Total3ptShots': grouped_stats['Total3ptShots'],
        'Total3ptMakes': grouped_stats['Total3ptMakes'],
        '3pt%': grouped_stats['3pt%'],
        'Total2ptShots': grouped_stats['Total2ptShots'],
        'Total2ptMakes': grouped_stats['Total2ptMakes'],
        '2pt%': grouped_stats['2pt%'],
        'TotalMidRangeShots': grouped_stats['TotalMidRangeShots'],
        'TotalMidRangeMakes': grouped_stats['TotalMidRangeMakes'],
        'MidRange%': grouped_stats['MidRange%'],
        'EFG%': grouped_stats['EFG%'],
        'Turnover': grouped_stats['Turnover'],
        'Foul': grouped_stats['Foul'],
        'playproportion': proportion  # Add play proportion to the dictionary
    }

    return stats_dict

    
if __name__ == "__main__":
    # Example usage: python seperate_player_data.py file1.csv file2.csv ... output_directory
    if len(sys.argv) < 3:
        print("Usage: python seperate_player_data.py <file1.csv> <file2.csv> ... <output_directory>")
        sys.exit(1)

    # List of input files
    file_list = sys.argv[1:-1]
    
    # Output directory for individual player files
    output_directory = '.'

    # Run the function
    insights = analyze_player_performance(file_list, output_directory)
