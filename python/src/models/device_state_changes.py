import time

from src.models.device_data import DeviceData

class DeviceStateChanges:

    def __init__(self, curr_doc, ds_doc):
        self.changes = 'none'
        self.curr_doc = curr_doc
        self.ds_doc = ds_doc
        self.updated_doc = None
        self.attr_changes = list()

        if self.ds_doc is None:
            return  # bad input, the streamed ds_doc is expected to be non-null
        
        if self.curr_doc is None:
            self.changes = 'new_doc'
            self.updated_doc = self.ds_doc
            for attr in ds_doc.keys():
                self.attr_changes.append(attr)
        else:
            pass

        if self.changes == 'none':
            self.updated_doc = None

    def has_changes(self):
        return self.changes != 'none'

