from typing import List

from handlers.graphql.types.blockdevice import BlockDevice


def resolve_disks(root, info, **args) -> List[BlockDevice]:
    def resolve_disk(key, value):
        return BlockDevice(**{'id': key, **value})

    return [resolve_disk(k, v) for k,v in root.disks.items()]