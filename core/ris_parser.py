import json
import yaml
import os

class RISParser:
    struct_types = ['RMessage', 'RComposite', 'REnum', 'RList', 'RUnion']

    def __init__(self, ris_schema: str = None):
        self.generator =  RISGenerator()
        self._ris_schema = None
        if ris_schema:
            if ris_schema.endswith('json'):
                self.load_from_json(ris_schema)
            if ris_schema.endswith('yaml') or ris_schema.endswith('yml'):
                self.load_from_yaml(ris_schema)

    @property
    def ris_schema(self):
        return self._ris_schema

    @ris_schema.setter
    def ris_schema(self, value):
        self._ris_schema = value
        self.generator.table_from_ris(value)

    def load_schema(self, schema: dict):
        self.ris_schema = schema

    def load_from_json(self, json_path: str):
        with open(json_path, "r") as f:
            self.ris_schema = json.load(f)

    def load_from_yaml(self, yaml_path: str):
        with open(yaml_path, "r") as f:
            self.ris_schema = yaml.safe_load(f)

    def generate_classes(self):
        # todo
        pass

    def generate_code(self, output_dir: str):
        for struct_type in self.struct_types:
            os.makedirs(os.path.join(output_dir, self.generator.get_folder(struct_type)), exist_ok=True)

        for struct_name, struct_def in self.ris_schema.get("messages", {}).items():
            self.generator.generate_structure(struct_name, struct_def, parent='RMessage', output_dir=output_dir)
        for struct_name, struct_def in self.ris_schema.get("composites", {}).items():
            self.generator.generate_structure(struct_name, struct_def, parent='RComposite', output_dir=output_dir)
        for struct_name, struct_def in self.ris_schema.get("arrays", {}).items():
            self.generator.generate_structure(struct_name, struct_def, parent='RList', output_dir=output_dir)
        for struct_name, struct_def in self.ris_schema.get("enums", {}).items():
            self.generator.generate_structure(struct_name, struct_def, parent='REnum', output_dir=output_dir)
        for struct_name, struct_def in self.ris_schema.get("unions", {}).items():
            self.generator.generate_structure(struct_name, struct_def, parent='RUnion', output_dir=output_dir)

        self.generator.generate_init(output_dir=output_dir, metadata=self.ris_schema['metadata'])


