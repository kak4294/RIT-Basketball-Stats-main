import os, sys
from datetime import datetime 
import pandas as pd
import json
import math
from visual_generator import create_bar_chart

def analyze_team_performance(file, output_directory, team_name):
    
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file)
    
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
    process_team_stats(df, team_name, insights, output_directory)
    
    return insights


def process_team_stats(df: pd.DataFrame, name, insights, output_directory):
    # Iterate through the types of insights
    for key in insights:
        if key == 'PNR_insights':  # PNR insights
            PNR_team_stats(df, insights[key], output_directory)
        elif key == 'Iso_insights':  # Iso insights
            Iso_team_stats(df, insights[key], output_directory)
        elif key == 'Post_insights':  # Post insights
            Post_team_stats(df, insights[key], output_directory)
        elif key == 'Cut_insights': # Cut insights
            Cut_team_stats(df, insights[key], output_directory)
        elif key == 'Handoff_insights': # Handoff insights
            Handoff_team_stats(df, insights[key], output_directory)
        elif key == 'Spotup_insights':  # Spotup insights
            Spotup_team_stats(df, insights[key], output_directory)
        elif key == 'Transition_insights':  # Transition insights
            Transition_team_stats(df, insights[key], output_directory)
        elif key == 'OffScreen_insights':   # Offscreen insights
            Offscreen_team_stats(df, insights[key], output_directory)
        elif key == 'Rollman_insights':  # Rollman insights
            Rollman_team_stats(df, insights[key], output_directory)
            

def PNR_team_stats(df: pd.DataFrame, insight, output_directory):
    # Finds total efficiency for ALL PNR scorer plays
    filtered_df1 = df[(df['SourceFile'] == 'player_pnr_efficiency.csv')]
    total_pnr_efficiency = compute_grouped_statistics(filtered_df1, 'player_pnr_efficiency', 'Team', 'PNR_Scorer')

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
    total_pnr_offpick_efficiency = compute_grouped_statistics(filtered_df2_offpick, 'player_pnr_offpick_efficiency', 'Team', 'PNR_Off')

    filtered_df2_rejectpick = df[(df['SourceFile'] == 'player_pnr_rejectpick_efficiency.csv')]
    total_pnr_reject_efficiency = compute_grouped_statistics(filtered_df2_rejectpick, 'player_pnr_rejectpick_efficiency', 'Team', 'PNR_Reject')

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
        y_max=100,
        title='PNR Direction/Location Frequency',
        output_filename=output_file_path
    )

    filtered_df3_high = df[(df['SourceFile'] == 'player_pnr_bhhigh_efficiency.csv')]
    total_pnr_bhhigh_efficiency = compute_grouped_statistics(filtered_df3_high, 'player_pnr_bhhigh_efficiency', 'Team', 'PNR_High')

    filtered_df3_left = df[(df['SourceFile'] == 'player_pnr_bhleft_efficiency.csv')]
    total_pnr_bhleft_efficiency = compute_grouped_statistics(filtered_df3_left, 'player_pnr_bhleft_efficiency', 'Team', 'PNR_Left')

    filtered_df3_right = df[(df['SourceFile'] == 'player_pnr_bhright_efficiency.csv')]
    total_pnr_bhright_efficiency = compute_grouped_statistics(filtered_df3_right, 'player_pnr_bhright_efficiency', 'Team', 'PNR_Right')

    # Calculate total proportion and efficiency for BH High --> Rejecting Screens
    filtered_df_bhhigh_reject = df[(df['SourceFile'] == 'player_pnr_bhhigh_rejectpick_efficiency.csv')]
    total_pnr_bhhigh_rejectpick_efficiency = compute_grouped_statistics(filtered_df_bhhigh_reject, 'player_pnr_bhhigh_rejectpick_efficiency', 'Team', 'PNR_High_Reject')
    bhhigh_reject_total = 0
    if 'PNR_High_Reject' in total_pnr_bhhigh_rejectpick_efficiency.keys():
        bhhigh_reject_total = total_pnr_bhhigh_rejectpick_efficiency['PNR_High_Reject']['TotalPlays']

    # Calculate total proportion and efficiency for BH High --> OFF Screens
    filtered_df_bhhigh_offpick = df[(df['SourceFile'] == 'player_pnr_bhhigh_offpick_efficiency.csv')]
    total_pnr_bhhigh_offpick_efficiency = compute_grouped_statistics(filtered_df_bhhigh_offpick, 'player_pnr_bhhigh_offpick_efficiency', 'Team', 'PNR_High_Off')
    bhhigh_off_total = 0
    if 'PNR_High_Off' in total_pnr_bhhigh_offpick_efficiency.keys():
        bhhigh_off_total = total_pnr_bhhigh_offpick_efficiency['PNR_High_Off']['TotalPlays']


    # Calculate total proportion and efficiency for BH Left --> Rejecting Screens
    filtered_df_bhleft_reject = df[(df['SourceFile'] == 'player_pnr_bhleft_rejectpick_efficiency.csv')]
    total_pnr_bhleft_rejectpick_efficiency = compute_grouped_statistics(filtered_df_bhleft_reject, 'player_pnr_bhleft_rejectpick_efficiency', 'Team', 'PNR_Left_Reject')
    bhleft_reject_total = 0
    if 'PNR_Left_Reject' in total_pnr_bhleft_rejectpick_efficiency.keys():
        bhleft_reject_total = total_pnr_bhleft_rejectpick_efficiency['PNR_Left_Reject']['TotalPlays']


    # Calculate total proportion and efficiency for BH Left --> OFF Screens
    filtered_df_bhleft_offpick = df[(df['SourceFile'] == 'player_pnr_bhleft_offpick_efficiency.csv')]
    total_pnr_bhleft_offpick_efficiency = compute_grouped_statistics(filtered_df_bhleft_offpick, 'player_pnr_bhleft_offpick_efficiency', 'Team', 'PNR_Left_Off')
    bhleft_off_total = 0
    if 'PNR_Left_Off' in total_pnr_bhleft_offpick_efficiency.keys():
        bhleft_off_total = total_pnr_bhleft_offpick_efficiency['PNR_Left_Off']['TotalPlays']


    # Calculate total proportion and efficiency for BH Right --> Rejecting Screens
    filtered_df_bhright_reject = df[(df['SourceFile'] == 'player_pnr_bhright_rejectpick_efficiency.csv')]
    total_pnr_bhright_rejectpick_efficiency = compute_grouped_statistics(filtered_df_bhright_reject, 'player_pnr_bhright_rejectpick_efficiency', 'Team', 'PNR_Right_Reject')
    bhright_reject_total = 0
    if 'PNR_Right_Reject' in total_pnr_bhright_rejectpick_efficiency.keys():
        bhright_reject_total = total_pnr_bhright_rejectpick_efficiency['PNR_Right_Reject']['TotalPlays']


    # Calculate total proportion and efficiency for BH Right --> OFF Screens
    filtered_df_bhright_offpick = df[(df['SourceFile'] == 'player_pnr_bhright_offpick_efficiency.csv')]
    total_pnr_bhright_offpick_efficiency = compute_grouped_statistics(filtered_df_bhright_offpick, 'player_pnr_bhright_offpick_efficiency', 'Team', 'PNR_Right_Off')
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

