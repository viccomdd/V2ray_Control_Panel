#!/bin/bash
# Credits to v2ray project
# This script is written by Cocoa <0xbbc@0xbbc.com>
# And this script is based on https://toutyrater.github.io/app/tproxy.html, massive thanks
#
# Usage:
# sudo ./v2raytproxy.sh CIDR局域网网段 服务器IP 服务器端口 用户ID
#
# Example:
# sudo ./v2raytproxy.sh '10.0.1.0/24' '1.2.3.4' '12345' '12345678-90ab-cdef-1234-567890abcdef'

function deploy_iptables_rules {
    echo "[INFO] Deploying iptables rules"
    
    ip rule add fwmark 1 table 100
    ip route add local 0.0.0.0/0 dev lo table 100
    
    iptables -t mangle -N V2RAY
    iptables -t mangle -A V2RAY -d 127.0.0.1/32 -j RETURN
    iptables -t mangle -A V2RAY -d 224.0.0.0/4 -j RETURN
    iptables -t mangle -A V2RAY -d 255.255.255.255/32 -j RETURN
    
    # 直连局域网，避免 V2Ray 无法启动时无法连网关的 SSH
    iptables -t mangle -A V2RAY -d "$1" -p tcp -j RETURN
    # 直连局域网，53 端口除外, 因为要使用 V2Ray 的
    iptables -t mangle -A V2RAY -d "$1" -p udp ! --dport 53 -j RETURN
    # 给 UDP 打标记 1，转发至 12345 端口
    iptables -t mangle -A V2RAY -p udp -j TPROXY --on-port 12345 --tproxy-mark 1
    # 给 TCP 打标记 1，转发至 12345 端口
    iptables -t mangle -A V2RAY -p tcp -j TPROXY --on-port 12345 --tproxy-mark 1
    # 应用规则
    iptables -t mangle -A PREROUTING -j V2RAY
    
    iptables -t mangle -N V2RAY_MASK
    iptables -t mangle -A V2RAY_MASK -d 224.0.0.0/4 -j RETURN
    iptables -t mangle -A V2RAY_MASK -d 255.255.255.255/32 -j RETURN
    # 直连局域网
    iptables -t mangle -A V2RAY_MASK -d "$1" -p tcp -j RETURN
    # 直连局域网，53 端口除外, 因为要使用 V2Ray 的 DNS
    iptables -t mangle -A V2RAY_MASK -d "$1" -p udp ! --dport 53 -j RETURN
    # 直连 SO_MARK 为 0xff 的流量 (0xff 是 16 进制数，数值上等同与上面 V2Ray 配置的 255), 此规则目的是避免代理本机(网关)流量出现回环问题
    iptables -t mangle -A V2RAY_MASK -j RETURN -m mark --mark 0xff
    # 给 UDP 打标记,重路由
    iptables -t mangle -A V2RAY_MASK -p udp -j MARK --set-mark 1
    # 给 TCP 打标记，重路由
    iptables -t mangle -A V2RAY_MASK -p tcp -j MARK --set-mark 1
    # 应用规则
    iptables -t mangle -A OUTPUT -j V2RAY_MASK
}

function set_autorestoring_iptables_rules_service {
echo "[INFO] Adding systemd service for auto-restoring the added iptables rules"
cat <<EOF >/etc/systemd/system/v2ray-iptables.service
[Unit]
Description=Tproxy rule
After=network.target
Wants=network.target

[Service]

Type=oneshot
ExecStart=/sbin/ip rule add fwmark 1 table 100 ; /sbin/ip route add local 0.0.0.0/0 dev lo table 100 ; /sbin/iptables-restore /etc/iptables/rules.v4

[Install]
WantedBy=multi-user.target
EOF
systemctl enable v2ray-iptables
}

function dump_iptables_rules {
    echo "[INFO] Dumping added iptables rules to /etc/iptables/rules.v4"
    mkdir -p /etc/iptables && iptables-save > /etc/iptables/rules.v4
}

