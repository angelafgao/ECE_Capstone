#!/usr/bin/expect -f

spawn "bluetoothctl"
expect "# "
send "discoverable on\r"
expect "Changing discoverable on succeeded"
send "power on\r"
expect "Chaning power on succeeded"
send "agent on\r"
expect "Agent registered"
send "scan on\r"
expect "Discovery started"
sleep 5
send "scan off\r"
expect "Discovery stopped"
send "pair 00:21:13:00:1A:EC\r"
expect "Attempting to pair with 00:21:13:00:1A:EC\r"
expect "Enter PIN code:"
send "1234\r"
expect "Pairing successful"
send "trust 00:21:13:00:1A:EC\r"
expect "Changing 00:21:13:00:1A:EC trust succeeded"

