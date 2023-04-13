# EMMA Federated Index

This repository contains copies of work products supporting the creation of the
index used by the [EMMA application](https://github.com/uvalib/emma),
which is a union of metadata entries related to remediated content from each of
the EMMA member repositories:

* Bookshare (Benetech)
* Internet Archive
* HathiTrust
* EMMA

The original copies of these work products reside in locations internal to
Benetech;
because this work was wholly funded by the
[Mellon-funded FRAME grant](https://mellon.org/grants/grants-database/grants/university-of-virginia/1804-05699/),
this repository has been created to provide public visibility to this
non-proprietary work.


## Search Engine

The search engine developed by Benetech runs on Amazon OpenSearch (a fork of
Elasticsearch) and accessed via APIs for read and write access to the index.
Work products relating to the Mellon-funded search engine includes the source
code for the AWS lambdas connected to the AWS APIGateway APIs and the configuration
for the search engine.

## emma-search-ingest

This is the software that implements the
[Federated Search API](https://app.swaggerhub.com/apis/bus/emma-federated-search-api/0.0.6), the
[Federated Ingest API](https://app.swaggerhub.com/domains/bus/emma-federated-shared-components/0.0.5),
and the configuration files and examples for Elasticsearch. 

The Ingest API is used by the EMMA service to allow submissions to the EMMA repository to be
added to the federated index in real-time. The Search API allows for real time searching of the contents of the index. These lambdas are available to be triggered from endpoints configured via AWS APIGateway. Both can be located in emma-search-ingest/api/lambda. 

The configuration files which define the supported search types and define the contents of search result records for Elasticsearch can be located in emma-search-ingest/elasticsearch.

## emma-metadata-scanners

This is the software that implements the workflows which generate the federated
index by adding/modifying/deleting index entries.
This includes source code for the processes that retrieve metadata updates from
each member repository and transform it into Elasticsearch updates.


### emma-metadata-scanners/bookshare_scan

This is source code for the lambdas which retrieve metadata for remediated
Bookshare items which are presented in the EMMA index.


### emma-metadata-scanners/internet_archive_scan

This is source code for the lambdas which retrieve metadata for remediated
Internet Archive items (including Ace titles) which are presented in the EMMA index.


### emma-metadata-scanners/hathitrust_scan

This is source code for the lambdas which retrieve metadata for remediated
HathiTrust items which are presented in the EMMA index.

## emma-hathitrust-processors
This is source code for the lambdas and AWS Batch job which retrieve the large daily files from Hathitrust for preprocessing into smaller chunks for the hathitrust_scan lambda to transform and send records on to be ingested by the index. 


## emma-maintenance-scripts

This is source code for all other software that supports the generation and
maintenance of the federated index. This includes intialization scripts, index maintanence like snapshots, etc.
