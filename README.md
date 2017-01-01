# py-dhcp-relay
Python library acting as a DHCP Relay

# Requirements

- pydhcp
- click
- PyYAML


# Installation

```bash
pip install dhcp-relay
```

# Usage

Configuration file example:

```yaml
server:
  host: 172.17.19.7
  port: 67
client:
  host: 192.168.4.204
  port: 67
lease_time: 86400
listener_threads: 5
max_time: 5
ddos_rate: 30
log_file: /path/to/log/file
log_level: warning
log_datefmt_logfile: '%Y-%m-%d %H:%M:%S'
log_full: true
```

Start the program:

```bash
$ dhcp-relay -l error -c /path/to/config.yml
```

Command line options:

- `-c` or `--config-file`: path to the YAML configuration file. Default: `/etc/dhcp-relay/config.yml`
- `-s` or `--server`: server IP address
- `--server-port`: server port. Default: 67
- `--lease`: lease time requested, in seconds. Default: 86400 (24 hours)
- `--threads`: maximum number of listener threads. Default: 5
- `-d` or `--daemon` run in background
- `--timeout`: maximum wait time. Default: 5 seconds
- `--client-host`: hostname or IP address to be used to make the requests. Default: will use the loopback address of the machine
- `--client-port`: client port. Default: 67
- `-l` or `--log-level`: logging level. Default: warning
- `--log-file`: logging file. Default: /var/log/dhcp-relay.log
- `--log-full`: if will log complete details (including packet structure etc.). Default: False

**Note**: the CLI options will override the settings from the YAML configuration file.
