#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from __future__ import annotations
import socket
import random
from draggable_plot import DraggablePlot
import json

BoneNode = dict
BoneNode = dict[str, BoneNode | str]

class JsonLiveLink(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.addr = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def __del__(self):
        self.socket.close()
    
    def send(self, data: bytes) -> None:
        self.socket.sendto(data, self.addr)

    def set_bones(self, bone_tree: dict[str, list[dict]]):
        self.bones, self.parents = self._flatten_bones(bone_tree)
        assert(len(self.bones) == len(self.parents))
        self.bones_transforms = {
            self.bones[i]: [0, 0, 0, 0, 0, 0, 0, 1, 1, 1] for i in range(len(self.bones))
        }

    @staticmethod
    def _flatten_bones(bone_tree: BoneNode):
        def fix_bone_format(node: BoneNode) -> BoneNode:
            if isinstance(node, str):
                # auto fix format
                node = {node: {}}
            if isinstance(node, list):  # list[str]
                for child_name in node:
                    assert isinstance(child_name, str), f"Unsupported child format {child_name} of bone {bone}"
                node = {child_name: {} for child_name in node}
            assert isinstance(node, dict)
            return node

        def walk_bones(bone_tree: BoneNode, callback: callable = None, parent_bone: str = ''):
            # print('walk_bones: ', parent_bone_id, bone_tree)
            for bone in bone_tree:
                if callback:
                    callback(parent_bone, bone)
                # all code below are for walking children. no stat change is involved.
                children = bone_tree[bone]
                children = fix_bone_format(children)
                walk_bones(children, callback, bone)
        
        bone_registry = {}
        current_bone_id = 0
        def register_bone(parent_bone:str, bone: str):
            nonlocal current_bone_id
            assert bone and isinstance(bone, str), f"bone name cannot be empty"
            assert bone not in bone_registry, f"duplicate bone {bone} in {parent_bone}"
            bone_registry[bone] = current_bone_id
            current_bone_id += 1
        walk_bones(bone_tree, register_bone)

        bone_array = sorted(bone_registry.keys(), key=lambda x: bone_registry[x])

        bone_parent_array = [-1] * len(bone_registry)
        def link_bone(parent_bone:str, bone: str):
            nonlocal bone_registry, bone_parent_array
            parent_bone_id = bone_registry.get(parent_bone, -1)
            bone_id = bone_registry[bone]
            # print(f"{parent_bone_id}:{parent_bone} -> {bone_id}:{bone}")
            assert bone_parent_array[bone_id] == -1, f"duplicate bone {bone} in {parent_bone}"
            bone_parent_array[bone_id] = parent_bone_id
        walk_bones(bone_tree, link_bone)

        return bone_array, bone_parent_array


# ======================  test ======================

jll = JsonLiveLink("127.0.0.1", 54321)
jll.set_bones({
    "root": {
        "base": {},
        "stone_1": "stone_2",
        "stupka": {}
    }
})

# matplot callback
def on_update_plot(points):
    global jll
    scale = 1.0
    for name in points:
        x,y = points[name]
        transform = jll.bones_transforms[name]
        transform[0] = x * scale
        transform[1] = 0 * scale
        transform[2] = y * scale
    subject = {
        "mortar": [    ##### EDIT SUBJECT NAME
            {
                "Name": jll.bones[i],
                "Parent": jll.parents[i],
                "Location": jll.bones_transforms[jll.bones[i]][0:3],
                "Rotation": jll.bones_transforms[jll.bones[i]][3:7],
                "Scale": jll.bones_transforms[jll.bones[i]][7:10],
            } for i in range(len(jll.bones))
        ]
    }
    jll.send(json.dumps(subject).encode("utf-8"))

xlim = (-100, 100)
ylim = xlim
plot = DraggablePlot(xlim, ylim, on_update_plot)
# add bones
for bone in jll.bones:
    rand_x = random.randint(*xlim)
    rand_y = random.randint(*ylim)
    plot.add_point(rand_x, rand_y, bone)
# manual update to plot newly added bones
plot.update_plot()

plot.show()
