# Codehelper - AI 编程助手

基于硅基流动 Qwen/Qwen2.5-Coder-7B-Instruct API 的智能编程助手，提供代码生成、代码解释、代码改错功能。

## 功能特性

- 💬 **AI 对话** - 智能对话，支持上下文理解
- ⚡ **代码生成** - 根据需求描述自动生成代码
- 📖 **代码解释** - 详细解释代码功能和逻辑
- 🔧 **代码改错** - 智能识别并修复代码中的错误
- ▶️ **代码运行** - 在代码解释模式下可直接运行代码（仅支持 Python）
- 📁 **文件上传** - 支持上传本地代码文件进行分析
- 💾 **对话管理** - 支持多个对话，可重命名、删除
- 🔄 **历史共享** - 所有功能模式共享对话历史，切换模式不丢失上下文
- 🌙 **主题切换** - 支持日间/夜间模式
- 📜 **对话历史** - 支持上下文连续对话，localStorage 本地保存

## 技术栈

- **后端**: FastAPI + Python
- **前端**: HTML + CSS + JavaScript
- **AI 模型**: Qwen/Qwen2.5-Coder-7B-Instruct (硅基流动)

## 项目结构

```
Codehelper/
├── backend/              # 后端模块
│   ├── __init__.py
│   ├── config.py       # 配置文件
│   ├── model.py        # 模型调用
│   ├── router.py       # API 路由
│   └── main.py         # 应用入口
├── templates/
│   └── index.html      # 前端页面
├── .env                # 环境变量
├── main.py             # 主入口
├── requirements.txt    # 依赖
├── Dockerfile          # 容器配置
└── README.md           # 说明文档
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Enderper/Codehelper.git
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
```

访问 http://localhost:8000

## 使用说明

### 基本操作

1. **选择功能模式**: 左侧边栏选择 AI 对话 / 代码生成 / 代码解释 / 代码改错
2. **输入内容**: 在底部输入框描述需求或粘贴代码
3. **发送消息**: 点击发送按钮或按 Enter 键
4. **切换主题**: 点击右下角按钮切换日间/夜间模式

### 高级功能

#### 对话管理
- 点击 AI 对话旁边的 ▼ 可展开对话列表
- 点击"新建对话"创建新对话（自动保存）
- 悬停对话可显示重命名 ✏️ 和删除 × 按钮

#### 代码运行（仅代码解释模式）
- 在代码解释模式下，有"解释"和"运行"两个按钮
- 点击"运行"会执行代码并显示结果，AI 还会分析执行结果
- 支持安全检查：禁止危险命令和 input() 调用

#### 文件上传
- 代码解释和代码改错模式下支持上传文件
- 点击"📤 上传"按钮选择本地代码文件
- AI 会读取文件内容进行分析

#### 对话历史
- 所有功能模式共享同一个对话历史
- 切换模式时不会清空对话
- 对话数据保存在浏览器 localStorage 中

## 容器部署

### 1. 构建镜像

```bash
docker build -t codehelper .
```

### 2. 运行容器

```bash
docker run -d -p 8000:8000 \
  -e SILICONFLOW_API_KEY=your_api_key \
  codehelper
```

### 3. Docker Compose（推荐）

创建 `docker-compose.yml`：

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
| `/api/chat` | POST | 对话接口（支持所有功能） |

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

## 安全说明

- 代码执行功能已添加安全检查
- 禁止执行危险命令（如 rm -rf、del 等）
- 不支持包含 input() 的代码（需要交互输入）
- 执行超时限制为 10 秒

## 注意事项

- 请妥善保管 API Key，不要提交到公开仓库
- 首次使用需确保 API Key 余额充足
- 建议使用虚拟环境避免依赖冲突

## 许可证

MIT License
