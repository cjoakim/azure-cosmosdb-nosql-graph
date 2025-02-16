
import logging
import uuid

from faker import Faker

# Chris Joakim, Microsoft

class DeviceData:

    @classmethod
    def initialize(cls) -> None:
        DeviceData.fake = Faker()
        DeviceData.deviceIDs = dict()
        DeviceData.ipAddresses = dict()
        DeviceData.macAddresses = dict()
        logging.info("DeviceData#initialize - completed")

    @classmethod
    def create_device_state_doc(cls) -> dict:
        doc = dict()
        docID = str(uuid.uuid4())
        deviceID = str(uuid.uuid4())
        doc = {
            "id": docID,
            "did": deviceID,
            "name": cls.fake.name(),
            "address": cls.fake.address(),
            "city": cls.fake.city(),
            "state": "NC",
            "email": cls.fake.email(),
            "phone": cls.fake.phone_number(),
            "dt": "ds"
        }
        return doc 