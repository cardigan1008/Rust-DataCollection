import pandas as pd
import glob


class FileMerger:
    def __init__(self, input_directory, output_file):
        self.input_directory = input_directory
        self.output_file = output_file

    def merge_files(self):
        # Get a list of all CSV files in the input directory
        file_pattern = f'{self.input_directory}/*.csv'
        file_list = glob.glob(file_pattern)

        # Create an empty DataFrame to store the merged data
        merged_data = pd.DataFrame()

        # Iterate through and merge all CSV files
        for file in file_list:
            df = pd.read_csv(file)
            merged_data = pd.concat([merged_data, df], ignore_index=True)

        # Remove duplicate rows based on 'Issue ID' column
        deduplicated_data = merged_data.drop_duplicates(subset='Issue ID')

        # Sort the data by 'Issue ID' column in descending order
        sorted_data = deduplicated_data.sort_values(by='Issue ID', ascending=False)

        # Save the merged and sorted data to a new CSV file
        sorted_data.to_csv(self.output_file, index=False)
