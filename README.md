# Actioneer HTML Processor

A tool for extracting and processing data from Actioneer HTML tables.

## Overview

This project provides a flexible parser for HTML tables from the Actioneer system. It extracts detailed information about listings including:

- Item details (name, quantity, image URLs)
- Seller information
- Pricing data
- Duration
- Faction details (when available)
- All metadata attributes

## Requirements

- Python 3.7+
- UV package manager

## Project Structure

```
./
├── data
│   ├── processed
│   │   └── actioneer_listings.csv
│   └── raw
│       └── actioneer-2025-03-04.html
├── .gitignore
├── .python-version
├── actioneer_raw_csv.py
├── Makefile
├── pyproject.toml
├── README.md
└── uv.lock
```

## Installation

1. Ensure UV is installed on your system.
2. Set up the Python environment using the Makefile:

```bash
make setup
```

This will install the required dependencies (BeautifulSoup4 and lxml).

## Usage

### Basic Usage

To process the default HTML file (`data/raw/actioneer-03-04-2025.html`):

```bash
make process
```

This will create a CSV file at `data/processed/actioneer_listings.csv`.

### Process the Most Recent File

To automatically find and process the most recent HTML file in the `data/raw` directory:

```bash
make process-latest
```

The script supports two filename date formats:

1. ISO 8601 format: `actioneer-YYYY-MM-DDTHHMMSS.html` (e.g., `actioneer-2025-03-04T114022.html`)
2. Legacy format: `actioneer-MM-DD-YYYY.html` (e.g., `actioneer-03-04-2025.html`)

If the date cannot be parsed from the filename, the script falls back to using the file modification time.

### Processing a Specific File

To process a specific HTML file:

```bash
make process-file FILE=path/to/your/file.html OUTPUT=path/to/output.csv
```

If you don't specify an output file, it will automatically generate one in the `data/processed` directory.

### Processing All Files

To process all HTML files in the `data/raw` directory:

```bash
make process-all
```

### Advanced Usage

For more control, you can run the script directly with UV:

```bash
uv run actioneer_raw_csv.py --input path/to/input.html --output path/to/output.csv [--silent]
```

To process the most recent file:

```bash
uv run actioneer_raw_csv.py --latest
```

Options:
- `--input` or `-i`: Path to the HTML file to process
- `--output` or `-o`: Path for the output CSV file
- `--latest` or `-l`: Process the most recent file in the raw directory
- `--silent` or `-s`: Suppress sample output (useful for batch processing)

### Cleaning Up

To remove all processed CSV files:

```bash
make clean
```

To remove all data files (both raw HTML and processed CSV):

```bash
make clean-all
```

## CSV Output Format

The generated CSV includes the following columns:

- `image_url`: URL of the item image
- `name`: Name of the item
- `quantity`: Quantity/amount
- `duration`: Duration (Short/Medium/Long)
- `seller`: Seller username
- `faction`: Faction information (if available)
- `price`: Price with coin denomination
- `data_entry`: Entry ID for the item
- `data_id`: Item ID
- `data_name`: Item name from data attributes
- `data_type`: Item type

## Customization

The script is designed to be flexible. If you encounter HTML tables with different structures, you may need to modify the selector paths in the `extract_table_data` function.
