#!/usr/bin/env python3

import sys
import requests
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
import json

def search_query_on_crtsh(query):
    url = f'https://crt.sh/?q={query}&output=json'
    result = None  # Initialize result to None
    try:
        response = requests.get(url)

        # Check if the response is successful (HTTP status code 200)
        if response.status_code == 200:
            try:
                # Try to parse the response as JSON
                result = response.json()
            except json.JSONDecodeError as e:
                # Handle JSON decoding errors
                print(f"Error decoding JSON for query '{query}': {e}")
        else:
            # Handle non-successful HTTP status codes
            print(f"HTTP request failed for query '{query}' with status code {response.status_code}")

    except requests.RequestException as e:
        # Handle other request-related exceptions
        print(f"Error making request for query '{query}': {e}")

    return result
    
def get_common_names(result):
    return [entry.get('common_name', '') for entry in result]

def process_query(query, output_file==None, result=None):
    try:
        # Check if the result is empty or doesn't contain the expected data
        if not result or not isinstance(result, list):
            print(f"No valid data for query '{query}'")
            print("\n" + "="*50 + "\n")
            return

        common_names = get_common_names(result)
        print(f"Common names for query '{query}':")

        # Print each common name on a separate line
        for common_name in common_names:
            print(common_name)

        print("\n" + "="*50 + "\n")

        # Write to the output file if specified
        if output_file:
            with open(output_file, 'a') as out_file:
                out_file.write('\n'.join(common_names) + '\n\n')

    except KeyboardInterrupt:
        print("\nExecution terminated or interrupted.")
    except Exception as e:
        print(f"Error processing query '{query}': {e}")
        print("\n" + "="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Search queries on crt.sh concurrently.')
    parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads for concurrent processing.')
    parser.add_argument('-d', '--delay', type=float, default=1.0, help='Delay between requests in seconds.')
    parser.add_argument('-o', '--output', help='Output file path.')
    parser.add_argument('input_file_path', nargs='?', default=None, help='Path to the file containing Organization names.')
    args = parser.parse_args()

    if args.input_file_path:
        with open(args.input_file_path, 'r') as file:
            queries = file.readlines()
    elif not sys.stdin.isatty():
        # Read from stdin
        queries = sys.stdin.readlines()
    else:
        parser.print_help()
        sys.exit()

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for query in map(str.strip, queries):
            # Store the result of search_query_on_crtsh in a variable named result
            result = search_query_on_crtsh(query)
            executor.submit(process_query, query, args.output, result)
            time.sleep(args.delay)  # Introduce a delay between requests

if __name__ == "__main__":
    main()
