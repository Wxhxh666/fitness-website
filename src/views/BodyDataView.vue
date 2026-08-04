<template>
  <div class="bodydata-page">
    <!-- ============ 上半区：页面标题 + 核心指标总览 ============ -->
    <section class="page-hero">
      <div class="page-hero__bg"></div>
      <div class="page-hero__content container">
        <span class="page-hero__label">BODY ANALYTICS</span>
        <h1 class="page-hero__title">身材数据管理</h1>
        <p class="page-hero__desc">用数据量化每一分努力，科学追踪身体变化，让进步清晰可见。</p>
      </div>
    </section>

    <section class="profile-strip section section-light">
      <div class="container">
        <div class="profile-strip__inner">
          <div class="profile-strip__title">
            <span class="profile-strip__label">PERSONAL PROFILE</span>
            <h2 class="profile-strip__heading">个人基础档案</h2>
          </div>
          <div class="profile-strip__fields">
            <div class="profile-strip__field">
              <label>性别</label>
              <el-radio-group v-model="profile.gender" size="small">
                <el-radio-button value="male">男</el-radio-button>
                <el-radio-button value="female">女</el-radio-button>
              </el-radio-group>
            </div>
            <div class="profile-strip__field">
              <label>年龄</label>
              <el-input-number v-model="profile.age" :min="10" :max="100" :controls="false" style="width: 90px" />
            </div>
            <div class="profile-strip__field">
              <label>运动强度</label>
              <el-select v-model="profile.activity_level" style="width: 170px" size="small">
                <el-option v-for="opt in activityOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
              </el-select>
            </div>
            <div class="profile-strip__field">
              <label>单位</label>
              <el-radio-group v-model="unit" size="small">
                <el-radio-button value="metric">公制 cm/kg</el-radio-button>
                <el-radio-button value="imperial">英制 in/lb</el-radio-button>
              </el-radio-group>
            </div>
            <button class="btn-primary profile-strip__save" @click="saveProfile">保存档案</button>
          </div>
        </div>
      </div>
    </section>

    <section class="metrics section section-white">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">KEY METRICS</p>
          <h2 class="section-title">身体核心指标总览</h2>
          <div class="gold-divider"></div>
        </div>
        <div class="metrics__grid">
          <div v-for="(m, idx) in topMetrics" :key="idx" class="metric-card">
            <div class="metric-card__icon"><el-icon :size="24"><component :is="m.icon" /></el-icon></div>
            <div class="metric-card__info"><span class="metric-card__value">{{ m.value }}</span><span class="metric-card__unit">{{ m.unit }}</span></div>
            <span class="metric-card__label">{{ m.label }}</span>
            <div v-if="m.change !== null" class="metric-card__trend" :class="m.trendClass">
              <el-icon><component :is="m.trendClass === 'up' ? 'Top' : 'Bottom'" /></el-icon>{{ m.change }}
            </div>
            <div v-else class="metric-card__trend muted">较上次 --</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 中部：左计算器 / 右参考与趋势 ============ -->
    <section class="analytics section section-light">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">METRICS &amp; TRENDS</p>
          <h2 class="section-title">指标计算与趋势</h2>
          <div class="gold-divider"></div>
          <p class="section-desc">左侧计算 BMI、体脂率、BMR、TDEE 等多维指标；右侧对照 BMI 参考标准，并查看历史身材数据趋势。</p>
        </div>

        <div class="analytics__grid">
          <!-- 左栏：多指标计算器 -->
          <div class="analytics__left">
            <div class="panel-card">
              <div class="panel-card__head">
                <h3 class="panel-card__title"><el-icon><DataAnalysis /></el-icon>多指标计算器</h3>
                <span class="panel-card__tag">BMI / 体脂 / BMR / TDEE</span>
              </div>
              <div class="calc__form">
                <div class="calc__form-grid">
                  <div class="calc__field">
                    <label>身高（{{ heightUnitLabel }}）</label>
                    <el-input-number v-model="heightDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：175" style="width: 100%" />
                  </div>
                  <div class="calc__field">
                    <label>体重（{{ weightUnitLabel }}）</label>
                    <el-input-number v-model="weightDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：70" style="width: 100%" />
                  </div>
                  <div class="calc__field">
                    <label>腰围（{{ cmUnitLabel }}）</label>
                    <el-input-number v-model="calcWaistDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：78" style="width: 100%" />
                  </div>
                  <div class="calc__field">
                    <label>臀围（{{ cmUnitLabel }}）</label>
                    <el-input-number v-model="calcHipDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：96" style="width: 100%" />
                  </div>
                  <div class="calc__field">
                    <label>颈围（{{ cmUnitLabel }}，选填）</label>
                    <el-input-number v-model="calcNeckDisplay" :min="0" :step="0.1" :controls="false" placeholder="例：38" style="width: 100%" />
                  </div>
                  <div class="calc__field">
                    <label>运动强度</label>
                    <el-select v-model="profile.activity_level" style="width: 100%">
                      <el-option v-for="opt in activityOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                    </el-select>
                  </div>
                  <div class="calc__field">
                    <label>年龄</label>
                    <el-input-number v-model="profile.age" :min="10" :max="100" :controls="false" style="width: 100%" />
                  </div>
                  <div class="calc__field">
                    <label>性别</label>
                    <el-radio-group v-model="profile.gender" style="margin-top: 6px">
                      <el-radio-button value="male">男</el-radio-button>
                      <el-radio-button value="female">女</el-radio-button>
                    </el-radio-group>
                  </div>
                </div>
                <div class="calc__actions">
                  <button class="btn-primary" @click="onCalculate">计算全部指标</button>
                  <button class="btn-outline-dark" :disabled="!results" @click="openSaveDialog">保存本次记录</button>
                  <button class="btn-text" @click="clearCalcInputs">清空输入</button>
                </div>
                <p v-if="calcDirty" class="form-hint">参数已更新，点击「计算全部指标」刷新结果</p>
              </div>

              <div class="calc__results">
                <div v-if="!results" class="calc__empty">
                  <el-icon :size="36"><DataAnalysis /></el-icon>
                  <p>填写上方参数并点击「计算全部指标」，这里会展示完整的身体数据画像。</p>
                </div>
                <template v-else>
                  <div class="calc__cards">
                    <div v-for="m in metricCards" :key="m.key" class="metric-detail-card">
                      <div class="metric-detail-card__head">
                        <span class="metric-detail-card__label">{{ m.label }}</span>
                        <span v-if="m.tag" class="metric-detail-card__tag">{{ m.tag }}</span>
                      </div>
                      <div class="metric-detail-card__value">
                        <span class="metric-detail-card__num">{{ m.value }}</span>
                        <span class="metric-detail-card__unit">{{ m.unit }}</span>
                      </div>
                      <div v-if="m.category" class="metric-detail-card__category" :class="m.categoryClass">{{ m.category }}</div>
                      <div class="metric-detail-card__bar">
                        <div class="metric-detail-card__track">
                          <div class="metric-detail-card__healthy" :style="healthyStyle(m)"></div>
                          <div class="metric-detail-card__dot" :style="dotStyle(m)"></div>
                        </div>
                        <div class="metric-detail-card__scale"><span>{{ m.scale[0] }}</span><span>{{ m.scale[1] }}</span></div>
                      </div>
                    </div>
                  </div>

                  <div class="health-tips">
                    <h3 class="health-tips__title"><el-icon><FirstAidKit /></el-icon>健康风险简易评估</h3>
                    <ul class="health-tips__list">
                      <li v-for="(tip, i) in results.health_tips" :key="i" class="health-tips__item" :class="`health-tips__item--${tip.level}`">
                        <span class="health-tips__dot"></span>{{ tip.text }}
                      </li>
                    </ul>
                    <p class="health-tips__note">* 提示基于 BMI、体脂、腰围与年龄自动生成，仅作参考，不构成医疗建议。</p>
                  </div>
                </template>
              </div>
            </div>
          </div>

          <!-- 右栏：BMI 参考标准 + 历史趋势 -->
          <div class="analytics__right">
            <div class="panel-card">
              <div class="panel-card__head">
                <h3 class="panel-card__title"><el-icon><Scale /></el-icon>BMI 参考标准</h3>
              </div>
              <div class="bmi-guide">
                <div class="bmi-guide__row"><span class="bmi-guide__range">&lt; 18.5</span><span class="bmi-guide__label">偏瘦</span></div>
                <div class="bmi-guide__row"><span class="bmi-guide__range">18.5 – 24.9</span><span class="bmi-guide__label normal">正常范围</span></div>
                <div class="bmi-guide__row"><span class="bmi-guide__range">25 – 29.9</span><span class="bmi-guide__label">超重</span></div>
                <div class="bmi-guide__row"><span class="bmi-guide__range">≥ 30</span><span class="bmi-guide__label">肥胖</span></div>
                <p class="bmi-guide__note">* BMI 仅供参考，运动员等肌肉量较高的人群可能不适用，请结合体脂率判断。</p>
              </div>
            </div>

            <div class="panel-card">
              <div class="panel-card__head">
                <h3 class="panel-card__title"><el-icon><TrendCharts /></el-icon>历史身材数据趋势</h3>
              </div>
              <div class="trend-tools">
                <el-select v-model="rangeDays" size="small" style="width: 110px">
                  <el-option label="近 30 天" value="30" />
                  <el-option label="近 90 天" value="90" />
                  <el-option label="全部" value="all" />
                </el-select>
                <el-select v-model="chartMetric" size="small" style="width: 120px">
                  <el-option v-for="opt in trendMetricOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                </el-select>
                <el-radio-group v-model="chartGroup" size="small">
                  <el-radio-button value="record">按次</el-radio-button>
                  <el-radio-button value="week">按周</el-radio-button>
                  <el-radio-button value="month">按月</el-radio-button>
                </el-radio-group>
              </div>
              <LineChart :items="trendItems" :unit="trendUnit" color="#c9a96e" />
              <div class="trend-foot">
                <span class="trend-foot__hint">选择两条记录可自动生成对比小结</span>
                <button class="btn-outline-dark trend-foot__btn" @click="historyDialog.visible = true">数据存档与对比</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 下半区：AI 智能饮食规划 ============ -->
    <section class="ai-diet section section-dark">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">AI DIET PLAN</p>
          <h2 class="section-title">AI 智能饮食规划</h2>
          <div class="gold-divider"></div>
          <p class="section-desc" style="color: var(--clr-gray)">结合身体指标、健身目标与饮食偏好生成科学饮食方案；配套每日打卡与每周复盘，并把数据同步到「计划制定」页，形成完整健身闭环。</p>
        </div>

        <div class="ai-diet__card">
          <div class="ai-diet__main">
            <div class="ai-diet__form">
              <p class="ai-diet__source"><el-icon><InfoFilled /></el-icon>{{ dietSourceHint }}</p>
              <div class="ai-diet__field">
                <label>健身目标</label>
                <el-select v-model="dietForm.target" style="width: 100%">
                  <el-option label="减脂" value="fatloss" />
                  <el-option label="增肌" value="muscle" />
                  <el-option label="维持体重" value="maintain" />
                </el-select>
              </div>
              <div class="ai-diet__field">
                <label>每周运动强度</label>
                <el-select v-model="dietForm.sport_level" style="width: 100%">
                  <el-option v-for="opt in activityOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                </el-select>
              </div>
              <div class="ai-diet__field">
                <label>就餐条件</label>
                <el-select v-model="dietForm.eat_scene" style="width: 100%">
                  <el-option v-for="s in eatSceneOptions" :key="s" :label="s" :value="s" />
                </el-select>
              </div>
              <div class="ai-diet__field">
                <label>饮食限制与偏好（忌口 / 过敏 / 口味）</label>
                <el-input v-model="dietForm.diet_limit" type="textarea" :rows="3" placeholder="例：不吃海鲜，乳糖不耐受，偏爱清淡少油" />
              </div>
              <div class="ai-diet__actions">
                <button class="btn-outline-dark" @click="syncToPlans">
                  <el-icon><Link /></el-icon>同步到计划制定
                </button>
                <button class="btn-text btn-text--light" @click="clearChat">清空对话</button>
              </div>
              <p class="ai-diet__hint">在右侧对话框输入你的饮食问题，或直接点击下方推荐问题开始对话。</p>
              <p v-if="dietDirty" class="form-hint">偏好已更新，下次生成方案时生效</p>
            </div>

            <div class="chat-panel">
              <div class="chat-panel__head">
                <span class="chat-panel__title"><el-icon><ChatDotRound /></el-icon>AI 营养师对话</span>
                <span class="chat-panel__sub">{{ chatMessages.length }} 条消息</span>
              </div>

              <div ref="chatBox" class="chat-panel__messages">
                <div v-if="!chatMessages.length" class="chat-panel__empty">
                  <el-icon :size="36"><MagicStick /></el-icon>
                  <p>输入你的饮食问题（例如「帮我生成一份减脂食谱」「换成外卖版」），AI 会结合你的身材数据回答。</p>
                  <button class="btn-primary" :disabled="chatSending" @click="sendChat('按我的身材数据生成一份' + dietTargetLabel(dietForm.target) + '食谱')">
                    生成 AI 饮食方案
                  </button>
                </div>

                <div v-for="(m, i) in chatMessages" :key="i" class="chat-msg" :class="'chat-msg--' + m.role">
                  <div class="chat-msg__bubble">
                    <template v-if="m.role === 'assistant'">
                      <div v-if="m.mock" class="ai-diet__mock">演示模式：以下为示例方案。</div>
                      <DietPlanCards v-if="m.plan" :plan="m.plan" />
                      <div class="chat-msg__text">
                        <pre>{{ m.content }}</pre>
                      </div>
                      <div v-if="m.plan" class="chat-msg__actions">
                        <button class="btn-outline-dark" @click="saveChatPlan(m)"><el-icon><FolderAdd /></el-icon>保存到档案</button>
                      </div>
                    </template>
                    <template v-else>{{ m.content }}</template>
                  </div>
                  <span class="chat-msg__time">{{ m.time }}</span>
                </div>

                <div v-if="chatSending" class="chat-msg chat-msg--assistant">
                  <div class="chat-msg__bubble chat-msg__thinking">
                    <span class="chat-dot"></span><span class="chat-dot"></span><span class="chat-dot"></span>
                  </div>
                </div>
              </div>

              <div class="chat-panel__chips">
                <button v-for="c in suggestionChips" :key="c" class="chat-chip" :disabled="chatSending" @click="sendChat(c)">{{ c }}</button>
              </div>

              <div class="chat-panel__input">
                <el-input
                  v-model="chatInput"
                  type="textarea"
                  :rows="2"
                  resize="none"
                  placeholder="输入你的饮食问题，例如：帮我换成外卖友好的版本 / 乳糖不耐受怎么吃"
                  @keydown.enter.prevent="sendChat()"
                />
                <button class="btn-primary chat-panel__send" :disabled="chatSending || !chatInput.trim()" @click="sendChat()">
                  {{ chatSending ? 'AI 思考中…' : '发送' }}
                </button>
              </div>
            </div>
          </div>

          <!-- 饮食打卡 + 周期复盘 -->
          <div class="ai-diet__extra">
            <div class="diet-checkin">
              <h3 class="ai-extra__title"><el-icon><KnifeFork /></el-icon>每日饮食打卡</h3>
              <div class="diet-checkin__compare">
                <div class="diet-checkin__cmp-item">
                  <span class="diet-checkin__cmp-label">今日摄入</span>
                  <b>{{ todayLog ? fmtNum(todayLog.calories, 0) : '--' }}</b><span class="diet-checkin__cmp-unit">kcal</span>
                </div>
                <div class="diet-checkin__cmp-item">
                  <span class="diet-checkin__cmp-label">TDEE 参考</span>
                  <b>{{ tdeeNow ? fmtNum(tdeeNow, 0) : '--' }}</b><span class="diet-checkin__cmp-unit">kcal</span>
                </div>
                <div class="diet-checkin__cmp-item">
                  <span class="diet-checkin__cmp-label">热量差值</span>
                  <b :class="diffClassSimple(caloriesDiff)">{{ caloriesDiff === null ? '--' : (caloriesDiff > 0 ? '+' : '') + fmtNum(caloriesDiff, 0) }}</b>
                </div>
              </div>
              <div class="diet-checkin__form">
                <div class="diet-checkin__row">
                  <div class="diet-checkin__field">
                    <label>日期</label>
                    <el-date-picker v-model="dietLogForm.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
                  </div>
                  <div class="diet-checkin__field">
                    <label>当日摄入（kcal）*</label>
                    <el-input-number v-model="dietLogForm.calories" :min="0" :step="10" :controls="false" style="width: 100%" placeholder="例：1850" />
                  </div>
                </div>
                <div class="diet-checkin__row">
                  <div class="diet-checkin__field">
                    <label>蛋白质 g</label>
                    <el-input-number v-model="dietLogForm.protein_g" :min="0" :controls="false" style="width: 100%" />
                  </div>
                  <div class="diet-checkin__field">
                    <label>碳水 g</label>
                    <el-input-number v-model="dietLogForm.carbs_g" :min="0" :controls="false" style="width: 100%" />
                  </div>
                  <div class="diet-checkin__field">
                    <label>脂肪 g</label>
                    <el-input-number v-model="dietLogForm.fat_g" :min="0" :controls="false" style="width: 100%" />
                  </div>
                </div>
                <div class="diet-checkin__field">
                  <label>备注</label>
                  <el-input v-model="dietLogForm.note" placeholder="例：训练日 / 外食聚餐" />
                </div>
                <button class="btn-primary" @click="saveDietLogNow">保存打卡</button>
              </div>
              <div v-if="dietLogs.length" class="diet-checkin__list">
                <div v-for="log in dietLogs.slice(0, 7)" :key="log.id" class="diet-checkin__item">
                  <span class="diet-checkin__date">{{ log.log_date }}</span>
                  <span class="diet-checkin__cal">{{ fmtNum(log.calories, 0) }} kcal</span>
                  <span class="diet-checkin__macros">P{{ fmtNum(log.protein_g, 0) }} / C{{ fmtNum(log.carbs_g, 0) }} / F{{ fmtNum(log.fat_g, 0) }}</span>
                  <el-popconfirm title="删除这条打卡？" confirm-button-text="删除" cancel-button-text="取消" @confirm="removeDietLog(log.id)">
                    <template #reference>
                      <button class="table-btn table-btn--danger">删除</button>
                    </template>
                  </el-popconfirm>
                </div>
              </div>
            </div>

            <div class="weekly-review">
              <h3 class="ai-extra__title"><el-icon><Refresh /></el-icon>周期复盘（近 7 天）</h3>
              <p class="weekly-review__desc">汇总本周身材数据与饮食打卡情况，AI 生成一周健身饮食复盘小结。</p>
              <button class="btn-primary" :disabled="reviewLoading" @click="generateReview">
                {{ reviewLoading ? 'AI 汇总中…' : '生成本周复盘' }}
              </button>
              <div v-if="weeklyReview" class="weekly-review__chips">
                <div v-for="c in reviewChips" :key="c.label" class="weekly-review__chip">
                  <span class="weekly-review__chip-label">{{ c.label }}</span>
                  <b>{{ c.value }}</b>
                </div>
              </div>
              <div v-if="weeklyReview" class="weekly-review__text">
                <div v-if="weeklyReview.mock" class="ai-diet__mock">演示模式：以下为示例复盘。</div>
                <pre>{{ weeklyReview.review_text }}</pre>
              </div>
            </div>
          </div>

          <div v-if="savedPlans.length" class="ai-diet__saved">
            <h3 class="ai-diet__saved-title"><el-icon><Files /></el-icon>已保存方案（{{ savedPlans.length }}）</h3>
            <div v-for="p in savedPlans" :key="p.id" class="ai-diet__saved-item">
              <div class="ai-diet__saved-info">
                <span class="ai-diet__saved-target">{{ dietTargetLabel(p.target) }}</span>
                <span class="ai-diet__saved-date">{{ (p.created_at || '').slice(0, 10) }}</span>
                <span v-if="p.diet_limit" class="ai-diet__saved-limit">{{ p.diet_limit }}</span>
              </div>
              <div class="ai-diet__saved-actions">
                <button class="table-btn" @click="viewSavedPlan(p.id)">查看</button>
                <el-popconfirm title="删除这份方案？" confirm-button-text="删除" cancel-button-text="取消" @confirm="removeSavedPlan(p.id)">
                  <template #reference>
                    <button class="table-btn table-btn--danger">删除</button>
                  </template>
                </el-popconfirm>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 最底部：数据管理入口 ============ -->
    <section class="data-entry section section-white">
      <div class="container">
        <div class="section-header text-center">
          <p class="section-subtitle">DATA MANAGEMENT</p>
          <h2 class="section-title">数据管理入口</h2>
          <div class="gold-divider"></div>
          <p class="section-desc">围度记录、身材目标管理、历史数据存档，三个入口集中管理你的全部身体数据。</p>
        </div>
        <div class="data-entry__grid">
          <div class="data-entry__card" @click="measDialog.visible = true">
            <div class="data-entry__icon"><el-icon :size="28"><Ruler /></el-icon></div>
            <h3 class="data-entry__title">围度记录</h3>
            <p class="data-entry__desc">胸围、肩宽、腰围、臀围、大腿围、手臂围测量存档与变化柱状图。</p>
            <span class="data-entry__meta">最近测量：{{ measLatestText }}</span>
            <button class="btn-outline-dark data-entry__btn">进入围度管理</button>
          </div>
          <div class="data-entry__card" @click="goalDialog.visible = true">
            <div class="data-entry__icon"><el-icon :size="28"><Flag /></el-icon></div>
            <h3 class="data-entry__title">身材目标管理</h3>
            <p class="data-entry__desc">目标体重 / BMI / 体脂率设定，结合 TDEE 推算热量缺口与达成天数。</p>
            <span class="data-entry__meta">{{ goal ? '目标已设定，进度随时可查' : '尚未设定目标' }}</span>
            <button class="btn-outline-dark data-entry__btn">进入目标管理</button>
          </div>
          <div class="data-entry__card" @click="historyDialog.visible = true">
            <div class="data-entry__icon"><el-icon :size="28"><Files /></el-icon></div>
            <h3 class="data-entry__title">历史数据存档</h3>
            <p class="data-entry__desc">全部身材记录表格、两条记录对比小结与 Excel 一键导出。</p>
            <span class="data-entry__meta">共 {{ records.length }} 条记录</span>
            <button class="btn-outline-dark data-entry__btn">进入数据存档</button>
          </div>
        </div>
      </div>
    </section>

    <!-- ============ 对话框：保存记录 ============ -->
    <el-dialog v-model="saveDialog.visible" title="保存本次记录" width="420px">
      <div class="save-dialog">
        <div class="save-dialog__field">
          <label>当前阶段</label>
          <el-select v-model="saveDialog.stage" style="width: 100%">
            <el-option label="减脂" value="fatloss" />
            <el-option label="增肌" value="muscle" />
            <el-option label="保持" value="maintain" />
          </el-select>
        </div>
        <div class="save-dialog__field">
          <label>记录日期</label>
          <el-date-picker v-model="saveDialog.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </div>
        <p class="save-dialog__tip">保存后会自动同步核心指标卡片，并进入趋势图与对比列表。</p>
      </div>
      <template #footer>
        <el-button @click="saveDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="confirmSaveRecord">保存</el-button>
      </template>
    </el-dialog>

    <!-- ============ 对话框：查看已保存方案 ============ -->
    <el-dialog v-model="planDialog.visible" title="已保存的 AI 饮食方案" width="760px">
      <div v-if="planDialog.detail" class="plan-dialog">
        <div class="plan-dialog__meta">
          <span>{{ dietTargetLabel(planDialog.detail.target) }}方案</span>
          <span>{{ (planDialog.detail.created_at || '').slice(0, 10) }}</span>
          <span v-if="planDialog.detail.eat_scene">{{ planDialog.detail.eat_scene }}</span>
          <span v-if="planDialog.detail.model">模型：{{ planDialog.detail.model }}</span>
        </div>
        <DietPlanCards :plan="planDialog.detail.plan" />
      </div>
    </el-dialog>

    <!-- ============ 对话框：围度记录 ============ -->
    <el-dialog v-model="measDialog.visible" title="围度记录" width="900px">
      <div class="entry-dialog">
        <div class="measurements__layout">
          <div class="measurements__form">
            <div class="measurements__grid">
              <div v-for="f in measurementFields" :key="f.key" class="measurement-field">
                <label>{{ f.label }}（{{ cmUnitLabel }}）</label>
                <el-input-number v-model="f.model" :min="0" :step="0.1" :controls="false" placeholder="输入数值" style="width: 100%" />
              </div>
            </div>
            <div class="measurements__actions">
              <button class="btn-primary" @click="saveMeasurements">保存本次围度</button>
              <button class="btn-text" @click="clearMeasurements">清空</button>
            </div>
          </div>
          <div class="measurements__chart">
            <div class="measurements__chart-head">
              <el-select v-model="measChartMetric" size="small" style="width: 140px">
                <el-option v-for="f in measurementFields" :key="f.key" :label="f.label" :value="f.key" />
              </el-select>
              <span class="measurements__chart-hint">最近 {{ measChartItems.length }} 次测量（{{ cmUnitLabel }}）</span>
            </div>
            <BarChart :items="measChartItems" :unit="cmUnitLabel" color="#c9a96e" />
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- ============ 对话框：身材目标管理 ============ -->
    <el-dialog v-model="goalDialog.visible" title="身材目标管理" width="860px">
      <div class="entry-dialog">
        <div class="goals__layout">
          <div class="goals__form">
            <div class="goals__form-grid">
              <div class="goals__field">
                <label>目标体重（{{ weightUnitLabel }}）</label>
                <el-input-number v-model="goalWeightDisplay" :min="0" :step="0.1" :controls="false" style="width: 100%" />
              </div>
              <div class="goals__field">
                <label>目标 BMI</label>
                <el-input-number v-model="goalForm.target_bmi" :min="10" :max="45" :step="0.1" :controls="false" style="width: 100%" />
              </div>
              <div class="goals__field">
                <label>目标体脂率（%）</label>
                <el-input-number v-model="goalForm.target_body_fat" :min="3" :max="50" :step="0.1" :controls="false" style="width: 100%" />
              </div>
              <div class="goals__field">
                <label>每日热量缺口 / 盈余（kcal）</label>
                <el-select v-model="calorieDelta" style="width: 100%">
                  <el-option label="250 kcal / 天（温和）" :value="250" />
                  <el-option label="350 kcal / 天" :value="350" />
                  <el-option label="500 kcal / 天（推荐）" :value="500" />
                  <el-option label="750 kcal / 天（激进）" :value="750" />
                </el-select>
              </div>
            </div>
            <div class="goals__actions">
              <button class="btn-primary" @click="saveGoal">保存目标</button>
              <button class="btn-text btn-text--light" @click="clearGoal">清除目标</button>
            </div>
            <p v-if="goalSavedAt" class="goals__saved">当前目标保存于 {{ goalSavedAt }}</p>
          </div>
          <div class="goals__result">
            <div v-if="!goalPlan" class="goals__empty">
              <el-icon :size="36"><Flag /></el-icon>
              <p>设定目标后，这里会展示完成进度与基于 TDEE 的热量方案。</p>
              <p class="goals__empty-note">提示：热量推算依赖已保存记录中的 TDEE，请先保存一条含年龄与运动强度的记录。</p>
            </div>
            <template v-else>
              <div class="goals__progress">
                <div v-for="g in goalProgressCards" :key="g.key" class="goal-progress">
                  <div class="goal-progress__head">
                    <span>{{ g.label }}</span>
                    <span class="goal-progress__pct">{{ g.percent === null ? '--' : g.percent + '%' }}</span>
                  </div>
                  <div class="goal-progress__track">
                    <div class="goal-progress__fill" :style="{ width: (g.percent ?? 0) + '%' }"></div>
                  </div>
                  <div class="goal-progress__sub">
                    <span>当前 {{ g.current }}</span>
                    <span>目标 {{ g.target }}</span>
                  </div>
                </div>
              </div>
              <div class="goal-plan">
                <h3 class="goal-plan__title"><el-icon><Odometer /></el-icon>每日热量方案</h3>
                <div class="goal-plan__row"><span>当前每日消耗 TDEE</span><b>{{ goalPlan.tdee }} kcal</b></div>
                <div class="goal-plan__row"><span>建议每日摄入</span><b class="goal-plan__accent">{{ goalPlan.intake }} kcal</b></div>
                <div class="goal-plan__row"><span>每日{{ goalPlan.direction === 'loss' ? '热量缺口' : '热量盈余' }}</span><b>{{ goalPlan.delta }} kcal</b></div>
                <div class="goal-plan__row"><span>预估达成天数</span><b>{{ goalPlan.days }} 天</b></div>
                <div class="goal-plan__row"><span>预计达成日期</span><b>{{ goalPlan.targetDate }}</b></div>
                <p class="goal-plan__note">* 按「每减 / 增 1kg 体重约需 7700 kcal」粗略估算，实际进度因人而异。</p>
              </div>
            </template>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- ============ 对话框：历史数据存档 ============ -->
    <el-dialog v-model="historyDialog.visible" title="历史数据存档" width="960px">
      <div class="entry-dialog">
        <div class="history__toolbar">
          <span class="history__hint">共 {{ records.length }} 条记录，选择两条可生成对比小结</span>
          <div class="history__toolbar-spacer"></div>
          <button class="btn-outline-dark" @click="onExport"><el-icon><Download /></el-icon>导出 Excel</button>
          <el-popconfirm title="确认清空全部身材记录？此操作不可恢复。" confirm-button-text="清空" cancel-button-text="取消" @confirm="onClearAll">
            <template #reference>
              <button class="btn-danger-outline">清空全部记录</button>
            </template>
          </el-popconfirm>
        </div>

        <div v-if="compareResult" class="compare-panel compare-panel--light">
          <div class="compare-panel__head">
            <h3 class="compare-panel__title"><el-icon><Switch /></el-icon>数据对比小结</h3>
            <button class="btn-text" @click="clearCompare">关闭</button>
          </div>
          <p class="compare-panel__summary">{{ compareResult.summary }}</p>
          <div class="compare-panel__grid">
            <div v-for="d in compareResult.diffs" :key="d.key" class="compare-item compare-item--light">
              <span class="compare-item__label">{{ d.label }}</span>
              <span class="compare-item__val">{{ fmtDisp(d.from, d.key) }} {{ d.unit }} → {{ fmtDisp(d.to, d.key) }} {{ d.unit }}</span>
              <span class="compare-item__diff" :class="diffClass(d)">{{ d.diff > 0 ? '+' : '' }}{{ d.diff }} {{ d.unit }}</span>
            </div>
          </div>
        </div>

        <el-table :data="records" empty-text="暂无记录，先在上方计算并保存一条吧" style="width: 100%">
          <el-table-column label="日期" width="110">
            <template #default="{ row }">{{ row.record_date }}</template>
          </el-table-column>
          <el-table-column label="阶段" width="80">
            <template #default="{ row }">
              <span v-if="row.stage" class="stage-tag">{{ stageLabel(row.stage) }}</span>
              <span v-else class="stage-tag stage-tag--none">未标注</span>
            </template>
          </el-table-column>
          <el-table-column label="体重" width="100">
            <template #default="{ row }">{{ fmtDisp(row.weight_kg, 'weight_kg') }} {{ weightUnitLabel }}</template>
          </el-table-column>
          <el-table-column label="BMI" width="80">
            <template #default="{ row }">{{ fmtNum(row.bmi) }}</template>
          </el-table-column>
          <el-table-column label="体脂率" width="90">
            <template #default="{ row }">{{ fmtNum(row.body_fat) }}%</template>
          </el-table-column>
          <el-table-column label="肌肉量" width="100">
            <template #default="{ row }">{{ fmtDisp(row.muscle_mass, 'muscle_mass') }} {{ weightUnitLabel }}</template>
          </el-table-column>
          <el-table-column label="TDEE" width="90">
            <template #default="{ row }">{{ fmtNum(row.tdee) }}</template>
          </el-table-column>
          <el-table-column label="操作" min-width="150">
            <template #default="{ row }">
              <button class="table-btn" :class="{ 'table-btn--active': compareSel.includes(row.id) }" @click="toggleCompare(row.id)">
                {{ compareSel.includes(row.id) ? '已选对比' : '对比' }}
              </button>
              <el-popconfirm title="删除这条记录？" confirm-button-text="删除" cancel-button-text="取消" @confirm="onDeleteRecord(row.id)">
                <template #reference>
                  <button class="table-btn table-btn--danger">删除</button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import LineChart from '@/components/LineChart.vue'
