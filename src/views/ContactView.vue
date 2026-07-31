<template>
  <div class="contact-page">
    <section class="page-hero">
      <div class="page-hero__bg"></div>
      <div class="page-hero__content container">
        <span class="page-hero__label">GET IN TOUCH</span>
        <h1 class="page-hero__title">联系</h1>
        <p class="page-hero__desc">无论你想咨询课程、定制计划还是提出建议，我们随时倾听。</p>
      </div>
    </section>

    <section class="contact__body section section-white">
      <div class="container">
        <div class="contact__grid">
          <div class="contact__form-wrap">
            <p class="section-subtitle">SEND A MESSAGE</p>
            <h2 class="section-title">发送留言</h2>
            <div class="gold-divider-left" style="margin:20px 0;"></div>
            <el-form ref="formRef" :model="form" :rules="formRules" label-position="top" class="contact__form">
              <el-form-item label="姓名" prop="name"><el-input v-model="form.name" placeholder="你的名字" /></el-form-item>
              <div class="contact__form-row">
                <el-form-item label="邮箱" prop="email"><el-input v-model="form.email" placeholder="your@email.com" /></el-form-item>
                <el-form-item label="电话" prop="phone"><el-input v-model="form.phone" placeholder="手机号码" /></el-form-item>
              </div>
              <el-form-item label="主题" prop="subject">
                <el-select v-model="form.subject" placeholder="选择主题" style="width:100%;">
                  <el-option label="课程咨询" value="course" />
                  <el-option label="计划定制" value="plan" />
                  <el-option label="教练预约" value="coach" />
                  <el-option label="合作洽谈" value="partner" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>
              <el-form-item label="留言内容" prop="message">
                <el-input v-model="form.message" type="textarea" :rows="5" placeholder="请详细描述你的需求…" />
              </el-form-item>
              <el-form-item>
                <button type="button" class="btn-primary" @click="submitForm">发送留言<el-icon><Promotion /></el-icon></button>
              </el-form-item>
            </el-form>
          </div>

          <div class="contact__info">
            <div class="contact__info-card">
              <div class="contact__info-item">
                <div class="contact__info-icon"><el-icon :size="22"><Location /></el-icon></div>
                <div><h4>地址</h4><p>{{ siteInfo.address }}<br />{{ siteInfo.address_extra }}</p></div>
              </div>
              <div class="contact__info-divider"></div>
              <div class="contact__info-item">
                <div class="contact__info-icon"><el-icon :size="22"><Phone /></el-icon></div>
                <div><h4>电话</h4><p><a :href="'tel:' + siteInfo.phone.replace(/[^+\d]/g, '')">{{ siteInfo.phone }}</a></p></div>
              </div>
              <div class="contact__info-divider"></div>
              <div class="contact__info-item">
                <div class="contact__info-icon"><el-icon :size="22"><Message /></el-icon></div>
                <div><h4>邮箱</h4><p><a :href="'mailto:' + siteInfo.email">{{ siteInfo.email }}</a></p></div>
              </div>
              <div class="contact__info-divider"></div>
              <div class="contact__info-item">
                <div class="contact__info-icon"><el-icon :size="22"><Clock /></el-icon></div>
                <div><h4>营业时间</h4><p>{{ siteInfo.hours_weekday }}<br />{{ siteInfo.hours_weekend }}</p></div>
              </div>
            </div>
            <div class="contact__social">
              <h4>关注我们</h4>
              <div class="contact__social-icons">
                <a href="#" class="contact__social-icon">微信</a>
                <a href="#" class="contact__social-icon">微博</a>
                <a href="#" class="contact__social-icon">小红书</a>
                <a href="#" class="contact__social-icon">抖音</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Location, Phone, Message, Clock, Promotion } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { submitContact, getContactInfo } from '@/api'

const formRef = ref<FormInstance>()
const form = reactive({ name: '', email: '', phone: '', subject: '', message: '' })
const submitting = ref(false)

const siteInfo = ref({
  address: '上海市静安区南京西路1788号',
  address_extra: '久光中心 12F',
  phone: '+86 21 6188 3000',
  email: 'hello@fitluxe.com',
  hours_weekday: '周一至周五 7:00 - 22:00',
  hours_weekend: '周末及节假日 8:00 - 20:00',
})

