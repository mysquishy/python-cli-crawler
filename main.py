#!/usr/binOkay con/env python3

import argparse
import asyncio
import json
import logging
import requests
import time
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

# New function to render dynamic content using Selenium
def render_page(url):
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("Error: selenium is not installed. Please install it via 'pip install selenium'")
        raise
    options = Options()
    options.headless = True
    # Optionally, specify your chromedriver path if needed.
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return html

# Synchronous crawling function with rate limiting, user agent, and plugin integration
def crawl_page(url, depth, visited, outputs, render=False, indent=0, delay=0, user_agent=None, use_plugins=False):
    indent_str = " " * (indent * 4)
    message = f"{indent_str}URL: {url}"
    outputs.append(message)
    logging.info(message)
    try:
        headers = {"User-Agent": user_agent} if user_agent else {}
        if render:
            html = render_page(url)
        else:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            html = response.text
        if delay:
            time.sleep(delay)
    except requests.RequestException as e:
        error_msg = f"{indent_str}Error fetching URL: {e}"
        outputs.append(error_msg)
        logging.error(error_msg)
        return
    except Exception as e:
        error_msg = f"{indent_str}Error rendering URL: {e}"
        outputs.append(error_msg)
        logging.error(error_msg)
        return

    # Plugin processing
    if use_plugins:
        try:
            from plugin_manager import load_plugins
            plugin_dir = "plugin_extensions"
            plugins = load_plugins(plugin_dir)
            for plugin in plugins:
                try:
                    plugin_result = plugin.process(html, url)
                    outputs.append(f"{indent_str}Plugin {plugin.__class__.__name__} output: {plugin_result}")
                    logging.info(f"{indent_str}Plugin {plugin.__class__.__name__} output: {plugin_result}")
                except Exception as e:
                    error_msg = f"{indent_str}Plugin {plugin.__class__.__name__} error: {e}"
                    outputs.append(error_msg)
                    logging.error(error_msg)
        except Exception as e:
            logging.error(f"{indent_str}Failed to load plugins: {e}")

    soup = BeautifulSoup(html, "html.parser")
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
                crawl_page(link, depth - 1, visited, outputs, render, indent + 1, delay, user_agent, use_plugins)

def create_crawler(args):
    outputs = []
    msg = f"Crawler Name: {args.name}"
    outputs.append(msg)
    logging.info(msg)
    for url in args.url:
        msg = f"Starting URL: {url}"
        outputs.append(msg)
        logging.info(msg)
        if args.depth > 1:
            visited = set([url])
            crawl_page(url, args.depth, visited, outputs, args.render, delay=args.delay, user_agent=args.user_agent, use_plugins=args.use_plugins)
        else:
            try:
                headers = {"User-Agent": args.user_agent} if args.user_agent else {}
                if args.render:
                    html = render_page(url)
                else:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    html = response.text
                if args.delay:
                    time.sleep(args.delay)
            except requests.RequestException as e:
                error_msg = f"Error fetching URL {url}: {e}"
                outputs.append(error_msg)
                logging.error(error_msg)
                continue
            except Exception as e:
                error_msg = f"Error rendering URL {url}: {e}"
                outputs.append(error_msg)
                logging.error(error_msg)
                continue

            # Plugin processing for top-level pages
            if args.use_plugins:
                try:
                    from plugin_manager import load_plugins
                    plugin_dir = "plugin_extensions"
                    plugins = load_plugins(plugin_dir)
                    for plugin in plugins:
                        try:
                            plugin_result = plugin.process(html, url)
                            outputs.append(f"Plugin {plugin.__class__.__name__} output: {plugin_result}")
                            logging.info(f"Plugin {plugin.__class__.__name__} output: {plugin_result}")
                        except Exception as e:
                            error_msg = f"Plugin {plugin.__class__.__name__} error: {e}"
                            outputs.append(error_msg)
                            logging.error(error_msg)
                except Exception as e:
                    logging.error(f"Failed to load plugins: {e}")

            soup = BeautifulSoup(html, "html.parser")
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
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=384, distance="Cosine")
        )
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

# Asynchronous crawling functions with domain-specific throttling, robust retry, and plugin integration
async def async_fetch(session, url, indent_str, render=False, delay=0, user_agent=None, semaphore=None, max_retries=3):
    retry = 0
    backoff = 1
    while retry < max_retries:
        try:
            if semaphore:
                async with semaphore:
                    headers = {"User-Agent": user_agent} if user_agent else {}
                    async with session.get(url, headers=headers) as response:
                        response.raise_for_status()
                        text = await response.text()
                        if delay:
                            await asyncio.sleep(delay)
                        return text
            else:
                headers = {"User-Agent": user_agent} if user_agent else {}
                async with session.get(url, headers=headers) as response:
                    response.raise_for_status()
                    text = await response.text()
                    if delay:
                        await asyncio.sleep(delay)
                    return text
        except Exception as e:
            logging.error(f"{indent_str}Attempt {retry+1} failed for URL {url}: {e}")
            retry += 1
            await asyncio.sleep(backoff)
            backoff *= 2
    logging.error(f"{indent_str}All {max_retries} attempts failed for URL {url}.")
    return None