import BarChart from '@/components/BarChart.vue'
import DietPlanCards from '@/components/DietPlanCards.vue'
import {
  getBodyMetrics,
  calculateBodyMetrics,
  saveBodyRecord,
  getBodyRecords,
  deleteBodyRecord,
  deleteAllBodyRecords,
  compareBodyRecords,
  exportBodyRecords,
  getBodyProfile,
  saveBodyProfile,
  getBodyGoals,
  saveBodyGoal,
  deleteBodyGoal,
  generateDietPlan,
  saveDietPlan as saveDietPlanReq,
  getDietPlans,
  getDietPlanDetail,
  deleteDietPlan,
  saveDietLog,
  getDietLogs,
  deleteDietLog,
  generateWeeklyReview,
} from '@/api'

const router = useRouter()

// ---------- 常量 ----------
const CM_PER_IN = 2.54
const KG_PER_LB = 0.45359237

const activityOptions = [
  { value: 'sedentary', label: '久坐少动' },
  { value: 'light', label: '轻度运动' },
  { value: 'moderate', label: '中度力量训练' },
  { value: 'intense', label: '高强度训练' },
]

const eatSceneOptions = ['自己做饭', '食堂就餐', '外卖为主', '外出就餐', '出差旅行']

const stageOptions = [
  { value: 'fatloss', label: '减脂' },
  { value: 'muscle', label: '增肌' },
  { value: 'maintain', label: '保持' },
]

