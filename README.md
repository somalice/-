# 网商园图片下载器

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

一个基于 Playwright 的自动化电商图片下载工具，支持从网商园平台批量下载店铺商品图片。

## ✨ 功能特点

- 🚀 **自动化下载**：一键启动，自动完成商品图片下载
- 🔄 **智能浏览器管理**：自动启动Chrome，支持持久化登录状态
- 📦 **批量处理**：支持同时处理多个店铺链接
- 📊 **实时日志**：清晰的操作日志，实时显示下载进度
- 🎨 **现代化界面**：简洁美观的图形用户界面

## 🛠️ 技术栈

- **Python 3.10+** - 主要编程语言
- **Playwright** - 浏览器自动化
- **Tkinter** - 图形用户界面
- **logging** - 日志管理

## 📁 项目结构

```
wsy_downloader/
├── src/
│   ├── __init__.py
│   ├── downloader.py    # 核心下载逻辑
│   ├── logger.py       # 日志配置
│   └── main.py         # 主程序入口
├── chrome_profile/     # Chrome浏览器配置（自动生成）
├── downloads/          # 下载的图片目录（自动生成）
├── requirements.txt    # 依赖列表
└── README.md          # 项目文档
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Chrome浏览器（已安装）
- 网络连接

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd wsy_downloader
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **安装Playwright浏览器**
```bash
playwright install chromium
```

### 使用方法

1. **启动程序**
```bash
python src/main.py
```

2. **启动Chrome浏览器**
   - 点击「启动 Chrome」按钮
   - 等待Chrome启动并跳转到金牌档口页面
   - 首次使用需要手动登录网商园（后续自动复用）

3. **输入店铺链接**
   - 手动输入或点击「填示例链接」
   - 每行一个链接，格式：`https://cs.wsy.com/1109067`

4. **开始下载**
   - 点击「开始下载」按钮
   - 观察日志显示进度
   - 可随时点击「停止」按钮中断

## 📝 使用示例

```
店铺链接示例：
https://cs.wsy.com/1109067
https://cs.wsy.com/1108199
```

## ⚠️ 注意事项

1. **首次登录**：第一次使用需要手动在Chrome中登录网商园，登录信息会自动保存
2. **网络稳定**：确保网络连接稳定，下载过程中避免中断
3. **Chrome进程**：程序启动时会开启新的Chrome实例，请确保保存重要工作

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

如有问题或建议，请联系开发者。
