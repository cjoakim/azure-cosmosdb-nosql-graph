# azure-cosmosdb-nosql-graph : devices graph example

In this example the dataset is streaming in nature and created dynamically,
and the related nodes of the graph are also created/updated dynamically.

The implementation code is in **main_devices.py** (this is a work-in-progress)

## Ingestion Flow

- **DeviceStateEvents (DE)** documents are ingested (5 RU) in an IoT manner:
  - instead of using an "until" time, these can be queried by their event time

  - Then execute the following logic to process the new DeviceStateEvent documents
    - This logic could be implemented in Azure Function listening to the ingestion container

    - Read and update the DeviceStateCurrent document (1 + 5 RU)
      - Calculate the ID/PK from the DeviceStateEvent so as to do a point-read
      - Overlay the application attributes, but retain the Cosmos DB system generated attributes
        - for example, _etag

    - Point-read on **ProducerDevices** (1 RU)
    - Create/update the **ProducerDevices** document as necessary (5 RU)

    - Point-read on **DeviceSingleton** (1 RU)
    - Create/update the **DeviceSingleton** document as necessary (5 RU)

    - Point-read on each **DeviceAttribute** in the DeviceState event (1 RU x n)
    - Create/update each **DeviceAttribute** document as necessary (5 RU x n)
    - Assume that n is 3; three attributes

## Ingestion Costs

  - DeviceState Ingestion cost range:
    - Typical Minimum Case:
      - 5 (ingest DE) + 
      - 6 (point-read and update previous DC) +
      - 1 (point-read PD) + 
      - 1 (point-read D1) + 
      - 3 (point-read 3 attrs)
      - Total RU: 16
    - Update PD, D1, and Attrs:
      - 5 (ingest DE) + 
      - 6 (point-read and update previous DC) +
      - 6 (point-read and update PD) + 
      - 6 (point-read and update D1) + 
      - 6 (point-read update 3 attrs)
      - Total RU: 29

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

- **DeviceStateEvents (DE)**
  - Represents a streamed event from a device at a producer
  - each has an event time (etime) that can be used in historical queries
  - base attrs: did, pid, extId
  - other attrs: os, build, mac, ser, ip, etc
  - typical size 500b to 2kb, example below is ~600

```
  Example Document
  {
      "id": "3e113135-3777-427f-87ff-98bc466e88cb",
      "pk": "8cf5c21f-8a7d-4aa8-8d5b-5a9be896b3cd",
      "did": "8cf5c21f-8a7d-4aa8-8d5b-5a9be896b3cd",
      "pid": "hunter",
      "extId": "426dd850-32f1-4a6e-88ff-3c100898b457",
      "ser": "90310",
      "cid": "712681",
      "host": "db-92",
      "mac": "ae591184-87ae-4431-b551-e1923d1fdaca",
      "build": 677173,
      "etime": 1739733895.2150435,

      "_rid": "8+kcAMsoK1NOAAAAAAAAAA==",
      "_self": "dbs/8+kcAA==/colls/8+kcAMsoK1M=/docs/8+kcAMsoK1NOAAAAAAAAAA==/",
      "_etag": "\"95000fe5-0000-0100-0000-67b23b880000\"",
      "_attachments": "attachments/",
      "_ts": 1739733896
  }
```

- **DeviceStateCurrent (DC)**
  - Represents the current state of a device at a producer
  - These documents are updated/overlaid as DeviceStateEvent documents arrive 
  - pid-did is the ID and PK, which can be computed from the DeviceStateEvent

```
  Example Document
  {
      "id": "hunter-8cf5c21f-8a7d-4aa8-8d5b-5a9be896b3cd",
      "pk": "hunter-8cf5c21f-8a7d-4aa8-8d5b-5a9be896b3cd",
      "did": "8cf5c21f-8a7d-4aa8-8d5b-5a9be896b3cd",
      "pid": "hunter",
      "extId": "426dd850-32f1-4a6e-88ff-3c100898b457",
      "ser": "90310",
      "cid": "712681",
      "host": "db-92",
      "mac": "ae591184-87ae-4431-b551-e1923d1fdaca",
      "build": 677173,
      "etime": 1739733895.2150435,

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


Thus there is a hierarchical structure:  
**DeviceSingleton --> ProducerDevices --> DeviceStateCurrent --> DeviceStateEvents**.


## Cosmos DB Implementation Notes

### Cosmos DB Attribute Names

- Use short attribute names to save space on billions of documents
  - did instead of deviceID
  - pid instead of producerID
  - ser instead of serialNum
  - cid instead of computerID
  - pk instead of partitionKey
  - dt instead of documentType
  - etime = the epoch time of the DeviceState event

The _id, _etag, and _ts attributes are computed and set by Cosmos DB.

### Cosmos DB Containers

In "design 1" has these five containers.

| Name               | Partition Key | Abbreviation | PK Format   | Id Format   | Document Size |
| ------------------ | ------------- | ------------ | ----------- | ----------- | ------------- |
| DeviceSingletons   | /pk           | D1           | did         | did         | 1K            |
| ProducerDevices    | /pk           | PD           | pid-did     | pid-did     | 1K            | 
| DeviceStateEvents  | /pk           | DE           | did         | uuid        | 1K            |
| DeviceStateCurrent | /pk           | DC           | pid-did     | pid-did     | 1K            |
| DeviceAttributes   | /pk           | DA           | a-attr-name | a-attr-name | 1K            |

The DeviceStateEvents container will be the largest, to store the historical events.

### Queries and Point-Reads

- D1 point-reads are enabled by computing the ID and PK for a DeviceStateEvent
- D  point-reads are enabled by computing the ID and PK for a DeviceStateEvent
- DC point-reads are enabled by computing the ID and PK for a DeviceStateCurrent 
- DA point-reads are enabled by computing the ID and PK for the attributes in a DeviceStateEvent
- DE Queries - these partition-key queries are aided by a composite index

DeviceStateEvents are unique, therefore they use uuid ID values

#### Get the ten most recent DeviceStateEvents (DE) for a device

```
  select * from c where c.pk = 'ddd' order by c.etime offset 0 limit 10
  - or -
  select * from c where c.pk = 'ddd' and c.pid = 'ppp' order by c.etime offset 0 limit 10
```

### Indexes

- DeviceStateEvents
  - Composite Index on pk, etime
  - Composite Index on pk, pid, etime

---

## Questions

- How unique are deviceIDs?  Possible "value space collisions".

- Should DeviceAttributes be associated to a specific Device or ProducerDevice or DeviceSingleton?
  - Or should each DeviceAttribute just have a name and value?

- What are the other queries or traversals are required?

- Use-cases for DeviceSingletons and ProducerDevices>
  - These could potentially be produced by queries rather than instantiated as documents.
