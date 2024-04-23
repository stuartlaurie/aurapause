# aurapause
Script using Neo4j Aura API to list instances and pause them

## Usage

Generate Neo4j Aura credentials following these [instructions in Neo4j documentation](https://neo4j.com/docs/aura/platform/api/authentication/#_creating_credentials)


### Generate Report

If you run the script and provide credentials file saved from above steps you will get a list of databases and their status

```
python3 aurapause.py -c auracreds.txt
```

This will generate output similar to the following

```
  tenant_id   name        id   status memory storage cloud_provider        region
1   tenant1  test0  54b2eda9  running   24GB    48GB            gcp   us-central1
2   tenant1  test1  7af24124  running    8GB    16GB            gcp   us-central1
4   tenant1  test2  e27e5959  running    8GB    16GB            gcp   us-central1
0   tenant1  test3  81381681   paused    NaN     NaN            gcp   us-central1
3   tenant1  test4  882231c2   paused    NaN     NaN            gcp   us-central1
5   tenant2  test5  03666a67   paused    NaN     NaN            gcp  europe-west1
```

You can also specify specific tenant id to limit to only databases in that tenant

```
python3 aurapause.py -c auracreds.txt -t tenant2
```

will filter to specified tenant


```
  tenant_id   name        id  status memory storage cloud_provider        region
0   tenant2  test5  03666a67  paused    NaN     NaN            gcp  europe-west1
```

### Pausing databases

There are 3 options to pause databases, either specify ALL or a list of database ids

#### Pausing specific running databases

```
python3 aurapause.py -c auracreds.txt -p database1,database2
```

#### Pausing all running databases

Attempt to pause all running instances:

```
python3 aurapause.py -c auracreds.txt -p ALL
```

This can also be filtered by tenant 

```
python3 aurapause.py -c auracreds.txt -t tenant2 -p ALL
```

If you want to exclude certain databases you can use the additional -e flag with a list of databases

```
python3 aurapause.py -c auracreds.txt -p ALL -e database1,database2
```

