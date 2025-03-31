#!/usr/bin/env python3

import argparse
import asyncio
import json
import logging
import requests
try:
    import aiohttp
except ImportError:
    print("Error: aiohttp is not installed. Please run 'pip install aiohttp'")
    raise
from bs4 import BeautifulSoup
import urllib.parse

# Import Qdrant client for persistence
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Import SentenceTransformer for semantic embeddings
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Synchronous crawling functions
def crawl_page(url, depth, visited, outputs, indent=0):
    indent_str = " " * (indent * 4)
    message = f"{indent_str}URL: {url}"
    outputs.append(message)
    logging.info(message)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        error_msg = f"{indent_str}Error fetching URL: {e}"
        outputs.append(error_msg)
        logging.error(error_msg)
        return

    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
    title_msg = f"{indent_str}Title: {title}"
    outputs.append(title_msg)
    logging.info(title_msg)

    if depth > 1:
        links = set()
        for anchor in soup.find_all("a", href=True):
            link = anchor["href"]
            absolute_link = urllib.parse.urljoin(url, link)
            links.add(absolute_link)
        for link in sorted(links):
            if link not in visited:
                visited.add(link)
                crawl_page(link, depth - 1, visited, outputs, indent + 1)

def create_crawler(args):
    outputs = []
    msg = f"Crawler Name: {args.name}"
    outputs.append(msg)
    logging.info(msg)
    # Iterate over each starting URL (supports multiple URLs)
    for url in args.url:
        msg = f"Starting URL: {url}"
        outputs.append(msg)
        logging.info(msg)
        if args.depth > 1:
            visited = set([url])
            crawl_page(url, args.depth, visited, outputs)
        else:
            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.RequestException as e:
                error_msg = f"Error fetching URL {url}: {e}"
                outputs.append(error_msg)
                logging.error(error_msg)
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
            title_msg = f"Page title for {url}: {title}"
            outputs.append(title_msg)
            logging.info(title_msg)
            
            if args.list_links:
                links = set()
                for anchor in soup.find_all("a", href=True):
                    links.add(anchor["href"])
                if links:
                    outputs.append(f"\nLinks found on the page for {url}:")
                    logging.info(f"Links found on the page for {url}:")
                    for link in sorted(links):
                        outputs.append(link)
                        logging.info(link)
                else:
                    no_links_msg = f"No links found on the page for {url}."
                    outputs.append(no_links_msg)
                    logging.info(no_links_msg)
    result_text = finalize_output(outputs, args)
    if args.qdrant:
        persist_results_qdrant(result_text, args)

def finalize_output(outputs, args):
    if args.json:
        result_text = json.dumps({"results": outputs}, indent=2)
    else:
        result_text = "\n".join(outputs)
    print(result_text)
    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write(result_text)
            logging.info(f"Results written to {args.output}")
        except Exception as e:
            logging.error(f"Error writing to output file: {e}")
    return result_text

# Function to persist results to Qdrant DB with semantic embeddings
def persist_results_qdrant(result_text, args):
    try:
        client = QdrantClient(host=args.qdrant_host, port=args.qdrant_port)
        collection_name = args.qdrant_collection
        # Recreate collection with vector size matching the embedding dimension.
        # Using SentenceTransformer "all-MiniLM-L6-v2" which outputs 384-dimensional embeddings.
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=384, distance="Cosine")
        )
        # Load the pre-trained model and encode the results.
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embedding = model.encode(result_text).tolist()
        point = models.PointStruct(
            id=1,
            vector=embedding,
            payload={"text": result_text}
        )
        client.upsert(collection_name=collection_name, points=[point])
        logging.info(f"Persisted semantic results to Qdrant collection '{collection_name}'.")
    except Exception as e:
        logging.error(f"Failed to persist results to Qdrant: {e}")

# Asynchronous crawling functions
async def async_fetch(session, url, indent_str):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            text = await response.text()
            return text
    except Exception as e:
        logging.error(f"{indent_str}Error fetching URL: {e}")
        return None

