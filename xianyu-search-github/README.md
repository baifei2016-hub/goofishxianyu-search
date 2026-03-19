# 🎯 闲鱼搜索工具 (XianYu Search Tool)

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-green)](https://openclaw.ai)

基于Selenium的闲鱼（goofish.com）自动化搜索工具，支持关键词搜索、价格筛选、个人闲置过滤，并生成可点击的商品链接。

## ✨ 功能特性

- 🔍 **智能搜索**：支持任意关键词搜索
- 💰 **价格筛选**：精确价格范围筛选
- 👤 **个人闲置**：自动勾选个人闲置筛选
- ⏰ **时间抓取**：完整支持所有时间格式（分钟前、小时前、天前、天内等）
- 🔗 **链接生成**：生成可点击的web_link和deep_link
- 📊 **数据导出**：自动保存JSON数据和截图
- 🎯 **排序正确**：保持浏览器窗口显示顺序

## 🚀 快速开始

### 安装依赖
```bash
# 安装Python依赖
pip install selenium requests beautifulsoup4 lxml

# 系统依赖
# 1. 安装Chrome浏览器
# 2. 下载对应版本的ChromeDriver
# 3. 将ChromeDriver添加到PATH
```

### 基本使用
```bash
# 基本搜索
python3 xianyu_clickable_links.py "闲鱼搜" "野豹球杆" 1000 3000

# 个人闲置搜索
python3 xianyu_clickable_links.py "闲鱼搜" "奥秘梦幻" 200 600 "个人"

# 价格筛选搜索
python3 xianyu_clickable_links.py "闲鱼搜" "测试" 100 200
```

### OpenClaw集成
```bash
# 作为OpenClaw技能使用
# 1. 将技能目录复制到 ~/.agents/skills/xianyu-search/
# 2. 在OpenClaw中直接使用：闲鱼搜 关键词 最低价 最高价 [个人]
```

## 📁 项目结构
```
xianyu-search/
├── xianyu_clickable_links.py      # 主程序
├── xianyu_hover_confirm.py        # 核心模块
├── xianyu_2138_format.py          # 简洁格式输出
├── xianyu_output_display.py       # 详细输出格式
├── requirements.txt               # 依赖列表
├── LICENSE                        # MIT许可证
└── README.md                      # 本文件
```

## 🔧 配置说明

### ChromeDriver配置
1. 下载与Chrome版本匹配的ChromeDriver
2. 将ChromeDriver放在系统PATH中
3. 或指定ChromeDriver路径：`export CHROMEDRIVER_PATH=/path/to/chromedriver`

### Cookies管理
- 首次使用需要扫码登录闲鱼
- 登录信息自动保存到`cookies/`目录
- 后续使用自动加载cookies，无需重复登录

## 📊 输出示例

### 终端输出
```
前10个产品:

1. 奥秘梦幻 台球杆
   价格: ¥580
   时间: 12小时前发布
   地区: 江苏
   商品ID: 1032526850390
   web_link: https://www.goofish.com/item?id=1032526850390&categoryId=126866353
   deep_link: https://h5.m.goofish.com/item?id=1032526850390
```

### JSON输出
```json
{
  "index": 1,
  "title": "奥秘梦幻 台球杆",
  "price": "¥580",
  "time": "12小时前发布",
  "location": "江苏",
  "product_id": "1032526850390",
  "web_link": "https://www.goofish.com/item?id=1032526850390&categoryId=126866353",
  "deep_link": "https://h5.m.goofish.com/item?id=1032526850390"
}
```

## 🛠️ 开发指南

### 代码结构
- `xianyu_clickable_links.py`: 主程序，控制流程和输出
- `xianyu_hover_confirm.py`: 核心浏览器操作模块
- `xianyu_2138_format.py`: 简洁输出格式
- `xianyu_output_display.py`: 详细输出格式

### 扩展功能
1. 支持更多电商平台
2. 添加批量搜索功能
3. 实现价格监控和提醒
4. 添加数据分析和可视化

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Selenium](https://www.selenium.dev/) - 浏览器自动化工具
- [闲鱼](https://goofish.com/) - 阿里巴巴旗下二手交易平台
- [OpenClaw](https://openclaw.ai) - AI助手平台

## 📧 联系

如有问题或建议，请通过GitHub Issues联系我们。
需要定制vx：411783771
---

**⭐ 如果这个项目对您有帮助，请给个Star！**
