#!/bin/bash
echo "Optimizing settings for UDP performances for enp2s0f1"
ifconfig enp0s31f6: txqueuelen 100000
ethtool -G enp0s31f6: rx 2047
sysctl -w net.core.netdev_max_backlog=64000
sysctl -w net.core.rmem_max=1677721600
sysctl -w net.core.wmem_max=1677721600
sysctl -w net.core.rmem_default=1677721600
sysctl -w net.core.wmem_default=1677721600
echo "Done"
sleep 3

