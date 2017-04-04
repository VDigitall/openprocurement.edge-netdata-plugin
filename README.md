# openprocurement.edge-netdata-plugin

Plugin visualize edge activity

### Support
* openprocurement.edge v1.0.0.dev6
* openprocurement_client v2.0b7

### Requirements
* kadabra
* iso8601

### How to install requirements to netdata python modules

`pip install --target /usr/libexec/netdata/python.d/python_modules/ -r requirements.txt`

## How to use

Put files to `/usr/libexec/netdata/python.d/`

### Configuration example
Put entry to file `/etc/netdata/python.d/edge.conf` and
                  `/etc/netdata/python.d/feeder_edge.conf`.
```
job_name:
  resource: 'tenders'
  metrics_key: 'edge'
```
