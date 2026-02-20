import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import jQuery from 'jquery'

// 全局设置 jQuery，luckysheet 需要
window.$ = jQuery
window.jQuery = jQuery

// 导入 jquery-mousewheel - 使用默认导出
import jQueryMousewheel from 'jquery-mousewheel'
jQueryMousewheel(jQuery)

// BPMN.js 样式
import 'bpmn-js/dist/assets/diagram-js.css'
import 'bpmn-js/dist/assets/bpmn-font/css/bpmn.css'

// 全局表格样式
import './styles/table-styles.css'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './store/auth'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus, { locale: zhCn })

app.mount('#app')

// 添加用户操作监听，重置无操作计时器
const userActivities = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click']

userActivities.forEach(event => {
  document.addEventListener(event, () => {
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) {
      authStore.resetInactivityTimer()
    }
  }, { passive: true })
})