def Iso_team_stats(df: pd.DataFrame, insight, output_directory):
    # Finds total efficiency for ALL Iso scorer plays
    filtered_df1 = df [ (df['SourceFile'] == 'player_iso_efficiency.csv') ]
    total_iso_efficiency = compute_grouped_statistics(filtered_df1, 'player_iso_efficiency', 'Team', 'Iso_Scorer')


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
        y_max=200,
        title='Iso Direction / Location Frequency',
        output_filename=output_file_path
    )

    filtered_df2 = df [ (df['SourceFile'] == 'player_iso_left_efficiency.csv') ]
    total_iso_left_efficiency = compute_grouped_statistics(filtered_df2, 'player_iso_left_efficiency', 'Team', 'Iso_Left')

    filtered_df2 = df [ (df['SourceFile'] == 'player_iso_right_efficiency.csv') ]
    total_iso_right_efficiency = compute_grouped_statistics(filtered_df2, 'player_iso_right_efficiency', 'Team', 'Iso_Right')

    filtered_df2 = df [ (df['SourceFile'] == 'player_iso_top_efficiency.csv') ]
    total_iso_top_efficiency = compute_grouped_statistics(filtered_df2, 'player_iso_top_efficiency', 'Team', 'Iso_Top')

    insight.extend([
        total_iso_efficiency,
        total_iso_proportion_dict,
        total_iso_left_efficiency,
        total_iso_right_efficiency,
        total_iso_top_efficiency
    ])

