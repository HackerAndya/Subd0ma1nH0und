
# Subd0ma1nH0und

## Overview

SubdomainHound is a powerful tool designed to hunt and discover subdomains associated with specified organizations. Leveraging the [crt.sh](https://crt.sh) and [whoisxmlapi](https://www.whoisxmlapi.com) websites/API, this tool enables concurrent searches, providing efficient and detailed results. Uncover hidden subdomains and elevate the depth of your reconnaissance activities in Red Teaming, Penetration Testing, and Bug Bounty hunting with SubdomainHound.

## Features

-   **crt.sh Lookup**: Search for queries on [crt.sh](https://crt.sh/) and retrieve information in JSON format.
-   **Reverse-Whois Lookup**: Perform a reverse-whois lookup using the [whoisxmlapi](https://www.whoisxmlapi.com) API by providing an organization name.
- **Concurrent Processing:** Utilizes multiple threads to perform concurrent queries, improving efficiency.
- **Delay Between Requests:** Introduces a customizable delay between requests to avoid rate-limiting issues.
- **Output to File:** Optionally saves the results to a specified output file for further analysis.
- **User-Agent Customization**: Specify a custom User-Agent string for HTTP requests.

## Requirements
```
Python 3.X
pip install requests
```

## Installation

```
git clone https://github.com/HackerAndya/Subd0ma1nH0und.git
cd Subd0ma1nH0und
python Subd0ma1nH0und.py
```

## Usage

Show the help message and exit:
```
python Subd0ma1nH0und.py -h
```
Run the script without any arguments:
```bash
python Subd0ma1nH0und.py
```
Specify no. of threads, delay between request, output file, and input file path:
```
python Subd0ma1nH0und.py -t <num_threads> -d <delay_seconds> -o <output_file> -q <input_file_path>
```
Pipe an organization name to the script:
```
echo "<Org Name>" | python Subd0ma1nH0und.py
```
Input organization name directly:
```
python Subd0ma1nH0und.py "<Org Name>"
```
Pipe a list of organization names from a file to the script:
```
cat inputFile | python Subd0ma1nH0und.py
```
Specify a custom User-Agent string:
```
cat inputFile | python Subd0ma1nH0und.py -u "My Custom User-Agent"
```
Perform a reverse-whois lookup with an API key:
```
cat inputFile | python Subd0ma1nH0und.py -m 2 -k your_api_key
```
Perform both crt.sh and reverse-whois lookups:
```
cat inputFile | python Subd0ma1nH0und.py -m all -k your_api_key
```
Perform an exact match in reverse-whois lookup:
```
cat inputFile | python Subd0ma1nH0und.py -m 2 -k your_api_key -e
```


## Options
| Flags              | Description | Defaults |
| :---------------- | :------ | :----: |
|`-h, --help  ` |Show help menu   | - |
|`-t, --threads  ` |Number of threads for concurrent processing   | 1 |
|` -d, --delay `  |   Delay between requests in seconds	   | 1.5 |
|` -o, --output`  |  Output file path (optional)	   | - |
|`-u, --user-agent`|Custom User-Agent string.|Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36|
|`-m, --mode`|Mode for lookup (1=crt.sh, 2=reverse-whois). all=both|1|
|`-k, --api-key`|API key for reverse-whois lookup.|-|
| `-q, --query-file` |  Path to the file containing organization names| - |
|`-e, --exact-match`|Perform an exact match for provided term.|True|

## Note
1. If your intention is to exclusively utilize it for crt.sh i.t `m 1` or `--mode 1` flag, consider passing not only organization names but also domain names like `domain.com`, `%.domain.com`, `%.%.domain.com` and so on.
2. Use flag -e only with -m 2 or -m all. Use it carefully as garbage data might come.

## Upcoming
- Reverse whois by `RegistrantContact.Email`

## Contributing
Feel free to contribute to this project. If you find issues or have suggestions, please open an issue or submit a pull request.