onMounted(async () => {
  try {
    const res = await getContactInfo()
    if (res && res.data) {
      const d = res.data
      if (d.address) {
        const parts = d.address.split('\n')
        siteInfo.value.address = parts[0] || siteInfo.value.address
        siteInfo.value.address_extra = parts[1] || siteInfo.value.address_extra
      }
      if (d.phone) siteInfo.value.phone = d.phone
      if (d.email) siteInfo.value.email = d.email
      if (d.business_hours) {
        if (d.business_hours.weekday) siteInfo.value.hours_weekday = '周一至周五 ' + d.business_hours.weekday
        if (d.business_hours.weekend) siteInfo.value.hours_weekend = '周末及节假日 ' + d.business_hours.weekend
      }
    }
  } catch {
    // fallback to defaults
  }
})


const formRules: FormRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }, { type: 'email', message: '请输入有效邮箱地址', trigger: 'blur' }],
  subject: [{ required: true, message: '请选择主题', trigger: 'change' }],
  message: [{ required: true, message: '请输入留言内容', trigger: 'blur' }],
}

async function submitForm() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await submitContact({ name: form.name, email: form.email, phone: form.phone, subject: form.subject, message: form.message })
    ElMessage.success('留言已提交，我们将尽快与你联系！')
    form.name = ''; form.email = ''; form.phone = ''
    form.subject = ''; form.message = ''
  } catch (e: any) {
    ElMessage.error(e?.message || '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-hero { position:relative; padding:160px 0 80px; background:var(--clr-black); overflow:hidden; }
.page-hero__bg { position:absolute; inset:0; background:radial-gradient(ellipse at 30% 60%,rgba(201,169,110,0.05),transparent 50%); }
.page-hero__content { position:relative; z-index:1; }
.page-hero__label { font-size:11px; letter-spacing:4px; color:var(--clr-gold); margin-bottom:16px; display:inline-block; }
.page-hero__title { font-family:var(--font-display); font-size:48px; font-weight:400; color:var(--clr-cream); margin-bottom:16px; letter-spacing:2px; }
.page-hero__desc { font-size:15px; color:var(--clr-gray-light); max-width:500px; }

.contact__grid { display:grid; grid-template-columns:1.2fr 1fr; gap:64px; align-items:start; }
.contact__form :deep(.el-input__wrapper), .contact__form :deep(.el-textarea__inner) { border-radius:0; box-shadow:0 0 0 1px rgba(0,0,0,0.08) inset; }
.contact__form :deep(.el-input__wrapper:hover), .contact__form :deep(.el-textarea__inner:hover) { box-shadow:0 0 0 1px var(--clr-gold) inset; }
.contact__form-row { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.contact__info-card { background:var(--clr-bg-section); border:1px solid rgba(0,0,0,0.04); padding:40px 32px; }
.contact__info-item { display:flex; gap:16px; align-items:flex-start; }
.contact__info-item h4 { font-family:var(--font-display); font-size:15px; font-weight:400; letter-spacing:1px; margin-bottom:4px; color:var(--clr-dark); }
.contact__info-item p, .contact__info-item a { font-size:13px; color:var(--clr-gray); line-height:1.6; text-decoration:none; }
.contact__info-item a:hover { color:var(--clr-gold); }
.contact__info-icon { width:48px; height:48px; flex-shrink:0; display:flex; align-items:center; justify-content:center; color:var(--clr-gold); border:1px solid rgba(201,169,110,0.2); }
.contact__info-divider { height:1px; background:rgba(0,0,0,0.04); margin:20px 0; }
.contact__social { margin-top:36px; }
.contact__social h4 { font-family:var(--font-display); font-size:14px; font-weight:400; letter-spacing:1px; margin-bottom:16px; color:var(--clr-dark); }
.contact__social-icons { display:flex; gap:12px; }
.contact__social-icon { padding:10px 20px; font-size:12px; letter-spacing:1px; color:var(--clr-gray); text-decoration:none; border:1px solid rgba(0,0,0,0.08); transition:var(--transition-default); }
.contact__social-icon:hover { color:var(--clr-gold); border-color:var(--clr-gold); }

@media (max-width:1024px) { .contact__grid { grid-template-columns:1fr; gap:48px; } }
@media (max-width:768px) { .contact__form-row { grid-template-columns:1fr; } }
</style>