def Post_team_stats(df: pd.DataFrame, insight, output_directory):
    # Finds total efficiency for ALL Post scorer plays
    filtered_df1 = df [ (df['SourceFile'] == 'player_post_efficiency.csv') ]
    total_post_efficiency = compute_grouped_statistics(filtered_df1, 'player_post_efficiency', 'Team', 'Post_Scorer')

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
        y_max=200,
        title='Post Location Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_post_leftblock_efficiency.csv') ]
    total_post_leftblock_efficiency = compute_grouped_statistics(filtered_df, 'player_post_leftblock_efficiency', 'Team', 'Post_LeftBlock')

    filtered_df = df [ (df['SourceFile'] == 'player_post_rightblock_efficiency.csv') ]
    total_post_rightblock_efficiency = compute_grouped_statistics(filtered_df, 'player_post_rightblock_efficiency', 'Team', 'Post_RightBlock')

    filtered_df = df [ (df['SourceFile'] == 'player_post_middle_efficiency.csv') ]
    total_post_middle_efficiency = compute_grouped_statistics(filtered_df, 'player_post_middle_efficiency', 'Team', 'Post_Middle')


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
    post_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'player_post_leftshoulder_efficiency', 'Team', 'Post_LeftShoulder')

    filtered_df = df [ (df['SourceFile'] == 'player_post_rightshoulder_efficiency.csv') ]
    post_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'player_post_rightshoulder_efficiency', 'Team', 'Post_RightShoulder')

    filtered_df = df [ (df['SourceFile'] == 'player_post_faceup_efficiency.csv') ]
    post_faceup_efficiency = compute_grouped_statistics(filtered_df, 'player_post_faceup_efficiency', 'Team', 'Post_Faceup')
    
    
    # Calculates the combinations of post plays
    filtered_df = df[(df['SourceFile'] == 'player_post_leftblock_faceup_efficiency.csv')]
    leftblock_faceup_efficiency = compute_grouped_statistics(filtered_df, 'player_post_leftblock_faceup_efficiency', 'Team', 'Post_LeftBlock_Faceup')
    leftblock_faceup_total = 0
    for key in leftblock_faceup_efficiency:
        if 'Post_LeftBlock_Faceup' == key:
            leftblock_faceup_total = leftblock_faceup_efficiency['Post_LeftBlock_Faceup']['TotalPlays']

    filtered_df = df[(df['SourceFile'] == 'player_post_leftblock_leftshoulder_efficiency.csv')]
    leftblock_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'player_post_leftblock_leftshoulder_efficiency', 'Team', 'Post_LeftBlock_LeftShoulder')
    leftblock_leftshoulder_total = 0
    for key in leftblock_leftshoulder_efficiency:
        if 'Post_LeftBlock_LeftShoulder' == key:
            leftblock_leftshoulder_total = leftblock_leftshoulder_efficiency['Post_LeftBlock_LeftShoulder']['TotalPlays']

    filtered_df = df[(df['SourceFile'] == 'player_post_leftblock_rightshoulder_efficiency.csv')]
    leftblock_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'player_post_leftblock_rightshoulder_efficiency', 'Team', 'Post_LeftBlock_RightShoulder' )
    leftblock_rightshoulder_total = 0
    for key in leftblock_rightshoulder_efficiency:
        if 'Post_LeftBlock_RightShoulder'== key:
            leftblock_rightshoulder_total = leftblock_rightshoulder_efficiency['Post_LeftBlock_RightShoulder']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_faceup_efficiency.csv')]
    rightblock_faceup_efficiency = compute_grouped_statistics(filtered_df, 'player_post_rightblock_faceup_efficiency', 'Team', 'Post_RightBlock_Faceup')
    rightblock_faceup_total = 0
    for key in rightblock_faceup_efficiency:
        if 'Post_RightBlock_Faceup'== key:
            rightblock_faceup_total = rightblock_faceup_efficiency['Post_RightBlock_Faceup']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_leftshoulder_efficiency.csv')]
    rightblock_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'player_post_rightblock_leftshoulder_efficiency', 'Team', 'Post_RightBlock_LeftShoulder')
    rightblock_leftshoulder_total = 0
    for key in rightblock_leftshoulder_efficiency:
        if 'Post_RightBlock_LeftShoulder'== key:
            rightblock_leftshoulder_total = rightblock_leftshoulder_efficiency['Post_RightBlock_LeftShoulder']["TotalPlays"]
    

    filtered_df = df[(df['SourceFile'] == 'player_post_rightblock_rightshoulder_efficiency.csv')]
    rightblock_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'player_post_rightblock_rightshoulder_efficiency', 'Team', 'Post_RightBlock_RightShoulder')
    rightblock_rightshoulder_total = 0
    for key in rightblock_rightshoulder_efficiency:
        if 'Post_RightBlock_RightShoulder'== key:
            rightblock_rightshoulder_total = rightblock_rightshoulder_efficiency['Post_RightBlock_RightShoulder']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_middle_faceup_efficiency.csv')]
    middle_faceup_efficiency = compute_grouped_statistics(filtered_df, 'player_post_middle_faceup_efficiency', 'Team', 'Post_Middle_Faceup')
    middle_faceup_total = 0
    for key in middle_faceup_efficiency:
        if 'Post_Middle_Faceup'== key:
            middle_faceup_total = middle_faceup_efficiency['Post_Middle_Faceup']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_middle_leftshoulder_efficiency.csv')]
    middle_leftshoulder_efficiency = compute_grouped_statistics(filtered_df, 'player_post_middle_leftshoulder_efficiency', 'Team', 'Post_Middle_LeftShoulder')
    middle_leftshoulder_total = 0
    for key in middle_leftshoulder_efficiency:
        if 'Post_Middle_LeftShoulder'== key:
            middle_leftshoulder_total = middle_leftshoulder_efficiency['Post_Middle_LeftShoulder']["TotalPlays"]

    filtered_df = df[(df['SourceFile'] == 'player_post_middle_rightshoulder_efficiency.csv')]
    middle_rightshoulder_efficiency = compute_grouped_statistics(filtered_df, 'player_post_middle_rightshoulder_efficiency', 'Team', 'Post_Middle_RightShoulder')
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

