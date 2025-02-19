# azure-cosmosdb-nosql-graph : devices graph example

In this example the dataset is streaming in nature and created dynamically,
and the related nodes of the graph are also created/updated dynamically.

The implementation code is in **main_devices.py**

## Vertices/Entities in Cosmos DB

- **DeviceSingleton, (d1)**
  - Represents the unique devices as their identifiers evolve
  - did (deviceID) is a uuid
  - attrs: id, label, firstEventEpoch
  - partition key: did (deviceID)
  - dt (documentType): "D1"

- **ProducerDevices, (pd)** 
  - did (deviceID) is a uuid
  - pid (producerID) is a string
  - attrs: did, pid, extId
  - partition key: did (deviceID)
  - dt (documentType): "pd"

- **DeviceState (ds)**
  - has current and history
  - since and until timestamps
  - base attrs: did, pid, extId
  - other attrs: os, build, mac, ip (these include identifiers)
  - typical size 500b to 2kb
  - partition key: did (deviceID)
  - dt (documentType): "DS"

```
  Example Document
  {
      "did": "8cf5c21f-8a7d-4aa8-8d5b-5a9be896b3cd",
      "pid": "hunt, combs and mcmahon",
      "extId": "426dd850-32f1-4a6e-88ff-3c100898b457",
      "ser": "90310",
      "cid": "712681",
      "host": "db-92",
      "mac": "ae591184-87ae-4431-b551-e1923d1fdaca",
      "build": 677173,
      "dt": "ds",
      "id": "3e113135-3777-427f-87ff-98bc466e88cb",
      "epoch": 1739733895.2150435,
      "_rid": "8+kcAMsoK1NOAAAAAAAAAA==",
      "_self": "dbs/8+kcAA==/colls/8+kcAMsoK1M=/docs/8+kcAMsoK1NOAAAAAAAAAA==/",
      "_etag": "\"95000fe5-0000-0100-0000-67b23b880000\"",
      "_attachments": "attachments/",
      "_ts": 1739733896
  }

doc size: 546
upsert request_charge: 9.33
```

- **DeviceAttributes (da)**
  - These are in two types, strong or weak, and have a value
    - Strong: deviceID, serialNum, computerID, hostname 
    - Weak: osName, ipAddress, macAddress, phoneNum, emailAddr, appUser, buildId
  - attrs: name, value, deviceID
  - partition key: "DA"
  - dt (documentType): "DA"

Thus there is a hierarchical structure from DeviceSingleton --> ProducerDevices --> DeviceState.

### Questions

- How unique are deviceIDs?  Possible "value space collisions".
- Should DeviceAttributes be associated to a specific Device or ProducerDevice or DeviceSingleton?

## Application Flow

- **DeviceState** documents are ingested (5 RU) in an IoT manner, then:
  - the "until" attribute (utime) is set to -1, indicating it is the active DS

  - Query the latest DeviceState for the deviceID (4 RU)
    - Set its' "until" (utime) attribute to the event time (etime) of the incoming DeviceState
    - It is possible that a previous DeviceState for the deviceID does not exist

  - Point-read on **ProducerDevices** (1 RU)
  - Create/update the **ProducerDevices** document as necessary (5 RU)

  - Point-read on **DeviceSingleton** (1 RU)
  - Create/update the **DeviceSingleton** document as necessary (5 RU)

  - Point-read on each **DeviceAttribute** in the DeviceState event (1 RU x n)
  - Create each **DeviceAttribute** document as necessary (5 RU x n)


## Cosmos DB Implementation Notes

- Use short attribute names to save space
  - did instead of deviceID
  - pid instead of producerID
  - pk instead of partitionKey
  - dt instead of documentType
  - etime = the epoch time of the DeviceState event
  - utime = the "until time" of the DeviceState event.  Initially -1, but set to the etime of the newer event.

The _id, _etag, and _ts attributes are computed and set by Cosmos DB.

### Cosmos DB Containers

In "design 1" all vertex types are in in one container.

| Name             | Partition Key | DocType | PK Format     | Id Format      | Document Size |
| ---------------- | ------------- | ------- | ------------- | -------------- | ------------- |
| DeviceSingletons | /pk           | D1      | <did>         | d1-<did>       | 1K            |
| ProducerDevices  | /pk           | PD      | <pid>^<did>   | <pid>^<did>    | 1K            | 
| DeviceState      | /pk           | DS      | <did>         | uuid           | 1K            |
| DeviceAttributes | /pk           | DA      | a-<attr-name> | a-<attr-name>  | 1K            |

#### Document Attributes

- pk = Partition Key
- did = Device ID
- pid = Producer ID
- etime = the epoch time of the DeviceState event
- utime = the "until time" of the DeviceState event.  Initially -1, but set to the etime of the newer event.

#### Queries and Point-Reads

- D1 point-reads are enabled by computing the ID and PK for a DeviceState event
- D point-reads are enabled by computing the ID and PK for a DeviceState event
- DA point-reads are enabled by computing the ID and PK for the attributes in a DeviceState event
- DS Queries - partition-key queries, aided by a composite index

#### Design Notes

- Point reads are enabled for D1, D, and DA attributes by computing their ID and PK values
- DeviceState events are unique, therefore the uuid ID values
- Composite Index on DocType and PK
- Composite Index on did, etime, and utime.  To find the previously latest DeviceState event

#### Alternative Design

Container per document type.
