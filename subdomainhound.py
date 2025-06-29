#!/usr/bin/env python3

import sys
import requests
import argparse
import time
from concurrent.futures import ThreadPoolExecutor
import json
from threading import Lock
from collections import defaultdict
import re

failed_requests = []
failed_lock = Lock()

def batch_queries(queries, batch_size=10):
    for i in range(0, len(queries), batch_size):
        yield ' OR '.join(q.strip() for q in queries[i:i + batch_size] if q.strip())

def fetch_and_process_crtsh(query, headers, output_data, delay, silent):
    time.sleep(delay)  # Delay is applied *inside* each thread
    result = search_query_on_crtsh(query, headers, silent)
    process_query(query, output_data, result, silent)

def get_common_names(result):
    domain_pattern = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return [
        entry.get('common_name', '').lstrip('*.')
        for entry in result
        if domain_pattern.match(entry.get('common_name', '').lstrip('*.')) 
        and len(entry.get('common_name', '')) <= 253
    ]

def process_query(query, output_data=None, result=None, silent=False):
    try:
        # Check if the result is empty or doesn't contain the expected data
        if not result or not isinstance(result, list):
            return

        common_names = list(set(get_common_names(result)))

        # Print each common name on a separate line
        for common_name in common_names:
            print(common_name)

        # If the query already exists in output_data, append the new data
        if output_data is not None:
            if query in output_data:
                output_data[query].extend(common_names)
            else:
                output_data[query] = common_names

    except KeyboardInterrupt:
        if not silent:
            print("\nExecution terminated or interrupted.")
    except Exception as e:
        if not silent:
            print(f"Error processing query '{query}': {e}")
            print("\n" + "="*50 + "\n")

def search_query_on_crtsh(query, headers, silent):
    url = f'https://crt.sh/?q={query}&output=json&exclude=expired&deduplicate=N'
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
                if not silent:
                    print(f"Error decoding JSON for query '{query}': {e}")
                with failed_lock:
                    failed_requests.append({
                        "type": "crtsh",
                        "query": query,
                        "url": url,
                        "headers": headers
                    })
        else:
            # Handle non-successful HTTP status codes
            if not silent:
                print(f"HTTP request failed for query '{query}' with status code {response.status_code}\n")
            failed_requests.append({
                        "type": "crtsh",
                        "query": query,
                        "url": url,
                        "headers": headers
                    })

    except requests.RequestException as e:
        # Handle other request-related exceptions
        if not silent:
            print(f"Error making request for query '{query}': {e}")
        failed_requests.append({
                        "type": "crtsh",
                        "query": query,
                        "url": url,
                        "headers": headers
                    })

    return result

def fetch_and_process_reverse_whois(query, api_key, headers, exact_match, output_data, delay, silent):
    time.sleep(delay)  # Delay is applied *inside* each thread
    process_reverse_whois(query, api_key, headers, exact_match, output_data, silent)

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
                if not silent:
                    print("Error: Unable to retrieve account balance data.")
        else:
            if not silent:
                print(f"Error checking account balance. HTTP Status Code: {response.status_code}")

    except requests.RequestException as e:
        if not silent:
            print(f"Error checking account balance: {e}")
        

    return False

def reverse_whois(query, api_key, headers,exact_match, silent):
    
    # Check remaining credits before making the API call
    if not check_remaining_credits(api_key, headers):
        return {"code":403,"messages":"Access restricted. Check the DRS credits balance or enter the correct API key."}
        
    
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
                if not silent:
                    print(f"Error decoding JSON for query '{query}': {e}")
                with failed_lock:
                    failed_requests.append({
                        "type": "reverse",
                        "query": query,
                        "url": url,
                        "headers": headers,
                        "data": data,
                        "api_key": api_key,
                        "exact_match": exact_match
                    })
        else:
            # Handle non-successful HTTP status codes
            if not silent:
                print(f"HTTP request failed for query '{query}' with status code {response.status_code}\n")
            with failed_lock:
                failed_requests.append({
                    "type": "reverse",
                    "query": query,
                    "url": url,
                    "headers": headers,
                    "data": data,
                    "api_key": api_key,
                    "exact_match": exact_match
                })

    except requests.RequestException as e:
        # Handle other request-related exceptions
        if not silent:
            print(f"Error making request for query '{query}': {e}")
        failed_requests.append({
                        "type": "crtsh",
                        "query": query,
                        "url": url,
                        "headers": headers
                    })

    return result

def process_reverse_whois(query, api_key, headers,exact_match,output_data=None):
    try:
        result = reverse_whois(query, api_key, headers,exact_match)

        # Check if the response contains an error message
        error_message = result.get('messages', '')
        error_code = result.get('code', None)
        
        if error_message and error_code is not None and error_code // 100 != 2:
            if not silent:
                print(f"Error in reverse-whois lookup for query '{query}': {error_message} (HTTP Status Code: {error_code})")
            return

        domains_list = result.get('domainsList', [])
        for domain in domains_list:
            print(domain)

        # If the query already exists in output_data, append the new data
        if output_data is not None:
            if query in output_data:
                output_data[query].extend(domains_list)
            else:
                output_data[query] = domains_list

    except Exception as e:
        if not silent:
            print(f"Error processing reverse-whois for query '{query}': {e}")

