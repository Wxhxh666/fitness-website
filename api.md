# FITLUXE · 接口文档

> **版本**：v1.0 · 2026-07-21  
> **基准 URL**：`http://localhost:8000/api`  
> **响应格式**：统一 JSON 结构 `{ "code": int, "msg": str, "data": any }`

---

**目录**

1. [通用约定](#1-通用约定)
2. [动作教学 (Exercises)](#2-动作教学-exercises)
3. [计划制定 (Plans)](#3-计划制定-plans)
4. [身材数据管理 (Body Data)](#4-身材数据管理-body-data)
5. [联系 (Contact)](#5-联系-contact)
6. [附录：数据模型](#6-附录数据模型)

---

## 1. 通用约定

### 1.1 统一响应格式

```json
{
  "code": 0,
  "msg": "success",
  "data": {}
}
```

| 字段   | 类型   | 说明                       |
|--------|--------|----------------------------|
| `code` | int    | 0 成功；非 0 为错误码      |
| `msg`  | string | 成功返回 "success"，失败返回错误描述 |
| `data` | any    | 业务数据对象或数组          |

### 1.2 常见错误码

| 错误码 | 说明         |
|--------|--------------|
| 400    | 请求参数错误 |
| 404    | 资源不存在   |
| 500    | 服务器内部错误 |

### 1.3 分页请求参数

| 参数       | 类型 | 必填 | 说明    | 默认值 |
|------------|------|------|---------|--------|
| `page`     | int  | 否   | 页码    | 1      |
| `page_size`| int  | 否   | 每页条数 | 20     |

### 1.4 分页响应格式

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 2. 动作教学 (Exercises)

### 2.1 获取动作分类列表

前端在动作教学页面顶部展示 6 个分类标签（胸部、背部、腿部、肩部、腹部、全身），点击即切换动作列表。

**`GET /exercises/categories`**

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    { "key": "chest",     "label": "胸部", "sort_order": 1 },
    { "key": "back",      "label": "背部", "sort_order": 2 },
    { "key": "legs",      "label": "腿部", "sort_order": 3 },
    { "key": "shoulders", "label": "肩部", "sort_order": 4 },
    { "key": "abs",       "label": "腹部", "sort_order": 5 },
    { "key": "fullbody",  "label": "全身", "sort_order": 6 }
  ]
}
```

### 2.2 获取动作列表

**`GET /exercises`**

**请求参数**：

| 参数         | 类型   | 必填 | 说明               | 默认值 |
|--------------|--------|------|--------------------|--------|
| `category`   | string | 否   | 分类 key，不传返回全部 | —    |
| `difficulty` | string | 否   | 难度筛选           | —      |
| `keyword`    | string | 否   | 搜索关键词（名称）   | —      |

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "name": "杠铃卧推",
      "category": "chest",
      "category_label": "胸部",
      "description": "经典胸大肌训练动作，有效增强胸部厚度与力量。",
      "difficulty": "intermediate",
      "difficulty_label": "中级",
      "duration": "12-15 次 × 4组",
      "cover_url": "/images/exercises/bench-press.jpg",
      "video_url": "/videos/exercises/bench-press.mp4",
      "created_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

> **字段对应**：前端 `Exercise` 接口中的 `desc` 对应后端 `description`；`icon` / `gradient` 为前端展示用，后端不需要存储。

### 2.3 获取动作详情

**`GET /exercises/:id`**

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "name": "杠铃卧推",
    "category": "chest",
    "category_label": "胸部",
    "description": "经典胸大肌训练动作，有效增强胸部厚度与力量。",
    "difficulty": "intermediate",
    "difficulty_label": "中级",
    "duration": "12-15 次 × 4组",
    "cover_url": "/images/exercises/bench-press.jpg",
    "video_url": "/videos/exercises/bench-press.mp4",
    "steps": [
      { "order": 1, "content": "平躺于卧推凳，双脚踩实地面，肩胛骨收紧后贴凳面。" },
      { "order": 2, "content": "正握杠铃，双手间距略宽于肩，从架子上推起杠铃。" },
      { "order": 3, "content": "缓慢下放至杠铃触胸，保持肘部与身体呈 75 度角。" },
      { "order": 4, "content": "发力推起至手臂接近伸直，顶峰收缩 1 秒。" }
    ],
    "target_muscles": ["胸大肌", "三角肌前束", "肱三头肌"],
    "tips": ["下落时吸气，推起时呼气", "避免借力或过度弓腰"],
    "created_at": "2026-01-15T10:00:00Z"
  }
}
```

---

## 3. 计划制定 (Plans)

### 3.1 获取训练目标列表

前端展示 4 个训练目标卡片（增肌塑形、减脂塑形、力量提升、耐力提升），点击切换方案列表。

**`GET /plans/goals`**

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    { "key": "muscle",    "label": "增肌塑形", "description": "增加肌肉量与力量" },
    { "key": "fatloss",   "label": "减脂塑形", "description": "降低体脂率、刻画线条" },
    { "key": "strength",  "label": "力量提升", "description": "突破力量瓶颈" },
    { "key": "endurance", "label": "耐力提升", "description": "提升心肺与持久力" }
  ]
}
```

### 3.2 获取训练计划列表

**`GET /plans`**

**请求参数**：

| 参数         | 类型   | 必填 | 说明               | 默认值 |
|--------------|--------|------|--------------------|--------|
| `goal`       | string | 否   | 目标 key，不传返回全部 | —    |
| `difficulty` | string | 否   | 难度筛选           | —      |

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "name": "经典五分化训练",
      "goal": "muscle",
      "badge": "推荐",
      "description": "每天专注一个肌群，充分刺激与恢复，适合有条理的训练者。",
      "duration": "12 周",
      "frequency": "5 天 / 周",
      "difficulty": "intermediate",
      "difficulty_label": "中级",
      "focus_tags": ["胸", "背", "肩", "腿", "臂"],
      "cover_url": "/images/plans/five-day-split.jpg",
      "created_at": "2026-02-01T10:00:00Z"
    }
  ]
}
```

> 前端 `Plan` 接口中的 `focus` 对应后端 `focus_tags`；前端 `desc` 对应后端 `description`。

### 3.3 获取计划详情

**`GET /plans/:id`**

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "name": "经典五分化训练",
    "goal": "muscle",
    "badge": "推荐",
    "description": "每天专注一个肌群，充分刺激与恢复，适合有条理的训练者。",
    "duration": "12 周",
    "frequency": "5 天 / 周",
    "difficulty": "intermediate",
    "difficulty_label": "中级",
    "focus_tags": ["胸", "背", "肩", "腿", "臂"],
    "cover_url": "/images/plans/five-day-split.jpg",
    "weekly_schedule": [
      {
        "day": "周一",
        "focus": "胸部",
        "exercises": [
          { "exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12" },
          { "exercise_id": 2, "name": "哑铃飞鸟", "sets": 4, "reps": "12-15" }
        ]
      }
    ],
    "created_at": "2026-02-01T10:00:00Z"
  }
}
```

---

## 4. 身材数据管理 (Body Data)

### 4.1 获取核心指标

前端首页看板展示 4 个核心指标卡片：体重、体脂率、肌肉量、基础代谢。

**`GET /body-metrics`**

**请求参数**：

| 参数      | 类型 | 必填 | 说明     | 默认值 |
|-----------|------|------|----------|--------|
| `user_id` | int  | 否   | 用户 ID（未登录返回默认） | — |

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "key": "weight",
      "label": "体重",
      "value": 72.5,
      "unit": "kg",
      "change": -1.2,
      "trend": "down"
    },
    {
      "key": "body_fat",
      "label": "体脂率",
      "value": 15.6,
      "unit": "%",
      "change": -0.8,
      "trend": "down"
    },
    {
      "key": "muscle_mass",
      "label": "肌肉量",
      "value": 34.2,
      "unit": "kg",
      "change": 0.6,
      "trend": "up"
    },
    {
      "key": "bmr",
      "label": "基础代谢",
      "value": 1685,
      "unit": "kcal",
      "change": 35,
      "trend": "up"
    }
  ]
}
```

