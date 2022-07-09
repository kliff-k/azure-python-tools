# Databricks IDE connection

## Apache Spark SQL

It is possible to access the Apache Spark instance in an Azure Databricks cluster directly from your IDE of choice, enabling DB introspection, code completion, linting and much more.

The required JDBC driver is included and the URL format provided.

You will need to fetch some IDs from your Databricks cluster, namely the host and cluster ID, present in the URL.

Additionally, a user token/key is required for proper authentication. 