async def async_crawl_page(url, depth, visited, outputs, session, render=False, indent=0, delay=0, user_agent=None, domain_semaphores=None, max_per_domain=3, max_retries=3, use_plugins=False):
    indent_str = " " * (indent * 4)
    message = f"{indent_str}URL: {url}"
    outputs.append(message)
    logging.info(message)
    
    domain = urllib.parse.urlparse(url).netloc
    if domain_semaphores is not None:
        if domain not in domain_semaphores:
            domain_semaphores[domain] = asyncio.Semaphore(max_per_domain)
        semaphore = domain_semaphores[domain]
    else:
        semaphore = None

    text = await async_fetch(session, url, indent_str, render, delay, user_agent, semaphore, max_retries)
    if text is None:
        outputs.append(f"{indent_str}Error fetching URL")
        return
    # Plugin processing in async mode
    if use_plugins:
        try:
            from plugin_manager import load_plugins
            plugin_dir = "plugin_extensions"
            plugins = load_plugins(plugin_dir)
            for plugin in plugins:
                try:
                    result_plugin = plugin.process(text, url)
                    outputs.append(f"{indent_str}Plugin {plugin.__class__.__name__} output: {result_plugin}")
                    logging.info(f"{indent_str}Plugin {plugin.__class__.__name__} output: {result_plugin}")
                except Exception as e:
                    outputs.append(f"{indent_str}Plugin {plugin.__class__.__name__} error: {e}")
                    logging.error(f"{indent_str}Plugin {plugin.__class__.__name__} error: {e}")
        except Exception as e:
            logging.error(f"{indent_str}Failed to load plugins: {e}")

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
                tasks.append(async_crawl_page(link, depth - 1, visited, outputs, session, render, indent + 1, delay, user_agent, domain_semaphores, max_per_domain, max_retries, use_plugins))
        if tasks:
            await asyncio.gather(*tasks)

async def async_create_crawler(args):
    outputs = []
    msg = f"Crawler Name: {args.name}"
    outputs.append(msg)
    logging.info(msg)
    domain_semaphores = {}
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in args.url:
            task = async_crawl_page(url, args.depth, set([url]), outputs, session, args.render, delay=args.delay, user_agent=args.user_agent, domain_semaphores=domain_semaphores, max_per_domain=args.max_per_domain, max_retries=args.max_retries, use_plugins=args.use_plugins)
            tasks.append(task)
        if tasks:
            await asyncio.gather(*tasks)
    result_text = finalize_output(outputs, args)
    if args.qdrant:
        persist_results_qdrant(result_text, args)

# Function to query Qdrant using semantic search over stored embeddings.
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
    crawl_parser.add_argument("--render", action="store_true", help="Render dynamic content using Selenium")
    crawl_parser.add_argument("--delay", type=float, default=0, help="Delay (in seconds) between requests")
    crawl_parser.add_argument("--user-agent", type=str, default="", help="Custom User-Agent string for HTTP requests")
    crawl_parser.add_argument("--max-per-domain", type=int, default=3, help="Max concurrent requests per domain (default 3)")
    crawl_parser.add_argument("--max-retries", type=int, default=3, help="Maximum retries for async requests (default 3)")
    crawl_parser.add_argument("--use-plugins", action="store_true", help="Enable plugin processing for additional metadata extraction")
    # Qdrant persistence options for crawler
    crawl_parser.add_argument("--qdrant", action="store_true", help="Persist results to Qdrant DB")
    crawl_parser.add_argument("--qdrant-host", type=str, default="localhost", help="Qdrant host (default: localhost)")
    crawl_parser.add_argument("--qdrant-port", type=int, default=6333, help="Qdrant port (default: 6333)")
    crawl_parser.add_argument("--qdrant-collection", type=str, default="crawler_collection", help="Qdrant collection name")

    # Subparser for query command
    query_parser = subparsers.add_parser("query", help="Query semantic data from Qdrant")
    query_parser.add_argument("--query", type=str, required=True, help="Query text to search")
    query_parser.add_argument("--limit", type=int, default=5, help="Number of search results to return (default: 5)")
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
