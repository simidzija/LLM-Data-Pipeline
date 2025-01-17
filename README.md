# LLM Data Pipeline

This repo implements the full pipeline for obtaining natural language data at scale and processing it into a form that can be used to train large language models.

We use the pipeline to process over 50k Wikipedia articles, yielding ~1GB of clean, training-ready data.
In the [`data`](data) folder we show a small subset of our data as it flows through the pipeline.

The pipeline involves the following steps:
1. [Crawling and Scraping](#1-crawling-and-scraping)
2. [Parsing](#2-parsing)
3. [Normalization](#3-normalization)
4. [Deduplication](#4-deduplication)
5. [Sentence Segmentation](#5-sentence-segmentation)
6. [Tokenization](#6-tokenization)


## 1. Crawling and Scraping
The canonical first step to obtaining LLM training data is to scrape text from the internet by crawling through webpages.
I impemented a crawler and scraper for Wikipedia.
The crawler starts with the seed urls located in [`config.yaml`](config/config.yaml). 
I used a single seed url, [List of Academic Fields](https://en.wikipedia.org/wiki/List_of_academic_fields), starting from which my program crawled and scraped 51,445 English language articles. This number was chosen so that I would end up with roughly ~1GB of clean training data.

To avoid getting blocked by Wikipedia for making too many requests to their server in too short a time frame, I incorporated rate limiting logic into my scraper, which ensured that on average I only send one get request to Wikipedia every second, in abidance with their bot policy.

- Source code: [`src/crawl.py`](src/crawl.py)
- Script: [`scripts/run_crawl.py`](scripts/run_crawl.py)
- Log file: [`log/crawl.log`](log/crawl.log)
- Data sample: [`data/crawl_data_5.jsonl`](data/crawl_data_5.jsonl)

## 2. Parsing

## 3. Normalization

## 4. Deduplication

## 5. Sentence Segmentation

## 6. Tokenization