const trendMetricOptions = [
  { value: 'weight_kg', label: '体重' },
  { value: 'bmi', label: 'BMI' },
  { value: 'body_fat', label: '体脂率' },
  { value: 'waist_cm', label: '腰围' },
  { value: 'muscle_mass', label: '肌肉量' },
  { value: 'tdee', label: '每日消耗' },
]

// ---------- 状态 ----------
const unit = ref<'metric' | 'imperial'>('metric')
const profile = reactive({ gender: 'male', age: 25, activity_level: 'light' })

const heightCm = ref<number | null>(null)
const weightKg = ref<number | null>(null)
const calcWaistCm = ref<number | null>(null)
const calcHipCm = ref<number | null>(null)
const calcNeckCm = ref<number | null>(null)

const results = ref<any>(null)
const records = ref<any[]>([])
const legacyMetrics = ref<any[]>([])

const rangeDays = ref<'30' | '90' | 'all'>('30')
const chartMetric = ref('weight_kg')
const chartGroup = ref<'record' | 'week' | 'month'>('week')

const compareSel = ref<number[]>([])
const compareResult = ref<any>(null)

const chestCm = ref<number | null>(null)
const shoulderCm = ref<number | null>(null)
const measWaistCm = ref<number | null>(null)
const measHipCm = ref<number | null>(null)
const thighCm = ref<number | null>(null)
const armCm = ref<number | null>(null)
const measChartMetric = ref('chest_cm')

const goalForm = reactive({ target_weight: null as number | null, target_bmi: null as number | null, target_body_fat: null as number | null })
const goal = ref<any>(null)
const goalSavedAt = ref('')
const calorieDelta = ref(500)

const saveDialog = reactive({ visible: false, stage: 'fatloss', date: '' })
const measDialog = reactive({ visible: false })
const goalDialog = reactive({ visible: false })
const historyDialog = reactive({ visible: false })

const dietForm = reactive({ target: 'fatloss', sport_level: 'light', eat_scene: '自己做饭', diet_limit: '' })
const chatMessages = ref<any[]>([])
const chatInput = ref('')
const chatSending = ref(false)
const chatBox = ref<HTMLElement | null>(null)
const savedPlans = ref<any[]>([])
const planDialog = reactive({ visible: false, detail: null as any })

// 参数修改后的淡金提示（样式优化要求，不影响原有功能）
const calcDirty = ref(false)
const dietDirty = ref(false)
let calcHintTimer: any = null
let dietHintTimer: any = null

function flashHint(target: 'calc' | 'diet') {
  if (target === 'calc') {
    calcDirty.value = true
    clearTimeout(calcHintTimer)
    calcHintTimer = setTimeout(() => { calcDirty.value = false }, 3000)
  } else {
    dietDirty.value = true
    clearTimeout(dietHintTimer)
    dietHintTimer = setTimeout(() => { dietDirty.value = false }, 3000)
  }
}

watch(
  [heightCm, weightKg, calcWaistCm, calcHipCm, calcNeckCm, () => profile.age, () => profile.activity_level, () => profile.gender],
  () => flashHint('calc')
)
watch(
  [() => dietForm.target, () => dietForm.sport_level, () => dietForm.eat_scene, () => dietForm.diet_limit],
  () => flashHint('diet')
)

const dietLogs = ref<any[]>([])
const dietLogForm = reactive({ date: '', calories: null as number | null, protein_g: null as number | null, carbs_g: null as number | null, fat_g: null as number | null, note: '' })
const weeklyReview = ref<any>(null)
const reviewLoading = ref(false)

