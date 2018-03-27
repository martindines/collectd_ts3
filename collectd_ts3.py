import ts3

READ_INTERVAL_IN_SECONDS = 10

METRICS_TO_READ = [
    'virtualserver_port',
    'virtualserver_id',
    'virtualserver_status',
    'virtualserver_voiceclientsonline',
    'virtualserver_queryclientsonline',
    'virtualserver_maxclients',
    'virtualserver_channelsonline',
    'virtualserver_reserved_slots',
    'virtualserver_uptime',
    'virtualserver_total_bytes_uploaded',
    'virtualserver_total_bytes_downloaded',
    'virtualserver_total_packetloss_control',
    'virtualserver_total_packetloss_speech',
    'virtualserver_total_packetloss_keepalive',
    'virtualserver_total_packetloss_total',
    'virtualserver_total_ping',
    'connection_bytes_sent_total',
    'connection_bytes_received_total',
    'connection_bytes_sent_speech',
    'connection_bytes_received_speech',
    'connection_bytes_sent_control',
    'connection_bytes_received_control',
    'connection_bytes_sent_keepalive',
    'connection_bytes_received_keepalive',
    'connection_packets_sent_total',
    'connection_packets_received_total',
    'connection_packets_sent_speech',
    'connection_packets_received_speech',
    'connection_packets_sent_control',
    'connection_packets_received_control',
    'connection_packets_sent_keepalive',
    'connection_packets_received_keepalive',
    'connection_bandwidth_sent_last_second_total',
    'connection_bandwidth_received_last_second_total'
]

# collectd is imported via Collectd Plugin interface. Mock CollectD and associated classes to allow local testing
# https://collectd.org/documentation/manpages/collectd-python.5.shtml
try:
    import collectd
except:
    import sys
    import time
    from pprint import pprint

    class Config:
        _key = ''
        _values = []
        _children = []

        def __init__(self, key, value, children=None):
            self._key = key
            self._values = [value]
            self._children = [] if children is None else children

        @property
        def key(self):
            return self._key

        @property
        def values(self):
            return self._values

        @property
        def children(self):
            return self._children

    class CollectD:
        def register_config(self, callback):
            callback(
                Config('', '', [
                    Config('Host', '127.0.0.1'),
                    Config('Port', '10011'),
                    Config('Username', 'serveradmin'),
                    Config('Password', sys.argv[1])
                ])
            )

        def register_init(self, callback):
            callback()

        def register_read(self, callback, interval=1):
            for i in range(0, 15):
                callback()
                time.sleep(interval)

        def register_shutdown(self, callback):
            callback()

        def debug(self, message):
            sys.stdout.write(message)
            sys.stdout.flush()

        def error(self, message):
            sys.stdout.write(message)
            sys.stdout.flush()

        def warning(self, message):
            sys.stdout.write(message)
            sys.stdout.flush()

        def notice(self, message):
            sys.stdout.write(message)
            sys.stdout.flush()

        def info(self, message):
            sys.stdout.write(message)
            sys.stdout.flush()

        class Values:
            def __init__(self, plugin, plugin_instance, type, type_instance):
                self.plugin = plugin
                self.plugin_instance = plugin_instance
                self.type = type
                self.type_instance = type_instance

            def dispatch(self, values, time):
                collectd.debug('\n' + self.type + ' ' + self.type_instance + ' [' + ', '.join(map(str, values)) + ']')

    collectd = CollectD()


class Teamspeak3MetricService:
    def __init__(self, metrics, collectionService):
        self.metrics = metrics
        self.serverQueryService = None
        self.collectionService = collectionService

        self.pluginName = 'ts3'
        self.host = '127.0.0.1'
        self.port = '10011'
        self.username = 'serveradmin'
        self.password = ''

    def config(self, config):
        for node in config.children:
            key = node.key.lower()
            value = node.values[0]

            if key in ['host', 'port', 'username', 'password']:
                setattr(self, key, value)
            else:
                self.collectionService.info("{} plugin: Unknown config key '{}'".format(self.pluginName, key))

    def connect(self):
        self.serverQueryService = ts3.TS3Server(self.host, self.port)
        isLoginSuccessful = self.serverQueryService.login(self.username, self.password)

        if not isLoginSuccessful:
            self.collectionService.error("Login failed")
            exit(1)

    def read(self):
        serverlistResponse = self.serverQueryService.serverlist()
        if not serverlistResponse.response['msg'] == 'ok':
            self.collectionService.error("Error retrieving serverlist")
            exit(1)

        servers = serverlistResponse.data

        for server in servers:
            virtualserver_id = server.get('virtualserver_id')
            self.serverQueryService.use(virtualserver_id)

            serverinfoResponse = self.serverQueryService.send_command('serverinfo')
            if not serverinfoResponse.response['msg'] == 'ok':
                self.collectionService.error("Error retrieving serverinfo")
                exit(1)

            serverinfo = serverinfoResponse.data[0]

            for metric in self.metrics:
                if metric == 'virtualserver_voiceclientsonline':
                    metricValue = int(serverinfo.get('virtualserver_clientsonline')) - int(
                        serverinfo.get('virtualserver_queryclientsonline'))
                elif metric == 'virtualserver_status':
                    metricValue = 1 if serverinfo.get('virtualserver_status') == 'online' else 2
                else:
                    metricValue = serverinfo.get(metric)

                Value = self.collectionService.Values(
                    plugin=self.pluginName,
                    plugin_instance=virtualserver_id,
                    type='gauge',
                    type_instance=metric
                )
                Value.dispatch(values=[metricValue], time=0)

    def disconnect(self):
        self.serverQueryService = None


ts3Service = Teamspeak3MetricService(METRICS_TO_READ, collectd)

collectd.register_config(ts3Service.config)
collectd.register_init(ts3Service.connect)
collectd.register_read(ts3Service.read, READ_INTERVAL_IN_SECONDS)
collectd.register_shutdown(ts3Service.disconnect)
