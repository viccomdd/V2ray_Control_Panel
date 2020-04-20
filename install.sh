#!/usr/bin/env bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

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
	apt-get install wget curl socat git unzip python3 python3-dev openssl libssl-dev ca-certificates supervisor -y
	wget -O - "https://bootstrap.pypa.io/get-pip.py" | python3
	pip install --upgrade python3-pip
fi

if [ ${OS} == CentOS ];then
	yum install epel-release -y
	yum install python3-pip python3-devel socat ca-certificates openssl unzip git curl crontabs wget supervisor -y
	pip install --upgrade python3-pip
fi

#Install acme.sh
#curl https://get.acme.sh | sh

if [ ! -d "/usr/local/V2ray_Control_Panel" ];then
    cd /usr/local/ && git clone https://github.com/viccomdd/V2ray_Control_Panel
    cd /usr/local/V2ray_Control_Panel && pip3 install virtualenv && virtualenv venv && source venv/bin/activate
    /usr/local/V2ray_Control_Panel/venv/bin/pip3 install -r requirements.txt
fi

if [ ${OS} == CentOS ];then
    [ -f /etc/supervisord.d/v2ray.ini ] && echo yes || ln -s /usr/local/V2ray_Control_Panel/V2ray_Control_Panel.conf /etc/supervisord.d/v2ray.ini
    echo "[INFO] Starting supervisord"
    systemctl restart supervisord
fi

if [ ${OS} == Ubuntu ] || [ ${OS} == Debian ];then
    [ -f /etc/supervisord.d/v2ray.conf ] && echo yes || ln -s /usr/local/V2ray_Control_Panel/V2ray_Control_Panel.conf /etc/supervisord.d/v2ray.conf
    echo "[INFO] Starting supervisord"
    systemctl restart supervisor
fi


echo "安装成功！"

#清理垃圾文件