// ---------- 单位换算 ----------
const cmToIn = (v: number | null) => (v == null ? null : v / CM_PER_IN)
const inToCm = (v: number | null) => (v == null ? null : v * CM_PER_IN)
const kgToLb = (v: number | null) => (v == null ? null : v / KG_PER_LB)
const lbToKg = (v: number | null) => (v == null ? null : v * KG_PER_LB)

const weightUnitLabel = computed(() => (unit.value === 'imperial' ? 'lb' : 'kg'))
const cmUnitLabel = computed(() => (unit.value === 'imperial' ? 'in' : 'cm'))
const heightUnitLabel = computed(() => (unit.value === 'imperial' ? 'in' : 'cm'))

function dispValue(metric: string, v: number | null) {
  if (v == null) return null
  if (metric === 'weight_kg' || metric === 'muscle_mass' || metric === 'standard_weight') {
    return unit.value === 'imperial' ? kgToLb(v) : v
  }
  if (metric === 'waist_cm' || metric === 'height_cm' || metric === 'hip_cm' || metric === 'neck_cm'
    || metric === 'chest_cm' || metric === 'shoulder_cm' || metric === 'thigh_cm' || metric === 'arm_cm') {
    return unit.value === 'imperial' ? cmToIn(v) : v
  }
  return v
}

function fmtNum(v: number | null | undefined, digits = 1) {
  if (v == null || Number.isNaN(v)) return '--'
  return Number(v).toFixed(digits)
}

function fmtDisp(v: number | null | undefined, metric = '') {
  const d = dispValue(metric, v == null ? null : Number(v))
  return d == null ? '--' : fmtNum(d)
}

function round1(v: number | null) {
  return v == null ? null : Math.round(v * 10) / 10
}

function cmField(target: { value: number | null }) {
  return computed({
    get: () => (unit.value === 'imperial' ? round1(cmToIn(target.value)) : target.value),
    set: (v: number | null | undefined) => {
      target.value = unit.value === 'imperial' ? inToCm(v ?? null) : (v ?? null)
    },
  })
}

function weightField(target: { value: number | null }) {
  return computed({
    get: () => (unit.value === 'imperial' ? round1(kgToLb(target.value)) : target.value),
    set: (v: number | null | undefined) => {
      target.value = unit.value === 'imperial' ? lbToKg(v ?? null) : (v ?? null)
    },
  })
}

const heightDisplay = cmField(heightCm)
const weightDisplay = weightField(weightKg)
const calcWaistDisplay = cmField(calcWaistCm)
const calcHipDisplay = cmField(calcHipCm)
const calcNeckDisplay = cmField(calcNeckCm)
const chestDisplay = cmField(chestCm)
const shoulderDisplay = cmField(shoulderCm)
const measWaistDisplay = cmField(measWaistCm)
const measHipDisplay = cmField(measHipCm)
const thighDisplay = cmField(thighCm)
const armDisplay = cmField(armCm)

const goalWeightDisplay = computed({
  get: () => (unit.value === 'imperial' ? round1(kgToLb(goalForm.target_weight)) : goalForm.target_weight),
  set: (v: number | null | undefined) => {
    goalForm.target_weight = unit.value === 'imperial' ? lbToKg(v ?? null) : (v ?? null)
  },
})

const measurementFields = computed(() => [
  { key: 'chest_cm', label: '胸围', model: chestDisplay },
  { key: 'shoulder_cm', label: '肩宽', model: shoulderDisplay },
  { key: 'waist_cm', label: '腰围', model: measWaistDisplay },
  { key: 'hip_cm', label: '臀围', model: measHipDisplay },
  { key: 'thigh_cm', label: '大腿围', model: thighDisplay },
  { key: 'arm_cm', label: '手臂围', model: armDisplay },
])

// ---------- 核心指标卡片 ----------
const topMetrics = computed(() => {
  const defs = [
    { key: 'weight_kg', label: '体重', icon: 'Scale', unit: weightUnitLabel.value },
    { key: 'body_fat', label: '体脂率', icon: 'Histogram', unit: '%' },
    { key: 'muscle_mass', label: '肌肉量', icon: 'Aim', unit: weightUnitLabel.value },
    { key: 'tdee', label: '每日消耗', icon: 'Lightning', unit: 'kcal' },
  ]
  return defs.map((d) => {
    const cur = latestWith(d.key)
    const prev = prevWith(d.key)
    let value: number | null = cur ? dispValue(d.key, cur[d.key]) : null
    if (value === null) {
      const legacyKey = d.key === 'weight_kg' ? 'weight' : d.key === 'tdee' ? 'bmr' : d.key
      const lm = legacyMetrics.value.find((m) => m.key === legacyKey)
      value = lm ? dispValue(d.key, lm.value) : null
    }
    let change: string | null = null
    let trendClass = ''
    if (cur && prev) {
      const diff = round1(dispValue(d.key, (cur[d.key] ?? 0) - (prev[d.key] ?? 0)))
      if (diff !== null && diff !== 0) {
        change = `${diff > 0 ? '+' : ''}${diff}${d.unit}`
        trendClass = diff > 0 ? 'up' : 'down'
      } else {
        change = '0' + d.unit
      }
    } else {
      const lm = legacyMetrics.value.find((m) => m.key === (d.key === 'weight_kg' ? 'weight' : d.key === 'tdee' ? 'bmr' : d.key))
      if (lm && lm.change) {
        change = `${lm.change > 0 ? '+' : ''}${lm.change}${d.unit}`
        trendClass = lm.trend === 'down' ? 'down' : 'up'
      }
    }
    return { ...d, value: value == null ? '--' : fmtNum(value), change, trendClass }
  })
})

function latestWith(field: string) {
  for (const r of records.value) if (r[field] != null) return r
  return null
}

function prevWith(field: string) {
  let found = false
  for (const r of records.value) {
    if (r[field] == null) continue
    if (found) return r
    found = true
  }
  return null
}

function earliestWith(field: string) {
  const asc = [...records.value].sort((a, b) => (a.record_date < b.record_date ? -1 : 1))
  for (const r of asc) if (r[field] != null) return r
  return null
}

// ---------- 计算结果卡片 ----------
function pct(v: number | null | undefined, scale: number[]) {
  if (v == null) return 0
  const [min, max] = scale
  return Math.max(0, Math.min(100, ((v - min) / (max - min)) * 100))
}

const metricCards = computed(() => {
  if (!results.value) return []
  const r = results.value
  const male = r.gender === 'male'
  const stdScale = r.healthy_weight_range ? [r.healthy_weight_range[0] - 8, r.healthy_weight_range[1] + 8] : [40, 90]
  return [
    {
      key: 'bmi', label: 'BMI 身体质量指数', value: fmtNum(r.bmi), unit: '',
      scale: [10, 40], healthy: [18.5, 24.9], category: r.bmi_category_label,
      categoryClass: `cat-${r.bmi_category || 'unknown'}`,
    },
    {
      key: 'body_fat', label: '体脂率', value: fmtNum(r.body_fat), unit: '%',
      scale: [0, 40], healthy: r.body_fat_range, category: male ? '男性正常 10% - 20%' : '女性正常 18% - 28%',
      categoryClass: 'cat-normal', tag: r.body_fat_formula === 'navy' ? 'US Navy 公式' : '简化公式',
    },
    {
      key: 'bmr', label: '基础代谢 BMR', value: fmtNum(r.bmr, 0), unit: 'kcal',
      scale: r.bmr_range, healthy: [1200, 1800], category: 'Mifflin-St Jeor 公式',
      categoryClass: 'cat-normal',
    },
    {
      key: 'tdee', label: '每日消耗 TDEE', value: fmtNum(r.tdee, 0), unit: 'kcal',
      scale: r.tdee_range, healthy: [1600, 3200], category: `${r.activity_label} × ${r.tdee_multiplier}`,
      categoryClass: 'cat-normal',
    },
    {
      key: 'whr', label: '腰臀比 WHR', value: fmtNum(r.whr, 2), unit: '',
      scale: r.whr_range, healthy: [0.6, r.whr_healthy_max], category: `健康参考 ≤ ${r.whr_healthy_max}`,
      categoryClass: 'cat-normal',
    },
    {
      key: 'muscle_mass', label: '肌肉量估算', value: fmtDisp(r.muscle_mass, 'muscle_mass'), unit: weightUnitLabel.value,
      scale: r.muscle_mass_range, healthy: r.muscle_mass_range, category: '基于体重与体脂估算',
      categoryClass: 'cat-normal',
    },
    {
      key: 'standard_weight', label: '标准体重参考', value: fmtDisp(r.standard_weight, 'standard_weight'), unit: weightUnitLabel.value,
      scale: stdScale, healthy: r.healthy_weight_range, category: '以 BMI 22 为理想值',
      categoryClass: 'cat-normal',
    },
  ]
})

function healthyStyle(m: any) {
  const left = pct(m.healthy?.[0], m.scale)
  const right = pct(m.healthy?.[1], m.scale)
  return { left: left + '%', width: Math.max(right - left, 2) + '%' }
}

function dotStyle(m: any) {
  const raw = results.value ? results.value[m.key] : null
  return { left: pct(raw, m.scale) + '%' }
}

// ---------- 计算 ----------
function buildCalcPayload() {
  return {
    gender: profile.gender,
    age: profile.age,
    activity_level: profile.activity_level,
    height_cm: heightCm.value,
    weight_kg: weightKg.value,
    waist_cm: calcWaistCm.value,
    hip_cm: calcHipCm.value,
    neck_cm: calcNeckCm.value,
  }
}

async function onCalculate() {
  if (!heightCm.value || !weightKg.value) {
    ElMessage.warning('请先填写身高与体重')
    return
  }
  try {
    const res = await calculateBodyMetrics(buildCalcPayload())
    results.value = res.data
  } catch (e: any) {
    ElMessage.error(e?.message || '计算失败')
  }
}

function clearCalcInputs() {
  heightCm.value = null
  weightKg.value = null
  calcWaistCm.value = null
  calcHipCm.value = null
  calcNeckCm.value = null
  results.value = null
}

// ---------- 保存记录 ----------
function openSaveDialog() {
  if (!results.value) return
  saveDialog.stage = 'fatloss'
  saveDialog.date = new Date().toISOString().slice(0, 10)
  saveDialog.visible = true
}

