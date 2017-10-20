# Cryptsetup SSH unlocker

Utility for unattended remote unlock of LUKS encrypted LVM/root disk partition using SSH and cryptsetup.
Periodically polls defined servers for open SSH port, then tries to unlock the server using cryptsetup.
Requires `dropbear` or any other SSH server which could be run from initial ramdisk.

## Is it secure?
This utility should run from independent server (possibly VPS), thus separating all passphrases and SSH
keys from the servers being unlocked. Server authentication is performed during the connection process
against a `known_hosts` file.

Server will be unlocked only when SSH is available on the specified IP address and port and if
the fingerprint in the `known_hosts` file matches. You should always use IP addresses in the
host configuration rather than domain names to limit the attack possibility after
compromising a DNS server.

Please also note that the server host keys are always stored on an unencrypted partition,
so this script won't protect you against an attack with both physical access to the server and the IP address used for unlocking.
To further limit the attack possibility, you should use monitoring and possibly disable SSH unlocker in the case of unexpected behavior.

Other possible security implications and solutions how to prevent them are beyond the scope of this documentation.

## Requirements

Python 3.5 and higher is required for the installation, because the async/await syntax is used.

## Installation and running

```bash
$ pip install ssh-unlocker
```

You should be able to run the utility by using `ssh-unlocker`. Run `ssh-unlocker -h` for the list of available options.

```bash
$ ssh-unlocker -h
usage: ssh-unlocker [-h] [-c CONFIG] [-v] [--logfile LOGFILE]

Cryptsetup SSH server unlocker. This utility is repeatedly polling configured
servers and tries to unlock the encrypted root partition using cryptsetup once
the SSH connection is available.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to config file - defaults to config.ini
  -v, --verbose         Increase verbosity level to DEBUG
  --logfile LOGFILE     Path to log file. By default the log messages are
                        printed to stderr
```

## Configuration

By default the configuration is read from `config.ini` configuration file, but this can be specified as a parameter.
Server configuration should be specified using respective `[server-identifier]` sections.
Unspecified parameters are inherited from the `[DEFAULT]` section.

### Configuration attributes

- `host` – SSH server domain or IP address
- `port` – SSH server port. It's recommended to run the dropbear SSH daemon for unlocking on a port that is closed on a
running (unlocked) server. This way the connection will be closed before attempting SSH authentication and you'll avoid spamming logs.
- `username` – username of a remote user
- `ssh_private_key` – private SSH key used for authentication (password authentication is not supported for security reasons and should be avoided)
- `ssh_private_key_passphrase` – passphrase for encrypted SSH private key (unused when blank)
- `cryptsetup_passphrase` – passphrase for unlocking encrypted disk using cryptsetup 

<br>

- `known_hosts` – file with DSA host keys of SSH servers (used for server authentication and MITM attack prevention). This file cannot be empty - you should always provide server keys beforehand for security reasons
- `connect_timeout` – connection timeout for TCP handshake during port scanning
- `ssh_connect_timeout` – timeout for connection and SSH auth
- `sleep_interval` – time between port scanning checks

Example configuration file:
```ini
; [server-identifier]
; host = 127.0.0.1
; port = 22
; username = default
; cryptsetup_passphrase = securePassword13!

[DEFAULT]
connect_timeout = 5
ssh_connect_timeout = 5
sleep_interval = 2

port = 22
username = root
ssh_private_key = unlock_key.rsa
ssh_private_key_passphrase =
known_hosts = known_hosts
```

# Starting automatically at system startup

In most scenarios ssh-unlocker should probably start automatically at system startup. You should also make sure, that the unlocker would be restarted in case of any unexpected exceptions. This can be done by a simple shell script or you can use one of more sophisticated solutions described below.

## Systemd config

Systemd is already pre-installed in most modern distribution, so using it should be only a matter of adding new configuration file. 

Example configuration:
```ini
[Unit]
Description=Utility for unattended remote unlock of LUKS encrypted LVM
After=network.target

[Service]
ExecStart=/root/ssh-unlocker/venv/bin/ssh-unlocker
WorkingDirectory=/root/ssh-unlocker/
Restart=always
TimeoutStopSec=60

# try to restart the service indefinitely (RestartSec * StartLimitBurst > StartLimitIntervalSec)
RestartSec=1
StartLimitBurst=20
StartLimitIntervalSec=1

[Install]
WantedBy=multi-user.target
```

## Supervisor config
If you're used to [Supervisor](http://supervisord.org/) or you don't want to use Systemd for some reason, here is a sample configuration file:

```ini
[program:cryptsetup-ssh-unlocker]
command=/root/ssh-unlocker/venv/bin/ssh-unlocker --logfile /var/log/ssh-unlocker
directory=/root/ssh-unlocker/

autostart=true
autorestart=true
startsecs=5
stopwaitsecs=60
```

# Server configuration
In order for this utility to work correctly, SSH daemon has to be installed into initial ramdisk.
There are some tutorials, how to do that, such as [this one for Ubuntu](https://stinkyparkia.wordpress.com/2014/10/14/remote-unlocking-luks-encrypted-lvm-using-dropbear-ssh-in-ubuntu-server-14-04-1-with-static-ipst/).

## Minimal Ubuntu installation

### Install dropbear and update configuration

```bash
$ apt update
$ apt install dropbear
```

Edit `/etc/initramfs-tools/initramfs.conf` and add or replace the following configuration:
```ini
DEVICE=eth0
IP=192.168.1.100::192.168.1.1:255.255.255.0::eth0:off
DROPBEAR_OPTIONS="-p 1022"
```

The format for `IP` is the following: `[host ip]::[gateway ip]:[netmask]:[hostname]::[device]:[autoconf]`
(please notice double colons `::`). SSH port is specified using `DROPBEAR_OPTIONS`. I strongly recommend using another port than `22`.

Update `/etc/default/dropbear` and 
change `NO_START=1` to `NO_START=0`
```ini
# disabled because OpenSSH is installed
# change to NO_START=0 to enable Dropbear
NO_START=0
```

`DROPBEAR_PORT` in the same configuration file is ignored in initial ramdisk phase and has to be specified in `initramfs.conf`.

### Add SSH keys

Add all public keys you would like to use for authentication during the unlock phase to `/etc/initramfs-tools/root/.ssh/authorized_keys`.
Create the file and/or folder(s) if they don't exist already.

Don't forget to add public key of the RSA key that will be used by this utility.
You can easily generate new RSA keypair by running `ssh-keygen -t rsa -b 4096`.

### [optional] Replace original host keys

```bash
$ dropbearkey -t rsa -f /etc/dropbear/dropbear_rsa_host_key
$ dropbearkey -t dss -f /etc/dropbear/dropbear_dss_host_key
```

### Update ramdisk

```bash
$ sudo update-initramfs -u
```

# License
This software is licensed under MIT license.
