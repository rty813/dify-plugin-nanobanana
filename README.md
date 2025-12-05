# Nanobanana - Gemini 图片生成器

[![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/doufu/nanobanana)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-orange.svg)](https://dify.ai)

一个基于 Gemini 3 Pro Image Preview 的 Dify 插件，支持通过文本提示词和参考图片生成高质量图片。

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用方法](#使用方法)
- [参数说明](#参数说明)
- [开发指南](#开发指南)
- [常见问题](#常见问题)
- [许可证](#许可证)

## ✨ 功能特性

-🎨 **文本生成图片**: 使用自然语言描述生成图片
- 🖼️ **参考图片支持**: 支持最多 10 张参考图片引导生成
- 📐 **多分辨率选择**: 支持 1K、2K、4K 三种分辨率输出
- ⏱️ **自定义超时**: 可配置请求超时时间（默认 300 秒）
- 🔄 **智能重试**: 支持失败自动重试机制（最多 5 次）
-📝 **详细日志**: 完整的请求和响应日志记录
- 🔐 **安全认证**: 支持自定义 API 端点和密钥配置

## 🚀 快速开始

### 前置要求

- Python 3.12+
- Dify 实例（SaaS 或自托管）
- Gemini API访问权限

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/doufu/nanobanana.git
cd nanobanana
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
INSTALL_METHOD=remote
REMOTE_INSTALL_URL=debug.dify.ai:5003
REMOTE_INSTALL_KEY=your_debug_key_here
```

4. **启动插件**
```bash
python -m main
```

## ⚙️ 配置说明

### 凭据配置

在Dify 插件管理页面配置以下凭据：

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `base_url` | 文本 | ✅ | Gemini API 端点的基础 URL | `your_base_url_here` |
| `api_key` | 密钥 | ✅ | 用于认证的 API 密钥 | `your_api_key_here` |

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `INSTALL_METHOD` | 安装方式（remote/local） | `remote` |
| `REMOTE_INSTALL_URL` | Dify 实例调试地址 | - |
| `REMOTE_INSTALL_KEY` | 调试密钥 | - |

## 📖 使用方法

### 在 Dify 工作流中使用

1. 在 Dify 工作流编辑器中添加"工具"节点
2. 选择"Gemini Image Generator"工具
3. 配置参数（见下方参数说明）
4. 连接输入输出节点
5. 运行工作流

### 基础示例

**简单文本生成**:
```
提示词: "一只可爱的橙色猫咪坐在窗台上，阳光洒在它身上"
分辨率: 2K
```

**使用参考图片**:
```
提示词: "将这张图片转换为水彩画风格"
参考图片: [上传 1-10张图片]
分辨率: 4K
```

## 📝 参数说明

### 输入参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `prompt` | 字符串 | ✅ | - | 图片生成的文本描述 |
| `reference_images` | 文件列表 | ❌ | `[]` | 参考图片（最多 10 张） |
| `resolution` | 字符串 | ❌ | `2K` | 输出分辨率（1K/2K/4K） |
| `timeout` | 数字 | ❌ | `300` | 请求超时时间（秒） |
| `retry` | 数字 | ❌ | `0` | 失败重试次数（0-5） |

### 输出格式

插件返回 Gemini API 生成的 Markdown 格式文本，通常包含：
- 生成的图片链接
- 图片描述信息
- 相关元数据

## 🛠️ 开发指南

### 项目结构

```
nanobanana/
├── main.py                 # 插件入口文件
├── manifest.yaml           # 插件清单文件
├── requirements.txt        # Python 依赖
├── GUIDE.md               # 开发指南
├── PRIVACY.md             # 隐私政策
├── provider/# 提供者配置
│   ├── nanobanana.py# 提供者实现
│   └── nanobanana.yaml   # 提供者配置
├── tools/                 # 工具实现
│   ├── nanobanana.py     # 工具核心逻辑
│   └── nanobanana.yaml   # 工具配置
├── _assets/              # 资源文件
│   ├── icon.svg          # 图标（亮色）
│   └── icon-dark.svg     # 图标（暗色）
└── .github/
    └── workflows/
        └── plugin-publish.yml  # 自动发布工作流
```

### 本地调试

1. 配置 `.env` 文件
2. 运行插件：
```bash
python -m main
```
3. 在 Dify 实例中刷新插件列表
4. 插件将显示为"调试中"状态

### 打包发布

使用 Dify CLI 打包插件：

```bash
dify-plugin plugin package ./
```

生成的 `plugin.difypkg` 文件可提交到 Dify 插件市场。

### 自动发布

项目已配置 GitHub Actions 自动发布工作流：

1. 更新 `manifest.yaml` 中的版本号
2. 创建 GitHub Release
3. 工作流自动打包并创建 PR到插件仓库

详见 [`.github/workflows/plugin-publish.yml`](.github/workflows/plugin-publish.yml)

## 🔧 技术栈

- **运行时**: Python 3.12
- **框架**: Dify Plugin SDK
- **HTTP 客户端**: requests
- **API**: Gemini 3 Pro Image Preview

## 📊 API 端点

插件调用以下 Gemini API 端点：

- **1K 分辨率**: `{base_url}/v1beta/models/gemini-3-pro-image-preview:generateContent`
- **2K 分辨率**: `{base_url}/v1beta/models/gemini-3-pro-image-preview-2k:generateContent`
- **4K 分辨率**: `{base_url}/v1beta/models/gemini-3-pro-image-preview-4k:generateContent`

## ❓ 常见问题

### Q: 为什么请求超时？
A: 图片生成可能需要较长时间，建议：
- 增加 `timeout` 参数值（如 600 秒）
- 启用 `retry` 重试机制
- 降低分辨率（使用 1K 或 2K）

### Q: 支持哪些图片格式作为参考？
A: 支持常见图片格式（JPEG、PNG 等），单张图片建议不超过 10MB。

### Q: 如何获取 API Key？
A: 需要从 Gemini API 提供商处获取，具体方式请咨询您的 API 服务提供商。

### Q: 可以同时生成多张图片吗？
A: 单次调用生成一张图片，如需多张请多次调用工具。

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意**: 本插件需要有效的 Gemini API 访问权限。使用前请确保已获取相应的 API 凭据。

更多信息请参阅 [开发指南](GUIDE.md) 和 [隐私政策](PRIVACY.md)。
