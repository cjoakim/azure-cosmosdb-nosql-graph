import time

from src.models.device_data import DeviceData

# Instances of this class are used to detect and identify changes,
# if any, between one DeviceState object and other.
# Chris Joakim, Microsoft

class DeviceStateChanges:

    cosmos_generated_attrs = "_rid,_self,_etag,_attachments,_ts".split(',')
    
    def __init__(self, curr_doc, ds_doc):
        self.changes = 'none'
        self.curr_doc = curr_doc
        self.ds_doc = ds_doc
        self.updated_doc = dict()
        self.attrs_added = list()
        self.attrs_removed = list()
        self.attrs_changed = list()

        if self.ds_doc is None:
            return  # bad input, the streamed ds_doc is expected to be non-null
    
        if (self.curr_doc is None) or (len(self.curr_doc.keys()) == 0):
            self.changes = 'new'
            self.updated_doc = self.ds_doc
            for attr in ds_doc.keys():
                self.attrs_added.append(attr)
        else:
            self.compare_docs(self.curr_doc, self.ds_doc)

        if self.changes == 'none':
            self.updated_doc = None

    def has_changes(self):
        return self.changes != 'none'
    
    def compare_docs(self, curr_doc, ds_doc):
        merged_keys = self.merge_keys(self.curr_doc, self.ds_doc)
        for key in merged_keys:
            if key in DeviceStateChanges.cosmos_generated_attrs:
                # don't compare the cosmos system-generated attbibutes,
                # but do add them to the updated doc for upsert operation
                if key in curr_doc.keys():
                    self.updated_doc[key] = curr_doc[key]
            else:
                if key not in ds_doc:
                    self.changes = 'attr'
                    self.attrs_removed.append(key)
                elif key not in curr_doc:
                    self.changes = 'attr'
                    self.attrs_added.append(key)
                    self.updated_doc[key] = ds_doc[key]
                elif curr_doc[key] != ds_doc[key]:
                    self.changes = 'attr'
                    self.attrs_changed.append(key)
                    self.updated_doc[key] = ds_doc[key]
                else:
                    self.updated_doc[key] = curr_doc[key]

    def merge_keys(self, curr_doc, ds_doc):
        merged = dict()
        for key in curr_doc.keys():
            merged[key] = 0
        for key in ds_doc.keys():
            merged[key] = 0
        return sorted(merged.keys())
    