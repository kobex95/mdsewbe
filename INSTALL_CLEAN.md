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

## 故障排除

如果安装后遇到目录结构错误（如 `No such file or directory`），可以使用以下方法修复：

### 方法1：使用快速修复脚本
```bash
curl -fsSL https://raw.githubusercontent.com/kobex95/mdsewbe/master/scripts/quick_fix.sh | bash
```

### 方法2：手动修复
```bash
cd /www/server/mdserver-web
mkdir -p data logs tmp config plugins
echo "admin" > data/default.pl
echo "/admin" > data/admin_path.pl
touch logs/panel_task.log logs/debug.log
chown -R www:www data logs tmp
bash cli.sh start
```

### 常见错误解决
- **权限错误**: 确保以 root 用户运行
- **端口占用**: 检查 7200 端口是否被占用
- **依赖缺失**: 确保系统已安装 python3 和相关依赖