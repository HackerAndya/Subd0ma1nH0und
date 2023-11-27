# Subd0ma1nH0und

## Overview

SubdomainHound is a powerful tool designed to hunt and discover subdomains associated with specified organizations. Leveraging the [crt.sh](https://crt.sh) website, this tool enables concurrent searches, providing efficient and detailed results. Use it to uncover subdomains and enhance your reconnaissance activities.

## Features

- **Concurrent Processing:** Utilizes multiple threads to perform concurrent queries, improving efficiency.
- **Delay Between Requests:** Introduces a customizable delay between requests to avoid rate-limiting issues.
- **Output to File:** Optionally saves the results to a specified output file for further analysis.

## Installation

```

```

## Usage

```bash
python subdomain_hound.py
python subdomain_hound.py -t <num_threads> -d <delay_seconds> -o <output_file> <input_file>
```
---
| Options              | Description | Defaults |
| :---------------- | :------ | :----: |
|`-t, --threads  ` |Number of threads for concurrent processing   | 1 |
|` -d, --delay `  |   Delay between requests in seconds	   | 1.0 |
|` -o, --output`  |  Output file path (optional)	   | - |
| `<input_file>` |  Path to the file containing organization names| - |
