# FITLUXE 健身网站

前后端分离项目：

- `src/`：Vue 3 + Vite + TypeScript + Element Plus 前端
- `backend/`：Flask + SQLAlchemy + MySQL 后端

## 环境要求

- Node.js 18+（本项目用 Node 24 验证）
- Python 3.10+（后端依赖建议装在独立 conda/venv 环境，例如 `DLS`）
- MySQL 8.0+

## 初始化数据库

1. 在 MySQL 中创建数据库和表：

   ```sql
   -- 直接用 MySQL 客户端执行
   SOURCE backend/init_db.sql;
   ```

   或使用后端 Python：

   ```bash
   cd backend
   python -c "from app import app, db; from models import *; app.app_context().push(); db.create_all()"
   ```

2. 导入种子数据：

   ```bash
   cd backend
   python seed_data.py
   ```

## 配置

复制 `backend/.env.example` 为 `backend/.env` 并填写：

```ini
DB_PASSWORD=你的MySQL密码
DEEPSEEK_API_KEY=你的DeepSeek Key（可选，AI饮食方案需要）
```

前端后端地址可通过 `VITE_API_BASE` 覆盖（默认 `http://127.0.0.1:8000/api`），复制 `src/.env.example` 为 `src/.env` 使用。

> CORS：后端默认放行 `localhost` 和 `127.0.0.1` 的 3000 / 4173 端口。
> 这两者在浏览器看来是**不同的源**，换域名或换端口访问时需同步更新 `CORS_ORIGINS`，
> 否则接口会返回 200 但响应被浏览器丢弃，表现为"页面数据加载不出来"。

## 启动

一键启动（推荐，在项目根目录执行，前后端一起起、Ctrl+C 一起停）：

```bash
start-dev.cmd              # 前端预览（4173）+ 后端（8000）
start-dev.cmd -Mode dev    # 前端开发模式（热更新，3000）+ 后端  ★改前端时用这个
```

> 启动时会自动检查前后端跨域是否放行，并提示 `dist` 构建产物是否过期。

手动分别启动（备用）：

后端（端口 8000）：

```bash
conda activate DLS   # 或你安装依赖的虚拟环境
cd backend
python app.py
```

前端（端口 4173 预览 / 3000 开发）：

```bash
cd fitness-website
npx vite preview      # 预览 dist 构建产物（改了源码必须先 npx vite build）
npx vite              # 开发模式，直接读源码 + 热更新
```

> 注意：`vite preview` 服务的是 `dist/` 构建产物而非源码，改了代码不重新 build 就会一直看到旧界面。
> Windows PowerShell 默认禁止执行 `.ps1` 脚本，若 `npx`/`npm` 报错请改用 `npx.cmd` / `npm.cmd`。

## 管理员账号

直接写入数据库（`is_admin=1`）：

```bash
cd backend
python - <<'EOF'
from werkzeug.security import generate_password_hash
from app import app, db
from models import User
with app.app_context():
    u = User(email="admin@example.com", password_hash=generate_password_hash("你的密码"), nickname="管理员", is_admin=True)
    db.session.add(u)
    db.session.commit()
EOF
```

管理后台：`/admin`
