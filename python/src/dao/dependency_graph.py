
# This class implements a "graph traversal" in Cosmos DB
# using the "aggregation pipeline" pattern.
# Chris Joakim, Microsoft

import asyncio
import time
import logging
import traceback

from src.services.config_service import ConfigService
from src.services.cosmos_nosql_service import CosmosNoSQLService
from src.util.counter import Counter
from src.util.fs import FS


class DependencyGraph:

    def __init__(self, nosql_svc):
        """
        Constructor method.  The given nosql_svc ctrproxy is a connection
        to the Cosmos DB container.
        """
        self.nosql_svc = nosql_svc
        self.ctrproxy = nosql_svc.current_ctrproxy()

    async def traverse_dependencies(self, root_library_name: str, depth: int) -> dict:
        """
        Traverse the graph starting from the given root library
        to the given depth (a positive integer).
        Return a dictionary of the collected libraries, with a 
        depth value added to each returned library.
        """
        collected_libs = dict()
        result_object = dict()
        result_object['root_library_name'] = root_library_name
        result_object['depth'] = depth
        result_object['start_time'] = time.time()
        result_object['elapsed_time'] = -1   # will overlay below
        result_object['collected_libs'] = collected_libs

        try:
            # First, find the given root library
            root_library_doc = await self.find_by_name(root_library_name)
            if root_library_doc is not None:
                root_library_doc['__traversal_depth'] = 0
                collected_libs[root_library_name] = root_library_doc
                # Now, traverse the dependencies to the given depth
                for traversal_depth in range(1, depth + 1):
                    await self.traverse_at_depth(collected_libs, traversal_depth)
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())
        result_object['elapsed_time'] = time.time() - result_object['start_time']
        return result_object

    async def find_by_name(self, name) -> dict | None:
        try:
            sql = self.lookup_by_name_sql(name)
            query_results = self.ctrproxy.query_items(query=sql)
            async for item in query_results:
                return item
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())
        return None 
    
    def lookup_by_name_sql(self, name):
        return "select * from c where c.name = '{}' offset 0 limit 1".format(name)

    async def traverse_at_depth(self, collected_libs, depth):
        # get the list of libraries at the previous depth, then execute
        # a a single query with an 'in' cause to fetch them.
        libs_to_get = dict()  # key is a string in '<id>|<pk>' format
        for libname in collected_libs.keys():
            libdoc = collected_libs[libname]
            if libdoc == 0:
                pass  # search previously attempted but not found
            else:
                if libdoc['__traversal_depth'] == (depth - 1):
                    for dep in libdoc['dependencies']:
                        dep_id = dep['id']
                        dep_id_pk = "{}|{}".format(dep_id, dep['pk'])
                        if dep_id in collected_libs.keys():
                            pass  # already collected or attempted
                        else:
                            libs_to_get[dep_id_pk] = dep_id_pk
        libs_to_get_keys = sorted(libs_to_get.keys())
        if len(libs_to_get_keys) > 0:
            for key in libs_to_get_keys:
                id, pk = key.split('|')
                doc = await self.nosql_svc.point_read(id, pk)
                if doc is not None:
                    doc['__traversal_depth'] = depth
                    collected_libs[doc['id']] = doc
