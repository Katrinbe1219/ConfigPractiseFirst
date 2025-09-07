from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import base64
import xml.etree.ElementTree as ET
import os
import hashlib

@dataclass
class VFSNode:
    name: str
    is_directory: bool
    is_binary: bool = False
    content: Optional[Union[bytes, str]] = None # if file - either bytes or str
    children: Optional[Dict[str, 'VFSNode']] = None

class VFS:
    def __init__(self):
        self.root = VFSNode(name = '', 
                            is_directory=True,
                            children={})
        self.current_directory = self.root

    def load_from_xml_file(self, path: str):

        if not os.path.exists(path):
            return False

        with open(path, 'r') as f:
            xml_content = f.read()
        
        root = ET.fromstring(xml_content)

        #создается новая структура
        self.root = VFSNode(name = '', 
                            is_directory=True,
                            children={})
        
        for directory in root.findall('directory'):
            dir_path = directory.get('name', '').strip('/')
            self.process_directory(directory, dir_path)
        
        return True

    def process_directory(self, directory: ET.Element, dirpath: str):
        current_node = self.ensure_path(dirpath)

        for file in directory.findall('file'):
            file_name = file.get('name', '')
            content = file.get('content', '')
            is_binary = file.get('binary','false').lower() == 'true'

            file_node = VFSNode(
                name = file_name,
                content= content,
                is_binary= is_binary,
                is_directory= False
            )

            current_node.children[file_name] = file_node
        
        for dir in directory.findall('directory'):
            dir_name = dir.get('name','')
            path_ = f"{dirpath}/{dir_name}" if dirpath else dir_name
            self.process_directory(dir, path_)
    

    def ensure_path(self, path:str):

        if path == '~':
            return self.root
        
        parts = path.strip('/').split('/')
        currrent_node = self.root

        for part in parts:
            if part not in currrent_node.children:
                new_dir = VFSNode(name = part, is_directory=True, children={})
                currrent_node.children[part] = new_dir
                currrent_node = new_dir
            else:
                currrent_node = currrent_node.children[part]
    
        return currrent_node
    
    def calculate_vfs_hash(self):
        hash_obj = hashlib.sha256()
        self.hash_node(self.root, hash_obj)
        return hash_obj.hexdigest()
    
    def hash_node(self, node: VFSNode, hash_obj):
        #хешируются метаданные узла - все, что есть в VFSNode
        self.hash_metadate(node, hash_obj)

        # if file - hash file content
        if not node.is_directory and node.content is not None:
            self.hash_content(node, hash_obj)
        
        #if directory - hash its children
        if node.is_directory and node.children is not None:
            self.hash_children(node, hash_obj)
    
    def hash_metadate(self, node: VFSNode, hash_obj):
        metadate = f"{node.name}:{node.is_directory}:{node.is_binary}"
        hash_obj.update(metadate.encode('utf-8'))
    
    def hash_content(self, node: VFSNode, hash_obj):
        # так как content может быть двух типов, то нужно два случая
        if isinstance(node.content, str):
            #unicode objects must be encoded before hashing
            hash_obj.update(node.content.encode('utf-8'))
        else:
            hash_obj.update(node.content)
    
    def hash_children(self, node: VFSNode, hash_obj):
        for child in node.children.keys():
            child_node = node.children[child]
            self.hash_node(child_node, hash_obj)
        

        

        
