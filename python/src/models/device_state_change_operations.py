import json

from src.services.config_service import ConfigService
from src.services.cosmos_nosql_service import CosmosNoSQLService
from src.models.device_state_changes import DeviceStateChanges

# Instances of this class implement the database mutation logic
# for a given DeviceState event.
# Chris Joakim, Microsoft

class DeviceStateChangeOperations:

    all_operations = list()

    def __init__(self, nosql_svc: CosmosNoSQLService, ds_doc: dict, insert_ru: float):
        self.nosql_svc = nosql_svc
        self.ds_doc = ds_doc
        self.ds_did = ds_doc['did'] 
        self.previous_ds_doc = None
        self.operations = list() # list of dicts with name and ru
        self.d1_container = ConfigService.envvar("COSMOSDB_NOSQL_D1_CONTAINER", "DeviceSingletons")
        self.d_container  = ConfigService.envvar("COSMOSDB_NOSQL_D_CONTAINER",  "Devices")
        self.ds_container = ConfigService.envvar("COSMOSDB_NOSQL_DS_CONTAINER", "DeviceState")
        self.da_container = ConfigService.envvar("COSMOSDB_NOSQL_DA_CONTAINER", "DeviceAttributes")
        self.add_operation('insert device state', insert_ru, ds_doc)

    async def execute(self) -> None:
        await self.read_update_previous_device_state()
        print("DSCO_execute_completed, ru: {} op_count: {} ops: {}".format(
            self.get_total_ru(), self.get_op_count(), self.operations))

    async def read_update_previous_device_state(self) -> None:
        sql = self.recent_events_for_device_sql(self.ds_doc)
        print(sql)
        results = await self.nosql_svc.query_items(
            sql, cross_partition=False, pk='/did', max_items=2)
        ru = self.nosql_svc.last_request_charge()
        self.add_operation('read device states', ru)
        print('read device states results: rows: {} sql: {}'.format(len(results), sql))
        for result in results:
            print("read device state result: {}".format(result))
        if len(results) == 2:
            self.previous_ds_doc = results[1]
            self.previous_ds_doc['until'] = self.ds_doc['evt_time']
            self.previous_ds_doc = await self.nosql_svc.upsert_item(self.previous_ds_doc)
            ru = self.nosql_svc.last_request_charge()
            self.add_operation('update previous device state', ru, self.previous_ds_doc)

    def add_operation(self, operation_name: str, request_units: float, doc:dict = None) -> None:
        entry = { 
            'did': self.ds_did,
            'operation': operation_name, 
            'ru': request_units,
            'doc_size': 0
        }
        if doc is not None:
            entry['doc_size'] = len(json.dumps(doc))
        self.operations.append(entry)
        DeviceStateChangeOperations.all_operations.append(entry)

    def get_op_count(self) -> int:
        return len(self.operations)
    
    def get_total_ru(self) -> float:
        total = 0.0
        for entry in self.operations:
            total = total + entry['ru']
        return total
    
    def recent_events_for_device_sql(self, doc: dict) -> str:
        parts = list()
        parts.append("select * from c where c.did = '{}'".format(doc['did']))
        parts.append("and c.dt = 'ds'")
        parts.append("order by c.evt_time desc offset 0 limit 2")
        return " ".join(parts).strip()
    
    