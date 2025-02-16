"""
This program is for CLI, or "console app" functionality related
to this demonstration of the Cosmos DB NoSQL API.
Usage:
    python main_devices.py print_defined_environment_variables
    python main_devices.py simulate_device_state_stream <event-count> <flag-args>
    python main_devices.py simulate_device_state_stream 100 
    python main_devices.py simulate_device_state_stream 100 --simulate-az-function
    python main_devices.py test_initialize_data 
Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import asyncio
import json
import sys
import time
import logging
import traceback

from docopt import docopt
from dotenv import load_dotenv


from src.dao.dependency_graph import DependencyGraph
from src.services.config_service import ConfigService
from src.services.cosmos_nosql_service import CosmosNoSQLService
from src.util.counter import Counter
from src.util.device_data import DeviceData
from src.util.fs import FS

# get the Cosmos DB database and container names from environment variables, with defaults
dbname = ConfigService.envvar("COSMOSDB_NOSQL_DB", "devices")
d1_container = ConfigService.envvar("COSMOSDB_NOSQL_D1_CONTAINER", "DeviceSingletons")
d_container  = ConfigService.envvar("COSMOSDB_NOSQL_D_CONTAINER",  "Devices")
ds_container = ConfigService.envvar("COSMOSDB_NOSQL_DS_CONTAINER", "DeviceState")
da_container = ConfigService.envvar("COSMOSDB_NOSQL_DA_CONTAINER", "DeviceAttributes")


def print_options(msg):
    print(msg)
    arguments = docopt(__doc__, version="1.0.0")
    print(arguments)


def print_defined_environment_variables():
    ConfigService.print_defined_env_vars()

def test_initialize_data():
    DeviceData.initialize()
    for i in range(3):
        ds = DeviceData.random_device_state()
        size = len(json.dumps(ds))
        print("device state: {} size:{}".format(ds, size))

async def simulate_device_state_stream(event_count: int, simulate_azure_function: bool):
    """
    Create a stream of device state events, and optionally simulate an Azure Function.
    """
    logging.info("simulate_device_state_stream, dbname: {}".format(dbname))
    logging.info("simulate_device_state_stream, d1_container: {}".format(d1_container))
    logging.info("simulate_device_state_stream, d_container:  {}".format(d_container))
    logging.info("simulate_device_state_stream, ds_container: {}".format(ds_container))
    logging.info("simulate_device_state_stream, da_container: {}".format(da_container))
    DeviceData.initialize()

    try:
        # First initialize the CosmosNoSQLService connection -
        # to the account, database, and DeviceState container.
        opts = dict()
        opts["enable_diagnostics_logging"] = True
        nosql_svc = CosmosNoSQLService(opts)
        await nosql_svc.initialize()

        dbs = await nosql_svc.list_databases()
        logging.info("databases: {}".format(dbs))

        dbproxy = nosql_svc.set_db(dbname)
        print("dbproxy: {}".format(dbproxy))

        containers = await nosql_svc.list_containers()
        print("containers: {}".format(containers))

        ctrproxy = nosql_svc.set_container(ds_container)
        print("ctrproxy: {}".format(ctrproxy))

        for i in range(event_count):
            seq = i + 1
            print('----------')
            obj = DeviceData.random_device_state()
            print("streaming device_state event: {}/{} id: {} did: {}".format(
                seq, event_count, obj['id'], obj['did']))
        
            ds_doc = await nosql_svc.upsert_item(obj)
            print("ds_doc doc: {}".format(ds_doc))
            print("ds_doc doc size: {}".format(len(json.dumps(ds_doc))))
            print("ds_doc last_request_charge: {}".format(nosql_svc.last_request_charge()))
            if True:
                outfile = "tmp/device_doc_{}_{}.json".format(seq, obj['id'])
                FS.write_json(ds_doc, outfile)
            time.sleep(0.1)
            if simulate_azure_function:
                await process_streamed_device_state_event(nosql_svc, ds_doc, dbproxy, ctrproxy)

        print("end of simulate_device_state_stream")
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())
    await nosql_svc.close()
    logging.info("end of simulate_device_state_stream")

async def process_streamed_device_state_event(nosql_svc, ds_doc, dbproxy, ctrproxy):
    """
    This implements logic that could be implemented in a ChangeFeed Azure Function
    so as to decouple the DeviceState ingestion stream from the downstream
    processing logic.
    """
    logging.info("process_streamed_device_state_event, ds_doc: {}".format(ds_doc))

    print('---')
    doc = await nosql_svc.point_read(ds_doc["id"], ds_doc["did"])
    print("point_read doc: {}".format(doc))
    print("point_read doc size: {}".format(len(json.dumps(doc))))
    print("point_read last_request_charge: {}".format(nosql_svc.last_request_charge()))
    
    print('---')
    doc["phone"] = "867-5309"
    updated = await nosql_svc.upsert_item(doc)
    print("updated doc: {}".format(updated))
    print("updated doc size: {}".format(len(json.dumps(doc))))
    print("updated last_request_charge: {}".format(nosql_svc.last_request_charge()))
    print('---')


if __name__ == "__main__":
    load_dotenv(override=True)  # load environment variable overrides from the .env file
    logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
    if len(sys.argv) < 2:
        print_options("")
        exit(1)
    else:
        try:
            func = sys.argv[1].lower()
            if func == "print_defined_environment_variables":
                print_defined_environment_variables()
            elif func == "test_initialize_data":
                test_initialize_data()
            elif func == "simulate_device_state_stream":
                event_count = int(sys.argv[2])
                simulate_azure_function = ConfigService.boolean_arg("--simulate-az-function")
                asyncio.run(simulate_device_state_stream(event_count, simulate_azure_function))
            else:
                print_options("".format(func))
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())
