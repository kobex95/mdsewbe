#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

VERSION=1.0.0

Install_Waf()
{
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/waf_plus
	mkdir -p $serverPath/waf_plus/logs
	mkdir -p $serverPath/waf_plus/rules
	
	echo "${VERSION}" > $serverPath/waf_plus/version.pl
	echo '安装Web防火墙增强版成功!'
	
	# 初始化数据库
	cd ${rootPath} && python3 ${rootPath}/plugins/waf_plus/index.py init_db
	echo "cd ${rootPath} && python3 ${rootPath}/plugins/waf_plus/index.py init_db"
	
	# 启动服务
	cd ${rootPath} && python3 ${rootPath}/plugins/waf_plus/index.py start
	echo "cd ${rootPath} && python3 ${rootPath}/plugins/waf_plus/index.py start"
	
	sleep 2
	
	# 重新加载配置
	cd ${rootPath} && python3 ${rootPath}/plugins/waf_plus/index.py reload
}

Uninstall_Waf()
{
	cd ${rootPath} && python3 ${rootPath}/plugins/waf_plus/index.py stop
	if [ "$?" == "0" ];then
		rm -rf $serverPath/waf_plus
	fi
}


action=$1
if [ "${1}" == 'install' ];then
	Install_Waf
else
	Uninstall_Waf
fi