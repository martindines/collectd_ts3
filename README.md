# collectd_ts3
Teamspeak 3 statistics collection for collectd

## Dependencies

[python-ts3 by Nikdoof](https://github.com/nikdoof/python-ts3)

`pip install git+https://github.com/nikdoof/python-ts3/#egg=python-ts3`


## Usage

### with collectd service

Configure collectd to execute plugin using the following configuration (in `/etc/collectd/collectd.conf`)
```
LoadPlugin python
<Plugin python>
  ModulePath "SCRIPT_PATH"
  LogTraces true
  Interactive false
  Import collectd_ts3
  <Module collectd_ts3>
      Host "TEAMSPEAK3_SERVER_QUERY_HOST"
      Port "TEAMSPEAK3_SERVER_QUERY_PORT"
      Username TEAMSPEAK3_SERVER_QUERY_USERNAME"
      Password "TEAMSPEAK3_SERVER_QUERY_PASSWORD"
  </Module>
</Plugin>
```

|Placeholder|Value|
|---|---|
|SCRIPT_PATH|Path to collectd_ts3.py|
|TEAMSPEAK3_SERVER_QUERY_HOST|Teamspeak 3 Server Query Host (default 127.0.0.1)|
|TEAMSPEAK3_SERVER_QUERY_PORT|Teamspeak 3 Server Query Port (default 10011)|
|TEAMSPEAK3_SERVER_QUERY_USERNAME|Teamspeak 3 Server Query Username (default serveradmin)|
|TEAMSPEAK3_SERVER_QUERY_PASSWORD|Teamspeak 3 Server Query Password|


### without collectd service

`$ python collect_ts3.py serveradmin_password`