MAX_RETRIES = 3
retry_counts = defaultdict(int)

def retry_failed_requests(output_data, delay, silent):
    global failed_requests

    for attempt in range(1, MAX_RETRIES + 1):
        if not failed_requests:
            break

        if not silent:
            print(f"\n[Retry Attempt #{attempt}] Retrying {len(failed_requests)} failed requests after 5 sec delay...\n")
        time.sleep(5)

        new_failed_requests = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            for item in failed_requests:
                query = item['query']

                if retry_counts[query] >= MAX_RETRIES:
                    continue  # Skip retrying if already hit max retries

                retry_counts[query] += 1

                if item['type'] == 'crtsh':
                    future = executor.submit(fetch_and_process_crtsh, query, item['headers'], output_data, delay)
                elif item['type'] == 'reverse':
                    future = executor.submit(fetch_and_process_reverse_whois, query, item['api_key'], item['headers'], item['exact_match'], output_data, delay)

                # Track future and item together
                future.item = item

            # Rebuild failed_requests with only those that fail again
            failed_requests = []

        # Now append skipped ones explicitly for user visibility
        for item in list(retry_counts):
            if retry_counts[item] >= MAX_RETRIES:
                if not silent:
                    print(f"Skipping '{item}' after {MAX_RETRIES} failed attempts.")

    if not silent:
        print("\n Retry attempts completed.\n")
      
    
def main():
    parser = argparse.ArgumentParser(description='Description: Search queries on crt.sh or perform reverse-whois lookup with whoisxmlapi.')
    parser.add_argument('-t', '--threads', type=int, default=1, help='Number of threads for concurrent processing.')
    parser.add_argument('-d', '--delay', type=float, default=1.0, help='Delay between requests in seconds.')
    parser.add_argument('-o', '--output', help='Output file path.')
    parser.add_argument('-u', '--user-agent', default='Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36', help='Custom User-Agent string.')
    parser.add_argument('-m', '--mode', choices=['1', '2','all'], default='1', help='Mode for lookup (1=crt.sh, 2=reverse-whois). all=both')
    parser.add_argument('-k', '--api-key', default='', help='API key for reverse-whois lookup.')
    parser.add_argument('-q', '--query-file', help='Path to the file containing Organization names.')
    parser.add_argument('-e', '--exact-match', default=True, action='store_false', help='Disable exact match. By default, exact match is enabled.')
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode: only output results, suppress logs.')
    parser.add_argument('query', nargs='?', default=None, help='Query for crt.sh or reverse-whois lookup. i.e oranization name.')
    args = parser.parse_args()

    # Prepare headers dictionary with the custom User-Agent and Content-Type
    headers = {'User-Agent': args.user_agent, 'Content-Type': 'application/json'}

    if args.mode in ('2','all') and not args.api_key:
            print("Error: API key is required for reverse-whois lookup.")
            sys.exit(1)
            
    if args.query:
        queries = [args.query.strip()] if args.query.strip() else []
    elif args.query_file:
        try:
            with open(args.query_file, 'r') as file:
                queries = [q.strip() for q in file.readlines() if q.strip()]
        except Exception as e:
            if not silent:
                print(f"Error: Unable to read file '{args.query_file}': {e}")
            sys.exit(1)
    elif not sys.stdin.isatty():
        # Read from stdin
        queries = [q.strip() for q in sys.stdin.readlines() if q.strip()]
    else:
        parser.print_help()
        sys.exit()
    
    # Create a dictionary to store the output data for all queries
    output_data = {} if args.output else None

    if args.mode in ('1','all'):
        # Perform crt.sh lookup
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for query in batch_queries(queries, batch_size=10):
                # Submit the crt.sh lookup and processing task to be executed concurrently
                executor.submit(fetch_and_process_crtsh, query, headers, output_data,args.delay, args.silent)

    if args.mode in ('2','all') and args.api_key:
        # Perform reverse-whois lookup
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            for query in map(str.strip, queries):
                # Submit the reverse-whois lookup and processing task to be executed concurrently
                executor.submit(fetch_and_process_reverse_whois, query, args.api_key, headers, args.exact_match, output_data, args.delay, args.silent)

    if failed_requests:
        retry_failed_requests(output_data, args.delay, args.silent)

    # Write the entire output_data to the output JSON file
    if args.output:
        try:
            with open(args.output, 'w') as out_file:
                json.dump(output_data, out_file, indent=2)
        except Exception as e:
            if not silent:
                print(f"Error: Unable to write to output file '{args.output}': {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
