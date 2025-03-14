import json
import logging
import traceback
import uuid

from azure.cosmos.aio import CosmosClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential

from src.services.config_service import ConfigService

# Chris Joakim, Microsoft

# azure_logger can be used to set the verbosity of the Azure and Cosmos SDK logging
azure_logger = logging.getLogger("azure")
azure_logger.setLevel(logging.WARNING)


LAST_REQUEST_CHARGE_HEADER = "x-ms-request-charge"


class CosmosNoSQLService:

    def __init__(self, opts={}):
        # https://www.slingacademy.com/article/python-defining-a-class-with-an-async-constructor/
        # https://stackoverflow.com/questions/33128325/how-to-set-class-attribute-with-await-in-init
        self._opts = opts
        self._dbname = None
        self._dbproxy = None
        self._ctrproxy = None
        self._cname = None
        self._client = None
        logging.info("CosmosNoSQLService - constructor")

    async def initialize(self):
        """This method should be called after the above constructor."""
        auth_mechanism = ConfigService.cosmosdb_nosql_auth_mechanism()
        logging.error("CosmosNoSQLService#auth_mechanism: {}".format(auth_mechanism))

        if auth_mechanism == "key":
            logging.info("CosmosNoSQLService#initialize with key")
            uri = ConfigService.cosmosdb_nosql_uri()
            key = ConfigService.cosmosdb_nosql_key()
            logging.error("CosmosNoSQLService#uri: {}".format(uri))
            logging.error("CosmosNoSQLService#key: {}".format(key))
            self._client = CosmosClient(uri, key)
            logging.info("CosmosNoSQLService - initialize() with key completed")
        else:
            logging.info("CosmosNoSQLService#initialize with DefaultAzureCredential")
            uri = ConfigService.cosmosdb_nosql_uri()
            credential = DefaultAzureCredential()
            # credential ino is injected into the runtime environment
            self._client = CosmosClient(uri, credential=credential)
            logging.info(
                "CosmosNoSQLService - initialize() with DefaultAzureCredential completed"
            )

    async def close(self):
        if self._client is not None:
            await self._client.close()
            logging.info("CosmosNoSQLService - client closed")

    async def list_databases(self):
        """Return the list of database names in the account."""
        dblist = list()
        async for db in self._client.list_databases():
            dblist.append(db["id"])
        return dblist

    def set_db(self, dbname):
        """Set the current database to the given dbname."""
        try:
            self._dbname = dbname
            self._dbproxy = self._client.get_database_client(dbname)
        except Exception as e:
            logging.critical(str(e))
            print(traceback.format_exc())
        return self._dbproxy  # <class 'azure.cosmos.aio._database.DatabaseProxy'>

    def get_current_cname(self):
        return self._cname

    def set_container(self, cname):
        """Set the current container in the current database to the given cname."""
        self._cname = cname
        self._ctrproxy = self._dbproxy.get_container_client(cname)
        return self._ctrproxy  # <class 'azure.cosmos.aio._container.ContainerProxy'>

    async def list_containers(self):
        """Return the list of container names in the current database."""
        container_list = list()
        async for container in self._dbproxy.list_containers():
            container_list.append(container["id"])
        return container_list

    async def point_read(self, id, pk):
        return await self._ctrproxy.read_item(item=id, partition_key=pk)

    async def create_item(self, doc):
        return await self._ctrproxy.create_item(body=doc)

    async def upsert_item(self, doc):
        return await self._ctrproxy.upsert_item(body=doc)

    async def delete_item(self, id, pk):
        return await self._ctrproxy.delete_item(item=id, partition_key=pk)

    # https://github.com/Azure/azure-sdk-for-python/blob/azure-cosmos_4.7.0/sdk/cosmos/azure-cosmos/samples/document_management_async.py

    async def execute_item_batch(self, item_operations: list, pk: str):
        # example item_operations:
        #   [("create", (get_sales_order("create_item"),)), next op, next op, ...]
        # each operation is a 2-tuple, with the operation name as tup[0]
        # tup[1] is a nested 2-tuple , with the document as tup[0]
        return await self._ctrproxy.execute_item_batch(
            batch_operations=item_operations, partition_key=pk
        )

    async def query_items(self, sql, cross_partition=False, pk=None, max_items=100):
        parameters_list, results_list = list(), list()
        parameters_list.append(
            {"name": "@enable_cross_partition_query", "value": cross_partition}
        )
        # parameters_list.append({"name": "@max_item_count", "value": max_items})
        if pk is not None:
            parameters_list.append({"name": "@partition_key", "value": pk})
        query_results = self._ctrproxy.query_items(
            query=sql, parameters=parameters_list
        )
        async for item in query_results:
            results_list.append(item)
        return results_list

    async def parameterized_query(
        self,
        sql_template,
        sql_parameters,
        cross_partition=False,
        pk=None,
        max_items=100,
    ):
        parameters_list, results_list = list(), list()
        parameters_list.append(
            {"name": "@enable_cross_partition_query", "value": cross_partition}
        )
        parameters_list.append({"name": "@max_item_count", "value": max_items})
        if pk is not None:
            parameters_list.append({"name": "@partition_key", "value": pk})
        if sql_parameters is not None:
            for sql_param in sql_parameters:
                parameters_list.append(sql_param)
        query_results = self._ctrproxy.query_items(
            query=sql_template, parameters=parameters_list
        )
        async for item in query_results:
            results_list.append(item)
        return results_list

    def last_response_headers(self):
        """
        The headers are an instance of class CIMultiDict.
        You can lookup the value of a header by name, like this:
            nosql_svc.last_response_headers()['x-ms-item-count']
        You can also iterate over the headers, like this:
            for two_tup in nosql_svc.last_response_headers().items():
                name, value = two_tup[0], two_tup[1]
        """
        try:
            return self._ctrproxy.client_connection.last_response_headers
        except:
            return None

    def last_request_charge(self):
        try:
            return float(
                self._ctrproxy.client_connection.last_response_headers[
                    LAST_REQUEST_CHARGE_HEADER
                ]
            )
        except:
            return -1.0

    def last_response_header(self, header):
        """
        Return the value of the given header name from the last response, or None.
        The following are some example header names and their values:

        Content-Length -> 62
        Content-Type -> application/json
        Date -> Wed, 21 Aug 2024 10:27:27 GMT
        Server -> Compute
        lsn -> 15386
        x-ms-activity-id -> 61171e8e-83cf-42c3-bf2b-86befec450e6
        x-ms-alt-content-path -> dbs/dev/colls/test
        x-ms-content-path -> hy5tAOrJ4DU=
        x-ms-cosmos-is-partition-key-delete-pending -> false
        x-ms-cosmos-llsn -> 15386
        x-ms-cosmos-physical-partition-id -> 0
        x-ms-cosmos-query-execution-info -> {"reverseRidEnabled":false,"reverseIndexScan":false}
        x-ms-documentdb-partitionkeyrangeid -> 0
        x-ms-gatewayversion -> 2.0.0
        x-ms-global-Committed-lsn -> 15386
        x-ms-item-count -> 1
        x-ms-item-count: 1
        x-ms-last-state-change-utc -> Tue, 20 Aug 2024 20:47:21.072 GMT
        x-ms-number-of-read-regions -> 0
        x-ms-request-charge -> 2.89
        x-ms-request-duration-ms -> 1.207
        x-ms-resource-quota -> documentSize=51200;documentsSize=52428800;documentsCount=-1;collectionSize=52428800;
        x-ms-resource-usage -> documentSize=0;documentsSize=382;documentsCount=63;collectionSize=398;
        x-ms-schemaversion -> 1.18
        x-ms-serviceversion -> version=2.14.0.0
        x-ms-session-token -> 0:-1#15386
        x-ms-throttle-retry-count -> 0
        x-ms-throttle-retry-wait-time-ms -> 0
        x-ms-transport-request-id -> 5133
        x-ms-xp-role -> 2
        """
        try:
            return self._ctrproxy.client_connection.last_response_headers[header]
        except:
            return None
