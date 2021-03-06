# -*- coding: utf-8 -*-
# Description: Edge log netdata python.d module

import json
from base import SimpleService
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
from socket import error
from logging import getLogger

logger = getLogger(__name__)

priority = 60000
retries = 60
update_every = 10

ORDER = [
    'queues',
    'workers',
    'problem_docs',
    'process_documents',
    'timeshift'
]
CHARTS = {
    'process_documents': {
        'options': [None, 'Processing', 'documents', 'Processing',
                    '', 'line'],
        'lines': [
            ['save_documents', 'saved', 'absolute', 1, 1],
            ['update_documents', 'updated', 'absolute', 1, 1],
            ['skiped', 'skiped', 'absolute', 1, 1],
            ['droped', 'droped', 'absolute', 1, 1],
            ['add_to_resource_items_queue', 'add to queue', 'absolute', 1, 1]
        ]
    },
    'workers': {
        'options': [None, 'Threads', 'threads', 'Threads', '', 'line'],
        'lines': [
            ['workers_count', 'main', 'absolute', 1, 1],
            ['retry_workers_count', 'retry', 'absolute', 1, 1],
            ['filter_workers_count', 'fill', 'absolute', 1, 1]
        ]
    },
    'problem_docs': {
        'options': [None, 'Documents', 'documents', 'Documents', '', 'line'],
        'lines': [
            ['not_actual_docs_count', 'not actual', 'absolute', 1, 1],
            ['not_found_count', 'not found', 'absolute', 1, 1],
            ['add_to_retry', 'add to retry', 'absolute', 1, 1]
        ]
    },
    'queues': {
        'options': [None, 'Queue', 'items', 'Queues', '', 'line'],
        'lines': [
            ['resource_items_queue_size', 'main queue', 'absolute', 1, 1],
            ['retry_resource_items_queue_size', 'retry queue', 'absolute', 1, 1]
        ]
    },
    'timeshift': {
        'options': [None, 'Delay', 'seconds', 'Time delay', '', 'line'],
        'lines': [
            ['timeshift', 'delay', 'absolute', 1, 1]
        ]
    }
}


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.couch_url = configuration['couch_url']
        self.resource = configuration['resource']
        if len(self.couch_url) == 0:
            raise Exception('Invalid couch_url')
        self.order = ORDER
        self.definitions = CHARTS
        self.data = {
            'save_documents': 0,
            'update_documents': 0,
            'workers_count': 0,
            'resource_items_queue_size': 0,
            'free_api_clients': 0,
            'exceptions_count': 0,
            'add_to_resource_items_queue': 0,
            'skiped': 0,
            'droped': 0,
            'retry_resource_items_queue_size': 0,
            'filter_workers_count': 0,
            'not_found_count': 0,
            'add_to_retry': 0,
            'retry_workers_count': 0,
            'not_actual_docs_count': 0,
            'timeshift': 0
        }
        self.last_time = ''

    def _get_data(self):
        for key in self.data.keys():
            self.data[key] = 0
        try:
            response = urllib2.urlopen(self.couch_url + '/' +
                                       self.resource).read()
            doc = json.loads(response)
            if doc['time'] == self.last_time:
                return self.data
            self.last_time = doc['time']
            for key in self.data.keys():
                self.data[key] = doc.get(key, 0)
        except (Exception, error):
            return self.data
        return self.data
