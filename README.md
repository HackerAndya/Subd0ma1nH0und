# Subd0ma1nH0und 🐾

Subd0ma1nH0und is a tool designed to enumerate subdomains and domain names associated with an organization using public certificate transparency logs (`crt.sh`) and reverse WHOIS lookups via the WhoisXML API.

---
## Requirements
```
Python 3.X
pip install requests
```
---
## 🚀 Features

##### 🔍 Organization to Domain/Subdomain Enumeration
```bash
Supports searching domains and subdomains associated with organizations using:
1. crt.sh (Certificate Transparency logs)
2. WhoisXML Reverse Whois API
```
##### 🧠 Smart Query Modes
```bash
Choose from:
Mode 1 → Only crt.sh
Mode 2 → Only WhoisXML
Mode all → Both sources combined
```
##### 🧵 Multithreaded Lookups
```bash
Speeds up processing with support for concurrent queries via threads
```
##### 🕐 Customizable Request Delay
```bash
Control request rate to avoid rate-limiting (-d flag)
```
##### 🛡️ Custom User-Agent Support
```bash
Spoof user agents using the -u flag
```
##### 🧾 Batch Input Support for crt.sh
```bash
Batching of input queries for crt.sh to reduce rate limiting and improve efficiency
```
##### 🔁 Automatic Retry of Failed Requests
```bash
Failed queries due to network or rate-limit errors are retried at the end using multithreading.
```
---
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
|`-e, --exact-match`|Disable exact match.|True|
---

## 🆘 Help Menu

```bash
python Subd0ma1nH0und.py
python Subd0ma1nH0und.py -h
```

---

## 🔍 Querying Domains Using Organization Name

### Mode 1 (Default): `crt.sh` Provider Only

```bash
python Subd0ma1nH0und.py "Tesla Inc"
echo "Tesla Inc" | python Subd0ma1nH0und.py
cat subsidiaries.txt | python Subd0ma1nH0und.py
python Subd0ma1nH0und.py -q ../subsidiaries.txt
```

---

### Mode 2: WhoisXML Reverse-WHOIS Lookup

```bash
python Subd0ma1nH0und.py "Tesla Inc" -m 2 -k <api_key>
echo "Tesla Inc" | python Subd0ma1nH0und.py -m 2 -k <api_key>
cat subsidiaries.txt | python Subd0ma1nH0und.py -m 2 -k <api_key>
python Subd0ma1nH0und.py -q ../subsidiaries.txt -m 2 -k <api_key>
```

#### Disable Exact Match (default is exact match = true)

```bash
python Subd0ma1nH0und.py -q ../subsidiaries.txt -m 2 -k <api_key> -e
```

---

### Mode `all`: Use Both crt.sh & WhoisXML

```bash
python Subd0ma1nH0und.py "Tesla Inc" -m all -k <api_key>
echo "Tesla Inc" | python Subd0ma1nH0und.py -m all -k <api_key>
cat subsidiaries.txt | python Subd0ma1nH0und.py -m all -k <api_key>
python Subd0ma1nH0und.py -q ../subsidiaries.txt -m all -k <api_key>
```

---

## 🧩 Additional Options

### Custom User-Agent

```bash
python Subd0ma1nH0und.py -q ../subsidiaries.txt -u "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.6.30 Version/10.61"
```

### Delay Between Requests (in seconds)

```bash
python Subd0ma1nH0und.py -q ../subsidiaries.txt -m all -k <api_key> -d 2
```

### Store Output in JSON File

```bash
python Subd0ma1nH0und.py -q ../subsidiaries.txt -m all -k <api_key> -d 2 -o output.json
```

---

## 🧾 Output JSON Format

```json
{
  "Tesla Inc": [
    "sub.tesla.com",
    "login.teslamotors.com",
    "energy.tesla.com"
  ],
  "SpaceX": [
    "launch.spacex.com",
    "shop.spacex.com"
  ]
}
```

---

## 📌 Notes

- `-e` flag disables exact match for reverse-WHOIS search (used with `-m 2` or `-m all`). ⚠️ Be cautious: Using this can return a lot of garbage/noisy data if not filtered properly.
- `-k` is required for any mode using WhoisXML API (2 or all).
- Supports input from direct query, stdin, or file.
- Multithreaded with customizable thread count and delay between requests.
- If your intention is to exclusively utilize it for crt.sh (i.e. -m 1 or --mode 1), consider passing not only organization names but also domain patterns like:
    * domain.com
    * %.domain.com
    * %.%.domain.com etc.

- This increases the chances of discovering subdomains via certificate transparency logs.

---

## 💬 Contribution

PRs and issues are welcome.