async function confirmSaveRecord() {
  try {
    const payload = {
      ...buildCalcPayload(),
      stage: saveDialog.stage,
      record_date: saveDialog.date,
    }
    await saveBodyRecord(payload)
    saveDialog.visible = false
    ElMessage.success('记录已保存')
    await loadRecords()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

// ---------- 历史趋势 ----------
const trendItems = computed(() => {
  let list = [...records.value]
  if (rangeDays.value !== 'all') {
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - Number(rangeDays.value))
    const cutoffStr = cutoff.toISOString().slice(0, 10)
    list = list.filter((r) => r.record_date >= cutoffStr)
  }
  list.sort((a, b) => (a.record_date < b.record_date ? -1 : 1))
  const key = chartMetric.value
  const points = list
    .filter((r) => r[key] != null)
    .map((r) => ({
      label: r.record_date,
      value: dispValue(key, r[key]) as number,
      marker: r.stage ? stageLabel(r.stage) : '',
    }))

  if (chartGroup.value === 'record') return points

  const groups: { label: string; value: number; marker: string }[] = []
  for (const p of points) {
    const gLabel = chartGroup.value === 'week' ? weekLabel(p.label) : monthLabel(p.label)
    const last = groups[groups.length - 1]
    if (last && last.label === gLabel) {
      last.value = p.value
      if (p.marker) last.marker = p.marker
    } else {
      groups.push({ label: gLabel, value: p.value, marker: p.marker })
    }
  }
  return groups
})

function weekLabel(dateStr: string) {
  const d = new Date(dateStr + 'T00:00:00')
  const day = (d.getDay() + 6) % 7
  d.setDate(d.getDate() - day)
  return `${d.getMonth() + 1}/${d.getDate()}周`
}

function monthLabel(dateStr: string) {
  const d = new Date(dateStr + 'T00:00:00')
  return `${d.getMonth() + 1}月`
}

const trendUnit = computed(() => {
  const key = chartMetric.value
  if (key === 'weight_kg' || key === 'muscle_mass') return weightUnitLabel.value
  if (key === 'waist_cm') return cmUnitLabel.value
  if (key === 'body_fat') return '%'
  if (key === 'tdee') return 'kcal'
  return ''
})

function stageLabel(stage: string) {
  return stageOptions.find((s) => s.value === stage)?.label || stage
}

function dietTargetLabel(target: string) {
  const map: Record<string, string> = { fatloss: '减脂', muscle: '增肌', maintain: '维持体重' }
  return map[target] || target
}

// ---------- 对比 ----------
async function toggleCompare(id: number) {
  const idx = compareSel.value.indexOf(id)
  if (idx >= 0) {
    compareSel.value.splice(idx, 1)
  } else {
    if (compareSel.value.length >= 2) {
      compareSel.value.shift()
    }
    compareSel.value.push(id)
  }
  compareResult.value = null
  if (compareSel.value.length === 2) {
    try {
      const res = await compareBodyRecords(compareSel.value[0], compareSel.value[1])
      compareResult.value = res.data
    } catch (e: any) {
      ElMessage.error(e?.message || '对比失败')
    }
  }
}

function clearCompare() {
  compareSel.value = []
  compareResult.value = null
}

function diffClass(d: any) {
  const key = d.key
  if (key === 'weight_kg' || key === 'body_fat' || key === 'waist_cm' || key === 'whr') {
    return d.diff < 0 ? 'good' : 'bad'
  }
  return d.diff > 0 ? 'good' : 'bad'
}

// ---------- 记录操作 ----------
async function onDeleteRecord(id: number) {
  try {
    await deleteBodyRecord(id)
    ElMessage.success('已删除')
    await loadRecords()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

async function onClearAll() {
  try {
    await deleteAllBodyRecords()
    ElMessage.success('全部记录已清空')
    clearCompare()
    await loadRecords()
  } catch (e: any) {
    ElMessage.error(e?.message || '清空失败')
  }
}

// ---------- 导出 ----------
async function onExport() {
  try {
    const blob = await exportBodyRecords()
    const isCsv = blob.type.includes('csv')
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `身材记录_${new Date().toISOString().slice(0, 10)}.${isCsv ? 'csv' : 'xlsx'}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功，请查收下载文件')
  } catch (e: any) {
    ElMessage.error(e?.message || '导出失败')
  }
}

// ---------- 围度记录 ----------
const measChartItems = computed(() => {
  const key = measChartMetric.value
  const list = [...records.value]
    .filter((r) => r[key] != null)
    .sort((a, b) => (a.record_date < b.record_date ? -1 : 1))
    .slice(-12)
    .map((r) => ({
      label: r.record_date.slice(5),
      value: dispValue(key, r[key]) as number,
    }))
  return list
})

const measLatestText = computed(() => {
  const withMeas = records.value.find((r) => r.waist_cm != null || r.chest_cm != null || r.hip_cm != null || r.shoulder_cm != null || r.thigh_cm != null || r.arm_cm != null)
  return withMeas ? withMeas.record_date : '暂无'
})

async function saveMeasurements() {
  const payload: any = {
    record_date: new Date().toISOString().slice(0, 10),
    chest_cm: chestCm.value,
    shoulder_cm: shoulderCm.value,
    waist_cm: measWaistCm.value,
    hip_cm: measHipCm.value,
    thigh_cm: thighCm.value,
    arm_cm: armCm.value,
  }
  const hasAny = [chestCm.value, shoulderCm.value, measWaistCm.value, measHipCm.value, thighCm.value, armCm.value].some((v) => v != null)
  if (!hasAny) {
    ElMessage.warning('请至少填写一项围度')
    return
  }
  try {
    await saveBodyRecord(payload)
    ElMessage.success('围度已保存')
    clearMeasurements()
    await loadRecords()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

function clearMeasurements() {
  chestCm.value = null
  shoulderCm.value = null
  measWaistCm.value = null
  measHipCm.value = null
  thighCm.value = null
  armCm.value = null
}

// ---------- 目标设定 ----------
const goalPlan = computed(() => {
  const cur = latestWith('weight_kg')
  if (!goal.value || !cur || !cur.tdee) return null
  const tdee = cur.tdee as number
  const target = goal.value.target_weight
  const current = cur.weight_kg as number
  if (target == null) {
    return {
      tdee, intake: tdee, delta: 0, days: 0,
      targetDate: new Date().toISOString().slice(0, 10),
      direction: 'maintain',
    }
  }
  const diff = current - target
  const delta = calorieDelta.value
  if (diff > 0.5) {
    const days = Math.ceil((diff * 7700) / delta)
    const d = new Date()
    d.setDate(d.getDate() + days)
    return { tdee, intake: tdee - delta, delta, days, targetDate: d.toISOString().slice(0, 10), direction: 'loss' }
  }
  if (diff < -0.5) {
    const days = Math.ceil((-diff * 7700) / delta)
    const d = new Date()
    d.setDate(d.getDate() + days)
    return { tdee, intake: tdee + delta, delta, days, targetDate: d.toISOString().slice(0, 10), direction: 'gain' }
  }
  return { tdee, intake: tdee, delta: 0, days: 0, targetDate: new Date().toISOString().slice(0, 10), direction: 'maintain' }
})

const goalProgressCards = computed(() => {
  const fields = [
    { key: 'weight_kg', label: '体重目标', target: goal.value?.target_weight, unit: weightUnitLabel.value },
    { key: 'bmi', label: 'BMI 目标', target: goal.value?.target_bmi, unit: '' },
    { key: 'body_fat', label: '体脂率目标', target: goal.value?.target_body_fat, unit: '%' },
  ]
  return fields.map((f) => {
    const start = earliestWith(f.key)
    const current = latestWith(f.key)
    if (!start || !current || f.target == null) {
      return { ...f, current: '--', target: f.target == null ? '--' : fmtDisp(f.target, f.key), percent: null }
    }
    const s = start[f.key] as number
    const c = current[f.key] as number
    const t = f.target as number
    const span = s - t
    const pctDone = span === 0 ? 100 : Math.max(0, Math.min(100, ((s - c) / span) * 100))
    return {
      ...f,
      current: fmtDisp(c, f.key),
      target: fmtDisp(t, f.key),
      percent: Math.round(pctDone),
    }
  })
})

async function saveGoal() {
  const hasAny = goalForm.target_weight != null || goalForm.target_bmi != null || goalForm.target_body_fat != null
  if (!hasAny) {
    ElMessage.warning('请至少设定一个目标')
    return
  }
  const payload: any = {
    target_weight: goalForm.target_weight,
    target_bmi: goalForm.target_bmi,
    target_body_fat: goalForm.target_body_fat,
  }
  if (goalPlan.value) payload.daily_calorie = goalPlan.value.intake
  try {
    const res = await saveBodyGoal(payload)
    goal.value = res.data
    goalSavedAt.value = new Date().toISOString().slice(0, 10)
    ElMessage.success('目标已保存')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

async function clearGoal() {
  if (!goal.value) return
  try {
    await deleteBodyGoal(goal.value.id)
    goal.value = null
    goalSavedAt.value = ''
    goalForm.target_weight = null
    goalForm.target_bmi = null
    goalForm.target_body_fat = null
    ElMessage.success('目标已清除')
  } catch (e: any) {
    ElMessage.error(e?.message || '清除失败')
  }
}

// ---------- AI 饮食方案 ----------
function buildDietPayload(regenerate = false) {
  const rec = latestWith('weight_kg')
  const src = rec || results.value
  if (!src || !src.height_cm || !src.weight_kg) return null
  return {
    height_cm: src.height_cm,
    weight_kg: src.weight_kg,
    bmi: src.bmi,
    body_fat: src.body_fat,
    gender: src.gender || profile.gender,
    age: src.age || profile.age,
    bmr: src.bmr,
    tdee: src.tdee,
    waist_cm: src.waist_cm,
    hip_cm: src.hip_cm,
    neck_cm: src.neck_cm,
    sport_level: dietForm.sport_level,
    target: dietForm.target,
    diet_limit: dietForm.diet_limit,
    eat_scene: dietForm.eat_scene,
    regenerate,
  }
}

const dietSourceHint = computed(() => {
  const rec = latestWith('weight_kg')
  return rec
    ? `使用最近一次保存记录（${rec.record_date}）中的身体指标`
    : results.value
      ? '使用当前计算结果中的身体指标'
      : '请先在上方计算指标或保存一条身材记录'
})

const suggestionChips = computed(() => {
  const rec = latestWith('weight_kg') || results.value
  const target = dietTargetLabel(dietForm.target)
  const chips = [`按我的身材数据生成一份${target}食谱`]
  if (rec?.tdee) chips.push(`我的 TDEE 是 ${fmtNum(rec.tdee, 0)}，帮我规划每日热量`)
  if (rec?.bmi) chips.push(`我 BMI ${fmtNum(rec.bmi)}，平时怎么吃更健康`)
  chips.push('换成外卖友好的版本', '给我 3 个快手晚餐搭配')
  if (dietForm.diet_limit.trim()) chips.push(`按我的忌口生成：${dietForm.diet_limit.trim()}`)
  return chips.slice(0, 6)
})

function chatNow() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function scrollChat() {
  nextTick(() => {
    if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight
  })
}

async function sendChat(text?: string) {
  const msg = (text ?? chatInput.value).trim()
  if (!msg || chatSending.value) return
  const payload = buildDietPayload(false)
  if (!payload) {
    ElMessage.warning('请先在上方填写身高体重并计算，或保存一条身材记录')
    return
  }
  chatInput.value = ''
  chatMessages.value.push({ role: 'user', content: msg, time: chatNow() })
  chatSending.value = true
  scrollChat()
  try {
    const history = chatMessages.value.slice(0, -1).map((m) => ({ role: m.role, content: m.content }))
    const res = await generateDietPlan({ ...payload, user_message: msg, history }, false)
    const d = res.data
    chatMessages.value.push({
      role: 'assistant',
      content: d.raw_text || (d.plan ? JSON.stringify(d.plan, null, 2) : '模型未返回内容，请重试'),
      plan: d.plan || null,
      mock: !!d.mock,
      time: chatNow(),
    })
    if (d.mock) ElMessage.info('当前未配置 DEEPSEEK_API_KEY，展示演示方案')
  } catch (e: any) {
    chatMessages.value.push({
      role: 'assistant',
      content: '生成失败：' + (e?.message || '请稍后重试'),
      plan: null,
      mock: false,
      time: chatNow(),
    })
  } finally {
    chatSending.value = false
    scrollChat()
  }
}

function clearChat() {
  chatMessages.value = []
  chatInput.value = ''
}

async function saveChatPlan(m: any) {
  if (!m.plan) return
  try {
    await saveDietPlanReq({
      target: dietForm.target,
      sport_level: dietForm.sport_level,
      diet_limit: dietForm.diet_limit,
      eat_scene: dietForm.eat_scene,
      plan_json: JSON.stringify(m.plan),
      raw_text: m.content || '',
      model: '',
    })
    ElMessage.success('方案已保存到档案')
    await loadDietPlans()
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

async function loadDietPlans() {
  try {
    const res = await getDietPlans()
    savedPlans.value = res.data.items
  } catch {
    savedPlans.value = []
  }
}

async function viewSavedPlan(id: number) {
  try {
    const res = await getDietPlanDetail(id)
    planDialog.detail = res.data
    planDialog.visible = true
  } catch (e: any) {
    ElMessage.error(e?.message || '加载失败')
  }
}

async function removeSavedPlan(id: number) {
  try {
    await deleteDietPlan(id)
    ElMessage.success('已删除')
    await loadDietPlans()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

// ---------- 饮食打卡 ----------
const tdeeNow = computed(() => latestWith('tdee')?.tdee ?? null)
const todayLog = computed(() => dietLogs.value.find((l) => l.log_date === dietLogForm.date) || dietLogs.value.find((l) => l.log_date === new Date().toISOString().slice(0, 10)) || null)
const caloriesDiff = computed(() => {
  if (!todayLog.value || !tdeeNow.value) return null
  return todayLog.value.calories - tdeeNow.value
})

async function loadDietLogs() {
  try {
    const res = await getDietLogs()
    dietLogs.value = res.data.items
  } catch {
    dietLogs.value = []
  }
}

async function saveDietLogNow() {
  if (!dietLogForm.calories || dietLogForm.calories <= 0) {
    ElMessage.warning('请填写当日摄入热量')
    return
  }
  try {
    await saveDietLog({
      log_date: dietLogForm.date,
      calories: dietLogForm.calories,
      protein_g: dietLogForm.protein_g,
      carbs_g: dietLogForm.carbs_g,
      fat_g: dietLogForm.fat_g,
      note: dietLogForm.note,
    })
    ElMessage.success('打卡成功')
    dietLogForm.note = ''
    await loadDietLogs()
  } catch (e: any) {
    ElMessage.error(e?.message || '打卡失败')
  }
}

async function removeDietLog(id: number) {
  try {
    await deleteDietLog(id)
    ElMessage.success('已删除')
    await loadDietLogs()
  } catch (e: any) {
    ElMessage.error(e?.message || '删除失败')
  }
}

function diffClassSimple(diff: number | null) {
  if (diff === null) return ''
  return diff > 0 ? 'bad' : 'good'
}

// ---------- 周期复盘 ----------
const reviewChips = computed(() => {
  if (!weeklyReview.value) return []
  const s = weeklyReview.value.summary || {}
  const w = s.weight
  return [
    { label: '本周记录', value: (s.record_count ?? 0) + ' 条' },
    { label: '体重变化', value: w ? `${w.change > 0 ? '+' : ''}${w.change}kg` : '数据不足' },
    { label: '打卡天数', value: (s.diet?.log_days ?? 0) + ' 天' },
    { label: '日均摄入', value: s.diet?.avg_calories != null ? fmtNum(s.diet.avg_calories, 0) + ' kcal' : '--' },
  ]
})

async function generateReview() {
  reviewLoading.value = true
  try {
    const res = await generateWeeklyReview()
    weeklyReview.value = res.data
    if (res.data.mock) ElMessage.info('当前为演示复盘，配置 API Key 后由 AI 生成')
  } catch (e: any) {
    ElMessage.error(e?.message || '复盘生成失败')
  } finally {
    reviewLoading.value = false
  }
}

// ---------- 同步到计划制定 ----------
function syncToPlans() {
  const rec = latestWith('weight_kg') || results.value
  const lastPlan = [...chatMessages.value].reverse().find((m) => m.plan)
  const payload: any = {
    synced_at: new Date().toISOString(),
    metrics: rec
      ? {
        weight_kg: rec.weight_kg,
        bmi: rec.bmi,
        body_fat: rec.body_fat,
        tdee: rec.tdee,
        height_cm: rec.height_cm,
      }
      : null,
    diet: lastPlan?.plan || null,
    target: dietForm.target,
  }
  localStorage.setItem('fitluxe_fitness_sync', JSON.stringify(payload))
  ElMessage.success('身材指标与饮食方案已同步，跳转计划制定页')
  router.push('/plans')
}

// ---------- 档案 ----------
async function saveProfile() {
  try {
    await saveBodyProfile({ ...profile, unit_system: unit.value })
    localStorage.setItem('fitluxe_body_profile', JSON.stringify({ ...profile, unit_system: unit.value }))
    ElMessage.success('档案已保存')
  } catch (e: any) {
    ElMessage.error(e?.message || '保存失败')
  }
}

// ---------- 加载 ----------
async function loadRecords() {
  try {
    const res = await getBodyRecords()
    records.value = res.data.items
  } catch {
    records.value = []
  }
}

async function loadProfile() {
  try {
    const res = await getBodyProfile()
    profile.gender = res.data.gender || 'male'
    profile.age = res.data.age || 25
    profile.activity_level = res.data.activity_level || 'light'
    unit.value = res.data.unit_system || 'metric'
  } catch {
    const cached = localStorage.getItem('fitluxe_body_profile')
    if (cached) {
      try {
        const p = JSON.parse(cached)
        profile.gender = p.gender || 'male'
        profile.age = p.age || 25
        profile.activity_level = p.activity_level || 'light'
        unit.value = p.unit_system || 'metric'
      } catch { /* ignore */ }
    }
  }
}

async function loadGoals() {
  try {
    const res = await getBodyGoals()
    if (res.data.items.length) {
      goal.value = res.data.items[0]
      goalSavedAt.value = (goal.value.updated_at || '').slice(0, 10) || new Date().toISOString().slice(0, 10)
      goalForm.target_weight = goal.value.target_weight
      goalForm.target_bmi = goal.value.target_bmi
      goalForm.target_body_fat = goal.value.target_body_fat
    }
  } catch { /* ignore */ }
}

onMounted(async () => {
  dietLogForm.date = new Date().toISOString().slice(0, 10)
  await Promise.all([loadRecords(), loadProfile(), loadGoals(), loadDietPlans(), loadDietLogs()])
  try {
    const res = await getBodyMetrics()
    legacyMetrics.value = res.data
  } catch { /* ignore */ }
})
</script>

<style scoped>
.page-hero { position: relative; padding: 160px 0 80px; background: var(--clr-black); overflow: hidden; }
.page-hero__bg { position: absolute; inset: 0; background: radial-gradient(ellipse at 30% 60%, rgba(201, 169, 110, 0.05), transparent 50%); }
.page-hero__content { position: relative; z-index: 1; }
.page-hero__label { font-size: 11px; letter-spacing: 4px; color: var(--clr-gold); margin-bottom: 16px; display: inline-block; }
.page-hero__title { font-family: var(--font-display); font-size: 48px; font-weight: 400; color: var(--clr-cream); margin-bottom: 16px; letter-spacing: 2px; }
.page-hero__desc { font-size: 15px; color: var(--clr-gray-light); max-width: 500px; }

/* ---------- 个人档案 ---------- */
.profile-strip { padding: 36px 0; }
.profile-strip__inner { display: flex; align-items: center; justify-content: space-between; gap: 32px; flex-wrap: wrap; }
.profile-strip__label { font-size: 11px; letter-spacing: 3px; color: var(--clr-gold); display: block; margin-bottom: 4px; }
.profile-strip__heading { font-family: var(--font-display); font-size: 24px; font-weight: 400; }
.profile-strip__fields { display: flex; align-items: flex-end; gap: 24px; flex-wrap: wrap; }
.profile-strip__field label { display: block; font-size: 12px; color: var(--clr-gray); margin-bottom: 6px; letter-spacing: 1px; }
.profile-strip__save { padding: 11px 24px; }

/* ---------- 核心指标总览 ---------- */
.metrics { padding: 80px 0; }
.metrics__grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 48px; }
.metric-card { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 32px 24px; text-align: center; transition: var(--transition-default); }
.metric-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.06); }
.metric-card__icon { margin-bottom: 16px; color: var(--clr-gold); }
.metric-card__info { display: flex; align-items: baseline; justify-content: center; gap: 4px; margin-bottom: 4px; }
.metric-card__value { font-family: var(--font-display); font-size: 32px; color: var(--clr-dark); }
.metric-card__unit { font-size: 14px; color: var(--clr-gray); }
.metric-card__label { font-size: 13px; color: var(--clr-gray); letter-spacing: 1px; }
.metric-card__trend { margin-top: 12px; font-size: 12px; display: flex; align-items: center; justify-content: center; gap: 4px; }
.metric-card__trend.up { color: #6b8e6b; }
.metric-card__trend.down { color: #888; }
.metric-card__trend.muted { color: var(--clr-gray-light); }

/* ---------- 指标计算与趋势 ---------- */
.analytics { padding: 100px 0; }
.analytics__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-top: 56px; align-items: start; }
.analytics__right { display: flex; flex-direction: column; gap: 28px; }
.panel-card { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 26px; }
.panel-card__head { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.panel-card__title { font-size: 16px; font-weight: 500; display: flex; align-items: center; gap: 8px; }
.panel-card__title .el-icon { color: var(--clr-gold); }
.panel-card__tag { font-size: 11px; color: var(--clr-gold-dark); border: 1px solid rgba(201, 169, 110, 0.4); padding: 2px 8px; letter-spacing: 1px; }

.calc__form { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 24px; margin-bottom: 20px; }
.calc__form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.calc__field label { display: block; font-size: 12px; letter-spacing: 1px; color: var(--clr-gray); margin-bottom: 6px; }
.calc__actions { display: flex; align-items: center; gap: 12px; margin-top: 22px; flex-wrap: wrap; }
.btn-text { background: none; border: none; color: var(--clr-gray); font-size: 13px; letter-spacing: 1px; cursor: pointer; padding: 8px 4px; transition: var(--transition-default); }
.btn-text:hover { color: var(--clr-gold-dark); }
.btn-text--light { color: var(--clr-gray-light); }
.btn-text--light:hover { color: var(--clr-gold); }

.calc__results { min-height: 160px; }
.calc__empty { border: 1px dashed rgba(0, 0, 0, 0.14); padding: 56px 24px; text-align: center; color: var(--clr-gray); font-size: 13px; }
.calc__empty .el-icon { color: var(--clr-gold); margin-bottom: 12px; }
.calc__cards { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.metric-detail-card { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 16px; }
.metric-detail-card__head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
.metric-detail-card__label { font-size: 12px; letter-spacing: 1px; color: var(--clr-gray); }
.metric-detail-card__tag { font-size: 10px; color: var(--clr-gold-dark); border: 1px solid rgba(201, 169, 110, 0.4); padding: 1px 6px; letter-spacing: 0.5px; }
.metric-detail-card__value { display: flex; align-items: baseline; gap: 4px; margin-bottom: 2px; }
.metric-detail-card__num { font-family: var(--font-display); font-size: 26px; color: var(--clr-dark); }
.metric-detail-card__unit { font-size: 12px; color: var(--clr-gray); }
.metric-detail-card__category { font-size: 11px; margin-bottom: 12px; }
.cat-normal { color: #6b8e6b; }
.cat-underweight { color: #c9a96e; }
.cat-overweight { color: #c9a96e; }
.cat-obese { color: #c0392b; }
.cat-unknown { color: var(--clr-gray); }
.metric-detail-card__bar { margin-top: 4px; }
.metric-detail-card__track { position: relative; height: 6px; background: linear-gradient(to right, #c9a96e 0%, #6b8e6b 30%, #6b8e6b 55%, #c9a96e 75%, #c0392b 100%); border-radius: 3px; }
.metric-detail-card__healthy { position: absolute; top: -2px; height: 10px; border: 1px dashed rgba(17, 17, 17, 0.45); border-radius: 3px; background: rgba(255, 255, 255, 0.25); }
.metric-detail-card__dot { position: absolute; top: -4px; width: 14px; height: 14px; border-radius: 50%; background: var(--clr-dark); border: 2px solid var(--clr-white); transform: translateX(-7px); z-index: 2; box-shadow: 0 1px 5px rgba(0, 0, 0, 0.3); }
.metric-detail-card__scale { display: flex; justify-content: space-between; margin-top: 8px; font-size: 10px; color: var(--clr-gray-light); }

.health-tips { margin-top: 18px; background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 18px 20px; }
.health-tips__title { font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 8px; margin-bottom: 12px; color: var(--clr-dark); }
.health-tips__title .el-icon { color: var(--clr-gold); }
.health-tips__list { display: flex; flex-direction: column; gap: 9px; }
.health-tips__item { display: flex; align-items: flex-start; gap: 10px; font-size: 12px; line-height: 1.6; color: var(--clr-gray-deep); }
.health-tips__dot { width: 7px; height: 7px; border-radius: 50%; margin-top: 7px; flex-shrink: 0; }
.health-tips__item--info .health-tips__dot { background: #6b8e6b; }
.health-tips__item--warn .health-tips__dot { background: #c9a96e; }
.health-tips__item--danger .health-tips__dot { background: #c0392b; }
.health-tips__note { margin-top: 12px; font-size: 11px; color: var(--clr-gray-light); }

.bmi-guide { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.04); padding: 8px 22px; }
.bmi-guide__row { display: flex; justify-content: space-between; align-items: center; padding: 13px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.04); }
.bmi-guide__range { font-family: var(--font-display); font-size: 16px; color: var(--clr-dark); }
.bmi-guide__label { font-size: 13px; color: var(--clr-gray); letter-spacing: 1px; }
.bmi-guide__label.normal { color: #6b8e6b; }
.bmi-guide__note { margin-top: 14px; font-size: 11px; color: var(--clr-gray-light); line-height: 1.6; }

.trend-tools { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; }
.trend-foot { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-top: 16px; flex-wrap: wrap; }
.trend-foot__hint { font-size: 12px; color: var(--clr-gray-light); }

/* ---------- AI 智能饮食规划 ---------- */
.ai-diet { padding: 100px 0; }
.ai-diet__card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); padding: 28px; margin-top: 56px; }
.ai-diet__main { display: grid; grid-template-columns: 1fr 1.5fr; gap: 24px; }
.ai-diet__form { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 24px; }
.ai-diet__source { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--clr-gray); background: var(--clr-bg-section); border: 1px dashed rgba(0, 0, 0, 0.14); padding: 10px 12px; margin-bottom: 18px; line-height: 1.6; }
.ai-diet__source .el-icon { color: var(--clr-gold); flex-shrink: 0; }
.ai-diet__field { margin-bottom: 16px; }
.ai-diet__field label { display: block; font-size: 12px; color: var(--clr-gray); letter-spacing: 1px; margin-bottom: 6px; }
.ai-diet__actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.ai-diet__result { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 22px; min-height: 360px; }
.ai-diet__empty { text-align: center; padding: 72px 20px; color: var(--clr-gray); font-size: 14px; }
.ai-diet__empty .el-icon { color: var(--clr-gold); margin-bottom: 14px; }
.ai-diet__mock { background: rgba(201, 169, 110, 0.08); border: 1px dashed rgba(201, 169, 110, 0.5); color: #8a6d3b; font-size: 12px; padding: 10px 14px; margin-bottom: 16px; line-height: 1.7; }
.ai-diet__mock code { background: rgba(0, 0, 0, 0.06); padding: 1px 5px; }
.ai-diet__raw { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.06); padding: 18px; margin-top: 16px; }
.ai-diet__raw-title { font-size: 13px; font-weight: 500; margin-bottom: 10px; }
.ai-diet__raw pre { white-space: pre-wrap; word-break: break-word; font-size: 12px; color: var(--clr-gray-deep); line-height: 1.8; font-family: var(--font-primary); }
.ai-diet__hint { margin-top: 14px; font-size: 12px; color: var(--clr-gray-light); line-height: 1.7; }

.chat-panel { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); display: flex; flex-direction: column; height: 640px; }
.chat-panel__head { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-bottom: 1px solid rgba(0, 0, 0, 0.05); }
.chat-panel__title { font-size: 14px; font-weight: 500; display: flex; align-items: center; gap: 8px; }
.chat-panel__title .el-icon { color: var(--clr-gold); }
.chat-panel__sub { font-size: 11px; color: var(--clr-gray-light); }
.chat-panel__messages { flex: 1; overflow-y: auto; padding: 18px; display: flex; flex-direction: column; gap: 14px; }
.chat-panel__empty { text-align: center; padding: 48px 20px; color: var(--clr-gray); font-size: 13px; }
.chat-panel__empty .el-icon { color: var(--clr-gold); margin-bottom: 12px; }
.chat-panel__empty p { margin-bottom: 16px; line-height: 1.8; }
.chat-msg { display: flex; flex-direction: column; max-width: 94%; }
.chat-msg--user { align-self: flex-end; align-items: flex-end; }
.chat-msg--assistant { align-self: flex-start; align-items: flex-start; }
.chat-msg__bubble { padding: 12px 16px; border-radius: 10px; font-size: 13px; line-height: 1.8; word-break: break-word; }
.chat-msg--user .chat-msg__bubble { background: var(--clr-gold); color: var(--clr-white); border-bottom-right-radius: 2px; }
.chat-msg--assistant .chat-msg__bubble { background: var(--clr-bg-section); color: var(--clr-gray-deep); border: 1px solid rgba(0, 0, 0, 0.05); border-bottom-left-radius: 2px; }
.chat-msg__text pre { white-space: pre-wrap; word-break: break-word; font-size: 13px; color: var(--clr-gray-deep); line-height: 1.8; font-family: var(--font-primary); max-height: 320px; overflow-y: auto; margin-top: 10px; }
.chat-msg__actions { margin-top: 10px; }
.chat-msg__actions .btn-outline-dark { padding: 7px 16px; font-size: 12px; }
.chat-msg__time { font-size: 10px; color: var(--clr-gray-light); margin-top: 4px; }
.chat-msg__thinking { display: flex; gap: 6px; align-items: center; min-width: 60px; justify-content: center; }
.chat-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--clr-gold); animation: chatPulse 1.2s infinite ease-in-out; }
.chat-dot:nth-child(2) { animation-delay: 0.2s; }
.chat-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes chatPulse { 0%, 100% { opacity: 0.3; transform: scale(0.85); } 50% { opacity: 1; transform: scale(1); } }
.chat-panel__chips { display: flex; gap: 8px; flex-wrap: wrap; padding: 12px 14px; border-top: 1px solid rgba(0, 0, 0, 0.05); }
.chat-chip { font-size: 12px; color: var(--clr-gold-dark); background: rgba(201, 169, 110, 0.08); border: 1px solid rgba(201, 169, 110, 0.35); padding: 6px 12px; cursor: pointer; transition: var(--transition-default); }
.chat-chip:hover { background: rgba(201, 169, 110, 0.18); }
.chat-chip:disabled { opacity: 0.5; cursor: not-allowed; }
.chat-panel__input { display: flex; gap: 10px; padding: 12px 14px; border-top: 1px solid rgba(0, 0, 0, 0.05); align-items: flex-end; }
.chat-panel__input .el-textarea { flex: 1; }
.chat-panel__send { padding: 12px 24px; white-space: nowrap; }

.ai-diet__extra { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px; }
.diet-checkin, .weekly-review { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); padding: 22px; }
.ai-extra__title { font-size: 15px; font-weight: 500; display: flex; align-items: center; gap: 8px; color: var(--clr-dark); margin-bottom: 14px; }
.ai-extra__title .el-icon { color: var(--clr-gold); }
.diet-checkin__compare { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px; }
.diet-checkin__cmp-item { display: flex; flex-direction: column; gap: 2px; padding: 12px; background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); }
.diet-checkin__cmp-label { font-size: 11px; color: var(--clr-gray); letter-spacing: 1px; }
.diet-checkin__cmp-item b { font-family: var(--font-display); font-size: 20px; color: var(--clr-dark); font-weight: 400; }
.diet-checkin__cmp-item b.good { color: #6b8e6b; }
.diet-checkin__cmp-item b.bad { color: #c0392b; }
.diet-checkin__cmp-unit { font-size: 11px; color: var(--clr-gray); }
.diet-checkin__form { display: flex; flex-direction: column; gap: 12px; }
.diet-checkin__row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.diet-checkin__field label { display: block; font-size: 12px; color: var(--clr-gray); margin-bottom: 6px; }
.diet-checkin__list { margin-top: 16px; display: flex; flex-direction: column; gap: 8px; }
.diet-checkin__item { display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: var(--clr-bg-section); font-size: 12px; }
.diet-checkin__date { color: var(--clr-gray-deep); }
.diet-checkin__cal { color: var(--clr-dark); font-weight: 500; }
.diet-checkin__macros { color: var(--clr-gray); flex: 1; }

.weekly-review__desc { font-size: 12px; color: var(--clr-gray); line-height: 1.7; margin-bottom: 14px; }
.weekly-review__chips { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 16px; }
.weekly-review__chip { display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); }
.weekly-review__chip-label { font-size: 11px; color: var(--clr-gray); }
.weekly-review__chip b { font-size: 15px; font-weight: 500; color: var(--clr-dark); }
.weekly-review__text { margin-top: 14px; background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.06); padding: 14px; }
.weekly-review__text pre { white-space: pre-wrap; word-break: break-word; font-size: 12px; color: var(--clr-gray-deep); line-height: 1.8; font-family: var(--font-primary); }

.ai-diet__saved { margin-top: 28px; }
.ai-diet__saved-title { font-size: 15px; font-weight: 500; display: flex; align-items: center; gap: 8px; color: var(--clr-cream); margin-bottom: 14px; }
.ai-diet__saved-title .el-icon { color: var(--clr-gold); }
.ai-diet__saved-item { display: flex; align-items: center; justify-content: space-between; gap: 16px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.07); padding: 12px 16px; margin-bottom: 10px; }
.ai-diet__saved-info { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; font-size: 13px; }
.ai-diet__saved-target { color: var(--clr-gold); font-weight: 500; }
.ai-diet__saved-date { color: var(--clr-gray); }
.ai-diet__saved-limit { color: var(--clr-gray-light); font-size: 12px; max-width: 360px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ai-diet__saved-actions { display: flex; gap: 4px; }

/* ---------- 数据管理入口 ---------- */
.data-entry { padding: 100px 0; }
.data-entry__grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-top: 56px; }
.data-entry__card { background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.06); padding: 40px 30px; text-align: center; cursor: pointer; transition: var(--transition-default); }
.data-entry__card:hover { transform: translateY(-5px); box-shadow: 0 14px 44px rgba(0, 0, 0, 0.08); border-color: rgba(201, 169, 110, 0.4); }
.data-entry__icon { color: var(--clr-gold); margin-bottom: 18px; }
.data-entry__title { font-family: var(--font-display); font-size: 20px; font-weight: 400; margin-bottom: 12px; color: var(--clr-dark); }
.data-entry__desc { font-size: 13px; color: var(--clr-gray); line-height: 1.8; margin-bottom: 16px; min-height: 48px; }
.data-entry__meta { display: inline-block; font-size: 12px; color: var(--clr-gray-light); margin-bottom: 18px; }
.data-entry__btn { width: 100%; justify-content: center; }

/* ---------- 通用弹窗 ---------- */
.entry-dialog .measurements__layout, .entry-dialog .goals__layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 24px; align-items: start; }
.entry-dialog .measurements__form { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 22px; }
.entry-dialog .measurements__grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.measurement-field label { display: block; font-size: 12px; color: var(--clr-gray); letter-spacing: 1px; margin-bottom: 6px; }
.entry-dialog .measurements__actions { display: flex; align-items: center; gap: 12px; margin-top: 20px; }
.entry-dialog .measurements__chart { background: var(--clr-bg-dark); border: 1px solid rgba(255, 255, 255, 0.06); padding: 18px; }
.measurements__chart-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; gap: 12px; flex-wrap: wrap; }
.measurements__chart-hint { font-size: 12px; color: var(--clr-gray); }

.entry-dialog .goals__form { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 22px; }
.entry-dialog .goals__form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.goals__field label { display: block; font-size: 12px; color: var(--clr-gray); letter-spacing: 1px; margin-bottom: 6px; }
.entry-dialog .goals__actions { display: flex; align-items: center; gap: 12px; margin-top: 20px; }
.goals__saved { margin-top: 12px; font-size: 12px; color: var(--clr-gray); }
.entry-dialog .goals__result { background: var(--clr-bg-section); border: 1px solid rgba(0, 0, 0, 0.05); padding: 22px; }
.goals__empty { text-align: center; padding: 40px 16px; color: var(--clr-gray); font-size: 13px; }
.goals__empty .el-icon { color: var(--clr-gold); margin-bottom: 12px; }
.goals__empty-note { margin-top: 8px; font-size: 11px; color: var(--clr-gray-light); }
.entry-dialog .goals__progress { display: flex; flex-direction: column; gap: 16px; margin-bottom: 20px; }
.goal-progress__head { display: flex; justify-content: space-between; font-size: 13px; color: var(--clr-dark); margin-bottom: 8px; }
.goal-progress__pct { color: var(--clr-gold-dark); font-weight: 500; }
.goal-progress__track { height: 6px; background: rgba(0, 0, 0, 0.08); border-radius: 3px; overflow: hidden; }
.goal-progress__fill { height: 100%; background: linear-gradient(to right, var(--clr-gold), var(--clr-gold-light)); border-radius: 3px; transition: width 0.5s ease; }
.goal-progress__sub { display: flex; justify-content: space-between; margin-top: 6px; font-size: 11px; color: var(--clr-gray); }
.goal-plan { border-top: 1px solid rgba(0, 0, 0, 0.08); padding-top: 16px; }
.goal-plan__title { font-size: 14px; display: flex; align-items: center; gap: 8px; color: var(--clr-dark); margin-bottom: 12px; font-weight: 500; }
.goal-plan__title .el-icon { color: var(--clr-gold); }
.goal-plan__row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(0, 0, 0, 0.05); font-size: 13px; color: var(--clr-gray-deep); }
.goal-plan__row b { font-weight: 500; color: var(--clr-dark); }
.goal-plan__accent { color: var(--clr-gold-dark) !important; font-size: 16px; }
.goal-plan__note { margin-top: 12px; font-size: 11px; color: var(--clr-gray-light); }

.history__toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; flex-wrap: wrap; }
.history__hint { font-size: 12px; color: var(--clr-gray); }
.history__toolbar-spacer { flex: 1; }
.btn-danger-outline { padding: 9px 18px; background: transparent; color: #b3554a; font-size: 12px; letter-spacing: 2px; border: 1px solid rgba(179, 85, 74, 0.5); cursor: pointer; transition: var(--transition-default); }
.btn-danger-outline:hover { background: rgba(179, 85, 74, 0.08); }
.compare-panel { margin-top: 16px; background: rgba(201, 169, 110, 0.07); border: 1px solid rgba(201, 169, 110, 0.35); padding: 18px 20px; margin-bottom: 18px; }
.compare-panel--light .compare-panel__title { color: var(--clr-dark); }
.compare-panel--light .compare-panel__summary { color: var(--clr-gray-deep); }
.compare-panel--light .compare-item { background: var(--clr-white); }
.compare-panel--light .compare-item__val { color: var(--clr-dark); }
.compare-panel--light .compare-item__label { color: var(--clr-gray); }
.compare-panel__head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.compare-panel__title { font-size: 14px; display: flex; align-items: center; gap: 8px; color: var(--clr-dark); font-weight: 500; }
.compare-panel__summary { font-size: 13px; color: var(--clr-gray-deep); line-height: 1.8; margin-bottom: 14px; }
.compare-panel__grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 10px; }
.compare-item { display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; background: var(--clr-white); border: 1px solid rgba(0, 0, 0, 0.05); }
.compare-item__label { font-size: 11px; color: var(--clr-gray); letter-spacing: 1px; }
.compare-item__val { font-size: 12px; color: var(--clr-dark); }
.compare-item__diff { font-size: 13px; font-weight: 500; }
.compare-item__diff.good { color: #5d8a5d; }
.compare-item__diff.bad { color: #b3554a; }

.stage-tag { font-size: 11px; padding: 2px 8px; border: 1px solid rgba(201, 169, 110, 0.45); color: var(--clr-gold-dark); }
.stage-tag--none { border-color: rgba(0, 0, 0, 0.15); color: var(--clr-gray); }
.table-btn { background: transparent; border: 1px solid rgba(0, 0, 0, 0.2); color: var(--clr-gray-deep); font-size: 12px; padding: 4px 12px; cursor: pointer; margin-right: 8px; transition: var(--transition-default); }
.table-btn:hover { border-color: var(--clr-gold); color: var(--clr-gold-dark); }
.table-btn--active { border-color: var(--clr-gold); color: var(--clr-gold-dark); }
.table-btn--danger { border-color: rgba(179, 85, 74, 0.45); color: #b3554a; }
.table-btn--danger:hover { border-color: #b3554a; color: #b3554a; }

.save-dialog__field { margin-bottom: 16px; }
.save-dialog__field label { display: block; font-size: 12px; color: var(--clr-gray); margin-bottom: 6px; }
.save-dialog__tip { font-size: 12px; color: var(--clr-gray-light); margin-top: 8px; }
.plan-dialog__meta { display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; color: var(--clr-gray); margin-bottom: 16px; }

@media (max-width: 1024px) {
  .metrics__grid { grid-template-columns: repeat(2, 1fr); }
  .analytics__grid, .ai-diet__main, .ai-diet__extra, .data-entry__grid { grid-template-columns: 1fr; }
  .entry-dialog .measurements__layout, .entry-dialog .goals__layout { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .page-hero { padding: 120px 0 56px; }
  .page-hero__title { font-size: 34px; }
  .metrics__grid, .calc__form-grid, .entry-dialog .measurements__grid, .entry-dialog .goals__form-grid, .diet-checkin__row { grid-template-columns: 1fr; }
  .calc__cards, .diet-checkin__compare, .weekly-review__chips { grid-template-columns: 1fr 1fr; }
  .profile-strip__inner { flex-direction: column; align-items: flex-start; }
}
/* ================================================================
   FITLUXE · 黑金轻奢质感升级（仅样式，不改布局与功能）
   主色暖金 #B89C66 / hover #A08652 / 顶部 #0A0A0A / 内容 #F8F5EF
   ================================================================ */
.bodydata-page {
  --clr-gold: #B89C66;
  --clr-gold-dark: #A08652;
  --clr-gold-light: #E2D2AC;
  --clr-accent: #8B7355;
  --clr-dark: #1A1A1A;
  --clr-gray: #777777;
  --clr-gray-light: #A9A29A;
  --clr-gray-lighter: #C9C4BC;
  --clr-bg-section: #F8F5EF;
  --clr-cream-light: #FBF8F2;
  --font-display: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, sans-serif;
  background: #F8F5EF;
}
.bodydata-page,
.bodydata-page * {
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ---------- 1. 卡片：12px 圆角 + 柔和金色弱阴影 + 24px 节奏 ---------- */
.bodydata-page .panel-card,
.bodydata-page .metric-card,
.bodydata-page .metric-detail-card,
.bodydata-page .calc__form,
.bodydata-page .health-tips,
.bodydata-page .bmi-guide,
.bodydata-page .diet-checkin,
.bodydata-page .weekly-review,
.bodydata-page .ai-diet__form,
.bodydata-page .chat-panel,
.bodydata-page .data-entry__card,
.bodydata-page .ai-diet__saved-item,
.bodydata-page .compare-item,
.bodydata-page .entry-dialog .measurements__form,
.bodydata-page .entry-dialog .goals__form,
.bodydata-page .entry-dialog .goals__result {
  border-radius: 12px;
  border-color: rgba(184, 156, 102, 0.18);
  box-shadow: 0 8px 28px rgba(184, 156, 102, 0.10);
}
.bodydata-page .metrics__grid,
.bodydata-page .analytics__grid,
.bodydata-page .data-entry__grid,
.bodydata-page .calc__cards,
.bodydata-page .ai-diet__extra {
  gap: 24px;
}
.bodydata-page .panel-card,
.bodydata-page .ai-diet__form,
.bodydata-page .diet-checkin,
.bodydata-page .weekly-review {
  padding: 28px;
}
.bodydata-page .metric-card {
  border: 1px solid rgba(184, 156, 102, 0.16);
  padding: 36px 24px;
}
.bodydata-page .metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 38px rgba(184, 156, 102, 0.16);
}
.bodydata-page .bmi-guide__row {
  border-bottom: 1px solid rgba(184, 156, 102, 0.16);
}
.bodydata-page .goal-plan__row {
  border-bottom: 1px solid rgba(184, 156, 102, 0.14);
}

/* ---------- 2. 输入框：浅米色 + 聚焦金色高亮；下拉适配 ---------- */
.bodydata-page :deep(.el-input__wrapper),
.bodydata-page :deep(.el-textarea__inner) {
  background: #F3EDDF;
  border-radius: 10px;
  box-shadow: 0 0 0 1px rgba(184, 156, 102, 0.22) inset;
  transition: box-shadow 0.25s ease, background 0.25s ease;
}
.bodydata-page :deep(.el-input__wrapper:hover),
.bodydata-page :deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px rgba(184, 156, 102, 0.45) inset;
}
.bodydata-page :deep(.el-input__wrapper.is-focus),
.bodydata-page :deep(.el-textarea__inner:focus) {
  background: #FBF7EC;
  box-shadow: 0 0 0 1.5px #B89C66 inset, 0 4px 16px rgba(184, 156, 102, 0.16);
}
.bodydata-page :deep(.el-input__inner::placeholder),
.bodydata-page :deep(.el-textarea__inner::placeholder) {
  color: #B9B2A8;
}
:global(.el-select-dropdown__item.is-selected) {
  color: #A08652;
  font-weight: 600;
}
:global(.el-select-dropdown__item:hover),
:global(.el-select-dropdown__item.is-hovering) {
  background: #F3EDDF;
}
:global(.el-popper.is-light) {
  border-radius: 10px;
  border-color: rgba(184, 156, 102, 0.25);
  box-shadow: 0 12px 32px rgba(184, 156, 102, 0.14);
}

/* ---------- 3. 按钮分层 ---------- */
.bodydata-page .btn-primary {
  background: linear-gradient(135deg, #C6A878, #B89C66);
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(184, 156, 102, 0.28);
  transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease, opacity 0.25s ease;
}
.bodydata-page .btn-primary:hover {
  transform: translateY(-1px);
  background: linear-gradient(135deg, #C9AD7E, #A08652);
  box-shadow: 0 10px 24px rgba(184, 156, 102, 0.36);
}
.bodydata-page .btn-primary:disabled {
  opacity: 0.55;
  transform: none;
  box-shadow: none;
}
.bodydata-page .btn-outline-dark {
  background: #FFFFFF;
  color: #A08652;
  border: 1px solid #B89C66;
  border-radius: 10px;
  transition: transform 0.25s ease, background 0.25s ease, box-shadow 0.25s ease;
}
.bodydata-page .btn-outline-dark:hover {
  background: #FBF7EC;
  color: #A08652;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(184, 156, 102, 0.18);
}
.bodydata-page .btn-outline {
  color: #E8DFCF;
  border: 1px solid rgba(184, 156, 102, 0.65);
  border-radius: 10px;
}
.bodydata-page .btn-outline:hover {
  background: rgba(184, 156, 102, 0.16);
  color: #E8DFCF;
}
.bodydata-page .chat-chip {
  background: #F3EDDF;
  color: #A08652;
  border: 1px solid rgba(184, 156, 102, 0.35);
  border-radius: 999px;
  padding: 7px 14px;
}
.bodydata-page .chat-chip:hover {
  background: #EADFC7;
  color: #8A6D3B;
}
.bodydata-page .btn-danger-outline {
  color: #B96A5E;
  border-color: rgba(185, 106, 94, 0.45);
  border-radius: 10px;
}
.bodydata-page .table-btn {
  border-radius: 8px;
  border-color: rgba(184, 156, 102, 0.3);
  color: #8B7355;
}
.bodydata-page .table-btn:hover {
  border-color: #B89C66;
  color: #A08652;
}
.bodydata-page .table-btn--active {
  border-color: #B89C66;
  color: #A08652;
  background: rgba(184, 156, 102, 0.08);
}
.bodydata-page .table-btn--danger {
  border-color: rgba(185, 106, 94, 0.4);
  color: #B96A5E;
}

/* ---------- 4. AI 对话气泡 ---------- */
.bodydata-page .chat-panel__messages {
  background: #FCFAF5;
}
.bodydata-page .chat-msg--assistant .chat-msg__bubble {
  background: #F6EEDD;
  border: 1px solid rgba(184, 156, 102, 0.28);
  border-left: 3px solid #B89C66;
  border-radius: 4px 12px 12px 12px;
}
.bodydata-page .chat-msg--user .chat-msg__bubble {
  background: #F0EFEB;
  color: #1A1A1A;
  border-radius: 12px 4px 12px 12px;
}
.bodydata-page .chat-msg__text pre {
  color: #4A463F;
}
.bodydata-page .chat-panel__input {
  background: #FFFFFF;
}
.bodydata-page .chat-panel__head {
  background: linear-gradient(135deg, #FFFFFF, #F8F5EF);
}

/* ---------- 6. 淡入淡出加载动画 ---------- */
@keyframes goldFadeInUp {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes goldFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.bodydata-page .chat-msg {
  animation: goldFadeInUp 0.4s ease both;
}
.bodydata-page .chat-msg__thinking {
  animation: goldFadeIn 0.3s ease both;
}
.bodydata-page .calc__cards .metric-detail-card {
  animation: goldFadeInUp 0.5s ease both;
}
.bodydata-page .calc__cards .metric-detail-card:nth-child(2) { animation-delay: 0.05s; }
.bodydata-page .calc__cards .metric-detail-card:nth-child(3) { animation-delay: 0.1s; }
.bodydata-page .calc__cards .metric-detail-card:nth-child(4) { animation-delay: 0.15s; }
.bodydata-page .calc__cards .metric-detail-card:nth-child(5) { animation-delay: 0.2s; }
.bodydata-page .calc__cards .metric-detail-card:nth-child(6) { animation-delay: 0.25s; }
.bodydata-page .calc__cards .metric-detail-card:nth-child(7) { animation-delay: 0.3s; }
.bodydata-page .panel-card,
.bodydata-page .data-entry__card {
  animation: goldFadeInUp 0.5s ease both;
}

/* 表单参数修改后的淡金色提示小字 */
.bodydata-page .form-hint {
  margin-top: 10px;
  font-size: 12px;
  color: #A08652;
  background: rgba(184, 156, 102, 0.10);
  border: 1px solid rgba(184, 156, 102, 0.28);
  padding: 7px 12px;
  border-radius: 8px;
  animation: goldFadeInUp 0.35s ease both;
}

/* ---------- 7. 留白与去线条 ---------- */
.bodydata-page .section {
  padding: 88px 0;
}
.bodydata-page .panel-card__head {
  margin-bottom: 24px;
}
.bodydata-page .metric-detail-card {
  padding: 20px;
}
.bodydata-page .metric-detail-card__bar {
  margin-top: 8px;
}
.bodydata-page .health-tips {
  padding: 22px 24px;
}
.bodydata-page .ai-diet__card {
  border-radius: 16px;
  border-color: rgba(184, 156, 102, 0.22);
  padding: 32px;
}
.bodydata-page .ai-diet__saved-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}
.bodydata-page .data-entry__card {
  border-radius: 16px;
  padding: 44px 32px;
}
.bodydata-page .data-entry__card:hover {
  border-color: rgba(184, 156, 102, 0.5);
  box-shadow: 0 16px 44px rgba(184, 156, 102, 0.16);
}
.bodydata-page .entry-dialog .measurements__layout,
.bodydata-page .entry-dialog .goals__layout {
  gap: 24px;
}
.bodydata-page .entry-dialog .measurements__chart {
  border-radius: 12px;
}
.bodydata-page .stage-tag {
  color: #A08652;
  border-color: rgba(184, 156, 102, 0.45);
  border-radius: 6px;
}
.bodydata-page .diet-summary__num,
.bodydata-page .diet-macro__val {
  font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
}
</style>
