import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import {
  Aim, ArrowDown, ArrowRight, Bottom, Bowl, Calendar, ChatDotRound, Check, CircleCheck, Clock,
  Close, CoffeeCup, Compass, Crop, DataAnalysis, DataBoard, Delete, DocumentChecked, Download,
  Edit, Files, FirstAidKit, Flag, FolderAdd, Histogram, HomeFilled, InfoFilled, KnifeFork,
  Lightning, Link, List, Location, Lock, MagicStick, Medal, Message, Notebook, Odometer, Phone,
  Plus, Promotion, Refresh, Select, Setting, Sunny, Sunrise, Switch, Timer, Top, TrendCharts,
  Trophy, TrophyBase, User, UserFilled, VideoCamera, Warning,
} from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import './styles/global.css'

/**
 * 全局图标白名单。
 *
 * 这里只注册项目真正用到的图标，而不是 `import * as Icons` 全量注册
 * （后者会把 293 个图标全部打进 bundle，实测 element chunk 约 950KB）。
 * 模板里的 `<User />` 和 `icon: 'User'` 这类字符串动态组件都依赖全局注册，
 * 所以新增图标时务必把名字补进这个对象。
 * 追加后可执行 `python scripts/scan-icons.py` 核对是否还有遗漏。
 */
const ICONS = {
  Aim, ArrowDown, ArrowRight, Bottom, Bowl, Calendar, ChatDotRound, Check, CircleCheck, Clock,
  Close, CoffeeCup, Compass, Crop, DataAnalysis, DataBoard, Delete, DocumentChecked, Download,
  Edit, Files, FirstAidKit, Flag, FolderAdd, Histogram, HomeFilled, InfoFilled, KnifeFork,
  Lightning, Link, List, Location, Lock, MagicStick, Medal, Message, Notebook, Odometer, Phone,
  Plus, Promotion, Refresh, Select, Setting, Sunny, Sunrise, Switch, Timer, Top, TrendCharts,
  Trophy, TrophyBase, User, UserFilled, VideoCamera, Warning,
}

const app = createApp(App)
app.use(ElementPlus, { locale: zhCn })
app.use(router)

for (const [key, component] of Object.entries(ICONS)) {
  app.component(key, component)
}

app.mount('#app')
