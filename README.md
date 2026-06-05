# Stellar Crawler

This repository contains the network crawler and connectivity checker for the **Stellar** protocol. 

## Structure

*   `js-stellar-node-crawler/`: The core crawler. It is an adapted version of the open-source `stellarbeat/js-stellar-node-crawler` that discovers nodes in the network.
*   `stellar_pinging.py`: Connectivity checker. It takes the list of discovered nodes and performs a parallel TCP ping (specifically checking standard ports like 11625) to determine which nodes are actively reachable.
*   `write_crawl_data.py`: Data processor. Extracts the discovered peer lists, aggregates the crawl results, and prepares the data for ingestion into ClickHouse.

## Usage

### 1. The Crawler
The core crawler is built in Node.js. To initialize and build the crawler dependencies for the first time:

```bash
cd js-stellar-node-crawler

# Install corepack if you haven't already
sudo npm install -g corepack

# Enable pnpm
corepack enable pnpm

# Install dependencies and build the crawler
pnpm install
pnpm build
```

To run a crawl, execute the compiled script and provide a path to a seed nodes file:

```bash
node lib/crawl.js <path_to_seed_nodes_file>
```
*Note: In production, this generates the initial discovery dataset.*

### 2. The Connectivity Checker
Once the network has been crawled, you can verify which discovered nodes are actually online and reachable from our vantage point.

Run the Python script from the root directory:

```bash
python3 stellar_pinging.py
```
This script will automatically read the latest discovered nodes from the data directory, perform fast parallel TCP pings, and save the list of responsive peers.

### 3. Data Processing
To process the raw crawled data and output the final node discovery logs:

```bash
python3 write_crawl_data.py
```
This will parse the crawler outputs and format the resulting active/discovered subsets.

## Dependencies

*   **Node.js & pnpm**: Required for the `js-stellar-node-crawler`.
*   **Python 3**: Required for the connectivity and processing scripts.
*   **Python Packages**: `requests`, `urllib3` (Used in `stellar_pinging.py` and `write_crawl_data.py`).
