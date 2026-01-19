# 新安装方式

## 一键安装命令

使用以下命令安装 cleaned 版本的 mdserver-web：

```bash
bash <(curl --insecure -fsSL https://raw.githubusercontent.com/kobex95/mdsewbe/master/scripts/install_new.sh)
```

## 或者分步安装

1. 下载安装脚本：
```bash
curl --insecure -fsSL https://raw.githubusercontent.com/kobex95/mdsewbe/master/scripts/install_new.sh -o install_new.sh
```

2. 执行安装：
```bash
bash install_new.sh
```

## 主要改动

- 移除了所有广告、统计代码和联系方式
- 禁用了 webstats 统计插件
- 删除了捐赠和推广相关内容
- 清理了 Telegram 插件中的广告推送功能
- 更新了仓库地址指向 `kobex95/mdsewbe`

## 注意事项

- 需要 root 权限运行
- 支持主流 Linux 发行版（Debian/Ubuntu/CentOS/RHEL/Fedora/Alpine等）
- 国内用户可选择代理地址加速下载