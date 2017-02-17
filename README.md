# openprocurement.edge-netdata-plugin

Plugin visualize edge activity

### Requirements
* openprocurement.edge v1.0.0.dev5
* openprocurement_client v2.0b5

## How to use

Put file to `/usr/libexec/netdata/python.d/`

### Configuration example
Put entry to file `/etc/netdata/python.d/edge.conf`.
```
resource_name:
  resource: 'resource_name'
  couch_url: 'http://IP:PORT/logs_db_name'
```
