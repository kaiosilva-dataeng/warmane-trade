# %% Imports
import csv
import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup


# %% read_file
def read_file(file_path):
    """Read content from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# %% get_most_recent_file
def get_most_recent_file(directory='data/raw', pattern='actioneer-*.html'):
    """
    Get the most recent file in the directory that matches the pattern.

    Args:
        directory (str): Directory to search in
        pattern (str): Glob pattern to match files

    Returns:
        Path: Path object to the most recent file or None if no files found
    """
    directory = Path(directory)

    # Ensure directory exists
    if not directory.exists() or not directory.is_dir():
        print(f'Directory {directory} does not exist or is not a directory')
        return None

    # Get all files matching the pattern
    matching_files = list(directory.glob(pattern))

    if not matching_files:
        print(f'No files matching pattern {pattern} found in {directory}')
        return None

    # Define regex patterns for both formats
    datetime_pattern = r'actioneer-(\d{4}-\d{2}-\d{2}T\d{6})'
    date_pattern = r'actioneer-(\d{4}-\d{2}-\d{2})'

    def extract_datetime(filename):
        """Extract datetime from filename and convert to datetime object"""
        # Try datetime format first (more specific)
        dt_match = re.search(datetime_pattern, filename.name)
        if dt_match:
            dt_str = dt_match.group(1)
            return datetime.strptime(dt_str, '%Y-%m-%dT%H%M%S')

        # Try date format
        date_match = re.search(date_pattern, filename.name)
        if date_match:
            date_str = date_match.group(1)
            return datetime.strptime(date_str, '%Y-%m-%d')

        # If no pattern matches, use file modification time as fallback
        return datetime.fromtimestamp(filename.stat().st_mtime)

    # Sort files by extracted datetime, most recent first
    matching_files.sort(key=extract_datetime, reverse=True)

    # Return the most recent file
    return matching_files[0]


# %% extract_table_data
def extract_table_data(soup):
    """Extract item listings data from the HTML table."""
    results = []

    # Find all table rows in tbody
    rows = soup.select('#data-table tbody tr')

    for row in rows:
        try:
            # Extract the image URL
            img_element = row.select_one('.iconAndQuantity img')
            image_url = img_element.get('src') if img_element else None

            # Extract item name and quantity
            name_element = row.select_one('.name')
            name = 'Unknown'
            quantity = 'Unknown'

            if name_element:
                # Get the full text and try to parse out name and quantity
                full_text = name_element.text.strip()
                quantity_element = name_element.select_one('.numeric')

                if quantity_element:
                    quantity = quantity_element.text.strip()

                    # Try to extract item name from the text
                    name_parts = full_text.replace(quantity, '').strip()
                    if name_parts:
                        name = name_parts

                # If we couldn't extract a name, try to get it from the link
                if name == 'Unknown' and name_element.select_one('a'):
                    link_text = name_element.select_one('a').text.strip()
                    if link_text and link_text != quantity:
                        name_parts = link_text.replace(quantity, '').strip()
                        if name_parts:
                            name = name_parts

            # Extract duration, seller, faction and price
            # Find all cells with align=center to handle variations
            aligned_cells = row.select("td[align='center']")

            duration = (
                aligned_cells[0].text.strip()
                if len(aligned_cells) > 0
                else 'Unknown'
            )
            seller = (
                aligned_cells[1].text.strip()
                if len(aligned_cells) > 1
                else 'Unknown'
            )

            # Extract faction if available (some items may not have faction)
            faction_cell = row.select_one('.factionEmblem')
            faction = (
                faction_cell.text.strip()
                if faction_cell and faction_cell.text.strip()
                else 'None'
            )

            # Extract price
            price_element = row.select_one('.costValues')
            price = 'Unknown'
            if price_element:
                numeric_element = price_element.select_one('.numeric')
                if numeric_element:
                    price = f'{numeric_element.text} coins'

            # Extract data attributes from shop button
            shop_button = row.select_one('.wm-ui-btn-shop-search')
            data_entry = shop_button.get('data-entry') if shop_button else None
            data_id = shop_button.get('data-id') if shop_button else None
            data_name = shop_button.get('data-name') if shop_button else None
            data_type = shop_button.get('data-type') if shop_button else None

            # Add to results
            results.append(
                {
                    'image_url': image_url,
                    'name': name,
                    'quantity': quantity,
                    'duration': duration,
                    'seller': seller,
                    'faction': faction,
                    'price': price,
                    'data_entry': data_entry,
                    'data_id': data_id,
                    'data_name': data_name,
                    'data_type': data_type,
                }
            )

        except Exception as e:
            print(f'Error processing row: {e}')

    return results


# %% save_to_csv
def save_to_csv(data, output_path):
    """Save the extracted data to a CSV file."""
    if not data:
        print('No data to save!')
        return

    # Use all fields from the first data row to ensure we capture everything
    fieldnames = data[0].keys() if data else []

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f'Data saved to {output_path}')


# %% process_html_file
def process_html_file(file_path, output_path=None):
    """Process an HTML file and extract table data."""
    # Process the HTML file
    html_doc = read_file(file_path)
    soup = BeautifulSoup(html_doc, 'html.parser')

    # Extract data from the table
    table_data = extract_table_data(soup)

    # Print sample of extracted data
    print(f'Extracted {len(table_data)} listings from {file_path}')

    # Save data to CSV if output path is provided
    if output_path and table_data:
        # Create the output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        save_to_csv(table_data, output_path)

    return table_data


# %% main
def main():
    """Main entry point for the script."""
    import argparse

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Extract data from HTML tables.'
    )
    parser.add_argument(
        '--input', '-i', type=str, help='Path to the HTML file to process'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Path to save the extracted data (CSV)',
    )
    parser.add_argument(
        '--latest',
        '-l',
        action='store_true',
        help='Process the most recent file in the raw directory',
    )
    parser.add_argument(
        '--silent', '-s', action='store_true', help='Suppress sample output'
    )

    args = parser.parse_args()

    # Determine input path
    if args.latest:
        input_path = get_most_recent_file()
        if not input_path:
            print('No files found to process.')
            return
    elif args.input:
        input_path = Path(args.input)
    else:
        # Use default if no input specified
        default_input = Path('data/raw/actioneer-03-04-2025.html')
        if default_input.exists():
            input_path = default_input
        else:
            # Try to find the most recent file as a fallback
            input_path = get_most_recent_file()
            if not input_path:
                print('No input file specified and no default file found.')
                return

    # Generate default output path if not provided
    if args.output:
        output_path = Path(args.output)
    else:
        # Create output path based on input filename
        output_name = input_path.stem + '.csv'
        output_path = Path('data/processed') / output_name

    # Process the file
    table_data = process_html_file(input_path, output_path)

    # Print sample data unless silent mode is enabled
    if not args.silent and table_data:
        print('\nSample data:')
        for i, item in enumerate(
            table_data[:3]
        ):  # Show only 3 items to keep output manageable
            print(f'Item {i + 1}:')
            for key, value in item.items():
                print(f'  {key}: {value}')

        print(f'\nTotal items extracted: {len(table_data)}')
        print(f'Fields available: {", ".join(table_data[0].keys())}')

        print(f'Full data saved to {output_path}')

        print('\nUsage examples:')
        print(
            '  Process specific file:  python script.py --input path/to/html --output path/to/output.csv'  # noqa: E501
        )
        print('  Process latest file:    python script.py --latest')


if __name__ == '__main__':
    main()