> **字段说明**：`value` 为数字类型；`change` 为差值（正数增加，负数减少）；`trend` 为趋势方向：`up` 上升 / `down` 下降。

### 4.2 计算 BMI

**`POST /body-metrics/bmi`**

**请求体**：
```json
{
  "height_cm": 175,
  "weight_kg": 72.5
}
```

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "bmi": 23.7,
    "category": "normal",
    "category_label": "正常范围",
    "healthy_range": "18.5 – 24.9"
  }
}
```

| `category` 值   | 说明 |
|-----------------|------|
| `underweight`   | 偏瘦 |
| `normal`        | 正常范围 |
| `overweight`    | 超重 |
| `obese`         | 肥胖 |

### 4.3 获取围度测量列表

前端展示 6 个身体部位的围度测量卡：胸围、腰围、臀围、上臂围、大腿围、小腿围。

**`GET /body-metrics/measurements`**

**请求参数**：

| 参数      | 类型 | 必填 | 说明     | 默认值 |
|-----------|------|------|----------|--------|
| `user_id` | int  | 否   | 用户 ID  | —      |

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    { "id": 1, "key": "chest", "label": "胸围",   "value": 102.0, "unit": "cm", "recorded_at": "2026-07-21T10:00:00Z" },
    { "id": 2, "key": "waist", "label": "腰围",   "value": 78.0,  "unit": "cm", "recorded_at": "2026-07-21T10:00:00Z" },
    { "id": 3, "key": "hips",  "label": "臀围",   "value": 96.0,  "unit": "cm", "recorded_at": "2026-07-21T10:00:00Z" },
    { "id": 4, "key": "arm",   "label": "上臂围", "value": 36.0,  "unit": "cm", "recorded_at": "2026-07-21T10:00:00Z" },
    { "id": 5, "key": "thigh", "label": "大腿围", "value": 54.0,  "unit": "cm", "recorded_at": "2026-07-21T10:00:00Z" },
    { "id": 6, "key": "calf",  "label": "小腿围", "value": 37.0,  "unit": "cm", "recorded_at": "2026-07-21T10:00:00Z" }
  ]
}
```

