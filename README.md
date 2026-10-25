# FITLUXE 健身网站

前后端分离项目：

- `src/`：Vue 3 + Vite + TypeScript + Element Plus 前端
- `backend/`：Flask + SQLAlchemy + MySQL 后端

## 环境要求

- Node.js 18+（本项目用 Node 24 验证）
- Python 3.10+（后端依赖建议装在独立 conda/venv 环境，例如 `DLS`）
- MySQL 8.0+

## 初始化数据库

建表统一由 **Alembic 迁移**负责，不要再用 `db.create_all()`——那样会绕过版本管理，
导致「本地库和模型对不上、上线时不知道少了哪一列」。

```bash
cd backend

# 1) 创建数据库（只需一次）
mysql -uroot -p -e "CREATE DATABASE fitluxe CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2) 建表 / 升级到最新版本
alembic upgrade head

# 3) 导入种子数据
python seed_data.py
```

数据库地址不会写死在 `alembic.ini` 里，而是由 `migrations/env.py` 从 Flask 的
`config.py` 读取（同样支持 `DATABASE_URL` 环境变量覆盖），所以迁移和应用永远指向同一个库。

常用迁移命令：

| 命令 | 用途 |
| --- | --- |
| `alembic upgrade head` | 升级到最新版本 |
| `alembic revision --autogenerate -m "说明"` | 改完模型后生成迁移，**生成后务必人工检查** |
| `alembic check` | 校验「模型」与「数据库」是否一致，CI 里可当作门禁 |
| `alembic current` / `alembic history` | 查看当前版本 / 历史 |
| `alembic downgrade -1` | 回滚一个版本 |

> 已经用旧方式建过库的项目：先 `alembic stamp head` 打上基线，再正常走升级流程。
> 本项目已执行过这一步，并补了一个「对齐旧库」的迁移，当前 `alembic check` 无差异。

## 配置

复制 `backend/.env.example` 为 `backend/.env` 并填写：

```ini
APP_ENV=development
# 生成方式：python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=你的64位随机串
JWT_SECRET=你的64位随机串
DB_PASSWORD=你的MySQL密码
DEEPSEEK_API_KEY=你的DeepSeek Key（可选，AI饮食方案需要）
```

> **密钥是必填项。** 生产环境（`APP_ENV=production`，也是默认值）缺少
> `SECRET_KEY` / `JWT_SECRET` 会直接拒绝启动，不会再回退到代码里的默认字符串。
> 开发环境允许留空——启动时会自动生成临时密钥并打印警告，但重启后已签发的 token 会失效。

前端后端地址可通过 `VITE_API_BASE` 覆盖（默认 `http://127.0.0.1:8000/api`），复制 `src/.env.example` 为 `src/.env` 使用。

> CORS：后端默认放行 `localhost` 和 `127.0.0.1` 的 3000 / 4173 端口。
> 这两者在浏览器看来是**不同的源**，换域名或换端口访问时需同步更新 `CORS_ORIGINS`，
> 否则接口会返回 200 但响应被浏览器丢弃，表现为"页面数据加载不出来"。

## 权限模型（重要）

所有"属于某个用户的数据"接口都要求登录，未登录一律返回 `401`，不再有"匿名共享数据池"：

| 类型 | 接口 | 是否需要登录 |
| --- | --- | --- |
| 计算类 | `POST /api/body-metrics/bmi`、`/calculate` | 否（纯计算，不落库） |
| 身材数据 | `records` / `profile` / `goals` / `measurements` / `history` / `export` | **是** |
| AI | `diet-plan`、`diet-plans`、`diet-logs`、`weekly-review` | **是** |
| 我的计划 / 训练记录 | `/api/user-plans/*` | **是** |
| 运动记录 | `/api/workouts/*` | **是** |
| 成就勋章 | `GET /api/achievements` | **是** |
| 上传 | `POST /api/upload` | **是** |
| 管理后台 | `/api/admin/*` | **是 + 管理员** |

对应前端行为：未登录进入身材数据页会显示"访客模式"提示条，计算器可用，但保存、
目标管理、AI 方案、导出等操作会引导登录；`/profile` 与 `/admin` 由路由守卫拦截。

## 运动记录（训练日志）

数据模型分三张表，粒度到「组」：

| 表 | 说明 |
| --- | --- |
| `workout_sessions` | 一次训练：日期、标题、时长、感受 + 冗余汇总（组数/次数/容量） |
| `workout_sets` | 一组：动作名快照、重量、次数、RPE、是否热身 |
| `personal_records` | 个人纪录：按 `(用户, 动作, 纪录类型)` 唯一，类型为 e1RM / 最大重量 / 最多次数 / 单组容量 |

