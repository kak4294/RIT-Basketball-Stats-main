import os
import shutil
import sys

def process_directories(parent_dir):
    # Check if the parent directory exists
    if not os.path.isdir(parent_dir):
        print(f"Error: The directory '{parent_dir}' does not exist.")
        sys.exit(1)

    # Iterate through each item in the parent directory
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        
        # Proceed only if the item is a directory
        if os.path.isdir(item_path):
            export_csv_path = os.path.join(item_path, "Export.csv")
            
            # Check if Export.csv exists in the subdirectory
            if os.path.isfile(export_csv_path):
                # Define the new CSV filename based on the folder name
                new_csv_name = f"{item}.csv"
                destination_csv_path = os.path.join(parent_dir, new_csv_name)
                
                try:
                    # Copy and rename the Export.csv to the parent directory
                    shutil.copy(export_csv_path, destination_csv_path)
                    print(f"Copied and renamed '{export_csv_path}' to '{destination_csv_path}'")
                    
                    # Delete the subdirectory after copying
                    shutil.rmtree(item_path)
                    print(f"Deleted directory '{item_path}'")
                
                except Exception as e:
                    print(f"Failed to process '{item_path}'. Error: {e}")
            else:
                print(f"No 'Export.csv' found in '{item_path}'. Skipping...")
        else:
            print(f"'{item_path}' is not a directory. Skipping...")

def rename_files_replace_spaces(parent_dir):
    # Iterate through each item in the parent directory
    for item in os.listdir(parent_dir):
        item_path = os.path.join(parent_dir, item)
        
        # Proceed only if the item is a file
        if os.path.isfile(item_path):
            # Check if the filename contains spaces
            if " " in item:
                # Define the new filename by replacing spaces with underscores
                new_item_name = item.replace(" ", "_")
                new_item_path = os.path.join(parent_dir, new_item_name)
                
                try:
                    os.rename(item_path, new_item_path)
                    print(f"Renamed '{item_path}' to '{new_item_path}'")
                except Exception as e:
                    print(f"Failed to rename '{item_path}'. Error: {e}")
            else:
                print(f"No spaces found in '{item}'. Skipping renaming.")
        else:
            print(f"'{item_path}' is not a file. Skipping renaming.")

def main():
    parent_directory = "/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/data/2023_24/raw/unsaved_games"
    
    print("\n--- Processing Subdirectories ---")
    process_directories(parent_directory)
    
    print("\n--- Renaming Files by Replacing Spaces with Underscores ---")
    rename_files_replace_spaces(parent_directory)
if __name__ == "__main__":
    main()
