
# This class implements a "graph traversal" in Cosmos DB
# using the "aggregation pipeline" pattern.
# Chris Joakim, Microsoft

from src.services.config_service import ConfigService
from src.services.cosmos_nosql_service import CosmosNoSQLService
from src.util.counter import Counter
from src.util.fs import FS


class DependencyGraph:

    def __init__(self, nosql_svc: CosmosNoSQLService, ):
        """
        Constructor method.  The given nosql_svc is an instance
        of CosmosNoSQLService that is already pointing at your
        Cosmos DB account, database, and container.
        """
        self.nosql_svc = nosql_svc


    def traverse(self, root_library: str, depth: int) -> dict:
        """
        Traverse the graph starting from the given root library
        to the given depth (a positive integer).
        Return a dictionary of the collected libraries, with a 
        depth value added to each returned library.
        """
        self.root_library = root_library
        self.depth = depth
        self.collected_libs = dict()

        return self.collected_libs