function generate_v2ray_config {
echo "[INFO] Generating v2ray config"
cat <<EOF >/etc/v2ray/config.json
{
    "inbounds": [
        {
            "tag":"transparent",
            "port": 12345,
            "protocol": "dokodemo-door",
            "settings": {
                "network": "tcp,udp",
                "followRedirect": true
            },
            "sniffing": {
                "enabled": true,
                "destOverride": [
                    "http",
                    "tls"
                ]
            },
            "streamSettings": {
                "sockopt": {
                    "tproxy": "tproxy"
                }
            }
        },
        {
            "listen": "0.0.0.0",
            "port": 1080,
            "protocol": "socks",
            "sniffing": {
                "enabled": true,
                "destOverride": ["http", "tls"]
            },
            "settings": {
                "auth": "noauth"
            }
        },
        {
            "listen": "0.0.0.0",
            "protocol": "http",
            "settings": {
                "timeout": 360
            },
            "port": "1087"
        }
    ],
    "outbounds": [
        {
            "streamSettings": {
                "network": "ws",
                "security": "tls",
                "tlsSettings": {
                "allowInsecure": true,
                "serverName": null
                },
                "tcpSettings": null,
                "kcpSettings": null,
                "wsSettings": {
                "connectionReuse": true,
                "path": "/abc176c0/",
                "headers": null
                },
                "httpSettings": null
            },
            "tag": "proxy",
            "protocol": "vmess",
            "settings": {
                "vnext": [
                    {
                        "address": "$1",
                        "port": 443,
                        "users": [
                            {
                                "id": "a39c3628-191c-4d0a-8a5b-47d1464b976b",
                                "alterId": 64,
                                "level": 1,
                                "security": "auto"
                            }
                        ]
                    }
                ]
            },
            "streamSettings": {
                "sockopt": {
                    "mark": 255
                }
            },
            "mux": {
                "enabled": false
            }
        },
        {
            "tag": "direct",
            "protocol": "freedom",
            "settings": {
                "domainStrategy": "UseIP"
            },
            "streamSettings": {
                "sockopt": {
                    "mark": 255
                }
            }
        },
        {
            "tag": "block",
            "protocol": "blackhole",
            "settings": {
                "response": {
                    "type": "http"
                }
            }
        },
        {
            "tag": "dns-out",
            "protocol": "dns",
            "streamSettings": {
                "sockopt": {
                    "mark": 255
                }
            }
        }
    ],
    "dns": {
        "servers": [
            "8.8.8.8",
            "1.1.1.1",
            "114.114.114.114",
            {
                "address": "223.5.5.5",
                "port": 53,
                "domains": [
					"$1",
                    "geosite:cn",
                    "ntp.org"
                ]
            }
        ]
    },
    "routing": {
        "domainStrategy": "IPOnDemand",
        "rules": [
            {
                "type": "field",
                "inboundTag": [
                    "transparent"
                ],
                "port": 53,
                "network": "udp",
                "outboundTag": "dns-out"
            },
            {
                "type": "field",
                "inboundTag": [
                    "transparent"
                ],
                "port": 123,
                "network": "udp",
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "ip": [
                    "223.5.5.5",
                    "114.114.114.114"
                ],
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "ip": [
                    "8.8.8.8",
                    "1.1.1.1"
                ],
                "outboundTag": "proxy"
            },
            {
                "type": "field",
                "domain": [
                    "geosite:category-ads-all"
                ],
                "outboundTag": "block"
            },
            {
                "type": "field",
                "protocol":["bittorrent"],
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "ip": [
                    "geoip:private",
                    "geoip:cn"
                ],
                "outboundTag": "direct"
            },
            {
                "type": "field",
                "domain": [
                    "geosite:cn"
                ],
                "outboundTag": "direct"
            }
        ]
    }
}
EOF
}

function modify_num_of_max_open_files {
    echo "[INFO] Setting number of max open files to 1000000"
    sed -i 's/Status=23/Status=23\nLimitNPROC=500\nLimitNOFILE=1000000\n/' /etc/systemd/system/v2ray.service
}

