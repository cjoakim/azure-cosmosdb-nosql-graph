# azure-cosmosdb-nosql-graph : devices graph example

In this example the dataset is streaming in nature and created dynamically,
and the related nodes of the graph are also created/updated dynamically.

The implementation code is in **main_devices.py**

## Ingestion Flow

- **DeviceState (DS)** documents are ingested (5 RU) in an IoT manner:
  - the "until" attribute (utime) is initially set to -1, indicating it is the active DS

  - Then execute the following logic to process the new DeviceState event
    - This logic could be implemented directly by the ingestion process
    - Or by an Azure Function listening to the ingestion container

    - Query the latest DeviceState for the deviceID (4 RU)
      - Set its "until" (utime) attribute to the event time (etime) of the incoming DeviceState
      - It is possible that a previous DeviceState for the deviceID does not exist

    - Point-read on **ProducerDevices** (1 RU)
    - Create/update the **ProducerDevices** document as necessary (5 RU)

    - Point-read on **DeviceSingleton** (1 RU)
    - Create/update the **DeviceSingleton** document as necessary (5 RU)

    - Point-read on each **DeviceAttribute** in the DeviceState event (1 RU x n)
    - Create each **DeviceAttribute** document as necessary (5 RU x n)
    - Assume that n is 3; three attributes

## Ingestion Costs

  - DeviceState Ingestion cost range:
    - Typical Minimum Case:
      - 5 (ingest DS) + 
      - 9 (query and update previous DS) +
      - 1 (point-read PD) + 
      - 1 (point-read D1) + 
      - 3 (point-read 3 attrs)
      - Total RU: 19
    - Update PD, D1, and Attrs:
      - 5 (ingest DS) + 
      - 9 (query and update previous DS) +
      - 6 (point-read and update PD) + 
      - 6 (point-read and update D1) + 
      - 6 (point-read update 3 attrs)
      - Total RU: 32

## Vertices/Entities in Cosmos DB

- **DeviceSingleton, (D1)**
  - Represents a universally unique device across all producers
  - did (deviceID) is a string
  - attrs: id, label, firstEventEpoch

- **ProducerDevices, (PD)** 
  - Represents a unique device at a producer
  - did (deviceID) is a string
  - pid (producerID) is a string
  - attrs: did, pid, extId

- **DeviceState (DS)**
  - Represents a streamed event from a device at a producer
  - has a current document and historical documents
  - each has a "since" and "until" timestamp (etime and utime)
    - only one is "current" for a given device
  - base attrs: did, pid, extId
  - other attrs: os, build, mac, ser, ip, etc
  - typical size 500b to 2kb, example below is ~600

```
  Example Document
  {
      "id": "3e113135-3777-427f-87ff-98bc466e88cb",
      "pk": "8cf5c21f-8a7d-4aa8-8d5b-5a9be896b3cd",
      "dt": "DS",

      "did": "8cf5c21f-8a7d-4aa8-8d5b-5a9be896b3cd",
      "pid": "hunt, combs and mcmahon",
      "extId": "426dd850-32f1-4a6e-88ff-3c100898b457",
      "ser": "90310",
      "cid": "712681",
      "host": "db-92",
      "mac": "ae591184-87ae-4431-b551-e1923d1fdaca",
      "build": 677173,
      "etime": 1739733895.2150435,
      "utime": -1

      "_rid": "8+kcAMsoK1NOAAAAAAAAAA==",
      "_self": "dbs/8+kcAA==/colls/8+kcAMsoK1M=/docs/8+kcAMsoK1NOAAAAAAAAAA==/",
      "_etag": "\"95000fe5-0000-0100-0000-67b23b880000\"",
      "_attachments": "attachments/",
      "_ts": 1739733896
  }
```

- **DeviceAttributes (DA)**
  - These are in two types, strong or weak, and have a value
    - Strong: deviceID, serialNum, computerID, hostname 
    - Weak: osName, ipAddress, macAddress, phoneNum, emailAddr, appUser, buildId
  - attrs: name, value, deviceID


Thus there is a hierarchical structure from **DeviceSingleton --> ProducerDevices --> DeviceState**.



## Cosmos DB Implementation Notes

### Cosmos DB Attribute Names

- Use short attribute names to save space
  - did instead of deviceID
  - pid instead of producerID
  - ser instead of serialNum
  - pk instead of partitionKey
  - dt instead of documentType
  - etime = the epoch time of the DeviceState event
  - utime = the "until time" of the DeviceState event.  Initially -1, but set to the etime of the newer event.

The _id, _etag, and _ts attributes are computed and set by Cosmos DB.

### Cosmos DB Containers

In "design 1" all vertex types are in in one container.

| Name             | Partition Key | DocType | PK Format   | Id Format   | Document Size |
| ---------------- | ------------- | ------- | ----------- | ----------- | ------------- |
| DeviceSingletons | /pk           | D1      | did         | D1-did      | 1K            |
| ProducerDevices  | /pk           | PD      | pid-did     | pid-did     | 1K            | 
| DeviceState      | /pk           | DS      | did         | uuid        | 1K            |
| DeviceAttributes | /pk           | DA      | a-attr-name | a-attr-name | 1K            |

### Queries and Point-Reads

- D1 point-reads are enabled by computing the ID and PK for a DeviceState event
- D point-reads are enabled by computing the ID and PK for a DeviceState event
- DA point-reads are enabled by computing the ID and PK for the attributes in a DeviceState event
- DS Queries - partition-key queries, aided by a composite index

DeviceState events are unique, therefore the uuid ID values

### Indexes

- Composite Index on DocType and PK
- Composite Index on did, etime, and utime.  To find the previously latest DeviceState event

#### Alternative Design

Container per document type

---

## Questions

- How unique are deviceIDs?  Possible "value space collisions".
- Should DeviceAttributes be associated to a specific Device or ProducerDevice or DeviceSingleton?
  - Or should each DeviceAttribute just have a name and value?
- What are the other queries, other than in the above ingestion flow?
