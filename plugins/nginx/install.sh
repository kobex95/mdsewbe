#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin:/opt/homebrew/bin
export PATH

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

sysName=`uname`
action=$1
type=$2

VERSION=$2

if [ "$action" == "uninstall" ];then
	VERSION=""
fi

nginxDir=${serverPath}/source/nginx

Install_nginx()
{
	if [ -d $serverPath/nginx ];then
		exit 0
	fi
	
	# CPU核心数检测
	if [ -z "${cpuCore}" ]; then
    	cpuCore="1"
	fi

	if [ -f /proc/cpuinfo ];then
		cpuCore=`cat /proc/cpuinfo | grep "processor" | wc -l`
	fi

	MEM_INFO=$(free -m|grep Mem|awk '{printf("%.f",($2)/1024)}')
	if [ "${cpuCore}" != "1" ] && [ "${MEM_INFO}" != "0" ];then
	    if [ "${cpuCore}" -gt "${MEM_INFO}" ];then
	        cpuCore="${MEM_INFO}"
	    fi
	else
	    cpuCore="1"
	fi

	if [ "$cpuCore" -gt "2" ];then
		cpuCore=`echo "$cpuCore" | awk '{printf("%.f",($1)*0.8)}'`
	else
		cpuCore="1"
	fi

	mkdir -p ${nginxDir}
	echo '正在安装Nginx...'

	# 下载Nginx源码
	if [ ! -f ${nginxDir}/nginx-${VERSION}.tar.gz ];then
		wget -O ${nginxDir}/nginx-${VERSION}.tar.gz http://nginx.org/download/nginx-${VERSION}.tar.gz
	fi

	if [ ! -d ${nginxDir}/nginx-${VERSION} ];then
		cd ${nginxDir} && tar -zxvf nginx-${VERSION}.tar.gz
	fi

	cd ${nginxDir}/nginx-${VERSION}

	# 配置编译选项
	./configure \
	--prefix=${serverPath}/nginx \
	--sbin-path=${serverPath}/nginx/sbin/nginx \
	--conf-path=${serverPath}/nginx/conf/nginx.conf \
	--error-log-path=${serverPath}/nginx/logs/error.log \
	--http-log-path=${serverPath}/nginx/logs/access.log \
	--pid-path=${serverPath}/nginx/logs/nginx.pid \
	--lock-path=${serverPath}/nginx/logs/nginx.lock \
	--http-client-body-temp-path=${serverPath}/nginx/temp/client_body \
	--http-proxy-temp-path=${serverPath}/nginx/temp/proxy \
	--http-fastcgi-temp-path=${serverPath}/nginx/temp/fastcgi \
	--http-uwsgi-temp-path=${serverPath}/nginx/temp/uwsgi \
	--http-scgi-temp-path=${serverPath}/nginx/temp/scgi \
	--with-http_ssl_module \
	--with-http_v2_module \
	--with-http_realip_module \
	--with-http_addition_module \
	--with-http_sub_module \
	--with-http_dav_module \
	--with-http_flv_module \
	--with-http_mp4_module \
	--with-http_gunzip_module \
	--with-http_gzip_static_module \
	--with-http_random_index_module \
	--with-http_secure_link_module \
	--with-http_stub_status_module \
	--with-http_auth_request_module \
	--with-mail \
	--with-mail_ssl_module \
	--with-file-aio \
	--with-ipv6 \
	--with-http_v2_module \
	--with-threads \
	--with-stream \
	--with-stream_ssl_module

	make -j${cpuCore} && make install

	# 创建必要的目录
	mkdir -p ${serverPath}/nginx/logs
	mkdir -p ${serverPath}/nginx/temp
	mkdir -p ${serverPath}/nginx/conf/vhost
	mkdir -p ${serverPath}/nginx/ssl

	# 复制默认配置文件
	cp ${nginxDir}/nginx-${VERSION}/conf/* ${serverPath}/nginx/conf/

	# 创建版本标识文件
	echo "${VERSION}" > ${serverPath}/nginx/version.pl

	# 清理源码包
	rm -rf ${nginxDir}/nginx-${VERSION}
	rm -f ${nginxDir}/nginx-${VERSION}.tar.gz

	echo 'Nginx安装完成'
}

Uninstall_nginx()
{
	if [ -d $serverPath/nginx ];then
		rm -rf $serverPath/nginx
	fi
	echo 'Nginx卸载完成'
}

action=$1
if [ "${1}" == 'install' ];then
	Install_nginx
elif [ "${1}" == 'uninstall' ];then
	Uninstall_nginx
else
	echo "Usage: $0 {install|uninstall} [version]"
fi