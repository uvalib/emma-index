# Federated Index APIs

This is a dump of the final EMMA Search/Ingest API definitions on 01 Oct, 2023.
In principle, these should match the definitions stored in
[emma-search-ingest/api/schema](/emma-search-ingest/api/schema).

It is not clear whether the 0.0.6 versions were actually in use at the time
that the infrastructure was transferred from Benetech.  On SwaggerHub, it is
the 0.0.5 versions that come up by default.

Each subdirectory contains JSON and YAML renderings of OpenAPI specifications,
along with ZIPs of fragments generated from SwaggerHub for rendering the API
descriptions as HTML and via Go, Python, and JavaScript.

# [Federated Index Search API](emma-federated-search-api%200.0.6)

A description of the search endpoint:
* `GET /search`

_Source_:   https://app.swaggerhub.com/apis/bus/emma-federated-search-api/0.0.6

# [Federated Index Ingest API](emma-federated-ingestion-api%200.0.6)

A description of ingest endpoints:
* `PUT /records`
* `GET /recordGets`
* `POST /recordDeletes`

_Source_: https://app.swaggerhub.com/apis/bus/emma-federated-ingestion-api/0.0.6

# [Shared Components](emma-federated-shared-components%200.0.6)

Schema definitions used by both the Search and Ingest API specifications.

_Source_: https://app.swaggerhub.com/domains/bus/emma-federated-shared-components/0.0.6