async def async_crawl_page(url, depth, visited, outputs, session, indent=0):
    indent_str = " " * (indent * 4)
    message = f"{indent_str}URL: {url}"
    outputs.append(message)
    logging.info(message)
    text = await async_fetch(session, url, indent_str)
    if text is None:
        outputs.append(f"{indent_str}Error fetching URL")
        return
    soup = BeautifulSoup(text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
    title_msg = f"{indent_str}Title: {title}"
    outputs.append(title_msg)
    logging.info(title_msg)
    if depth > 1:
        links = set()
        for anchor in soup.find_all("a", href=True):
            link = anchor["href"]
            absolute_link = urllib.parse.urljoin(url, link)
            links.add(absolute_link)
        tasks = []
        for link in sorted(links):
            if link not in visited:
                visited.add(link)
                tasks.append(async_crawl_page(link, depth - 1, visited, outputs, session, indent + 1))
        if tasks:
            await asyncio.gather(*tasks)

async def async_create_crawler(args):
    outputs = []
    msg = f"Crawler Name: {args.name}"
    outputs.append(msg)
    logging.info(msg)
    tasks = []
    async with aiohttp.ClientSession() as session:
        # Iterate over each starting URL concurrently.
        for url in args.url:
            task = async_crawl_page(url, args.depth, set([url]), outputs, session)
            tasks.append(task)
        if tasks:
            await asyncio.gather(*tasks)
    result_text = finalize_output(outputs, args)
    if args.qdrant:
        persist_results_qdrant(result_text, args)

# Function to query Qdrant using a semantic search over stored embeddings.
def query_qdrant(args):
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_embedding = model.encode(args.query).tolist()
        client = QdrantClient(host=args.qdrant_host, port=args.qdrant_port)
        collection_name = args.qdrant_collection
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=args.limit
        )
        if search_results:
            print("Search results:")
            for point in search_results:
                print(f"ID: {point.id}, Score: {point.score}")
                print("Payload:", point.payload)
        else:
            print("No matching results found.")
    except Exception as e:
        logging.error(f"Failed to query Qdrant: {e}")

def main():
    parser = argparse.ArgumentParser(description="Python CLI for creating crawlers and querying semantic data.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subparser for crawling command
    crawl_parser = subparsers.add_parser("crawl", help="Crawl target URL(s)")
    crawl_parser.add_argument("--name", type=str, required=True, help="Name of the crawler")
    crawl_parser.add_argument("--url", type=str, required=True, nargs="+", help="Target URL(s) to crawl")
    crawl_parser.add_argument("--list-links", action="store_true", help="List links found on the page (for non-recursive crawl)")
    crawl_parser.add_argument("--output", type=str, help="File to write results to")
    crawl_parser.add_argument("--depth", type=int, default=1, help="Crawl depth for recursive crawling (default 1)")
    crawl_parser.add_argument("--concurrent", action="store_true", help="Enable asynchronous concurrent crawling")
    crawl_parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    # Qdrant persistence options for crawler
    crawl_parser.add_argument("--qdrant", action="store_true", help="Persist results to Qdrant DB")
    crawl_parser.add_argument("--qdrant-host", type=str, default="localhost", help="Qdrant host (default: localhost)")
    crawl_parser.add_argument("--qdrant-port", type=int, default=6333, help="Qdrant port (default: 6333)")
    crawl_parser.add_argument("--qdrant-collection", type=str, default="crawler_collection", help="Qdrant collection name")

    # Subparser for query command
    query_parser = subparsers.add_parser("query", help="Query semantic data from Qdrant")
    query_parser.add_argument("--query", type=str, required=True, help="Query text to search")
    query_parser.add_argument("--limit", type=int, default=5, help="Number of search results to return (default: 5)")
    # Qdrant options for query
    query_parser.add_argument("--qdrant-host", type=str, default="localhost", help="Qdrant host (default: localhost)")
    query_parser.add_argument("--qdrant-port", type=int, default=6333, help="Qdrant port (default: 6333)")
    query_parser.add_argument("--qdrant-collection", type=str, default="crawler_collection", help="Qdrant collection name")

    args = parser.parse_args()

    if args.command == "crawl":
        if args.concurrent:
            asyncio.run(async_create_crawler(args))
        else:
            create_crawler(args)
    elif args.command == "query":
        query_qdrant(args)

if __name__ == "__main__":
    main()
