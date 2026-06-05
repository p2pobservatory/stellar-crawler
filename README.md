# Stellar Crawler

This repository crawls the **Stellar** network and prepares the results for ingestion. The crawling itself is performed by the upstream [Stellarbeat `js-stellar-node-crawler`](https://github.com/stellarbeat/js-stellar-node-crawler) (vendored in `js-stellar-node-crawler/`); two Python scripts at the repository root adapt its output into a convenient layout and add a connectivity (TCP ping) check.

**Note:**
- The actual peer discovery is done by the bundled Stellarbeat crawler (TypeScript, MIT licensed). See `js-stellar-node-crawler/src/README.md` for its internal architecture.
- The wrapper scripts assume they are run from the repository root. By default, they write output to `./data/stellar/`, but you can pass a custom data directory as the first argument.

## Components

- **`js-stellar-node-crawler/`**: the vendored Stellarbeat crawler. It connects to a set of seed nodes, follows the network to discover peers, and records each node's validating status, version, lag and known peers. The runnable entry point used here is `crawler/crawl.js`, which crawls from a `nodes.json` seed and writes raw results into `crawler/crawl_result/`.
- **`write_crawl_data.py`**: parses the crawl results and the crawl log, then writes the discovered nodes, per-node responses (peers, version, validating status, …), the active set and the raw crawl log into a specified directory. It also refreshes the seed file with the latest active nodes for the next run.
- **`stellar_pinging.py`**: reads the most recent discovered-node list and performs a TCP connectivity check on each node, recording those that are reachable.

## Setup Instructions

### Prerequisites
- Node.js and `pnpm` (for the crawler).
- Python 3 with `requests` (for the wrapper scripts).

### Installation
1. Clone the repository.
2. Build the crawler:
   ```bash
   cd js-stellar-node-crawler
   pnpm install
   pnpm build          # compiles the TypeScript sources into lib/
   ```
3. Configure the node connector if needed by copying the environment template:
   ```bash
   cp crawler/.env.dist crawler/.env
   ```

## Usage

The three components run in sequence.

1. **Crawl the network.** Run from the crawler directory; the crawl log is redirected to a file that the exporter parses:
   ```bash
   cd js-stellar-node-crawler/crawler
   node crawl.js ./nodes.json > crawl_result/stellar_crawl.json
   ```
   This produces, in `crawl_result/`: `nodes.json` (per-node records), `all_nodes.json` (all discovered addresses), `crawldata.json` (latest closed ledger), and the redirected `stellar_crawl.json` log.

2. **Export the crawl data** and refresh the seed list:
   ```bash
   cd ../..                 # back to the repository root
   python write_crawl_data.py <path_to_data_dir>
   ```

3. **Check connectivity** by pinging the discovered nodes (run on a schedule against the latest discovery snapshot):
   ```bash
   python stellar_pinging.py <path_to_data_dir>
   ```
   Each node is probed on its advertised port and on the default Stellar port `11625`; reachable nodes are recorded.

## Output Structure

`write_crawl_data.py` and `stellar_pinging.py` write under the specified data directory (e.g. `data/stellar/`), organised by date:

- `discovered/`: all discovered node IPs.
- `active/`: `ip:port` of nodes that returned node information.
- `responded_peerList/`: per-node records (peers, version, validating status, …).
- `crawl_data/`: the raw crawl log.
- `pinged_peerList/`: nodes that responded to a TCP ping.

The exporter additionally rewrites `js-stellar-node-crawler/crawler/nodes.json` with the latest active nodes, so each run reseeds itself from the previous one.

## Credits

Peer discovery is provided by the [Stellarbeat `js-stellar-node-crawler`](https://github.com/stellarbeat/js-stellar-node-crawler) (MIT). The wrapper scripts are specific to this repository.