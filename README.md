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
code for those APIs and the configuration for the search engine.

### Federated Index Search API

This is the software that implements the
[Federated Search API](https://app.swaggerhub.com/apis/bus/emma-federated-search-api/0.0.5),
used by the EMMA service to allow EMMA users to query the index.

<input type="checkbox">&nbsp;</input> <strong style="color:red">TODO</strong>

### Federated Index Ingest API

This is the software that implements the
[Federated Ingest API](https://app.swaggerhub.com/domains/bus/emma-federated-shared-components/0.0.5),
used by the EMMA service to allow submissions to the EMMA repository to be
added to the federated index in real-time.

<input type="checkbox">&nbsp;</input> <strong style="color:red">TODO</strong>

### Elasticsearch Configuration

These are the configuration file(s) which define the supported search types and
define the contents of search result records.

<input type="checkbox">&nbsp;</input> <strong style="color:red">TODO</strong>

## Index Construction

This is the software that implements the workflows which generate the federated
index by adding/modifying/deleting index entries.
This includes source code for the processes that retrieve metadata updates from
each member repository and transform it into Elasticsearch updates.


### Benetech Index Workflow

This is source code for the software which retrieves metadata for remediated
Bookshare items which are presented in the EMMA index.

<input type="checkbox">&nbsp;</input> <strong style="color:red">TODO</strong>

### Internet Archive Index Workflow

This is source code for the software which retrieves metadata for remediated
Internet Archive items which are presented in the EMMA index.

<input type="checkbox">&nbsp;</input> <strong style="color:red">TODO</strong>


### HathiTrust Index Workflow

This is source code for the software which retrieves metadata for remediated
HathiTrust items which are presented in the EMMA index.

<input type="checkbox">&nbsp;</input> <strong style="color:red">TODO</strong>


### Index Construction Workflow

This is source code for all other software that supports the generation and
maintenance of the federated index.

<input type="checkbox">&nbsp;</input> <strong style="color:red">TODO</strong>