### 4.4 更新围度测量值

**`PUT /body-metrics/measurements/:id`**

**请求体**：
```json
{
  "value": 80.5
}
```

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 2,
    "key": "waist",
    "label": "腰围",
    "value": 80.5,
    "unit": "cm",
    "previous_value": 78.0,
    "recorded_at": "2026-07-21T12:00:00Z"
  }
}
```

### 4.5 获取历史趋势数据

供未来扩展趋势图表使用。

**`GET /body-metrics/history`**

| 参数          | 类型   | 必填 | 说明                       | 默认值 |
|---------------|--------|------|----------------------------|--------|
| `metric_key`  | string | 否   | 指标 key，不传返回全部      | —      |
| `days`        | int    | 否   | 最近多少天的数据            | 30     |

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "metric_key": "weight",
      "records": [
        { "date": "2026-06-21", "value": 74.0 },
        { "date": "2026-06-28", "value": 73.2 },
        { "date": "2026-07-05", "value": 72.8 },
        { "date": "2026-07-12", "value": 72.5 },
        { "date": "2026-07-19", "value": 72.3 }
      ]
    }
  ]
}
```

---

## 5. 联系 (Contact)

### 5.1 提交留言

**`POST /contact`**

**请求体**：
```json
{
  "name": "张三",
  "email": "zhangsan@example.com",
  "phone": "13800138000",
  "subject": "course",
  "message": "您好，我想了解更多关于增肌训练课程的信息。"
}
```

| 字段      | 类型   | 必填 | 说明                                           |
|-----------|--------|------|------------------------------------------------|
| `name`    | string | 是   | 姓名                                           |
| `email`   | string | 是   | 邮箱，需符合 email 格式                        |
| `phone`   | string | 否   | 电话，可选                                      |
| `subject` | string | 是   | 主题枚举：`course`(课程咨询) / `plan`(计划定制) / `coach`(教练预约) / `partner`(合作洽谈) / `other`(其他) |
| `message` | string | 是   | 留言内容                                       |

**前端表单验证规则**（后端需同步）：

| 字段      | 规则                              |
|-----------|-----------------------------------|
| `name`    | 必填，最大 50 字符                |
| `email`   | 必填，有效 email 格式             |
| `subject` | 必填，须为枚举值之一              |
| `message` | 必填，最大 2000 字符              |

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "created_at": "2026-07-21T12:00:00Z"
  }
}
```

### 5.2 获取站点联系信息

前端联系页面右侧展示地址、电话、邮箱、营业时间。

**`GET /site/contact-info`**

**响应示例**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "address": "上海市静安区南京西路1788号久光中心 12F",
    "phone": "+86 21 6188 3000",
    "email": "hello@fitluxe.com",
    "business_hours": {
      "weekday": "7:00 – 22:00",
      "weekend": "8:00 – 20:00"
    },
    "social_media": [
      { "platform": "wechat",      "name": "微信" },
      { "platform": "weibo",       "name": "微博" },
      { "platform": "xiaohongshu", "name": "小红书" },
      { "platform": "douyin",      "name": "抖音" }
    ]
  }
}
```

---

## 6. 附录：数据模型

### 6.1 Exercise（动作）

| 字段               | 类型       | 说明                                |
|--------------------|------------|-------------------------------------|
| `id`               | int        | 主键                                |
| `name`             | string     | 动作名称                             |
| `category`         | string     | 所属分类 key                        |
| `category_label`   | string     | 分类中文名                           |
| `description`      | string     | 动作描述（前端字段 `desc`）          |
| `difficulty`       | string     | 难度：`beginner` / `intermediate` / `advanced` |
| `difficulty_label` | string     | 难度中文名：入门 / 中级 / 高级        |
| `duration`         | string     | 建议组数，如"12-15 次 × 4组"         |
| `cover_url`        | string     | 封面图片 URL                        |
| `video_url`        | string     | 教学视频 URL（可选）                 |
| `steps`            | array      | 步骤说明列表（可选）                  |
| `target_muscles`   | string[]   | 目标肌群（可选）                      |
| `tips`             | string[]   | 注意事项（可选）                      |
| `sort_order`       | int        | 排序权重（可选）                      |
| `is_active`        | bool       | 是否上架                             |
| `created_at`       | datetime   | 创建时间                             |
| `updated_at`       | datetime   | 更新时间                             |