def Cut_team_stats(df: pd.DataFrame, insight, output_directory):
    # Finds total efficiency for ALL Cutter scorer plays
    filtered_df = df [ (df['SourceFile'] == 'player_cut_efficiency.csv') ]
    total_cut_efficiency = compute_grouped_statistics(filtered_df, 'player_cut_efficiency', 'Team', 'Cut_Scorer')

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
    total_cut_basket_efficiency = compute_grouped_statistics(filtered_df, 'player_cut_basket_efficiency', 'Team', 'Basket_Cuts')

    filtered_df = df [ (df['SourceFile'] == 'player_cut_flash_efficiency.csv') ]
    total_cut_flash_efficiency = compute_grouped_statistics(filtered_df, 'player_cut_flash_efficiency', 'Team', 'Flash_Cuts')

    filtered_df = df [ (df['SourceFile'] == 'player_cut_screen_efficiency.csv') ]
    total_cut_screen_efficiency = compute_grouped_statistics(filtered_df, 'player_cut_screen_efficiency', 'Team', 'Screen_Cuts')
    
    insight.extend([
        total_cut_efficiency,
        [total_cut_proportion_dict],
        total_cut_basket_efficiency,
        total_cut_flash_efficiency,
        total_cut_screen_efficiency
    ])

def Spotup_team_stats(df: pd.DataFrame, insight, output_directory):
    # Finds total efficiency for ALL Spotup scorer plays
    filtered_df = df [ (df['SourceFile'] == 'player_spotup_efficiency.csv') ]
    total_spotup_efficiency = compute_grouped_statistics(filtered_df, 'player_spotup_efficiency', 'Team', 'SpotUp_Scorer')

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
        y_max=200,
        title='Spot Up Play Type Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_spotup_jumpshot_efficiency.csv') ]
    total_spotup_jumpshot_efficiency = compute_grouped_statistics(filtered_df, 'player_spotup_jumpshot_efficiency', 'Team', 'SpotUp_Jumper')

    total_drive_csvs = ['player_spotup_leftdrive_efficiency.csv', 'player_spotup_rightdrive_efficiency.csv', 'player_spotup_straightdrive_efficiency.csv']
    filtered_df = df [ (df['SourceFile'].isin(total_drive_csvs))]
    total_spotup_drive_efficiency = compute_grouped_statistics(filtered_df, 'spotup_drives_efficiency', 'Team', 'SpotUp_Drive')


    filtered_df = df [ (df['SourceFile'] == 'player_spotup_leftdrive_efficiency.csv') ]
    total_spotup_leftdrive_efficiency = compute_grouped_statistics(filtered_df, 'player_spotup_leftdrive_efficiency', 'Team', 'SpotUp_LeftDrive')
    total_spotup_leftdrive_total = 0
    if 'SpotUp_LeftDrive' in total_spotup_leftdrive_efficiency.keys():
        total_spotup_leftdrive_total = total_spotup_leftdrive_efficiency['SpotUp_LeftDrive']['TotalPlays']
    

    filtered_df = df [ (df['SourceFile'] == 'player_spotup_rightdrive_efficiency.csv') ]
    total_spotup_rightdrive_efficiency = compute_grouped_statistics(filtered_df, 'player_spotup_rightdrive_efficiency', 'Team', 'SpotUp_RightDrive')
    total_spotup_rightdrive_total = 0
    if 'SpotUp_RightDrive' in total_spotup_rightdrive_efficiency.keys():
        total_spotup_rightdrive_total = total_spotup_rightdrive_efficiency['SpotUp_RightDrive']['TotalPlays']
   

    filtered_df = df [ (df['SourceFile'] == 'player_spotup_straightdrive_efficiency.csv') ]
    total_spotup_straightdrive_efficiency = compute_grouped_statistics(filtered_df, 'player_spotup_straightdrive_efficiency', 'Team', 'SpotUp_StraightDrive')
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
        y_max=200,
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

