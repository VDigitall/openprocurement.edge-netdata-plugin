# -*- coding: utf-8 -*-
# Description: Edge log netdata python.d module

from kadabra import Kadabra
from base import SimpleService
from logging import getLogger
from iso8601 import parse_date
from datetime import datetime
from pytz import timezone

TZ = timezone('Europe/Kiev')

logger = getLogger(__name__)

priority = 60000
retries = 60
update_every = 1

ORDER = [
    'requests',
    'durations',
    'documents',
    'queue',
    'last_response'
]

CHARTS = {
    'requests': {
        'options': [None, 'Requests count', 'requests', 'Requests count', '', 'line'],
        'lines': [
            ['forward_success_requests', 'fwd. success', 'absolute', 1, 1],
            ['backward_success_requests', 'bwd. success', 'absolute', 1, 1],
            ['forward_precondition_failed', 'fwd. precondition', 'absolute', 1, 1],
            ['backward_precondition_failed', 'bwd. precondition', 'absolute', 1, 1],
            ['forward_connection_error', 'fwd. connection', 'absolute', 1, 1],
            ['backward_connection_error', 'bwd. connection', 'absolute', 1, 1],
            ['forward_request_failed', 'fwd. failed', 'absolute', 1, 1],
            ['backward_request_failed', 'bwd. failed', 'absolute', 1, 1],
            ['forward_resource_not_found', 'fwd. not found', 'absolute', 1, 1],
            ['backward_resource_not_found', 'bwd. not found', 'absolute', 1, 1],
            ['forward_exception', 'fwd. exception', 'absolute', 1, 1],
            ['backward_exception', 'bwd. exception', 'absolute', 1, 1]
        ]
    },
    'durations': {
        'options': [None, 'Request processing', 'miliseconds', 'Request processing', '', 'line'],
        'lines': [
            ['forward_process_request', 'forward', 'abosulte', 1, 1],
            ['backward_process_request', 'backward', 'abosulte', 1, 1]
        ]
    },
    'documents': {
        'options': [None, 'Received documents', 'documents', 'Received documents', '', 'line'],
        'lines': [
            ['forward_resource_count', 'forward', 'absolute', 1, 1],
            ['backward_resource_count', 'backward', 'absolute', 1, 1]
        ]
    },
    'queue': {
        'options': [None, 'Queue', 'documents', 'Queue', '', 'line'],
        'lines': [
            ['queue_size', 'documents', 'absolute', 1, 1]
        ]
    },
    'last_response': {
        'options': [None, 'Last response', 'seconds', 'Last response', '', 'line'],
        'lines': [
            ['forward_last_response', 'forward', 'absolute', 1, 1],
            ['backward_last_response', 'backward', 'absolute', 1, 1]
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
                'queue_key': '{}_{}_feeder_metrics'.format(self.metrics_key,
                                                           self.resource)
            }
        }
        self.kadabra_client = Kadabra(kadabra_args)
        self.order = ORDER
        self.definitions = CHARTS
        self.data = {
            'forward_success_requests': 0,
            'backward_success_requests': 0,
            'forward_precondition_failed': 0,
            'backward_precondition_failed': 0,
            'forward_connection_error': 0,
            'backward_connection_error': 0,
            'forward_request_failed': 0,
            'backward_request_failed': 0,
            'forward_resource_not_found': 0,
            'backward_resource_not_found': 0,
            'forward_exception': 0,
            'backward_exception': 0,
            'forward_process_request': 0,
            'backward_process_request': 0,
            'forward_resource_count': 0,
            'backward_resource_count': 0,
            'forward_last_response': 0,
            'backward_last_response': 0,
            'queue_size': 0
        }
        self.last_time = ''
        self.same_data_count = 0
        self.forward_last_response = datetime.now(TZ).isoformat()
        self.backward_last_response = datetime.now(TZ).isoformat()

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
                        if m['name'] == 'backward_last_response':
                            self.backward_last_response = m['value']
                        if m['name'] == 'forward_last_response':
                            self.forward_last_response = m['value']

            self.data['forward_last_response'] = (
                datetime.now(TZ) - parse_date(self.forward_last_response)).total_seconds()
            if self.data.get('backward_finished', False):
                self.data['backward_last_response'] = 0
            else:
                self.data['backward_last_response'] = (
                    datetime.now(TZ) - parse_date(self.backward_last_response)).total_seconds()

            backward_success_requests = self.data.get('backward_success_requests', 0)
            forward_success_requests = self.data.get('forward_success_requests', 0)

            if forward_success_requests > 1:
                self.data['forward_process_request'] = round(
                    float((self.data['forward_process_request'] /
                           forward_success_requests)), 3) * 1000
            else:
                self.data['forward_process_request'] =\
                    self.data['forward_process_request'] * 1000
            if backward_success_requests > 1:
                self.data['fbackard_process_request'] = round(
                    float((self.data['backward_process_request'] /
                           backward_success_requests)), 3) * 1000
            else:
                self.data['backward_process_request'] =\
                    self.data['backward_process_request'] * 1000
        return self.data

    def check(self):
        try:
            self._get_data()
        except:
            return False
        return True
