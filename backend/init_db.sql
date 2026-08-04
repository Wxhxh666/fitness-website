-- ============================================
-- FITLUXE · Database Schema
-- MySQL 8.0+
-- ============================================

CREATE DATABASE IF NOT EXISTS fitluxe
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE fitluxe;

-- ---------- 动作分类 ----------
CREATE TABLE IF NOT EXISTS exercise_categories (
  id          INT           AUTO_INCREMENT PRIMARY KEY,
  `key`       VARCHAR(32)   NOT NULL UNIQUE COMMENT "分类标识: chest/back/legs/shoulders/abs/fullbody",
  label       VARCHAR(32)   NOT NULL COMMENT "中文名称",
  sort_order  INT           DEFAULT 0 COMMENT "排序",
  is_active   TINYINT(1)    DEFAULT 1,
  created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="动作分类";

-- ---------- 动作库 ----------
CREATE TABLE IF NOT EXISTS exercises (
  id              INT           AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(100)  NOT NULL COMMENT "动作名称",
  category        VARCHAR(32)   NOT NULL COMMENT "分类 key",
  category_label  VARCHAR(32)   NOT NULL COMMENT "分类中文名",
  description     TEXT          COMMENT "动作描述",
  difficulty      VARCHAR(16)   DEFAULT "intermediate" COMMENT "难度: beginner/intermediate/advanced",
  difficulty_label VARCHAR(8)   DEFAULT "中级",
  duration        VARCHAR(64)   COMMENT "建议组数 如 12-15 次 x 4组",
  cover_url       VARCHAR(256)  COMMENT "封面图",
  video_url       VARCHAR(256)  COMMENT "教学视频",
  steps           JSON          COMMENT "步骤 [{order, content}]",
  target_muscles  JSON          COMMENT "目标肌群",
  tips            JSON          COMMENT "注意事项",
  sort_order      INT           DEFAULT 0,
  is_active       TINYINT(1)    DEFAULT 1,
  created_at      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="动作库";

-- ---------- 训练目标 ----------
CREATE TABLE IF NOT EXISTS plan_goals (
  id          INT           AUTO_INCREMENT PRIMARY KEY,
  `key`       VARCHAR(32)   NOT NULL UNIQUE COMMENT "目标标识",
  label       VARCHAR(32)   NOT NULL COMMENT "中文名称",
  description VARCHAR(128)  COMMENT "简短描述",
  sort_order  INT           DEFAULT 0,
  created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="训练目标";

-- ---------- 训练计划 ----------
CREATE TABLE IF NOT EXISTS plans (
  id              INT           AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(100)  NOT NULL COMMENT "计划名称",
  goal            VARCHAR(32)   NOT NULL COMMENT "目标 key",
  badge           VARCHAR(16)   DEFAULT "推荐",
  description     TEXT          COMMENT "计划描述",
  duration        VARCHAR(32)   COMMENT "周期",
  frequency       VARCHAR(32)   COMMENT "频次",
  difficulty      VARCHAR(16)   DEFAULT "intermediate",
  difficulty_label VARCHAR(8)   DEFAULT "中级",
  focus_tags      JSON          COMMENT "专注标签",
  cover_url       VARCHAR(256)  COMMENT "封面图",
  weekly_schedule JSON          COMMENT "周训安排",
  is_active       TINYINT(1)    DEFAULT 1,
  sort_order      INT           DEFAULT 0,
  created_at      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="训练计划";

-- ---------- 身体数据 ----------
CREATE TABLE IF NOT EXISTS body_metrics (
  id           INT           AUTO_INCREMENT PRIMARY KEY,
  user_id      INT           DEFAULT 0 COMMENT "用户 ID",
  `key`        VARCHAR(32)   NOT NULL COMMENT "指标 key",
  label        VARCHAR(32)   NOT NULL COMMENT "中文名",
  value        DECIMAL(8,1)  NOT NULL COMMENT "当前值",
  unit         VARCHAR(16)   DEFAULT "cm",
  `change`     DECIMAL(8,1)  DEFAULT 0.0,
  trend        VARCHAR(8)    DEFAULT "up",
  recorded_at  DATETIME      DEFAULT CURRENT_TIMESTAMP COMMENT "记录时间",
  created_at   DATETIME      DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="身体数据";

-- ---------- 联系留言 ----------
CREATE TABLE IF NOT EXISTS contact_messages (
  id          INT           AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(50)   NOT NULL COMMENT "姓名",
  email       VARCHAR(100)  NOT NULL COMMENT "邮箱",
  phone       VARCHAR(20)   COMMENT "电话",
  subject     VARCHAR(32)   NOT NULL COMMENT "主题",
  message     TEXT          NOT NULL COMMENT "留言内容",
  is_read     TINYINT(1)    DEFAULT 0 COMMENT "是否已读",
  created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="联系留言";

-- ---------- 站点信息 ----------
CREATE TABLE IF NOT EXISTS site_info (
  id             INT           AUTO_INCREMENT PRIMARY KEY,
  address        VARCHAR(256)  COMMENT "地址",
  phone          VARCHAR(32)   COMMENT "联系电话",
  email          VARCHAR(100)  COMMENT "邮箱",
  business_hours JSON          COMMENT '{"weekday":"...","weekend":"..."}',
  social_media   JSON          COMMENT "[{platform, name}]",
  created_at     DATETIME      DEFAULT CURRENT_TIMESTAMP,
  updated_at     DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="站点信息";

-- ---------- 用户表 ----------
CREATE TABLE IF NOT EXISTS users (
  id            INT           AUTO_INCREMENT PRIMARY KEY,
  phone         VARCHAR(20)   UNIQUE COMMENT "手机号",
  email         VARCHAR(100)  UNIQUE COMMENT "邮箱",
  password_hash VARCHAR(256)  COMMENT "密码哈希",
  nickname      VARCHAR(50)   COMMENT "昵称",
  avatar_url    VARCHAR(256)  COMMENT "头像",
  is_active     TINYINT(1)    DEFAULT 1,
  is_admin      TINYINT(1)    DEFAULT 0 COMMENT "?????",
  last_login_at DATETIME      COMMENT "最后登录时间",
  created_at    DATETIME      DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="用户表";

-- ---------- 验证码表 ----------
CREATE TABLE IF NOT EXISTS verification_codes (
  id          INT           AUTO_INCREMENT PRIMARY KEY,
  identifier  VARCHAR(100)  NOT NULL COMMENT "手机号或邮箱",
  code        VARCHAR(6)    NOT NULL COMMENT "验证码",
  purpose     VARCHAR(16)   DEFAULT "login" COMMENT "用途: login/register",
  is_used     TINYINT(1)    DEFAULT 0,
  expires_at  DATETIME      NOT NULL COMMENT "过期时间",
  created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="验证码表";

-- ---------- 用户计划表 ----------
CREATE TABLE IF NOT EXISTS `user_plans` (
  `user_id` int NOT NULL COMMENT '用户 ID',
  `name` varchar(100) NOT NULL COMMENT '计划名称',
  `goal` varchar(32) DEFAULT NULL COMMENT '目标',
  `description` text COMMENT '计划描述',
  `duration` varchar(32) DEFAULT NULL COMMENT '周期',
  `frequency` varchar(32) DEFAULT NULL COMMENT '频次',
  `difficulty` varchar(16) DEFAULT NULL COMMENT '难度',
  `difficulty_label` varchar(8) DEFAULT NULL COMMENT '难度中文名',
  `focus_tags` json DEFAULT NULL COMMENT '专注标签',
  `cover_url` varchar(256) DEFAULT NULL COMMENT '封面图',
  `weekly_schedule` json DEFAULT NULL COMMENT '周训安排',
  `is_active` tinyint(1) DEFAULT NULL,
  `source_plan_id` int DEFAULT NULL COMMENT '来源官方计划ID',
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- 训练日志表 ----------
CREATE TABLE IF NOT EXISTS `training_logs` (
  `user_id` int NOT NULL COMMENT '用户 ID',
  `plan_id` int NOT NULL COMMENT '计划 ID',
  `is_official` tinyint(1) DEFAULT NULL COMMENT '是否官方计划',
  `log_date` date NOT NULL COMMENT '训练日期',
  `focus` varchar(32) DEFAULT NULL COMMENT '训练重点',
  `exercises` json DEFAULT NULL COMMENT '完成动作列表',
  `note` text COMMENT '备注',
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------- 身材记录快照 ----------
CREATE TABLE IF NOT EXISTS `body_records` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT 0 COMMENT '用户 ID',
  `record_date` DATE DEFAULT NULL COMMENT '记录日期',
  `stage` VARCHAR(16) DEFAULT NULL COMMENT '阶段: fatloss/muscle/maintain',
  `gender` VARCHAR(8) DEFAULT 'male' COMMENT '性别',
  `age` INT DEFAULT NULL COMMENT '年龄',
  `activity_level` VARCHAR(16) DEFAULT 'light' COMMENT '运动强度',
  `height_cm` DOUBLE DEFAULT NULL,
  `weight_kg` DOUBLE DEFAULT NULL,
  `waist_cm` DOUBLE DEFAULT NULL,
  `hip_cm` DOUBLE DEFAULT NULL,
  `neck_cm` DOUBLE DEFAULT NULL,
  `chest_cm` DOUBLE DEFAULT NULL,
  `shoulder_cm` DOUBLE DEFAULT NULL,
  `thigh_cm` DOUBLE DEFAULT NULL,
  `arm_cm` DOUBLE DEFAULT NULL,
  `calf_cm` DOUBLE DEFAULT NULL,
  `bmi` DOUBLE DEFAULT NULL,
  `body_fat` DOUBLE DEFAULT NULL,
  `bmr` DOUBLE DEFAULT NULL,
  `tdee` DOUBLE DEFAULT NULL,
  `whr` DOUBLE DEFAULT NULL,
  `muscle_mass` DOUBLE DEFAULT NULL,
  `standard_weight` DOUBLE DEFAULT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_records_user_date` (`user_id`, `record_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='身材数据快照';

-- ---------- 目标身材设定 ----------
CREATE TABLE IF NOT EXISTS `body_goals` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT 0 COMMENT '用户 ID',
  `target_weight` DOUBLE DEFAULT NULL COMMENT '目标体重 kg',
  `target_bmi` DOUBLE DEFAULT NULL COMMENT '目标 BMI',
  `target_body_fat` DOUBLE DEFAULT NULL COMMENT '目标体脂率 %',
  `daily_calorie` DOUBLE DEFAULT NULL COMMENT '每日目标摄入 kcal',
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_goals_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='目标身材设定';

-- ---------- 个人基础档案 ----------
CREATE TABLE IF NOT EXISTS `body_profiles` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT 0 UNIQUE COMMENT '用户 ID',
  `gender` VARCHAR(8) DEFAULT 'male',
  `age` INT DEFAULT 25,
  `activity_level` VARCHAR(16) DEFAULT 'light',
  `unit_system` VARCHAR(8) DEFAULT 'metric',
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='个人基础档案';

-- ---------- AI 饮食方案存档 ----------
CREATE TABLE IF NOT EXISTS `diet_plans` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT 0 COMMENT '用户 ID',
  `target` VARCHAR(16) DEFAULT 'fatloss' COMMENT '目标: fatloss/muscle/maintain',
  `sport_level` VARCHAR(32) DEFAULT NULL COMMENT '运动强度',
  `diet_limit` VARCHAR(256) DEFAULT NULL COMMENT '饮食限制与偏好',
  `eat_scene` VARCHAR(64) DEFAULT NULL COMMENT '就餐条件',
  `plan_json` TEXT COMMENT '结构化方案 JSON',
  `raw_text` TEXT COMMENT '模型原始输出',
  `model` VARCHAR(64) DEFAULT NULL COMMENT '模型名称',
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_diet_plans_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI 饮食方案存档';

-- ---------- 每日饮食打卡 ----------
CREATE TABLE IF NOT EXISTS `diet_logs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT DEFAULT 0 COMMENT '用户 ID',
  `log_date` DATE DEFAULT NULL COMMENT '打卡日期',
  `calories` DOUBLE DEFAULT NULL COMMENT '当日摄入热量 kcal',
  `protein_g` DOUBLE DEFAULT NULL COMMENT '蛋白质 g',
  `carbs_g` DOUBLE DEFAULT NULL COMMENT '碳水 g',
  `fat_g` DOUBLE DEFAULT NULL COMMENT '脂肪 g',
  `note` VARCHAR(256) DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_diet_logs_user_date` (`user_id`, `log_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日饮食打卡';

-- ---------- 资料修改申请表 ----------
CREATE TABLE IF NOT EXISTS `profile_change_requests` (
  `user_id` int NOT NULL,
  `field_name` varchar(32) NOT NULL,
  `old_value` varchar(256) DEFAULT NULL,
  `new_value` varchar(256) NOT NULL,
  `status` varchar(16) DEFAULT NULL,
  `remark` varchar(256) DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

