#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from __future__ import annotations
import socket
import json

BoneNode = dict
BoneNode = dict[str, BoneNode | str | list[str]]

class JsonLiveLink(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.addr = (ip, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skeleton = {}
        self.transforms = {}
    
    def __del__(self):
        self.socket.close()
    
    def set_bones(self, subject_name: str, bone_tree: BoneNode):
        bones, parents = self._flatten_bones(bone_tree)
        self.skeleton[subject_name] = (bones, parents)
        self.transforms[subject_name] = {
            bones[i]: [0, 0, 0, 0, 0, 0, 0, 1, 1, 1] for i in range(len(bones))
        }
    
    def update(self, *subjects_to_update: list[str]):
        if not subjects_to_update:
            subjects_to_update = list(self.skeleton.keys())
        for subject in subjects_to_update:
            bones, parents = self.skeleton[subject]
            transforms = self.transforms[subject]
            bones_data = []
            for i in range(len(bones)):
                transform = transforms[bones[i]]
                bones_data.append({
                    "Name": bones[i],
                    "Parent": parents[i],
                    "Location": transform[0:3],
                    "Rotation": transform[3:7],
                    "Scale": transform[7:10],
                })

            subject_data = {subject: bones_data}
            self._send(json.dumps(subject_data).encode("utf-8"))

    def _send(self, data: bytes) -> None:
        self.socket.sendto(data, self.addr)

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
            if not bone_tree:
                return
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

