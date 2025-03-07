# RIS (R Interface Schema) Guide

## **General Structure of the RIS**
The R.I.S. is the descriptor of the basic 
structures used by the R.I.P. for the automatic creation of a 
communication interface. The purpose of this scheme is to standardize the input data 
before passing it to the interface constructor.

---

## **Main Sections of the RIS Schema**
| Section | Description |
|---------|------------|
| **metadata** | Contains general information about binary representation |
| **structures** | Contains all structures defined in the RIS interface |

```yaml
metadata:
  byte_order: "<"  # "<" for little-endian, ">" for big-endian
  enum_size_in_bytes: 4  # Default size for enums
  list_length_field_size: 4  # Number of bytes used for the list length field

structures:
  StructureName:
    fields:
      FieldName: Type  # Example: "id: int32", "bearing: float32"
```

The metadata fields and basic structures that RIS currently makes available and that the 
project core can read for the generation of Serializable Classes are illustrated below. 
The modularity with which the project was written (@RG) allows these fields to be expanded 
according to needs (however, I do not recommend it! :) ).

---

## **Available Metadata (`metadata`)**
| Field | Type | Description |
|-------|------|------------|
| **byte_order** | `string` | Specifies endianness (`"<"` for little-endian, `">"` for big-endian) |
| **enum_size_in_bytes** | `int` | Default number of bytes used for `enum` values |
| **list_length_field_size** | `int` | Number of bytes for the list length field |


These metadata are passed and managed within the RSerializable base class.

---

## **Available Structure Types (`structures`)**

### **1️. Composite (RComposite)**
 A **composite structure** that contains multiple fields with mixed types.
```yaml
CompositeName:
  fields:
    FieldName1: Type
    FieldName2: Type
```
 **Example:**
```yaml
SensorData:
  fields:
    id: int32
    temperature: float32
    status: SensorStatus
```

### **1️. Message (RMessage)**
 A **message structure** is an RComposite structure that defines an ID.
Usually the first field of a message is an Header structure, 
 which is a special Composite structure that defines how to obtain the 
 specifications of an incoming message
```yaml
MessageName:
  id: int32
  fields:
    Header: RComposite
    FieldName1: Type
    FieldName2: Type
```
 **Example:**
```yaml
MessageData:
  id: 100
  fields:
    Header: HeaderStruct
    a: int32
    b: string64
```


---

### **2️. Enum (REnum)**
A structure that defines a set of **fixed values**.
```yaml
EnumName:
  values:
    OptionName1: Value
    OptionName2: Value
  size_in_bytes: NumberOfBytes
```
 **Example:**
```yaml
SensorStatus:
  values:
    OK: 0
    WARNING: 1
    ERROR: 2
  size_in_bytes: 4
```

---

### **3️. List (RList)**
 A structure that represents a **list of elements of the same type**.
```yaml
ListName:
  element_type: TypeName
  length_field: LengthFieldName  # (optional)
```
 **Example:**
```yaml
SensorList:
  element_type: SensorData
  length_field: count
```

---

### **4️. Union (RUnion)**
 A structure that can contain **only one value among multiple possible types**.
```yaml
UnionName:
  possible_types:
    VariantName1: Type
    VariantName2: Type
```
 **Example:**
```yaml
MeasurementUnion:
  possible_types:
    float_value: float32
    int_value: int32
    string_value: string32
```

---

