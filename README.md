<p align="center">
  <img alt="logo" src="https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/route/static/logo.png" height="140" />
  <h3 align="center">mdserver-web</h3>
  <p align="center">一款简单Linux面板服务</p>
  <p align="center">强烈推荐系统:debian</p>
</p>





[![jsdelivr](https://data.jsdelivr.com/v1/package/gh/midoks/mdserver-web/badge)](https://www.jsdelivr.com/package/gh/midoks/mdserver-web)

* SSH终端工具
* 面板收藏功能
* 网站备份功能
* 插件方式管理

基本上可以使用,后续会继续优化!欢迎提供意见！



```
Talk is cheap, show me the code.  -- linus
```

- [兼容性测试报告](/compatibility.md)
- [常用命令说明](/cmd.md) [ mw default ] [ mw dev ]



### 主要插件介绍

* OpenResty - 轻量级，占有内存少，并发能力强。
* PHP[53-85] - PHP是世界上最好的编程语言。
* MySQL - 一种关系数据库管理系统。
* MariaDB - 是MySQL的一个重要分支。
* MySQL[community] - 一种关系数据库管理系统。
* MongoDB - 一种非关系NOSQL数据库管理系统。
* PostgreSQL - 功能强大的开源数据库。
* phpMyAdmin - 著名Web端MySQL管理工具。
* Memcached - 一个高性能的分布式内存对象缓存系统。
* Redis - 一个高性能的KV数据库。
* PureFtpd - 一款专注于程序健壮和软件安全的免费FTP服务器软件。
* Gogs - 一款极易搭建的自助Git服务。
* Rsyncd - 通用同步服务。








# Note

```
phpMyAdmin[4.4.15]支持MySQL[5.5-5.7]
phpMyAdmin[5.2.1]支持MySQL[8.0+]

PHP[53-72]支持phpMyAdmin[4.4.15]
PHP[72-84]支持phpMyAdmin[5.2.1]
```

# 郑重声明

不卖、不会监控(统计使用除外)、更不会注入病毒,大家使用方便(望大家不吝捐赠)。

- https://www.youtube.com/watch?v=2taa5K-Jmmw


# Docker

- 由[DDS-Derek](https://github.com/DDS-Derek)开发维护。
- https://github.com/DDS-Derek/mdserver-web-Docker

```
docker run -itd --name mw-server --privileged=true -p 7200:7200 -p 80:80 -p 443:443 -p 888:888 ddsderek/mw-server:latest
```


### 版本更新 0.18.4

- 国内安装优化。

### JSDelivr安装地址

- 初始安装

```
bash <(curl --insecure -fsSL https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/scripts/install.sh)
```

- 直接更新

```
bash <(curl --insecure -fsSL https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/scripts/update.sh)
```

- 卸载脚本

```
wget --no-check-certificate -O uninstall.sh https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/scripts/uninstall.sh && bash uninstall.sh
```

### 备用地址

- 初始安装

```

bash <(curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/install.sh)
bash <(curl --insecure -fsSL https://code.midoks.icu/midoks/mdserver-web/raw/branch/master/scripts/install.sh)
```

- 直接更新

```
bash <(curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/update.sh)
```

- 卸载脚本

```
wget --no-check-certificate -O uninstall.sh https://raw.githubusercontent.com/midoks/mdserver-web/master/scripts/uninstall.sh && bash uninstall.sh
```


### 通用软件安装[命令行安装]

- 需已经安装mdserver-web

```
bash <(curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/quick/app.sh)
```


### DEV使用

```
bash <(curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/install.sh)
bash <(curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/update.sh)

bash <(curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/install_dev.sh)
bash <(curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/update_dev.sh)

wget --no-check-certificate -O install.sh https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/install.sh && bash install.sh

wget --no-check-certificate -O uninstall.sh https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/uninstall.sh && bash uninstall.sh

bash <(curl --insecure -fsSL https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/quick/debug.sh)

bash <(curl --insecure -fsSL https://code.midoks.icu/midoks/mdserver-web/raw/branch/dev/scripts/install.sh)
bash <(curl --insecure -fsSL https://code.midoks.icu/midoks/mdserver-web/raw/branch/dev/scripts/update.sh)

bash <(curl --insecure -fsSL https://code.midoks.icu/midoks/mdserver-web/raw/branch/dev/scripts/install_dev.sh)
bash <(curl --insecure -fsSL https://code.midoks.icu/midoks/mdserver-web/raw/branch/dev/scripts/update_dev.sh)
```

### 旧版安装/更新
```
curl --insecure -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/old/install.sh | bash
curl --insecure -fsSL  https://raw.githubusercontent.com/midoks/mdserver-web/dev/scripts/old/update.sh | bash
```

### 偶然问题
- 在安装/更新时，突然出现python插件pip,psutil,可尝试如下解决方案
```
cd /www/server/mdserver-web rm -rf lib
cd /www/server/mdserver-web && rm -rf lib64
cd /www/server/mdserver-web && rm -rf bin
cd /www/server/mdserver-web && rm -rf include

mw update/mw update_dev/mw dev
```




### 无图不真相

[![截图](https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/route/static/mdw.jpg)](https://cdn.jsdelivr.net/gh/midoks/mdserver-web@latest/route/static/mdw.jpg)


### Stargazers over time

[![Stargazers over time](https://starchart.cc/midoks/mdserver-web.svg)](https://starchart.cc/midoks/mdserver-web)




### 授权许可

本项目采用 Apache 开源授权许可证，完整的授权说明已放置在 [LICENSE](https://github.com/midoks/mdserver-web/blob/master/LICENSE) 文件中。

