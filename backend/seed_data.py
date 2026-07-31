"""
FITLUXE · 数据初始化种子脚本
用法: 在虚拟环境 py1 下执行
  python seed_data.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.exercise import ExerciseCategory, Exercise
from models.plan import PlanGoal, Plan
from models.body_metric import BodyMetric
from models.site import SiteInfo


def ok(msg):
    print(f"  [OK] {msg}")


def seed_categories():
    items = [
        {"key": "chest", "label": "胸部", "weekly_schedule": [{"day": "周一", "focus": "胸部", "exercises": [{"exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12"}]}, {"day": "周二", "focus": "背部", "exercises": [{"exercise_id": 6, "name": "引体向上", "sets": 4, "reps": "8-12"}]}, {"day": "周三", "focus": "肩部", "exercises": [{"exercise_id": 14, "name": "哑铃侧平举", "sets": 4, "reps": "12-15"}]}, {"day": "周四", "focus": "腿部", "exercises": [{"exercise_id": 10, "name": "杠铃深蹲", "sets": 4, "reps": "8-12"}]}, {"day": "周五", "focus": "腹部", "exercises": [{"exercise_id": 18, "name": "悬垂举腿", "sets": 3, "reps": "12-15"}]}]},
        {"key": "back", "label": "背部"},
        {"key": "legs", "label": "腿部", "sort_order": 3},
        {"key": "shoulders", "label": "肩部", "sort_order": 4},
        {"key": "abs", "label": "腹部", "sort_order": 5},
        {"key": "fullbody", "label": "全身", "sort_order": 6},
    ]
    for d in items:
        if not ExerciseCategory.query.filter_by(key=d["key"]).first():
            db.session.add(ExerciseCategory(**d))
    db.session.commit()
    ok("动作分类")


def seed_exercises():
    items = [
        {"name": "杠铃卧推", "category": "chest", "category_label": "胸部", "description": "经典胸大肌训练动作，有效增强胸部厚度与力量。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "12-15 次 x 4组"},
        {"name": "哑铃飞鸟", "category": "chest", "category_label": "胸部", "description": "孤立刺激胸肌外侧与中缝，打造胸肌轮廓线条。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "12-15 次 x 4组"},
        {"name": "上斜哑铃推举", "category": "chest", "category_label": "胸部", "description": "重点强化上胸束，提升胸部的整体饱满度。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "10-12 次 x 4组", "sort_order": 3},
        {"name": "绳索夹胸", "category": "chest", "category_label": "胸部", "description": "通过绳索的高低位变化，全面刺激不同角度。", "difficulty": "advanced", "difficulty_label": "高级", "duration": "12-15 次 x 4组", "sort_order": 4},
        {"name": "俯卧撑", "category": "chest", "category_label": "胸部", "description": "无器械经典胸部训练，多种变式可调节难度。", "difficulty": "beginner", "difficulty_label": "入门", "duration": "15-20 次 x 4组", "sort_order": 5},
        {"name": "引体向上", "category": "back", "category_label": "背部", "description": "背部宽度的王牌训练动作，强化背阔肌。", "difficulty": "advanced", "difficulty_label": "高级", "duration": "8-12 次 x 4组"},
        {"name": "杠铃划船", "category": "back", "category_label": "背部", "description": "增加背厚度的核心动作，同时强化后链肌群。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "10-12 次 x 4组"},
        {"name": "高位下拉", "category": "back", "category_label": "背部", "description": "引体向上的替代与辅助动作，有效加宽背部。", "difficulty": "beginner", "difficulty_label": "入门", "duration": "12-15 次 x 4组", "sort_order": 3},
        {"name": "单臂哑铃划船", "category": "back", "category_label": "背部", "description": "单侧训练可纠正两侧肌力不平衡。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "10-12 次 x 4组", "sort_order": 4},
        {"name": "杠铃深蹲", "category": "legs", "category_label": "腿部", "description": "腿部训练之王，全面刺激股四头肌、臀大肌与核心。", "difficulty": "advanced", "difficulty_label": "高级", "duration": "8-12 次 x 5组"},
        {"name": "罗马尼亚硬拉", "category": "legs", "category_label": "腿部", "description": "强化腘绳肌与臀部的最佳动作，提升运动表现。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "10-12 次 x 4组"},
        {"name": "腿举机", "category": "legs", "category_label": "腿部", "description": "安全高效的腿部复合动作，可承受较大负荷。", "difficulty": "beginner", "difficulty_label": "入门", "duration": "12-15 次 x 4组", "sort_order": 3},
        {"name": "保加利亚分腿蹲", "category": "legs", "category_label": "腿部", "description": "单腿训练改善稳定性，对臀大肌刺激极佳。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "10-12 次 x 4组", "sort_order": 4},
        {"name": "哑铃侧平举", "category": "shoulders", "category_label": "肩部", "description": "孤立刺激三角肌中束，打造肩部宽度。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "12-15 次 x 4组"},
        {"name": "杠铃推举", "category": "shoulders", "category_label": "肩部", "description": "三角肌前束与中束的复合推举动作。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "8-12 次 x 4组"},
        {"name": "阿诺德推举", "category": "shoulders", "category_label": "肩部", "description": "旋转与推举结合，多角度刺激三角肌各束。", "difficulty": "advanced", "difficulty_label": "高级", "duration": "10-12 次 x 4组", "sort_order": 3},
        {"name": "卷腹", "category": "abs", "category_label": "腹部", "description": "腹直肌的基础训练动作，控制节奏效果更佳。", "difficulty": "beginner", "difficulty_label": "入门", "duration": "15-20 次 x 4组"},
        {"name": "悬垂举腿", "category": "abs", "category_label": "腹部", "description": "发展核心力量与下腹部的顶级动作。", "difficulty": "advanced", "difficulty_label": "高级", "duration": "10-15 次 x 4组"},
        {"name": "俄罗斯转体", "category": "abs", "category_label": "腹部", "description": "强化腹斜肌与旋转稳定性，刻画腰部线条。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "16-20 次 x 4组", "sort_order": 3},
        {"name": "波比跳", "category": "fullbody", "category_label": "全身", "description": "全身燃脂王牌动作，调动全身肌群的高强度训练。", "difficulty": "advanced", "difficulty_label": "高级", "duration": "12-15 次 x 4组"},
        {"name": "壶铃摆荡", "category": "fullbody", "category_label": "全身", "description": "发展爆发力与心肺功能，强化后链动力链。", "difficulty": "intermediate", "difficulty_label": "中级", "duration": "15-20 次 x 4组"},
        {"name": "平板支撑", "category": "fullbody", "category_label": "全身", "description": "核心稳定的基础训练，建立身体张力的基础。", "difficulty": "beginner", "difficulty_label": "入门", "duration": "45-60秒 x 4组", "sort_order": 3},
    ]
    for d in items:
        if not Exercise.query.filter_by(name=d["name"]).first():
            db.session.add(Exercise(**d))
    db.session.commit()
    ok(f"动作库 ({len(items)}条)")


def seed_goals():
    items = [
        {"key": "muscle", "label": "增肌塑形", "description": "增加肌肉量与力量"},
        {"key": "fatloss", "label": "减脂塑形", "description": "降低体脂率、刻画线条"},
        {"key": "strength", "label": "力量提升", "description": "突破力量瓶颈", "sort_order": 3},
        {"key": "endurance", "label": "耐力提升", "description": "提升心肺与持久力", "sort_order": 4},
    ]
    for d in items:
        if not PlanGoal.query.filter_by(key=d["key"]).first():
            db.session.add(PlanGoal(**d))
    db.session.commit()
    ok("训练目标")


def seed_plans():
    items = [
        {"name": "经典五分化训练", "goal": "muscle", "badge": "推荐", "description": "每天专注一个肌群，充分刺激与恢复，适合有条理的训练者。", "duration": "12 周", "frequency": "5 天 / 周", "difficulty": "intermediate", "difficulty_label": "中级", "focus_tags": ["胸", "背", "肩", "腿", "臂"], "weekly_schedule": [{"day": "周一", "focus": "胸部", "exercises": [{"exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12"}]}, {"day": "周二", "focus": "背部", "exercises": [{"exercise_id": 6, "name": "引体向上", "sets": 4, "reps": "8-12"}]}, {"day": "周三", "focus": "肩部", "exercises": [{"exercise_id": 14, "name": "哑铃侧平举", "sets": 4, "reps": "12-15"}]}, {"day": "周四", "focus": "腿部", "exercises": [{"exercise_id": 10, "name": "杠铃深蹲", "sets": 4, "reps": "8-12"}]}, {"day": "周五", "focus": "腹部", "exercises": [{"exercise_id": 18, "name": "悬垂举腿", "sets": 3, "reps": "12-15"}]}]},
        {"name": "推拉腿分化", "goal": "muscle", "badge": "进阶", "description": "按动作模式分化训练，频率更高、刺激更全面，增肌效率优异。", "duration": "8 周", "frequency": "6 天 / 周", "difficulty": "advanced", "difficulty_label": "高级", "focus_tags": ["推类", "拉类", "腿部"], "weekly_schedule": [{"day": "周一", "focus": "推类", "exercises": [{"exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12"}]}, {"day": "周二", "focus": "拉类", "exercises": [{"exercise_id": 6, "name": "引体向上", "sets": 4, "reps": "8-12"}]}, {"day": "周三", "focus": "腿部", "exercises": [{"exercise_id": 10, "name": "杠铃深蹲", "sets": 4, "reps": "8-12"}]}]},
        {"name": "新手全身训练", "goal": "muscle", "badge": "入门", "description": "每次训练涵盖全身主要肌群，建立基础力量与动作模式。", "duration": "8 周", "frequency": "3 天 / 周", "difficulty": "beginner", "difficulty_label": "入门", "focus_tags": ["全身", "核心", "基础"], "sort_order": 3},
        {"name": "HIIT 燃脂计划", "goal": "fatloss", "badge": "高效", "description": "高强度间歇训练与有氧结合，快速提升代谢与脂肪燃烧。", "duration": "6 周", "frequency": "5 天 / 周", "difficulty": "intermediate", "difficulty_label": "中级", "focus_tags": ["燃脂", "心肺", "全身"], "weekly_schedule": [{"day": "周一", "focus": "胸部", "exercises": [{"exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12"}]}, {"day": "周二", "focus": "背部", "exercises": [{"exercise_id": 6, "name": "引体向上", "sets": 4, "reps": "8-12"}]}, {"day": "周三", "focus": "肩部", "exercises": [{"exercise_id": 14, "name": "哑铃侧平举", "sets": 4, "reps": "12-15"}]}, {"day": "周四", "focus": "腿部", "exercises": [{"exercise_id": 10, "name": "杠铃深蹲", "sets": 4, "reps": "8-12"}]}, {"day": "周五", "focus": "腹部", "exercises": [{"exercise_id": 18, "name": "悬垂举腿", "sets": 3, "reps": "12-15"}]}]},
        {"name": "渐进塑形计划", "goal": "fatloss", "badge": "推荐", "description": "力量训练配合有氧，在减脂同时保留肌肉，塑造紧致线条。", "duration": "12 周", "frequency": "4 天 / 周", "difficulty": "intermediate", "difficulty_label": "中级", "focus_tags": ["力量", "有氧", "塑形"], "weekly_schedule": [{"day": "周一", "focus": "推类", "exercises": [{"exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12"}]}, {"day": "周二", "focus": "拉类", "exercises": [{"exercise_id": 6, "name": "引体向上", "sets": 4, "reps": "8-12"}]}, {"day": "周三", "focus": "腿部", "exercises": [{"exercise_id": 10, "name": "杠铃深蹲", "sets": 4, "reps": "8-12"}]}]},
        {"name": "低碳适应计划", "goal": "fatloss", "badge": "专项", "description": "配合低碳饮食策略的低强度训练方案，加速体脂下降。", "duration": "4 周", "frequency": "3 天 / 周", "difficulty": "beginner", "difficulty_label": "入门", "focus_tags": ["低强度", "燃脂", "恢复"], "sort_order": 3},
        {"name": "5×5 力量突破", "goal": "strength", "badge": "经典", "description": "久经考验的力量训练方案，专注复合动作提高绝对力量。", "duration": "12 周", "frequency": "3 天 / 周", "difficulty": "intermediate", "difficulty_label": "中级", "focus_tags": ["深蹲", "卧推", "硬拉"], "weekly_schedule": [{"day": "周一", "focus": "胸部", "exercises": [{"exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12"}]}, {"day": "周二", "focus": "背部", "exercises": [{"exercise_id": 6, "name": "引体向上", "sets": 4, "reps": "8-12"}]}, {"day": "周三", "focus": "肩部", "exercises": [{"exercise_id": 14, "name": "哑铃侧平举", "sets": 4, "reps": "12-15"}]}, {"day": "周四", "focus": "腿部", "exercises": [{"exercise_id": 10, "name": "杠铃深蹲", "sets": 4, "reps": "8-12"}]}, {"day": "周五", "focus": "腹部", "exercises": [{"exercise_id": 18, "name": "悬垂举腿", "sets": 3, "reps": "12-15"}]}]},
        {"name": "举重专项计划", "goal": "strength", "badge": "进阶", "description": "包含抓举与挺举技术训练，发展爆发力与神经协调能力。", "duration": "16 周", "frequency": "5 天 / 周", "difficulty": "advanced", "difficulty_label": "高级", "focus_tags": ["爆发力", "技术", "力量"], "weekly_schedule": [{"day": "周一", "focus": "推类", "exercises": [{"exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12"}]}, {"day": "周二", "focus": "拉类", "exercises": [{"exercise_id": 6, "name": "引体向上", "sets": 4, "reps": "8-12"}]}, {"day": "周三", "focus": "腿部", "exercises": [{"exercise_id": 10, "name": "杠铃深蹲", "sets": 4, "reps": "8-12"}]}]},
        {"name": "马拉松预备计划", "goal": "endurance", "badge": "推荐", "description": "系统提升心肺耐力与跑步经济性，为长跑赛事做好准备。", "duration": "16 周", "frequency": "5 天 / 周", "difficulty": "intermediate", "difficulty_label": "中级", "focus_tags": ["跑步", "耐力", "核心"], "weekly_schedule": [{"day": "周一", "focus": "胸部", "exercises": [{"exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12"}]}, {"day": "周二", "focus": "背部", "exercises": [{"exercise_id": 6, "name": "引体向上", "sets": 4, "reps": "8-12"}]}, {"day": "周三", "focus": "肩部", "exercises": [{"exercise_id": 14, "name": "哑铃侧平举", "sets": 4, "reps": "12-15"}]}, {"day": "周四", "focus": "腿部", "exercises": [{"exercise_id": 10, "name": "杠铃深蹲", "sets": 4, "reps": "8-12"}]}, {"day": "周五", "focus": "腹部", "exercises": [{"exercise_id": 18, "name": "悬垂举腿", "sets": 3, "reps": "12-15"}]}]},
        {"name": "循环耐力训练", "goal": "endurance", "badge": "综合", "description": "力量与有氧交替的循环训练，全面提升体能储备。", "duration": "8 周", "frequency": "4 天 / 周", "difficulty": "beginner", "difficulty_label": "入门", "focus_tags": ["综合体能", "心肺", "力量"], "weekly_schedule": [{"day": "周一", "focus": "推类", "exercises": [{"exercise_id": 1, "name": "杠铃卧推", "sets": 4, "reps": "10-12"}]}, {"day": "周二", "focus": "拉类", "exercises": [{"exercise_id": 6, "name": "引体向上", "sets": 4, "reps": "8-12"}]}, {"day": "周三", "focus": "腿部", "exercises": [{"exercise_id": 10, "name": "杠铃深蹲", "sets": 4, "reps": "8-12"}]}]},
    ]
    for d in items:
        if not Plan.query.filter_by(name=d["name"]).first():
            db.session.add(Plan(**d))
    db.session.commit()
    ok(f"训练计划 ({len(items)}条)")


def seed_metrics():
    items = [
        {"user_id": 0, "key": "weight", "label": "体重", "value": 72.5, "unit": "kg", "change": -1.2, "trend": "down"},
        {"user_id": 0, "key": "body_fat", "label": "体脂率", "value": 15.6, "unit": "%", "change": -0.8, "trend": "down"},
        {"user_id": 0, "key": "muscle_mass", "label": "肌肉量", "value": 34.2, "unit": "kg", "change": 0.6, "trend": "up"},
        {"user_id": 0, "key": "bmr", "label": "基础代谢", "value": 1685, "unit": "kcal", "change": 35, "trend": "up"},
        {"user_id": 0, "key": "chest", "label": "胸围", "value": 102.0, "unit": "cm", "change": 0, "trend": "up"},
        {"user_id": 0, "key": "waist", "label": "腰围", "value": 78.0, "unit": "cm", "change": 0, "trend": "down"},
        {"user_id": 0, "key": "hips", "label": "臀围", "value": 96.0, "unit": "cm", "change": 0, "trend": "up"},
        {"user_id": 0, "key": "arm", "label": "上臂围", "value": 36.0, "unit": "cm", "change": 0, "trend": "up"},
        {"user_id": 0, "key": "thigh", "label": "大腿围", "value": 54.0, "unit": "cm", "change": 0, "trend": "up"},
        {"user_id": 0, "key": "calf", "label": "小腿围", "value": 37.0, "unit": "cm", "change": 0, "trend": "up"},
    ]
    for d in items:
        if not BodyMetric.query.filter_by(user_id=d["user_id"], key=d["key"]).first():
            db.session.add(BodyMetric(**d))
    db.session.commit()
    ok(f"身体数据 ({len(items)}条)")


def seed_site_info():
    if SiteInfo.query.first():
        return
    info = SiteInfo(
        address="上海市静安区南京西路1788号久光中心 12F",
        phone="+86 21 6188 3000",
        email="hello@fitluxe.com",
        business_hours={"weekday": "7:00 - 22:00", "weekend": "8:00 - 20:00"},
        social_media=[
            {"platform": "wechat", "name": "微信"},
            {"platform": "weibo", "name": "微博"},
            {"platform": "xiaohongshu", "name": "小红书"},
            {"platform": "douyin", "name": "抖音"},
        ],
    )
    db.session.add(info)
    db.session.commit()
    ok("站点信息")


if __name__ == "__main__":
    with app.app_context():
        print("Seeding FITLUXE database...")
        db.create_all()
        seed_categories()
        seed_exercises()
        seed_goals()
        seed_plans()
        seed_metrics()
        seed_site_info()
        print("Done! All seed data inserted.")