选这个结构而不是「一天一条 + JSON」，是为了让下面这些变成普通聚合查询：

- 本周/本月/总训练容量（`total_volume` 汇总列，列表页不做全表 SUM）
- 某个动作的 8 周曲线与最佳 e1RM（Epley 公式：`w × (1 + reps/30)`）
- 连续训练天数（今天没练不算断，从昨天往前数）
- 个人纪录榜：增删改组后**全量重算**该动作的 PR，避免增量比较留下脏纪录

主要接口：

```
GET    /api/workouts                    训练列表（分页、按天数过滤）
POST   /api/workouts                    开始一次训练
GET    /api/workouts/:id                详情（按动作分组的组列表）
PUT    /api/workouts/:id                改标题/时长/感受
DELETE /api/workouts/:id                删除（连带重算 PR）
POST   /api/workouts/:id/sets           添加一组或多组，返回最新汇总与「新纪录」
PUT    /api/workouts/:id/sets/:set_id   改组（会重算该动作 PR）
DELETE /api/workouts/:id/sets/:set_id   删组
GET    /api/workouts/overview           今日/本周/本月/总计 + 连续天数
GET    /api/workouts/volume-series      近 N 周容量序列
GET    /api/workouts/calendar?month=    月历热力图
GET    /api/workouts/prs                个人纪录
GET    /api/workouts/exercises          练过的动作 + 上次重量（用于快速录入）
GET    /api/workouts/exercises/:name/history  单动作历史曲线
```

前端入口：顶部导航「运动记录」→ `/workouts`（需登录）。

## 目标进度与成就勋章

两个功能都只读现有数据，不新增数据表。

**目标进度**（`/body-data` 概览页底部）

`BodyGoal` 里的目标体重 / BMI / 体脂率，与「最早一条记录 → 最近一条记录」对比，
换算成 0~100% 的环形进度。进度公式是 `(起点 - 当前) / (起点 - 目标)`，
减重和增重共用同一个式子（方向由起点与目标的相对大小自动决定）。
计算逻辑抽在 `src/utils/goal.ts`，是纯函数，可脱离组件单独验证。

达成判定按方向来：减重目标降到 70 以下（如 68）也算达成，不会因为"超过目标"反而判为未完成。

**成就勋章**（个人中心 → 成就勋章）

```
GET /api/achievements   全部成就 + 汇总（已解锁数、金银铜分布、下一个目标）
```

18 个成就分三类，全部由原始数据推导，**不落库**：

| 分类 | 示例 |
| --- | --- |
| 训练 | 首次训练、10/50/100 次、单场 5 吨/10 吨、累计 50 吨、练过 5/20 个动作 |
| 坚持 | 连续 3/7/30 天 |
| 身材 | 首条记录、10/30 条记录、设定目标、达成目标 |

不建表的原因：成就都能从训练与身材记录算出来（几个聚合查询的成本），
存一张表反而要处理"删了记录成就还算不算"的一致性问题。
排序规则是「已解锁的按等级从高到低，未解锁的按进度从高到低」，
所以用户看到的"下一个目标"总是最快能拿到的那个。

## 前端构建

`manualChunks` 把第三方库拆成独立 chunk，业务代码迭代时用户只需重新下载很小的 `index` chunk：

| chunk | 内容 |
| --- | --- |
| `vendor-vue` | vue / vue-router |
| `vendor-element` | element-plus（全量引入，约 825KB / gzip 261KB） |
| `vendor-echarts` | echarts + zrender（仅图表页加载） |
| `vendor` | 其余依赖 |
| `index` | 业务代码（约 20KB） |

图标采用**显式白名单**注册（`src/main.ts` 的 `ICONS`），不再 `import * as Icons` 全量注册。
模板里的 `<User />` 和 `icon: 'User'` 这类字符串动态组件依赖全局注册，
所以**新增图标必须把名字补进 `ICONS`**，否则页面上会渲染成空白（不会报编译错误）。

核对是否漏注册：

```bash
python scripts/scan-icons.py
```

脚本会扫描全部 `.vue` / `.ts`，列出实际用到的图标名，以及不在图标库中的名字（多半是自定义组件）。
注意 `BarChart.vue` / `LineChart.vue` 是本项目自建组件，不是图标。

## 构建与类型检查
```bash
npm run dev        # 开发（热更新）
npm run build      # 类型检查 + 构建（vue-tsc --noEmit && vite build）
npm run build:fast # 只构建，跳过类型检查（应急用）
npm run type-check # 单独跑类型检查
```

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
