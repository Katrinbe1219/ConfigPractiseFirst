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
    parent: Optional['VFSNode'] = None

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
        self.root = VFSNode(name = '~', 
                            is_directory=True,
                            children={})
        
        main_dir = root.find('directory')


        for directory in main_dir.findall('directory'):
            dir_path = directory.get('name', '').strip('/')
            result = self.process_directory(directory, dir_path, self.root)
            self.root.children[dir_path] = result
        
        self.current_directory = self.root
        return True

    def process_directory(self, directory: ET.Element, dirpath: str, parent: VFSNode):
        current_node = self.ensure_path(dirpath)
        current_node.parent = parent
        
        for file in directory.findall('file'):
            file_name = file.get('name', '')
            content = file.get('content', '')
            is_binary = file.get('binary','false').lower() == 'true'

            file_node = VFSNode(
                name = file_name,
                content= content,
                is_binary= is_binary,
                is_directory= False,
                parent = current_node
            )

            current_node.children[file_name] = file_node
        
        for dir in directory.findall('directory'):
            dir_name = dir.get('name','')
            path_ = f"{dirpath}/{dir_name}" if dirpath else dir_name
            new_dir = self.process_directory(dir, path_, current_node)
            current_node.children[dir_name] = new_dir

        #print(current_node.name, " ", current_node.children.keys())
        return current_node
    

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
        
    #cmd---------------------
    def get_current_node_children(self, args: list):
        children = self.current_directory.children

        if children is None or len(children)==0:
            return []
        if len(args) ==0 :
            result = []
            for child in children.keys():
                result.append( children[child].name)
            return result
        else:
            result = []
            _keys = children.keys()  if 'r' not  in args else list(children.keys())[::-1]
            #_keys = sorted(children.keys(), reverse=('-r' in args)) interesting alternative

            if 'l' not in args:
                for child in _keys:
                    result.append(children[child].name) 
            else:
                for child in _keys:
                    result.append( f"{children[child].name:<30} {children[child].is_directory:<10} {children[child].is_binary:<10}")
            
            return result
    
    def execute_cd(self, command: str, old_path: str):
        current_node = self.current_directory
        returning_path = '~'

        if command == "/":
            self.current_directory = self.root
            return returning_path
        
        if command == "..":
            if self.current_directory.parent is not None:
               self.current_directory = self.current_directory.parent
               returning_path = ("/").join(old_path.split('/')[:-1])
            
            return  returning_path
            

        paths = command.split('/')

        for path in paths:
            if path in current_node.children.keys():
                current_node = current_node.children[path]
            else:
                return False
            
        self.current_directory = current_node

        returning_path = old_path + '/' + command
        return  returning_path
            
         
    def execute_head(self, file_name:str):

        pathes = file_name.split('/')
        cur_dir = self.current_directory

        for path in pathes:
            if path in cur_dir.children.keys():
                cur_dir = cur_dir.children[path]
            else: 
                return False
        
        if cur_dir.content is  None:
            return ""
        else:
            if isinstance(cur_dir.content, str):
                text = cur_dir.content.splitlines()
                return text if len(text) <10 else text[:10]
            else:
                try:
                    text = cur_dir.content.decode('utf-8').splitlines()
                    return text if len(text) <10 else text[:10]
                
                except Exception as e:
                    print(f'problem with decoding {e} ')
                    return False

    



    #basic---------
    

        

        
