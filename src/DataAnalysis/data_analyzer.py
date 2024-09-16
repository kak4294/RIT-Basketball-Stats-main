import pandas as pd
import sys
import os

def analyze_player_performance(file_list, output_directory):
    # Load the CSV file into a DataFrame
    for file in file_list:
        
        df = pd.read_csv(file)
        
        primary_df, secondary_df, scorer_df, player_name  = split_player_data_by_role(file_path)
        
        PNR_insights = []
        Cut_insights = []
        Handoff_insights = []
        Post_insights = []
        Spotup_insights = []
        Transition_insights = []
        Offscreen_insights = []
        Iso_insights =[]
        
        insights = [PNR_insights, Cut_insights, Handoff_insights, Post_insights, Spotup_insights, Transition_insights, Offscreen_insights, Iso_insights]
        
        team = ['']
        process_primary_stats(primary_df, player_name, insights)
        process_secondary_stats(secondary_df, player_name, insights)
        process_scorer_stats(primary_df, player_name, insights)
        
        
       
            
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


def process_primary_stats(df: pd.DataFrame, name, team, insights):
    # These are a player passing stats.
    # Go through each play type possible ( Iso, PNR, Post )
    # PNR ( High, Left, Right ) -  efficiency as a passer
    # Iso - efficiency as a passer when driving a specific way
    # Post - efficiency as a passer
    # What types of shots do they get when this player goes into a PNR?
    
    for i in range(8):
        insight = insights[i]
        if insight == 'PNR_insights':
            insights[i] = PNR_passer_stats(df, name, insight)
        elif insight == 'Iso_insights':
            insights[i] == Iso_passer_stats(df, name, insight)
        elif insight == 'Post_insights':
            insights[i] == Post_passer_stats(df, name, insight)
            
def PNR_passer_stats(df: pd.DataFrame, name, insights):
        
    # Calculates total passing proportion and efficiency for secondary plays out of a pick n roll
    total_passing_proport_csvs = ['twoplayer_pnr_cut_efficiency.csv', 'twoplayer_pnr_spotupsdrives_efficiency.csv', 'twoplayer_pnr_spotupsjumpers_efficiency.csv', 'player_rollman_efficiency.csv' ]
    filtered_df1 = df [ (df['SourceFile'].isin(total_passing_proport_csvs)) & (df['PrimaryPlayer'] == name) ]
    total_passing_proportion = find_play_proportions(filtered_df1, total_passing_proport_csvs)
    total_passing_proportion_dict = {'Pass PNR Cut' : total_passing_proportion[0], 'Pass PNR Spotup Drive': total_passing_proportion[1],
                                    'Pass PNR Spotup Jumper': total_passing_proportion[2], 'Pass PNR Rollman': total_passing_proportion[3], 'Total Plays': total_passing_proportion[4]}
    total_passing_efficiency = compute_grouped_statistics(filtered_df1, 'Efficiency for all PNR secondary plays together.')

    # Calculates proportion and efficiency of secondary plays when going left on a pick n roll
    total_bhleftpassing_proport_csvs = ['twoplayer_pnrbhleft_cuts_efficiency.csv', 'twoplayer_pnrbhleft_spotupdrives_efficiency.csv', 'twoplayer_pnrbhleft_spotupjumper_efficiency.csv', 'twoplayer_pnrbhleft_rollman_efficiency.csv' ]
    filtered_df2 = df [ (df['SourceFile'].isin(total_bhleftpassing_proport_csvs)) & (df['PrimaryPlayer'] == name) ]
    total_bhleftpassing_proportion = find_play_proportions(filtered_df2, total_bhleftpassing_proport_csvs)
    total_bhleftpassing_proportion_dict = {'BH Left Pass PNR Cut' : total_bhleftpassing_proportion[0], 'BH Left Pass PNR Spotup Drive': total_bhleftpassing_proportion[1],
                                    'BH Left Pass PNR Spotup Jumper': total_bhleftpassing_proportion[2], 'BH Left Pass PNR Rollman': total_bhleftpassing_proportion[3], 'Total Plays': total_bhleftpassing_proportion[4]}
    total_bhleftpassing_efficiency = compute_grouped_statistics(filtered_df2, 'Efficiency for all PNR secondary plays going left.')

    # Calculates proportion and efficiency of secondary plays when going right on a pick n roll
    total_bhrightpassing_proport_csvs = ['twoplayer_pnrbhright_cuts_efficiency.csv', 'twoplayer_pnrbhright_spotupdrives_efficiency.csv', 'twoplayer_pnrbhright_spotupjumper_efficiency.csv', 'twoplayer_pnrbhright_rollman_efficiency.csv' ]
    filtered_df3 = df [ (df['SourceFile'].isin(total_bhrightpassing_proport_csvs)) & (df['PrimaryPlayer'] == name) ]
    total_bhrightpassing_proportion = find_play_proportions(filtered_df3, total_bhrightpassing_proport_csvs)
    total_bhrightpassing_proportion_dict = {'BH right Pass PNR Cut' : total_bhrightpassing_proportion[0], 'BH right Pass PNR Spotup Drive': total_bhrightpassing_proportion[1],
                                    'BH right Pass PNR Spotup Jumper': total_bhrightpassing_proportion[2], 'BH right Pass PNR Rollman': total_bhrightpassing_proportion[3], 'Total Plays': total_bhrightpassing_proportion[4]}
    total_bhrightpassing_efficiency = compute_grouped_statistics(filtered_df3, 'Efficiency for all PNR secondary plays going right.')

    # Calculates proportion and efficiency of secondary plays when going on high pick n rolls
    total_bhhighpassing_proport_csvs = ['twoplayer_pnrbhhigh_cuts_efficiency.csv', 'twoplayer_pnrbhhigh_spotupdrives_efficiency.csv', 'twoplayer_pnrbhhigh_spotupjumper_efficiency.csv', 'twoplayer_pnrbhhigh_rollman_efficiency.csv' ]
    filtered_df4 = df [ (df['SourceFile'].isin(total_bhhighpassing_proport_csvs)) & (df['PrimaryPlayer'] == name) ]
    total_bhhighpassing_proportion = find_play_proportions(filtered_df4, total_bhhighpassing_proport_csvs)
    total_bhhighpassing_proportion_dict = {'BH High Pass PNR Cut' : total_bhhighpassing_proportion[0], 'BH High Pass PNR Spotup Drive': total_bhhighpassing_proportion[1],
                                        'BH High Pass PNR Spotup Jumper': total_bhhighpassing_proportion[2], 'BH High Pass PNR Rollman': total_bhhighpassing_proportion[3], 'TotalPlays': total_bhhighpassing_proportion[4]}
    total_bhhighpassing_efficiency = compute_grouped_statistics(filtered_df4, 'Efficiency for all secondary plays in high PNRs.')
    
    # Calculates proportion and efficiency of a player hitting a specific second player off of a pick n roll
    bhhighpassing_cut_csv = 'twoplayer_pnrbhhigh_cut_efficiency.csv'
    filtered_df5 = df [ df['SourceFile'] == bhhighpassing_cut_csv ]
    bhhighpassing_cut_player_proportion = find_player_proportions(filtered_df5, bhhighpassing_cut_csv)
    for player in bhhighpassing_cut_player_proportion:
        player_data = find_player_efficiency(filtered_df5, bhhighpassing_cut_csv, player, bhhighpassing_cut_player_proportion[player] )
        bhhighpassing_cut_player_proportion[player] = player_data
    
