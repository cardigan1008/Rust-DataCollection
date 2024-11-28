# Rust-DataCollection

## OverView

This tool is a web crawler designed for collecting issues and their associated pull requests (PRs) from Rust repositories. It helps in aggregating and analyzing data related to development and maintenance activities within Rust projects.

**Note: The current version does not support automatic replacement of the GitHub Token in case of a Rate Limit error.*

## Requirements

To install the necessary dependencies, run the following command:

```bash
pip install coloredlogs
pip install requests
pip install pandas
pip install tqdm
```

## Usage

### Issue collection

To collect issues from Rust repositories, use the following command. Replace `<output_path>` with your desired output directory and `<token>` with your GitHub authentication token.

```bash
python main.py issue <output_path> <token>
```

This command will collect issues and save them to the specified output path.

### PR collection

For collecting pull requests, use:

```bash
python main.py pr <input_path> <output_path> <token>
```

Here, `<input_path>` is the directory where the pull requests will be collected from, `<output_path>` is where the collected pull requests will be saved, and `<token>` is your GitHub authentication token.

### Merge CSV files

To merge multiple CSV files into a single file, use:

```bash
python command.py merge <input_directory> <output_file>
```

In this command, `<input_directory>` is the directory containing the CSV files you want to merge, and `<output_file>` is the path where the merged CSV file will be saved.
