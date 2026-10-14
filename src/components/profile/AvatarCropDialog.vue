<template>
  <el-dialog v-model="visible" title="裁剪头像" width="460px" append-to-body @opened="initCropper" @closed="destroyCropper">
    <div class="avatar-crop">
      <div v-if="imageUrl" class="avatar-crop__box">
        <img ref="imgRef" :src="imageUrl" class="avatar-crop__img" alt="头像" />
      </div>
      <p v-else class="avatar-crop__empty">请先选择图片</p>
      <p class="avatar-crop__tip">拖动调整位置，滚轮缩放，确认后生成正方形头像</p>
    </div>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :disabled="!imageUrl" @click="confirmCrop">确认裁剪</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, shallowRef, watch, onBeforeUnmount } from 'vue'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'
import { ElMessage } from 'element-plus'

const visible = defineModel<boolean>({ default: false })

const props = defineProps<{
  src: string
  fallbackFile?: File | null
}>()

const emit = defineEmits<{
  (e: 'cropped', blob: Blob): void
}>()

const imgRef = ref<HTMLImageElement | null>(null)
const imageUrl = ref('')
/** 裁切器实例：必须是响应式（shallowRef），否则确认按钮的 disabled 状态不会刷新 */
const cropper = shallowRef<Cropper | null>(null)

watch(
  () => props.src,
  (v) => {
    if (v) imageUrl.value = v
  }
)

// 打开状态变化时兜底初始化（@opened 与状态监听双保险）
watch([visible, imageUrl], () => {
  if (visible.value && imageUrl.value) {
    initCropper()
  }
})

/** 弹窗打开动画结束 + 图片加载完成后初始化裁切器 */
function initCropper() {
  destroyCropper()
  const img = imgRef.value
  if (!img || !imageUrl.value) return
  const start = () => {
    try {
      cropper.value = new Cropper(img, {
        aspectRatio: 1,
        viewMode: 1,
        autoCropArea: 1,
        background: false,
        movable: true,
        zoomable: true,
        rotatable: false,
        scalable: false,
      })
    } catch (e) {
      console.error('[AvatarCrop] cropper init failed:', e)
    }
  }
  if (img.complete) {
    start()
  } else {
    img.addEventListener('load', start, { once: true })
  }
}

function destroyCropper() {
  if (cropper.value) {
    cropper.value.destroy()
    cropper.value = null
  }
}

function confirmCrop() {
  // 裁切器未就绪时降级：直接用原图上传，保证功能可用
  if (!cropper.value) {
    if (props.fallbackFile) {
      emit('cropped', props.fallbackFile as Blob)
      visible.value = false
    } else {
      ElMessage.warning('图片尚未就绪，请重新选择')
    }
    return
  }
  try {
    const canvas = cropper.value.getCroppedCanvas({ width: 256, height: 256 })
    canvas.toBlob((blob) => {
      if (blob) {
        emit('cropped', blob)
        visible.value = false
      }
    }, 'image/png')
  } catch (e) {
    console.error('[AvatarCrop] crop failed:', e)
    ElMessage.error('裁剪失败，请重新选择图片')
  }
}

onBeforeUnmount(destroyCropper)
</script>

<style scoped>
.avatar-crop__box {
  width: 100%;
  height: 300px;
  overflow: hidden;
  background: #EAF6F2;
  border-radius: 10px;
}
.avatar-crop__img { display: block; max-width: 100%; }
.avatar-crop__empty { text-align: center; padding: 90px 0; color: var(--clr-gray-light); font-size: 13px; }
.avatar-crop__tip { margin-top: 12px; font-size: 12px; color: var(--clr-gray-light); }
</style>
