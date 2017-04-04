# -*- coding: utf-8 -*-
# Description: Edge log netdata python.d module

from base import SimpleService
from kadabra import Kadabra

priority = 60000
retries = 60
update_every = 10

ORDER = [
    'queues',
    'workers',
    'clients',
    'requests',
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
    'clients': {
        'options': [None, 'Clients', 'clients', 'Clients', '', 'line'],
        'lines': [['api_clients_count', 'clients', 'absolute', 1, 1]]
    },
    'requests': {
        'options': [None, 'Request durations', 'miliseconds', 'Request durations', '', 'area'],
        'lines': [
            ['max_avg_request_duration', 'max avg.', 'absolute', 1, 1],
            ['avg_request_duration', 'avg.', 'absolute', 1, 1],
            ['request_dev', 'avg. + stdev', 'absolute', 1, 1],
            ['min_avg_request_duration', 'min avg.', 'absolute', 1, 1]
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
        self.metrics_key = configuration.get('metrics_key', None)
        self.resource = configuration.get('resource', None)
        if self.metrics_key is None or self.resource is None:
            raise Exception('Missed configuration.')
        kadabra_args = {
            'CLIENT_CHANNEL_ARGS': {
                'rewrite_metrics': True,
                'queue_key': '{}_{}_metrics'.format(self.metrics_key,
                                                    self.resource)
            }
        }
        self.kadabra_client = Kadabra(kadabra_args)
        self.order = ORDER
        self.definitions = CHARTS
        self.data = {
            'save_documents': 0,
            'update_documents': 0,
            'workers_count': 0,
            'resource_items_queue_size': 0,
            'api_clients_count': 0,
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
            'timeshift': 0,
            'avg_request_duration': 0,
            'request_dev': 0,
            'api_clients_count': 0,
            'min_avg_request_duration': 0,
            'max_avg_request_duration': 0
        }
        self.last_time = ''
        self.same_data_count = 0

    def _get_data(self):
        for key in self.data.keys():
            self.data[key] = 0
        try:
            metrics = self.kadabra_client.channel.receive()
        except:
            metrics = None
        if metrics:
            metrics = metrics.serialize()
            if self.last_time == metrics['serialized_at']:
                self.same_data_count += 1
            else:
                self.last_time = metrics['serialized_at']
                self.same_data_count = 0
            if self.same_data_count < 3:
                for k in ['timers', 'counters', 'dimensions']:
                    for m in metrics[k]:
                        self.data[m['name']] = m['value']
        return self.data

    def check(self):
        try:
            self._get_data()
        except:
            return False
        return True
