#Output file
import requests
import argparse
import time
from concurrent.futures import ThreadPoolExecutor

def search_query_on_crtsh(query):
    url = f'https://crt.sh/?q={query}&output=json'
    response = requests.get(url)
    return response.json()

def get_common_names(result):
    return [entry.get('common_name', '') for entry in result]

def process_query(query, output_file=None):
    try:
        result = search_query_on_crtsh(query)
        common_names = get_common_names(result)
        print(f"Common names for query '{query}':")

        # Print each common name on a separate line
        for common_name in common_names:
            print(common_name)

        print("\n" + "="*50 + "\n")

        # Write to the output file if specified
        if output_file:
            with open(output_file, 'a') as out_file:
                # out_file.write(f"Common names for query '{query}':\n")
                out_file.write('\n'.join(common_names) + '\n\n')

    except KeyboardInterrupt:
        print("\nExecution terminated or interrupted.")

def main():
    parser = argparse.ArgumentParser(description='Search queries on crt.sh concurrently.')
    parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads for concurrent processing')
    parser.add_argument('-d', '--delay', type=float, default=1.0, help='Delay between requests in seconds')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('input_file_path', help='Path to the file containing queries')
    args = parser.parse_args()

    with open(args.file_path, 'r') as file:
        queries = file.readlines()

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for query in map(str.strip, queries):
            executor.submit(process_query, query, args.output)
            time.sleep(args.delay)  # Introduce a delay between requests

if __name__ == "__main__":
    main()