class RISGenerator:

    def __init__(self):
        self._struct_table = None
        self._import_code = set()
        self._message_map = set()

    @property
    def struct_table(self):
        return self._struct_table

    @struct_table.setter
    def struct_table(self, value):
        self._struct_table = value

    @staticmethod
    def get_folder(struct_type):
        struct_type = 'RArray' if struct_type == 'RList' else struct_type
        return struct_type[1:].lower() + 's'

    def table_from_ris(self, schema):
        self.struct_table = {struct_name: struct_type
                             for struct_type, struct in schema.items()
                             for struct_name in struct}

    def reset_import_code(self):
        self._import_code = set()
        self._import_code.add("from rip.core import *")

    def generate_structure(self, struct_name, struct_def, parent, output_dir=None):
        self.reset_import_code()
        code = '\n\n' + getattr(self, f'generate_{parent}')(struct_name, struct_def)
        code = "\n".join(list(self._import_code)) + code
        if output_dir:
            with open(os.path.join(output_dir, f'{self.get_folder(parent)}/{struct_name}.py'), 'w') as file:
                file.write(code)
        return code

    def generate_RMessage(self, struct_name, struct_def):
        self._message_map.add((struct_def['id'], struct_name))
        self._import_code.add(f"from ..{self.get_folder('RComposite')}.Header import Header")
        class_code = f"class {struct_name}(RMessage):\n"
        class_code += f"    id = {struct_def['id']}\n"
        class_code += f"    source = {struct_def['source']}\n"
        class_code += f"    dest = {struct_def['dest']}\n"
        class_code += f"    header = Header()\n"
        for field_name, field_info in struct_def.get("fields", {}).items():
            field_type = self._map_type(field_info)
            class_code += f"    {field_name}: {field_type}\n"
        return class_code

    def generate_RComposite(self, struct_name, struct_def):
        class_code = f"class {struct_name}(RComposite):\n"
        for field_name, field_info in struct_def.get("fields", {}).items():
            field_type = self._map_type(field_info)
            class_code += f"    {field_name}: {field_type}\n"
        return class_code

    def generate_RList(self, struct_name, struct_def):
        class_code = f"class {struct_name}(RList):\n"
        element_type = self._map_type(struct_def["element_type"])
        length_field = struct_def.get("length_field", None)
        class_code += f"    element_type = {element_type}\n"
        if length_field:
            class_code += (f"    length_field = " +
                (f"{length_field}\n" if isinstance(length_field, int) else f"'{length_field}'\n"))
        return class_code

    def generate_REnum(self, struct_name, struct_def):
        class_code = f"class {struct_name}(REnum):\n"
        size_in_bytes = struct_def.get("size_in_bytes", 4)
        class_code += f"    size_in_bytes = {size_in_bytes}\n"
        class_code += "    values: dict = {\n"
        for name, value in struct_def["values"].items():
            class_code += f"        \"{name}\": {value},\n"
        class_code += "    }\n"
        return class_code

    def generate_RUnion(self, struct_name, struct_def):
        class_code = f"class {struct_name}(RUnion):\n"
        class_code += "    possible_types = {\n"
        for name, value in struct_def["possible_types"].items():
            mapped_type = self._map_type(value)
            class_code += f"        \"{name}\": {mapped_type},\n"
        class_code += "    }\n"
        return class_code

    def generate_init(self, output_dir=None, metadata=None):
        # Generazione dell'__init__.py
        metadata = metadata or {}
        code = "from rip.core.rserializable import RSerializable\n"
        code += "from .composites.Header import Header\n"
        message_map = dict(self._message_map)
        for message_name in message_map.values():
            code += f"from .messages.{message_name} import {message_name}\n"
        code += "\n"
        code += f"BYTE_ORDER = '{'big' if 'big' in metadata['byte_order'].lower() else 'little'}'\n"
        code += f"RSerializable.byte_order = '{'>' if 'big' in metadata['byte_order'].lower() else '<'}'\n"
        code += f"RSerializable.enum_size_in_bytes = {metadata['enum_size_in_bytes']}\n"
        code += f"RSerializable.list_length_field_size = {metadata['list_length_field_size']}\n"
        code += "\nmessage_map = {\n"
        for message_id, message_name in message_map.items():
            code += f"   {message_id}:{message_name},\n"
        code += "}\n\n"

        code += "def deserialize(data: bytearray, to_dict=False):\n"
        code += "     header = Header.deserialize(data[:Header().size_in_bytes()])\n"
        code += "     message = message_map[header.id].deserialize(data)\n"
        code += "     if to_dict:\n"
        code += "         message = message.to_dict()\n"
        code += "     return message\n"

        if output_dir:
            with open(os.path.join(output_dir, f'__init__.py'), 'w') as file:
                file.write(code)
        return code




    def _map_type(self, field_info):
        """Mappa i tipi di RIS sui tipi Python appropriati."""
        type_mapping = {
            'double': "RFloat64",
            "int8": "RInt8",
            "int16": "RInt16",
            "int32": "RInt32",
            "int64": "RInt64",
            "uint8": "RUint8",
            "uint16": "RUint16",
            "uint32": "RUint32",
            "uint64": "RUint64",
            "float": "RFloat32",
            "float32": "RFloat32",
            "float64": "RFloat64",
            "string8": "RString8",
            "string16": "RString16",
            "string32": "RString32",
            "string40": "RString40",
            "string64": "RString64",
            "string128": "RString128",
            "string256": "RString256",
            "bool": "RBool",
            "list": "RList",
            "composite": "RComposite",
            "enum": "REnum",
            "union": "RUnion",
            "message": "RMessage",
        }

        if isinstance(field_info, int) or isinstance(field_info, float):
            return field_info
        if (res := type_mapping.get(field_info.lower())) is not None:
            return res
        self._import_code.add(f"from ..{self.struct_table[field_info]}.{field_info} import {field_info}")
        return field_info
