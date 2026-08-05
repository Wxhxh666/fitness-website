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

## 启动

后端（端口 8000）：

```bash
conda activate DLS   # 或你安装依赖的虚拟环境
cd backend
python app.py
```

前端（端口 4173 预览 / 3000 开发）：

```bash
cd fitness-website
npx vite preview      # 预览构建产物；开发用 npx vite
```

> 注意：Windows PowerShell 默认禁止执行 `.ps1` 脚本，若 `npx`/`npm` 报错请改用 `npx.cmd` / `npm.cmd`。

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