### 6.2 Plan（训练计划）

| 字段                | 类型       | 说明                                |
|---------------------|------------|-------------------------------------|
| `id`                | int        | 主键                                |
| `name`              | string     | 计划名称                             |
| `goal`              | string     | 目标 key                            |
| `badge`             | string     | 标签，如"推荐" / "进阶"              |
| `description`       | string     | 计划描述                             |
| `duration`          | string     | 周期，如 "12 周"                     |
| `frequency`         | string     | 频次，如 "5 天 / 周"                 |
| `difficulty`        | string     | 难度                                |
| `difficulty_label`  | string     | 难度中文名                           |
| `focus_tags`        | string[]   | 专注标签（前端字段 `focus`）          |
| `cover_url`         | string     | 封面图（可选）                        |
| `weekly_schedule`   | array      | 周训安排（可选）                      |
| `is_active`         | bool       | 是否上架                             |
| `created_at`        | datetime   | 创建时间                             |
| `updated_at`        | datetime   | 更新时间                             |

#### weekly_schedule 子项

| 字段        | 类型   | 说明              |
|-------------|--------|-------------------|
| `day`       | string | 周几，如 "周一"    |
| `focus`     | string | 训练重点          |
| `exercises` | array  | 动作子列表         |

#### exercises 子项

| 字段          | 类型   | 说明           |
|---------------|--------|----------------|
| `exercise_id` | int    | 动作 ID        |
| `name`        | string | 动作名称        |
| `sets`        | int    | 组数            |
| `reps`        | string | 次数，如"10-12" |

### 6.3 BodyMetric（核心指标/围度）

| 字段          | 类型       | 说明                  |
|---------------|------------|-----------------------|
| `id`          | int        | 主键                  |
| `user_id`     | int        | 用户 ID               |
| `key`         | string     | 指标 key              |
| `label`       | string     | 指标中文名             |
| `value`       | decimal    | 当前值                 |
| `unit`        | string     | 单位                   |
| `recorded_at` | datetime   | 记录时间               |

**`key` 枚举值**：`weight`(体重)、`body_fat`(体脂率)、`muscle_mass`(肌肉量)、`bmr`(基础代谢)、`chest`(胸围)、`waist`(腰围)、`hips`(臀围)、`arm`(上臂围)、`thigh`(大腿围)、`calf`(小腿围)。

### 6.4 ContactMessage（联系留言）

| 字段         | 类型       | 说明             |
|--------------|------------|------------------|
| `id`         | int        | 主键              |
| `name`       | string     | 姓名              |
| `email`      | string     | 邮箱              |
| `phone`      | string     | 电话（可选）       |
| `subject`    | string     | 主题枚举值         |
| `message`    | string     | 留言内容           |
| `is_read`    | bool       | 是否已读           |
| `created_at` | datetime   | 创建时间           |

### 6.5 ExerciseCategory（动作分类）

| 字段         | 类型   | 说明        |
|--------------|--------|-------------|
| `key`        | string | 唯一标识     |
| `label`      | string | 中文名称     |
| `sort_order` | int    | 排序权重     |

### 6.6 PlanGoal（训练目标）

| 字段          | 类型   | 说明        |
|---------------|--------|-------------|
| `key`         | string | 唯一标识     |
| `label`       | string | 中文名称     |
| `description` | string | 简短描述     |

### 6.7 SiteInfo（站点信息）

| 字段             | 类型   | 说明          |
|------------------|--------|---------------|
| `address`        | string | 地址          |
| `phone`          | string | 联系电话       |
| `email`          | string | 邮箱          |
| `business_hours` | object | 营业时间       |
| `social_media`   | array  | 社交媒体列表   |

---

## 附录：前端字段映射速查

| 前端字段名         | 对应后端字段    | 说明                              |
|--------------------|-----------------|-----------------------------------|
| `ex.desc`          | `description`   | 动作/计划描述                      |
| `ex.icon`          | —               | 前端展示用字符图标，后端无需存储    |
| `ex.gradient`      | —               | 前端展示用渐变配色，后端无需存储    |
| `ex.difficulty`    | `difficulty`    | 后端存储 key，前端映射中文          |
| `plan.desc`        | `description`   | 计划描述                          |
| `plan.focus`       | `focus_tags`    | 重点标签数组（字段名称不同）         |
| `m.icon`           | —               | Element Plus 图标名，后端无需存储   |
| `item.input`       | —               | 前端临时编辑框绑定，见 4.4 更新接口 |