def Transition_team_stats(df: pd.DataFrame, insight, output_directory):
    # Calculates total proportion and efficiency for Transition plays
    total_transition_proport_csvs = ['player_transition_bh_efficiency.csv', 'player_transition_leakouts_efficiency.csv', 
                                    'player_transition_leftwing_efficiency.csv', 'player_transition_rightwing_efficiency.csv', 'player_transition_trailer_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_transition_proport_csvs) ]
    total_transition_proportion = find_play_proportions(filtered_df, total_transition_proport_csvs)
    total_transition_proportion_dict = {'Ball Handler' : total_transition_proportion[0], 'Leakouts': total_transition_proportion[1],
                                        'Leftwing': total_transition_proportion[2], 'Rightwing' : total_transition_proportion[3], 
                                        'Trailer': total_transition_proportion[4], 'Total Plays': total_transition_proportion[5] }
    total_transition_efficiency = compute_grouped_statistics(filtered_df, 'transition_efficiency', 'Team', 'Transition_Scorer')

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
        y_max=200,
        title='Transition Type Frequency',
        output_filename=output_file_path
    )


    filtered_df = df [ (df['SourceFile'] == 'player_transition_bh_efficiency.csv') ]
    total_transition_bh_efficiency = compute_grouped_statistics(filtered_df, 'player_transition_bh_efficiency', 'Team', 'Transition_BH')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_leakouts_efficiency.csv') ]
    total_transition_leakouts_efficiency = compute_grouped_statistics(filtered_df, 'player_transition_leakouts_efficiency', 'Team', 'Transition_Leakouts')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_leftwing_efficiency.csv') ]
    total_transition_leftwing_efficiency = compute_grouped_statistics(filtered_df, 'player_transition_leftwing_efficiency', 'Team', 'Transition_LeftWing')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_rightwing_efficiency.csv') ]
    total_transition_rightwing_efficiency = compute_grouped_statistics(filtered_df, 'player_transition_rightwing_efficiency', 'Team', 'Transition_RightWing')

    filtered_df = df [ (df['SourceFile'] == 'player_transition_trailer_efficiency.csv') ]
    total_transition_trailer_efficiency = compute_grouped_statistics(filtered_df, 'player_transition_trailer_efficiency', 'Team', 'Transition_Trailer')

    insight.extend([
        total_transition_proportion_dict,
        total_transition_efficiency,
        total_transition_bh_efficiency,
        total_transition_leakouts_efficiency,
        total_transition_leftwing_efficiency,
        total_transition_rightwing_efficiency,
        total_transition_trailer_efficiency
    ])

