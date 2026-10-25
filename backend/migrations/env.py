# -*- coding: utf-8 -*-
"""
Alembic 运行环境。

要点：
1. 数据库地址**不写死在 alembic.ini**，统一从 Flask 的 Config 读取，
   保证「应用连哪个库」和「迁移改哪个库」永远是同一个库；
   需要临时指向别的库时用环境变量 DATABASE_URL 覆盖。
2. target_metadata 用 db.metadata，必须先 import models 把所有表注册进来，
   否则 autogenerate 会认为「所有表都该被删掉」。
3. 开 compare_type / compare_server_default，字段类型改动也能被检测到。
"""
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 让 alembic 命令在 backend/ 下能找到 app / models / config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config  # noqa: E402
from models import db  # noqa: E402
import models  # noqa: E402,F401  —— 触发 models/__init__ 里所有模型导入，注册 metadata

# Alembic Config 对象
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 允许用环境变量覆盖（CI / 多环境）
db_url = os.environ.get("DATABASE_URL") or Config.SQLALCHEMY_DATABASE_URI
# ini 里是 configparser 语法，% 需要转义
config.set_main_option("sqlalchemy.url", db_url.replace("%", "%%"))

target_metadata = db.metadata


def include_object(obj, name, type_, reflected, compare_to):
    """过滤掉不属于本应用的表（第三方表、临时表），避免 autogenerate 生成 DROP"""
    if type_ == "table" and name.startswith("_"):
        return False
    return True


def run_migrations_offline() -> None:
    """离线模式：只生成 SQL，不连库（alembic upgrade head --sql）"""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式：连库执行迁移"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_object=include_object,
            # MySQL 的 DDL 不能整体回滚，逐条执行便于定位失败语句
            transactional_ddl=False,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
