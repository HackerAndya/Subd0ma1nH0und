#!/usr/bin/env python3

import sys
import requests
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
import json

def search_query_on_crtsh(query, headers):
    url = f'https://crt.sh/?q={query}&output=json'
    result = None  # Initialize result to None
    try:
        response = requests.get(url, headers=headers)

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

def check_remaining_credits(api_key, headers):
    url = 'https://user.whoisxmlapi.com/user-service/account-balance?productId=14&apiKey='+api_key
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            balance_data = response.json().get('data', [])
            if balance_data:
                remaining_credits = balance_data[0].get('credits', 0)
                return remaining_credits > 1
            else:
                print("Error: Unable to retrieve account balance data.")
        else:
            print(f"Error checking account balance. HTTP Status Code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Error checking account balance: {e}")

    return False

def reverse_whois(query, api_key, headers,exact_match):
    
    # Check remaining credits before making the API call
    if not check_remaining_credits(api_key, headers):
        print("Error: Insufficient credits remaining.")
        
    
    url = 'https://reverse-whois.whoisxmlapi.com/api/v2'
    data = {
        "apiKey": api_key,
        "searchType": "current",
        "mode": "purchase",
        "punycode": True,
        "advancedSearchTerms": [{
            "field": "RegistrantContact.Organization",
            "term": query,
            "exactMatch": exact_match
        }]
    }
    result = None
    try:
        response = requests.post(url, json=data, headers=headers)

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

def process_query(query, output_data=None, result=None):
    try:
        # Check if the result is empty or doesn't contain the expected data
        if not result or not isinstance(result, list):
            return

        common_names = get_common_names(result)

        # Print each common name on a separate line
        for common_name in common_names:
            print(common_name)

        # If the query already exists in output_data, append the new data
        if query in output_data:
            output_data[query].extend(common_names)
        else:
            output_data[query] = common_names

    except KeyboardInterrupt:
        print("\nExecution terminated or interrupted.")
    except Exception as e:
        print(f"Error processing query '{query}': {e}")
        print("\n" + "="*50 + "\n")

def process_reverse_whois(query, api_key, headers,exact_match,output_data=None):
    try:
        result = reverse_whois(query, api_key, headers,exact_match)

        # Check if the response contains an error message
        error_message = result.get('messages', '')
        error_code = result.get('code', None)
        
        if error_message and error_code is not None and error_code // 100 != 2:
            print(f"Error in reverse-whois lookup for query '{query}': {error_message} (HTTP Status Code: {error_code})")
            return

        domains_list = result.get('domainsList', [])
        for domain in domains_list:
            print(domain)

        # If the query already exists in output_data, append the new data
        if query in output_data:
            output_data[query].extend(domains_list)
        else:
            output_data[query] = domains_list

    except Exception as e:
        print(f"Error processing reverse-whois for query '{query}': {e}")

def main():
    parser = argparse.ArgumentParser(description='Description: Search queries on crt.sh or perform reverse-whois lookup with whoisxmlapi.')
    parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads for concurrent processing.')
    parser.add_argument('-d', '--delay', type=float, default=1.0, help='Delay between requests in seconds.')
    parser.add_argument('-o', '--output', help='Output file path.')
    parser.add_argument('-u', '--user-agent', default='Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36', help='Custom User-Agent string.')
    parser.add_argument('-m', '--mode', choices=['1', '2','all'], default='1', help='Mode for lookup (1=crt.sh, 2=reverse-whois). all=both')
    parser.add_argument('-k', '--api-key', default='', help='API key for reverse-whois lookup.')
    parser.add_argument('-q', '--query-file', help='Path to the file containing Organization names.')
    parser.add_argument('-e', '--exact-match', default=True, action='store_false', help='Perform an exact match. Default is True.')
    parser.add_argument('query', nargs='?', default=None, help='Query for crt.sh or reverse-whois lookup. i.e oranization name.')
    args = parser.parse_args()

    # Prepare headers dictionary with the custom User-Agent and Content-Type
    headers = {'User-Agent': args.user_agent, 'Content-Type': 'application/json'}

    if args.mode in ('2','all') and not args.api_key:
            print("Error: API key is required for reverse-whois lookup.")
            sys.exit(1)
            
    if args.query:
        queries = [args.query]
    elif args.query_file:
        with open(args.query_file, 'r') as file:
            queries = file.readlines()
    elif not sys.stdin.isatty():
        # Read from stdin
        queries = sys.stdin.readlines()
    else:
        parser.print_help()
        sys.exit()
    
    # Create a dictionary to store the output data for all queries
    output_data = {}

    if args.mode in ('1','all'):
        # Perform crt.sh lookup
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for query in map(str.strip, queries):
                # Store the result of search_query_on_crtsh in a variable named result
                # result = search_query_on_crtsh(query, headers)
                executor.submit(process_query, query, output_data, search_query_on_crtsh(query, headers))
                time.sleep(args.delay)  # Introduce a delay between requests

    if args.mode in ('2','all') and args.api_key:
        # Perform reverse-whois lookup
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for query in map(str.strip, queries):
                # Store the result of reverse-whoisS in a variable named result
                # result = reverse_whois(query, args.api_key, headers, args.exact_match)
                executor.submit(process_reverse_whois, query, args.api_key, headers, args.exact_match, output_data)
                time.sleep(args.delay)  # Introduce a delay between requests

    # Write the entire output_data to the output JSON file
    if args.output:
        with open(args.output, 'w') as out_file:
            json.dump(output_data, out_file, indent=2)

if __name__ == "__main__":
    main()
