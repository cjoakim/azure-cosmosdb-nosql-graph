
import logging
import random
import time
import uuid

from faker import Faker

from src.util.fs import FS

fake = Faker()

# This class is used to generate random simulated DeviceState events.
# Chris Joakim, Microsoft

class DeviceData:

    strong_attrs = 'ser,cid,host'.split(',')
    weak_attrs = 'ip,mac,build'.split(',')

    @classmethod
    def random_device_state(cls) -> dict:
        idx = random.randint(0, len(DeviceData.deviceStatesKeys) - 1)
        key = DeviceData.deviceStatesKeys[idx]
        print("DeviceData#random_device_state, idx/key: {}".format(idx,key))
        ds = DeviceData.deviceStates[key]
        ds['id'] = str(uuid.uuid4())
        ds['evt_time'] = int(time.time())

        # randomly simulate changes to the DeviceState
        change = random.randint(0, 100)
        if change < 5:
            print("DeviceData#random_device_state, idx/key/change: {}".format(idx,key,change))
            what_changed = random.randint(0, 5)
            # Strong: serialNum, computerID, hostname 
            # Weak: osName, ipAddress, macAddress, buildId
            if what_changed == 0:
                ds['ser'] = cls.random_serial_number()
            elif what_changed == 1:
                ds['cid'] = cls.random_computer_id()
            elif what_changed == 2:
                ds['host'] = cls.random_hostname()
            elif what_changed == 3:
                ds['ip'] = cls.random_ip_address()
            elif what_changed == 4:
                ds['mac'] = cls.random_mac_address()
            elif what_changed == 5:
                ds['build'] = random.randint(1000, 1_000_000)
            # update the DeviceState in memory as it may be emitted multiple times
            DeviceData.deviceStates[idx] = ds
        return ds

    @classmethod
    def simulated_etag(cls):
        return str(fake.hexify(text='^^^^^^^^^^^^'))

    @classmethod
    def initialize(cls) -> None:
        # Strong: deviceID, serialNum, computerID, hostname 
        # Weak: osName, ipAddress, macAddress, phoneNum, emailAddr, appUser, buildId

        # deviceIDs
        values = dict()
        for i in range(100_000):
            #value = str(uuid.uuid4())
            value = str(fake.hexify(text='^^^^^^^^^^^^'))
            values[value] = 0
        DeviceData.deviceIDs = sorted(values.keys())
        FS.write_json(DeviceData.deviceIDs, "tmp/deviceIDs.json")

        # serialNumbers
        values = dict()
        for i in range(100_000):
            value = str(i + 1)
            values[value] = 0
        DeviceData.serialNumbers = sorted(values.keys())
        FS.write_json(DeviceData.serialNumbers, "tmp/serialNumbers.json")

        # computerIDs
        values = dict()
        for i in range(100_000):
            value = str(random.randint(0, 1_000_000))
            values[value] = 0
        DeviceData.computerIDs = sorted(values.keys())
        FS.write_json(DeviceData.computerIDs, "tmp/computerIDs.json")

        # hostNames
        values = dict()
        for i in range(100_000):
            value = fake.hostname(0)
            values[value] = 0
        DeviceData.hostNames = sorted(values.keys())
        FS.write_json(DeviceData.hostNames, "tmp/hostNames.json")

        # producerIDs
        values = dict()
        for i in range(1_000):
            value = str(fake.company()).lower()
            values[value] = 0
        DeviceData.producerIDs = sorted(values.keys())
        FS.write_json(DeviceData.producerIDs, "tmp/producerIDs.json")

        # ipAddresses
        values = dict()
        for i in range(100_000):
            part1 = random.randint(0, 255) + 1
            part2 = random.randint(0, 255) + 1
            part3 = random.randint(0, 255) + 1
            part4 = random.randint(0, 255) + 1
            ip = "{}.{}.{}.{}".format(part1, part2, part3, part4)
            values[ip] = 0
        DeviceData.ipAddresses = sorted(values.keys())
        FS.write_json(DeviceData.ipAddresses, "tmp/ipAddresses.json")

        # macAddresses
        values = dict()
        for i in range(100000):
            #  It's a 12-digit hexadecimal number that's usually found on a device's network interface card (NIC). 
            value = str(fake.hexify(text='^^:^^:^^:^^:^^:^^'))
            values[value] = 0
        DeviceData.macAddresses = sorted(values.keys())
        FS.write_json(DeviceData.macAddresses, "tmp/macAddresses.json")

        # create the in-memory deviceStates
        # the random_device_state() method will add the 'id' and 'epoch' attributes
        # as well as randomly change various attribute values
        DeviceData.deviceStates = dict()
        for did in DeviceData.deviceIDs:
            producerID = cls.random_producer_id()
            ser = cls.random_serial_number()
            cid = cls.random_computer_id()
            host = cls.random_hostname()
            mac = cls.random_mac_address()
            build = random.randint(1000, 1_000_000)
            evt_time = int(time.time()) - 5  # 5-seconds from device emitting to current time
            doc = {
                "did": did,
                "pid": producerID,
                "extId": str(uuid.uuid4()),
                "ser": ser,
                "cid": cid,
                "host": host,
                "mac": mac,
                "build": build,
                "evt_time": evt_time,
                "until": -1,
                "dt": "ds"
            }
            DeviceData.deviceStates[did] = doc
        DeviceData.deviceStatesKeys = sorted(DeviceData.deviceStates.keys())

    # private/random methods below

    @classmethod
    def random_device_id(cls) -> dict:
        idx = random.randint(0, len(DeviceData.deviceIDs) - 1)
        return DeviceData.deviceIDs[idx]

    @classmethod
    def random_producer_id(cls) -> dict:
        idx = random.randint(0, len(DeviceData.producerIDs) - 1)
        return DeviceData.producerIDs[idx]
    
    @classmethod
    def random_serial_number(cls) -> dict:
        idx = random.randint(0, len(DeviceData.serialNumbers) - 1)
        return DeviceData.serialNumbers[idx]
    
    @classmethod
    def random_computer_id(cls) -> dict:
        idx = random.randint(0, len(DeviceData.computerIDs) - 1)
        return DeviceData.computerIDs[idx]
    
    @classmethod
    def random_hostname(cls) -> dict:
        idx = random.randint(0, len(DeviceData.hostNames) - 1)
        return DeviceData.hostNames[idx]
    
    @classmethod
    def random_ip_address(cls) -> dict:
        idx = random.randint(0, len(DeviceData.deviceIDs) - 1)
        return DeviceData.deviceIDs[idx]
    
    @classmethod
    def random_mac_address(cls) -> dict:
        idx = random.randint(0, len(DeviceData.deviceIDs) - 1)
        return DeviceData.deviceIDs[idx]
    