function start_v2ray_transparent_proxy_service {
    echo "[INFO] Starting v2ray transparent proxy service"
    systemctl daemon-reload
    systemctl restart v2ray
}

function install_v2ray_online {
    echo "[INFO] Installing v2ray online from official"
    curl -L -s https://install.direct/go.sh|bash
}

function install_needed_Packages {
    #Check Root
    [ $(id -u) != "0" ] && { echo "${CFAILURE}Error: You must be root to run this script${CEND}"; exit 1; }
    #Check OS
    if [ -n "$(grep 'Aliyun Linux release' /etc/issue)" -o -e /etc/redhat-release ]; then
      OS=CentOS
      [ -n "$(grep ' 7\.' /etc/redhat-release)" ] && CentOS_RHEL_version=7
      [ -n "$(grep ' 6\.' /etc/redhat-release)" -o -n "$(grep 'Aliyun Linux release6 15' /etc/issue)" ] && CentOS_RHEL_version=6
      [ -n "$(grep ' 5\.' /etc/redhat-release)" -o -n "$(grep 'Aliyun Linux release5' /etc/issue)" ] && CentOS_RHEL_version=5
    elif [ -n "$(grep 'Amazon Linux AMI release' /etc/issue)" -o -e /etc/system-release ]; then
      OS=CentOS
      CentOS_RHEL_version=6
    elif [ -n "$(grep bian /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == 'Debian' ]; then
      OS=Debian
      [ ! -e "$(which lsb_release)" ] && { apt-get -y update; apt-get -y install lsb-release; clear; }
      Debian_version=$(lsb_release -sr | awk -F. '{print $1}')
    elif [ -n "$(grep Deepin /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == 'Deepin' ]; then
      OS=Debian
      [ ! -e "$(which lsb_release)" ] && { apt-get -y update; apt-get -y install lsb-release; clear; }
      Debian_version=$(lsb_release -sr | awk -F. '{print $1}')
    elif [ -n "$(grep Ubuntu /etc/issue)" -o "$(lsb_release -is 2>/dev/null)" == 'Ubuntu' -o -n "$(grep 'Linux Mint' /etc/issue)" ]; then
      OS=Ubuntu
      [ ! -e "$(which lsb_release)" ] && { apt-get -y update; apt-get -y install lsb-release; clear; }
      Ubuntu_version=$(lsb_release -sr | awk -F. '{print $1}')
      [ -n "$(grep 'Linux Mint 18' /etc/issue)" ] && Ubuntu_version=16
    else
      echo "${CFAILURE}Does not support this OS, Please contact the author! ${CEND}"
      kill -9 $$
    fi
    #Install Needed Packages
    if [ ${OS} == Ubuntu ] || [ ${OS} == Debian ];then
        apt-get update -y
        apt-get install wget curl socat git unzip -y
    fi

    if [ ${OS} == CentOS ];then
        yum install epel-release -y
        yum install unzip git curl crontabs wget -y
    fi

    if [ ${Debian_version} == 9 ];then
      echo "${CFAILURE}Does not support this OS, Please contact the author! ${CEND}"
      kill -9 $$
    fi

}

function main {
    install_needed_Packages
    install_v2ray_online
    generate_v2ray_config $2
    modify_num_of_max_open_files
    # start_v2ray_transparent_proxy_service
    # set_autorestoring_iptables_rules_service
    if [ -f "/usr/bin/v2ray/v2ray" ];then
        echo "[INFO] Starting v2ray from console"
        systemctl disable v2ray
        systemctl stop v2ray
        iptables -t mangle -F
        iptables -t mangle -X
        deploy_iptables_rules $1
        # dump_iptables_rules
        /usr/bin/v2ray/v2ray -config /etc/v2ray/config.json
        echo "[INFO] Clean v2ray iptables mangle rules"
        iptables -t mangle -F
        iptables -t mangle -X
        ip rule del fwmark 1 table 100
        ip route del local 0.0.0.0/0 dev lo table 100
        rm -f /etc/v2ray/config.json
    else
        echo "[INFO] /usr/bin/v2ray/v2ray not found"
    fi
}

main $1 $2
