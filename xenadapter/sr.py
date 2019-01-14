from xenadapter.xenobject import XenObject

class SR(XenObject):
    api_class = "SR"
    db_table_name = "srs"
    EVENT_CLASSES=["sr"]
    PROCESS_KEYS = ["uuid", "name_label", "name_description", "content_type", "VDIs", "PBDs"]