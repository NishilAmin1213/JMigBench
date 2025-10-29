# JMigBench
JMigBench - A Benchmark for Evaluating LLMs on Real-World Source Code Migration (Java 8 to Java 11)


# Overview
JMigBench is a benchmark suite and evaluation pipeline designed to assess large language models (LLMs) in the task of migrating Java functions from Java 8 to Java 11. It provides a dataset, a prompting and evaluation pipeline, and metrics geared toward code migration tasks. 

# Why JMigBench?
* Many enterprises are tasked with migrating legacy Java 8 codebases to newer long-term-support (LTS) versions like Java 11.

* Migrating code involves changes such as removed APIs, newer language features whilst retaining functional correctness.

* LLMs are increasingly used in code transformations, but to benchmark their performance in migration we need a dedicated dataset and evaluation setup—this is what JMigBench provides.

* The benchmark enables a standardized comparison of how well LLMs handle migration between Java 8 and Java 11.

# Getting Started
## Prerequisites
* Python 3.10
* Necessary Dependencies:
```
pip install -r requirements.txt
```

# Contents
* /Build_Synthetic_Dataset - Scripts to build a dataset for synthetic functions using a JSON file of input functions.
* /Built_Web_Scraped_Dataset – Scripts to web-scrape GitHub to build a dataset of real world functions.  
* /Outputs – Storage location for the output visualisations (SVG's)
* /Process_Results – Scripts to process the results pkl file and plot/output the metrics.
* /Prompting_Pipeline – Script used to prompt the Mistral API for each function in the dataset and store the output
* /Shared_Files – Directory for common file, utilities and datasets
* README.md – ReadMe for the project  
* requirements.txt – Text file with the dependencies of the project 
