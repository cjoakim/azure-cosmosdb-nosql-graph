import time

from src.models.device_data import DeviceData
from src.models.device_state_changes import DeviceStateChanges

# pytest -v tests/test_device_state_changes.py

DeviceData.initialize()

def test_new_device_state():
    curr_doc = None
    ds_doc = DeviceData.random_device_state()
    dsc = DeviceStateChanges(curr_doc, ds_doc)
    assert dsc.has_changes() == True
    assert dsc.is_new() == True
    assert dsc.changes == 'new'
    assert dsc.updated_doc != None
    assert sorted(dsc.attrs_added) == sorted(ds_doc.keys())
    assert len(dsc.attrs_added) == len(ds_doc.keys())
    assert len(dsc.attrs_removed) == 0
    assert len(dsc.attrs_changed) == 0

    for attr_name in sorted(ds_doc.keys()):
        assert dsc.updated_doc[attr_name] == ds_doc[attr_name]

    assert '_etag' not in dsc.updated_doc.keys()

def test_no_changes():
    curr_doc = DeviceData.random_device_state()
    curr_doc['_etag'] = DeviceData.simulated_etag()
    ds_doc = dict(curr_doc)
    dsc = DeviceStateChanges(curr_doc, ds_doc)
    assert dsc.has_changes() == False
    assert dsc.is_new() == False
    assert dsc.changes == 'none'
    assert dsc.updated_doc == None
    assert len(dsc.attrs_added) == 0
    assert len(dsc.attrs_removed) == 0
    assert len(dsc.attrs_changed) == 0

def test_attr_change():
    curr_doc = DeviceData.random_device_state()
    curr_doc['_etag'] = DeviceData.simulated_etag()
    ds_doc = dict(curr_doc)
    ds_doc['mac'] = int(time.time())
    dsc = DeviceStateChanges(curr_doc, ds_doc)
    print(dsc.updated_doc)
    assert dsc.has_changes() == True
    assert dsc.is_new() == False
    assert dsc.changes == 'attr'
    assert dsc.updated_doc != None
    assert len(curr_doc.keys()) == len(dsc.updated_doc.keys())
    assert len(dsc.attrs_added) == 0
    assert len(dsc.attrs_removed) == 0
    assert len(dsc.attrs_changed) == 1
    assert dsc.attrs_changed == ['mac']

    assert curr_doc['_etag'] == dsc.updated_doc['_etag']

def test_attr_added():
    curr_doc = DeviceData.random_device_state()
    curr_doc['_etag'] = DeviceData.simulated_etag()
    ds_doc = dict(curr_doc)
    ds_doc['cat'] = 'elsa'
    dsc = DeviceStateChanges(curr_doc, ds_doc)
    print(dsc.updated_doc)
    assert dsc.has_changes() == True
    assert dsc.is_new() == False
    assert dsc.changes == 'attr'
    assert dsc.updated_doc != None
    expected_attr_count = len(curr_doc.keys()) + 1
    assert len(dsc.updated_doc.keys()) == expected_attr_count
    assert len(dsc.attrs_added) == 1
    assert len(dsc.attrs_removed) == 0
    assert len(dsc.attrs_changed) == 0
    assert dsc.attrs_added == ['cat']

    assert curr_doc['_etag'] == dsc.updated_doc['_etag']

def test_attr_removed():
    curr_doc = DeviceData.random_device_state()
    curr_doc['_etag'] = DeviceData.simulated_etag()
    ds_doc = dict(curr_doc)
    del ds_doc['build']
    dsc = DeviceStateChanges(curr_doc, ds_doc)
    print(dsc.updated_doc)
    assert dsc.has_changes() == True
    assert dsc.is_new() == False
    assert dsc.changes == 'attr'
    assert dsc.updated_doc != None
    expected_attr_count = len(curr_doc.keys()) - 1
    assert len(dsc.updated_doc.keys()) == expected_attr_count
    assert len(dsc.attrs_added) == 0
    assert len(dsc.attrs_removed) == 1
    assert len(dsc.attrs_changed) == 0
    assert dsc.attrs_removed == ['build']

    assert curr_doc['_etag'] == dsc.updated_doc['_etag']
