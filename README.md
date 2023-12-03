# Subd0ma1nH0und

## Overview

SubdomainHound is a powerful tool designed to hunt and discover subdomains associated with specified organizations. Leveraging the [crt.sh](https://crt.sh) website, this tool enables concurrent searches, providing efficient and detailed results. Use it to uncover subdomains and enhance your reconnaissance activities.

## Features

- **Concurrent Processing:** Utilizes multiple threads to perform concurrent queries, improving efficiency.
- **Delay Between Requests:** Introduces a customizable delay between requests to avoid rate-limiting issues.
- **Output to File:** Optionally saves the results to a specified output file for further analysis.

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

Run the script without any arguments:
```bash
python Subd0ma1nH0und.py
```
Specify threads, delay, output file, and input file path:
```
python Subd0ma1nH0und.py -t <num_threads> -d <delay_seconds> -o <output_file> <input_file_path>
```
Pipe an organization name to the script:
```
echo "Org Name" | python Subd0ma1nH0und.py
```
Pipe a list of organization names from a file to the script:
```
cat inputFile | python Subd0ma1nH0und.py
```

## Options
| Flags              | Description | Defaults |
| :---------------- | :------ | :----: |
|`-h, --help  ` |Show help menu   | - |
|`-t, --threads  ` |Number of threads for concurrent processing   | 1 |
|` -d, --delay `  |   Delay between requests in seconds	   | 1.5 |
|` -o, --output`  |  Output file path (optional)	   | - |
|`-u, ----user-agent`|Custom User-Agent string.|Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36|
| `<input_file>` |  Path to the file containing organization names| - |



## Upcoming
- Integration of whoisxmlapi
