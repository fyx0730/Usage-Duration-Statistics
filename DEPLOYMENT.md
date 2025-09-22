# 部署指南

## 架构说明

本项目采用前后端分离架构：
- **前端**：部署到 GitHub Pages（静态网站）
- **后端**：部署到 Heroku 或其他云平台（Python API 服务）

## 前端部署到 GitHub Pages

### 1. 推送代码到 GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 2. 启用 GitHub Pages

1. 进入 GitHub 仓库设置
2. 找到 "Pages" 选项
3. Source 选择 "GitHub Actions"
4. 代码推送后会自动部署

### 3. 访问前端

部署完成后，访问：`https://你的用户名.github.io/你的仓库名/`

## 后端部署选项

### 选项1: Railway 部署 ⭐ 推荐

1. **注册账号**：访问 [railway.app](https://railway.app)
2. **连接 GitHub**：授权 Railway 访问你的仓库
3. **创建项目**：
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择你的仓库
4. **配置环境变量**：
   ```
   PORT=5001
   MQTT_HOST=mqtt.aimaker.space
   MQTT_PORT=1883
   MQTT_USERNAME=guest
   MQTT_PASSWORD=test
   ```
5. **自动部署**：推送代码到 GitHub 会自动部署

### 选项2: Render 部署

1. **注册账号**：访问 [render.com](https://render.com)
2. **创建 Web Service**：
   - 连接 GitHub 仓库
   - 选择 "Web Service"
   - 配置：
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python run.py`
3. **设置环境变量**：在 Environment 标签页添加
4. **部署**：点击 "Create Web Service"

### 选项3: Fly.io 部署

1. **安装 CLI**：
   ```bash
   # macOS
   brew install flyctl
   
   # 或访问 https://fly.io/docs/getting-started/installing-flyctl/
   ```

2. **登录并初始化**：
   ```bash
   fly auth login
   fly launch
   ```

3. **部署**：
   ```bash
   fly deploy
   ```

## 其他部署选项

### 选项4: PythonAnywhere

1. **注册免费账号**：访问 [pythonanywhere.com](https://www.pythonanywhere.com)
2. **上传代码**：使用 Git 或文件上传
3. **配置 Web 应用**：
   - 创建新的 Web 应用
   - 选择 Flask
   - 配置 WSGI 文件
4. **安装依赖**：在 Bash 控制台运行 `pip install -r requirements.txt`

### 选项5: Vercel (Serverless)

1. **安装 Vercel CLI**：
   ```bash
   npm i -g vercel
   ```
2. **登录并部署**：
   ```bash
   vercel login
   vercel
   ```
3. **配置**：需要将 Flask 应用改为 Serverless 函数

## 配置前端连接后端

1. 部署后端获得 API 地址（如：`https://your-app.herokuapp.com`）
2. 访问前端页面
3. 在 "API 配置" 部分输入：`https://your-app.herokuapp.com/api`
4. 点击 "保存配置" 和 "测试连接"

## 环境变量配置

后端可能需要的环境变量：

```bash
PORT=5001                    # 端口（Heroku 自动设置）
MQTT_HOST=mqtt.aimaker.space # MQTT 服务器地址
MQTT_PORT=1883              # MQTT 端口
MQTT_USERNAME=guest         # MQTT 用户名
MQTT_PASSWORD=test          # MQTT 密码
DATABASE_URL=sqlite:///game_usage.db  # 数据库 URL
```

## 故障排除

### 前端无法连接后端

1. 检查后端是否正常运行
2. 确认 API 地址配置正确
3. 检查 CORS 设置
4. 查看浏览器控制台错误

### 后端部署失败

1. 检查 `requirements.txt` 是否完整
2. 确认 Python 版本兼容性
3. 查看部署日志
4. 检查端口配置

### MQTT 连接问题

1. 确认 MQTT 服务器地址和端口
2. 检查用户名密码
3. 验证网络连接
4. 查看后端日志

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动完整系统
python run.py

# 或分别启动
python api.py          # 启动 API 服务器
python mqtt_client.py  # 启动 MQTT 客户端
```

访问：`http://localhost:5001/`