# Codehelper - AI 编程助手

基于硅基流动 Qwen/Qwen2.5-Coder-7B-Instruct API 的智能编程助手，提供代码生成、代码解释、代码改错功能。

## 功能特性

- 💬 **AI 对话** - 智能对话，支持上下文理解
- ⚡ **代码生成** - 根据需求描述自动生成代码
- 📖 **代码解释** - 详细解释代码功能和逻辑
- 🔧 **代码改错** - 智能识别并修复代码中的错误
- 🌙 **主题切换** - 支持日间/夜间模式
- 📜 **对话历史** - 支持上下文连续对话

## 技术栈

- **后端**: FastAPI + Python
- **前端**: HTML + CSS + JavaScript
- **AI 模型**: Qwen/Qwen2.5-Coder-7B-Instruct (硅基流动)

## 项目结构

```
Codehelper/
├── backend/              # 后端模块
│   ├── __init__.py
│   ├── config.py         # 配置文件
│   ├── model.py         # 模型调用
│   ├── router.py        # API 路由
│   └── main.py          # 应用入口
├── templates/
│   └── index.html       # 前端页面
├── .env                 # 环境变量
├── main.py              # 主入口（兼容旧版）
├── requirements.txt     # 依赖
├── Dockerfile           # 容器配置
└── README.md            # 说明文档
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/Codehelper.git
cd Codehelper
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# 硅基流动 API Key
SILICONFLOW_API_KEY=your_api_key_here
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动服务

```bash
# 方式1: 直接运行
python main.py

# 方式2: 使用 uvicorn
uvicorn backend.main:app --reload

# 方式3: 使用 backend/main.py
python backend/main.py
```

访问 http://localhost:8000

## 容器部署

### 1. 构建镜像

```bash
docker build -t codehelper .
```

### 2. 运行容器

```bash
# 使用环境变量
docker run -d -p 8000:8000 \
  -e SILICONFLOW_API_KEY=your_api_key \
  codehelper

# 或使用 .env 文件
docker run -d -p 8000:8000 \
  --env-file .env \
  codehelper
```

### 3. Docker Compose（推荐）

```yaml
version: '3.8'

services:
  codehelper:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY}
    restart: unless-stopped
```

```bash
docker-compose up -d
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页 |
| `/api/chat` | POST | 对话接口（带历史） |
| `/api/generate` | POST | 代码生成 |
| `/api/explain` | POST | 代码解释 |
| `/api/fix` | POST | 代码改错 |

### 对话接口示例

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "用 Python 写一个排序算法"}
    ],
    "mode": "generate"
  }'
```

## 使用说明

1. **选择功能模式**: 左侧边栏选择 AI 对话 / 代码生成 / 代码解释 / 代码改错
2. **输入内容**: 在底部输入框描述需求或粘贴代码
3. **发送消息**: 点击发送按钮或按 Enter 键
4. **切换主题**: 点击右下角按钮切换日间/夜间模式
5. **新建对话**: 点击"新建对话"按钮清空历史

## 开发说明

### 运行开发服务器

```bash
uvicorn backend.main:app --reload --port 8000
```

### 代码规范

- 遵循 PEP 8
- 使用中文注释
- Commit 消息遵循 Conventional Commits 规范

## 注意事项

- 请妥善保管 API Key，不要提交到公开仓库
- 首次使用需确保 API Key 余额充足
- 建议使用虚拟环境避免依赖冲突

## 许可证

MIT License
