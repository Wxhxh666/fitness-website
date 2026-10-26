<template>
  <el-dialog v-model="visible" :title="`咨询 · ${peerName}`" width="520px"
    :close-on-click-modal="false" @open="onOpen" @closed="onClosed">
    <div ref="listRef" class="chat">
      <div v-if="loading" class="chat__loading">加载中...</div>
      <div v-else-if="messages.length === 0" class="chat__empty">
        还没有消息，打个招呼吧
      </div>
      <div v-for="m in messages" :key="m.id" class="chat__row"
        :class="{ 'chat__row--mine': m.sender_id === meId }">
        <div class="chat__bubble" :class="{ 'chat__bubble--mine': m.sender_id === meId }">
          <p class="chat__text">{{ m.content }}</p>
          <span class="chat__time">{{ fmtTime(m.created_at) }}</span>
        </div>
      </div>
    </div>
    <div class="chat__input">
      <el-input v-model="draft" type="textarea" :rows="2" maxlength="1000" show-word-limit
        placeholder="输入消息（Enter 发送，Shift+Enter 换行）" @keydown.enter.exact.prevent="submit" />
      <el-button type="primary" :loading="sending" @click="submit">
        <el-icon><Promotion /></el-icon> 发送
      </el-button>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { nextTick, ref } from "vue"
import { ElMessage } from "element-plus"
import { getMessages, sendMessage } from "@/api/coach"

const props = defineProps<{
  relationId: number
  peerName: string
}>()

const visible = defineModel<boolean>({ required: true })

const messages = ref<any[]>([])
const meId = ref(0)
const loading = ref(false)
const sending = ref(false)
const draft = ref("")
const listRef = ref<HTMLElement>()
let pollTimer: number | undefined
let lastId = 0

function fmtTime(s?: string) {
  if (!s) return ""
  return s.slice(5, 16).replace("T", " ")
}

async function scrollToBottom() {
  await nextTick()
  if (listRef.value) listRef.value.scrollTop = listRef.value.scrollHeight
}

async function fetchMessages() {
  try {
    const res = await getMessages(props.relationId, lastId)
    meId.value = res.data.me
    if (res.data.items.length) {
      messages.value.push(...res.data.items)
      lastId = res.data.items[res.data.items.length - 1].id
      scrollToBottom()
    }
  } catch (e: any) {
    // 轮询失败静默（会话可能已被解绑关闭）
    if (lastId === 0) ElMessage.error(e?.message || "消息加载失败")
  }
}

async function onOpen() {
  messages.value = []
  lastId = 0
  loading.value = true
  await fetchMessages()
  loading.value = false
  pollTimer = window.setInterval(fetchMessages, 5000)
}

function onClosed() {
  if (pollTimer) { window.clearInterval(pollTimer); pollTimer = undefined }
}

async function submit() {
  const content = draft.value.trim()
  if (!content) return
  sending.value = true
  try {
    const res = await sendMessage(props.relationId, content)
    messages.value.push(res.data)
    lastId = res.data.id
    draft.value = ""
    scrollToBottom()
  } catch (e: any) {
    ElMessage.error(e?.message || "发送失败")
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.chat {
  height: 360px; overflow-y: auto; padding: 12px;
  background: #f7f8f7; border-radius: 8px; display: flex; flex-direction: column; gap: 10px;
}
.chat__loading, .chat__empty { text-align: center; color: #999; font-size: 13px; margin-top: 40px; }
.chat__row { display: flex; }
.chat__row--mine { justify-content: flex-end; }
.chat__bubble {
  max-width: 72%; background: #fff; border-radius: 10px; padding: 8px 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.chat__bubble--mine { background: #d9f7ec; }
.chat__text { margin: 0; font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; }
.chat__time { font-size: 10px; color: #a0a8a4; }
.chat__input { display: flex; gap: 8px; margin-top: 12px; align-items: flex-end; }
</style>
