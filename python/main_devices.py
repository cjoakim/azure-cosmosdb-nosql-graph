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
import uuid

from docopt import docopt
from dotenv import load_dotenv

from src.services.config_service import ConfigService
from src.services.cosmos_nosql_service import CosmosNoSQLService
from src.models.device_data import DeviceData
from src.models.device_state_changes import DeviceStateChanges
from src.models.device_state_change_operations import DeviceStateChangeOperations
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

        # create the events_list that will be iterated several times
        # with slight modifications to the device states
        events_list = list()
        for i in range(event_count):
            events_list.append(DeviceData.random_device_state())

        for i in range(3):
            await stream_device_state_events(i, events_list, nosql_svc)
            await asyncio.sleep(5)

        FS.write_json(
            DeviceStateChangeOperations.all_operations,
            "tmp/device_state_change_operations.json")
    except Exception as e:
        logging.info(str(e))
        logging.info(traceback.format_exc())
    await nosql_svc.close()
    logging.info("end of simulate_device_state_stream")


async def stream_device_state_events(iteration: int, events_list: list, nosql_svc: CosmosNoSQLService):
    for obj in events_list:
        print('----------')
        obj['id'] = str(uuid.uuid4())
        obj['evt_time'] = int(time.time())
        print("iter: {} streaming device_state event: did: {} id: {}".format(
            iteration, event_count, obj['did'], obj['id']))
        
        if iteration > 0:
            make_random_changes(obj)

        ds_doc = await nosql_svc.upsert_item(obj)
        insert_ru = nosql_svc.last_request_charge()
        print("ds_doc doc: {}".format(ds_doc))
        print("ds_doc doc size: {}".format(len(json.dumps(ds_doc))))
        print("ds_doc insert request_charge: {}".format(insert_ru))
        time.sleep(0.1)

        if True:
            ops: DeviceStateChangeOperations = DeviceStateChangeOperations(nosql_svc, ds_doc)
            ops.add_operation("DeviceState insert", insert_ru)
            await ops.execute()

def make_random_changes(obj):
    # TODO - implement
    pass

def delete_tmp_files():
    FS.delete_dir("tmp")


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
                FS.delete_files_in_dir("tmp")
                test_initialize_data()
            elif func == "simulate_device_state_stream":
                FS.delete_files_in_dir("tmp")
                event_count = int(sys.argv[2])
                simulate_azure_function = ConfigService.boolean_arg("--simulate-az-function")
                asyncio.run(simulate_device_state_stream(event_count, simulate_azure_function))
            else:
                print_options("".format(func))
        except Exception as e:
            logging.info(str(e))
            logging.info(traceback.format_exc())
