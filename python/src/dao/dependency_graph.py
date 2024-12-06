
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

    def __init__(self, nosql_svc: CosmosNoSQLService):
        """
        Constructor method.  The given nosql_svc is an instance
        of CosmosNoSQLService that is already pointing at your
        Cosmos DB account, database, and container.
        """
        self.nosql_svc = nosql_svc


    async def traverse_dependencies(self, root_library: str, depth: int) -> dict:
        """
        Traverse the graph starting from the given root library
        to the given depth (a positive integer).
        Return a dictionary of the collected libraries, with a 
        depth value added to each returned library.
        """
        collected_libs = dict()
        result_object = dict()
        result_object['root_library'] = root_library
        result_object['depth'] = depth
        result_object['start_time'] = time.time()
        result_object['elapsed_time'] = -1   # will overlay below
        result_object['collected_libs'] = collected_libs

        try:
            root_library = root_library
            depth = depth

            await asyncio.sleep(0.1)

        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())
        result_object['elapsed_time'] = time.time() - result_object['start_time']
        return result_object