def Offscreen_team_stats(df: pd.DataFrame, insight, output_directory):
    # Finds total efficiency for ALL Off Screen scorer plays
    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_efficiency.csv') ]
    total_offscreens_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_efficiency', 'Team', 'OffScreen_Scorer')

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
        y_max=200,
        title='Off Screen Running Off Shoulder Frequency',
        output_filename=output_file_path
    )
    

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_efficiency.csv') ]
    total_offscreens_left_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_leftshoulder_efficiency', 'Team', 'OffScreen_LeftShoulder')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_efficiency.csv') ]
    total_offscreens_right_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_rightshoulder_efficiency', 'Team', 'OffScreen_RightShoulder')

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
        y_max=200,
        title='Off Screen Type Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_flare_efficiency.csv') ]
    total_offscreens_flare_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_flare_efficiency', 'Team', 'Flare')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_straight_efficiency.csv') ]
    total_offscreens_straight_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_straight_efficiency', 'Team', 'Straight')

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_curl_efficiency.csv') ]
    total_offscreens_curl_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_curl_efficiency', 'Team', 'Curl')

    # Calculates total proportion and efficiency for combinations of direction and type of off screen
    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_flare_efficiency.csv') ]
    total_offscreens_left_flare_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_leftshoulder_flare_efficiency', 'Team', 'LeftShoulder_Flare')
    offscreens_left_flare_total = 0
    if 'LeftShoulder_Flare' in total_offscreens_left_flare_efficiency.keys():
        offscreens_left_flare_total = total_offscreens_left_flare_efficiency['LeftShoulder_Flare']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_straight_efficiency.csv') ]
    total_offscreens_left_straight_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_leftshoulder_straight_efficiency', 'Team', 'LeftShoulder_Straight')
    offscreens_left_straight_total = 0
    if 'LeftShoulder_Straight' in total_offscreens_left_straight_efficiency.keys():
        offscreens_left_straight_total = total_offscreens_left_straight_efficiency['LeftShoulder_Straight']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_leftshoulder_curl_efficiency.csv') ]
    total_offscreens_left_curl_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_leftshoulder_curl_efficiency', 'Team', 'LeftShoulder_Curl')
    offscreens_left_curl_total = 0
    if 'LeftShoulder_Curl' in total_offscreens_left_curl_efficiency.keys():
        offscreens_left_curl_total = total_offscreens_left_curl_efficiency['LeftShoulder_Curl']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_flare_efficiency.csv') ]
    total_offscreens_right_flare_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_rightshoulder_flare_efficiency', 'Team', 'RightShoulder_Flare')
    offscreens_right_flare_total = 0
    if 'RightShoulder_Flare' in total_offscreens_right_flare_efficiency.keys():
        offscreens_right_flare_total = total_offscreens_right_flare_efficiency['RightShoulder_Flare']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_straight_efficiency.csv') ]
    total_offscreens_right_straight_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_rightshoulder_straight_efficiency', 'Team', 'RightShoulder_Straight')
    offscreens_right_straight_total = 0
    if 'RightShoulder_Straight' in total_offscreens_right_straight_efficiency.keys():
        offscreens_right_straight_total = total_offscreens_right_straight_efficiency['RightShoulder_Straight']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_offscreens_rightshoulder_curl_efficiency.csv') ]
    total_offscreens_right_curl_efficiency = compute_grouped_statistics(filtered_df, 'player_offscreens_rightshoulder_curl_efficiency', 'Team', 'RightShoulder_Curl')
    offscreens_right_curl_total = 0
    if 'RightShoulder_Curl' in total_offscreens_right_curl_efficiency.keys():
        offscreens_right_curl_total = total_offscreens_right_curl_efficiency['RightShoulder_Curl']['TotalPlays']
    
    
    combo_dict = {'Left Shoulder - Flare': offscreens_left_flare_total, 'Left Shoulder - Straight': offscreens_left_straight_total, 'Left Shoulder': offscreens_left_curl_total,
                  'Right Shoulder - Flare': offscreens_right_flare_total, 'Right Shoulder - Straight': offscreens_right_straight_total, 'Right Shoulder': offscreens_right_curl_total}
    output_file_path = os.path.join(output_directory, 'OffScreen_Combination_Freq.png')
    create_bar_chart(
        data_dict=combo_dict,
        section=6,
        y_max=200,
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
    
def Handoff_team_stats(df: pd.DataFrame, insight, output_directory):
        # Finds total efficiency for ALL Handoff scorer plays
    filtered_df1 = df [ (df['SourceFile'] == 'player_handoffs_efficiency.csv') ]
    total_handoffs_efficiency = compute_grouped_statistics(filtered_df1, 'player_handoffs_efficiency', 'Team', 'Handoff_Scorer')

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
        y_max=200,
        title='Hand Off Directio Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhleft_efficiency.csv') ]
    total_handoffs_left_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_bhleft_efficiency', 'Team', 'BHLeft')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhright_efficiency.csv') ]
    total_handoffs_right_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_bhright_efficiency', 'Team', 'BHRight')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_top_efficiency.csv') ]
    total_handoffs_top_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_top_efficiency', 'Team', 'BHTop')
    
    
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
        y_max=200,
        title='Hand Off Type Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_stationary_efficiency.csv') ]
    total_handoffs_stationary_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_stationary_efficiency', 'Team', 'Stationary')

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_dribble_efficiency.csv') ]
    total_handoffs_dribble_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_dribble_efficiency', 'Team', 'Dribble')
    
    
    # Calculates combinations  of type of handoff and direction
    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhleft_stationary_efficiency.csv') ]
    total_handoffs_stationary_left_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_bhleft_stationary_efficiency', 'Team', 'Left_Stationary')
    handoffs_stationary_left_total = 0
    if 'Left_Stationary' in total_handoffs_stationary_left_efficiency.keys():
        handoffs_stationary_left_total = total_handoffs_stationary_left_efficiency['Left_Stationary']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhright_stationary_efficiency.csv') ]
    total_handoffs_stationary_right_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_bhright_stationary_efficiency', 'Team', 'Right_Stationary')
    handoffs_stationary_right_total = 0
    if 'Right_Stationary' in total_handoffs_stationary_right_efficiency.keys():
        handoffs_stationary_right_total =total_handoffs_stationary_right_efficiency['Right_Stationary']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_top_stationary_efficiency.csv') ]
    total_handoffs_stationary_top_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_top_stationary_efficiency', 'Team', 'Top_Stationary')
    handoffs_stationary_top_total = 0
    if 'Top_Stationary' in total_handoffs_stationary_top_efficiency.keys():
        handoffs_stationary_top_total = total_handoffs_stationary_top_efficiency['Top_Stationary']['TotalPlays']


    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhleft_dribble_efficiency.csv') ]
    total_handoffs_dribble_left_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_bhleft_dribble_efficiency', 'Team', 'Left_Dribble')
    handoffs_dribble_left_total = 0
    if 'Left_Dribble' in total_handoffs_dribble_left_efficiency.keys():
        handoffs_dribble_left_total = total_handoffs_dribble_left_efficiency['Left_Dribble']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_bhright_dribble_efficiency.csv') ]
    total_handoffs_dribble_right_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_bhright_dribble_efficiency', 'Team', 'Right_Dribble')
    handoffs_dribble_right_total = 0
    if 'Right_Dribble' in total_handoffs_dribble_right_efficiency.keys():
        handoffs_dribble_right_total = total_handoffs_dribble_right_efficiency['Right_Dribble']['TotalPlays']

    filtered_df = df [ (df['SourceFile'] == 'player_handoffs_top_dribble_efficiency.csv') ]
    total_handoffs_dribble_top_efficiency = compute_grouped_statistics(filtered_df, 'player_handoffs_top_dribble_efficiency', 'Team', 'Top_Dribble')
    handoffs_dribble_top_total = 0
    if 'Top_Dribble' in total_handoffs_dribble_top_efficiency.keys():
        handoffs_dribble_top_total = total_handoffs_dribble_top_efficiency['Top_Dribble']['TotalPlays']
        
    combo_dict = {'Stationary - Left': handoffs_stationary_left_total, 'Stationary - Right': handoffs_stationary_right_total, 'Stationary - Top': handoffs_stationary_top_total,
                  'Dribble - Left': handoffs_dribble_left_total, 'Stationary - Right': handoffs_dribble_right_total, 'Stationary - Top': handoffs_dribble_top_total}
    output_file_path = os.path.join(output_directory, 'HandOff_Combination_Freq.png')
    create_bar_chart(
        data_dict=combo_dict,
        section=7,
        y_max=200,
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
    
def Rollman_team_stats(df: pd.DataFrame, insight, output_directory):
    
    # Calculates total proportion and efficiency for Rollman plays
    filtered_df = df [ (df['SourceFile'] == 'player_rollman_efficiency.csv')]
    total_rollman_efficiency = compute_grouped_statistics(filtered_df, 'player_rollman_efficiency', 'Team', 'Rollman_Total')


    # Calculates proportion / efficiency for rollman Slips vs Rolls vs Pops
    total_rollman_type_proport_csvs = ['player_rollman_slip_efficiency.csv', 'player_rollman_roll_efficiency.csv',
                                    'player_rollman_pop_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_rollman_type_proport_csvs) ]
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
        y_max=200,
        title='Rollman Play Type Frequency',
        output_filename=output_file_path
    )


    filtered_df = df [ (df['SourceFile'] == 'player_rollman_slip_efficiency.csv') ]
    total_slip_efficiency = compute_grouped_statistics(filtered_df, 'player_rollman_slip_efficiency', 'Team', 'Rollman_Slip')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_roll_efficiency.csv') ]
    total_roll_efficiency = compute_grouped_statistics(filtered_df, 'player_rollman_roll_efficiency', 'Team', 'Rollman_Roll')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_pop_efficiency.csv') ]
    total_pop_efficiency = compute_grouped_statistics(filtered_df, 'player_rollman_pop_efficiency', 'Team', 'Rollman_Pop')
    
    
    # Calculates proportion / efficiency for Left Drives vs Right Drives for SLIPS
    total_rollman_direction_proport_csvs = ['player_rollman_leftdrive_slip_efficiency.csv', 'player_rollman_rightdrive_slip_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_rollman_direction_proport_csvs)]
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
        y_max=200,
        title='Rollman Slip - Drive Direction Frequency',
        output_filename=output_file_path
    )
    

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_leftdrive_slip_efficiency.csv') ]
    total_slip_left_efficiency = compute_grouped_statistics(filtered_df, 'player_rollman_leftdrive_slip_efficiency', 'Team', 'Rollman Slip_Left_Drive')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_rightdrive_slip_efficiency.csv') ]
    total_slip_right_efficiency = compute_grouped_statistics(filtered_df, 'player_rollman_rightdrive_slip_efficiency', 'Team', 'Rollman Slip_Right_Drive')


    # Calculates proportion / efficiency for Left Drives vs Right Drives for POPS
    total_rollman_direction_pop_proport_csvs = ['player_rollman_leftdrive_pop_efficiency.csv', 'player_rollman_rightdrive_pop_efficiency.csv']
    filtered_df = df [ df['SourceFile'].isin(total_rollman_direction_pop_proport_csvs) ]
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
        y_max=200,
        title='Rollman Pop - Drive Direction Frequency',
        output_filename=output_file_path
    )

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_leftdrive_pop_efficiency.csv') ]
    total_pop_left_efficiency = compute_grouped_statistics(filtered_df, 'player_rollman_leftdrive_pop_efficiency', 'Team', 'Rollman_Pop_Left')

    filtered_df = df [ (df['SourceFile'] == 'player_rollman_rightdrive_pop_efficiency.csv') ]
    total_pop_right_efficiency = compute_grouped_statistics(filtered_df, 'player_rollman_rightdrive_pop_efficiency', 'Team', 'Rollman_Pop_Right')
    
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
    ])


          
            
