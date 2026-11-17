import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
// 统一中文语言包（弹窗按钮等文案随 locale 走 zh-cn）
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
