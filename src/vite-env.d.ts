/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// element-plus 的语言包没有随包提供类型声明，这里补一个，否则 vue-tsc 会报 TS7016
declare module 'element-plus/dist/locale/zh-cn.mjs' {
  import type { Language } from 'element-plus/es/locale'
  const locale: Language
  export default locale
}