def compute_grouped_statistics(df, filename, playertype, key):
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
            'File': filename,
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
    #if len(sys.argv) < 2:
    #    print("Usage: python team_offense_analyzer.py <team_file.csv> <output_directory>")
    #    sys.exit(1)

    # Extract command-line arguments
    team_offense_file = os.path.join("/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/cleaned/Teams/team_offense_data/Rochester_Institute_of_Technology_Tigers.csv")
    output_directory = "/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/cleaned/reports/team/"


    print(f"Processing Team Offensive File: {team_offense_file}")
    
    base_filename = os.path.basename(team_offense_file)  # Extracts 'location_name.csv'
    name_part = os.path.splitext(base_filename)[0]  # Removes '.csv' -> 'location_name'
    team_file = name_part.replace('_', '-')  # 'location-name'
    team_name = name_part.replace('_', ' ')  # 'location name'
    
    # 2. Get the current date
    current_datetime = datetime.now()
    month = current_datetime.strftime("%m")
    day = current_datetime.strftime("%d")
    year = current_datetime.strftime("%Y")
        
    # 3. Create the folder name
    foldername = f"{team_file}-{month}-{day}-{year}"
    
    team_output_folder = os.path.join(output_directory, foldername)
    os.makedirs(team_output_folder, exist_ok=True)
    
    image_output_folder = os.path.join(team_output_folder, 'images')
    os.makedirs(image_output_folder, exist_ok=True)
    
    # Run the function
    insights = analyze_team_performance(team_offense_file, image_output_folder, team_name)
    
    # Specify the path for the output insights JSON file
    output_insights_file = os.path.join(team_output_folder, 'team_insights.json')

    # Write the insights to the JSON file
    write_insights_to_json(insights, output_insights_file)
