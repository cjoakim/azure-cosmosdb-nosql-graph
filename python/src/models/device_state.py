import time

from src.models.device_state_changes import DeviceStateChanges

class DeviceState:
    """
    This class implements a simple int counter with an underlying dict object.
    """

    def __init__(self):
        self.data = {}

    def changes(self, curr_doc, ds_doc) -> DeviceStateChanges:
        """
        Return the doc to be updated if the new ds_doc has changes from the current_doc.
        Else, return None.
        """
        changes = DeviceStateChanges()
        
        return changes

