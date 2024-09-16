#!/bin/bash

# Make the script executable by running... " chmod +x export_views_to_csv.sh "
# To run the script... " ./export_views_to_csv.sh "

# Database credentials
DB_HOST="localhost"
DB_NAME="basketball_stats"
DB_PORT="3306"
DB_USER="kylekrebs11"
DB_PASS="Alleyoop11!11"

# Directory to export CSV files
EXPORT_PATH="/Users/kylekrebs/Documents/RIT-Basketball-Stats-main/Data-Analysis/efficiency_playdata"

# Initialize a variable to store the list of CSV files
CSV_FILES=""

# Get all view names from the database using the environment variables
VIEW_NAMES=$(mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS -e "SELECT table_name FROM information_schema.views WHERE table_schema='$DB_NAME';" -s --skip-column-names)

# Export each view to a separate CSV file
for VIEW in $VIEW_NAMES; do
  echo "Exporting $VIEW to CSV..."
  
  # Define the path for the CSV file
  CSV_FILE_PATH="$EXPORT_PATH/${VIEW}.csv"
  
  # Run the SQL query and output to CSV format with column names
  mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASS --batch -e "SELECT * FROM $VIEW;" $DB_NAME | sed 's/\t/,/g' > "$CSV_FILE_PATH"
  
  # Add the CSV file path to the list of CSV files
  CSV_FILES="$CSV_FILES $CSV_FILE_PATH"
done

echo "All views have been exported to CSV files in $EXPORT_PATH."

# Output the CSV file names in a single row for easy copy-pasting
echo "CSV files created: $CSV_FILES"
