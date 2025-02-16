import os
import pytest

from src.util.template import Template
from src.services.config_service import ConfigService
from src.models.device_data import DeviceData
from src.models.device_state_changes import DeviceStateChanges

# pytest -v tests/test_device_state_changes.py

DeviceData.initialize()

def test_new_device_state():
    curr_doc = None
    ds_doc = DeviceData.random_device_state()
    dsc = DeviceStateChanges(curr_doc, ds_doc)
    assert dsc.has_changes() == True
    assert dsc.changes == 'new_doc'
    assert dsc.updated_doc != None
    assert sorted(dsc.attr_changes) == sorted(ds_doc.keys())

    for attr_name in sorted(ds_doc.keys()):
        assert dsc.updated_doc[attr_name] == ds_doc[attr_name]

def test_no_changes():
    curr_doc = DeviceData.random_device_state()
    ds_doc = dict(curr_doc)
    dsc = DeviceStateChanges(curr_doc, ds_doc)
    assert dsc.has_changes() == False
    assert dsc.changes == 'none'
    assert dsc.updated_doc == None

def test_strong_change():
    # TODO - test and impl is WIP
    curr_doc = DeviceData.random_device_state()
    curr_doc['_etag'] = DeviceData.simulated_etag()
    ds_doc = dict(curr_doc)
    dsc = DeviceStateChanges(curr_doc, ds_doc)
    assert dsc.has_changes() == False
    assert dsc.changes == 'none'
    assert dsc.updated_doc == None