def Iso_passer_stats(df: pd.DataFrame, name, insights):
    pass

def Post_passer_stats(df: pd.DataFrame, name, insights):
    pass
    
            
    
def process_secondary_stats(df: pd.DataFrame, name, insights):
    pass

def process_scorer_stats(df: pd.DataFrame, name, insights):
    pass



def compute_grouped_statistics(df, statdescription):
    """
    Groups efficiency statistics by 'PrimaryPlayer' and returns a dictionary with the aggregated statistics.
    
    :param df: Input DataFrame containing basketball statistics data.
    :param statdescription: Description for the statistics.
    :return: Dictionary with grouped statistics, grouped by 'PrimaryPlayer'.
    """

    # Group by 'PrimaryPlayer' and aggregate statistics
    grouped_stats = df.groupby('PrimaryPlayer').agg({
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
        stats_dict[row['PrimaryPlayer']] = {
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
        filtered_df = df['SourceFile'] == sourcefile
        total_plays = filtered_df['TotalPlays'].sum()
        play_totals.append(total_plays)
        total_plays_all += total_plays
    
    # Calculate the proportions for each Sourcefile
    proportions = [total / total_plays_all if total_plays_all > 0 else 0 for total in play_totals]
    
    proportions.append(total_plays_all)

    return proportions
    
    
def find_player_proportions(df, sourcefile):
    """
    Calculates the proportion of total plays each SecondaryPlayer was involved in and rounds it to 2 decimal places.

    :param df: Input DataFrame containing 'SecondaryPlayer' and 'TotalPlays' columns.
    :return: Dictionary where keys are 'SecondaryPlayer' and values are their proportion of total plays (rounded to 2 decimal places).
    """
    # Initialize an empty dictionary to store the total plays for each secondary player
    secondary_player_dict = {}
    total_plays = 0
    filtered_df = df['SourceFile'] == sourcefile

    # Loop through each row in the DataFrame
    for _, row in filtered_df.iterrows():
        # Calculates proportion of players hit for specific play
        secondary_player = row['SecondaryPlayer']
        plays = row['TotalPlays']
        # Add the total plays for the current secondary player
        secondary_player_dict[secondary_player] = plays
        # Keep track of the total number of plays
        total_plays += plays

    # Adjust the values to be proportions between 0 and 1 and round to 2 decimal places
    for player in secondary_player_dict:
        secondary_player_dict[player] = round(secondary_player_dict[player] / total_plays, 2)
    
    return secondary_player_dict
    
    
def find_player_efficiency(df, sourcefile, secondaryplayer, proportion):
    """
    Finds player efficiency statistics based on a specific 'SourceFile' and 'SecondaryPlayer'.
    
    :param df: Input DataFrame containing basketball statistics data.
    :param sourcefile: Specific value to filter by in the 'SourceFile' column.
    :param secondaryplayer: Specific secondary player to filter by in the 'SecondaryPlayer' column.
    :param proportion: Proportion of plays involving the player.
    :return: Dictionary with the player's efficiency statistics and the play proportion.
    """
    
    # Filter the DataFrame where 'SourceFile' matches and 'SecondaryPlayer' matches
    filtered_df = df[(df['SourceFile'] == sourcefile) & (df['SecondaryPlayer'] == secondaryplayer)]

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
    analyze_player_performance(file_list, output_directory)
