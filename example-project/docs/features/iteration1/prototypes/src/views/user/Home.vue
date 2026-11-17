<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'
const router=useRouter()
const q=reactive({keyword:'',category:'全部分类',price:'any',date:''})
const categories=['全部分类','职业发展','情绪心理','家庭教育','法律咨询']
const hot=[{name:'职业发展',count:326},{name:'情绪心理',count:218},{name:'家庭教育',count:154},{name:'法律咨询',count:97}]
const list=[{name:'李文静',tags:['职业规划','简历优化'],rating:4.9,price:'¥399 / 次',slot:'今天 15:00'},{name:'周砚秋',tags:['情绪心理','压力管理'],rating:4.8,price:'¥499 / 次',slot:'明天 10:30'},{name:'陈舒',tags:['家庭教育','亲子沟通'],rating:4.7,price:'¥359 / 次',slot:'周六 09:00'}]
</script>
<template><UserLayout who="未登录" auth-action="登录" auth-to="/user/login">
<h1 class="proto-page-title">找到适合你的咨询师</h1><p class="proto-page-desc">按领域、价格与可预约时间筛选，支持在线预约与履约保障。</p>
<el-card class="proto-card-gap"><el-form :inline="true"><el-form-item label="关键词"><el-input v-model="q.keyword" placeholder="姓名 / 领域 / 服务" /></el-form-item><el-form-item label="分类"><el-select v-model="q.category" style="width:140px"><el-option v-for="c in categories" :key="c" :label="c" :value="c" /></el-select></el-form-item><el-form-item label="价格"><el-select v-model="q.price" style="width:140px"><el-option label="不限" value="any"/><el-option label="200 以下" value="lt200"/><el-option label="200-500" value="200-500"/><el-option label="500 以上" value="gt500"/></el-select></el-form-item><el-form-item label="可约日期"><el-date-picker v-model="q.date" type="date"/></el-form-item><el-form-item><el-button type="primary" @click="router.push('/user/search')">搜索咨询师</el-button></el-form-item></el-form></el-card>
<div class="proto-section-title">热门分类</div><el-row :gutter="12" class="proto-card-gap"><el-col v-for="c in hot" :key="c.name" :span="6"><el-card shadow="hover" style="cursor:pointer" @click="router.push('/user/search')"><strong>{{c.name}}</strong><div style="color:#909399;font-size:12px;margin-top:6px">{{c.count}} 位咨询师</div></el-card></el-col></el-row>
<div class="proto-section-title">推荐咨询师</div><el-card class="proto-card-gap"><el-table :data="list" stripe><el-table-column label="咨询师"><template #default="{row}"><a href="/user/consultant-detail" class="proto-link" @click.prevent="router.push('/user/consultant-detail')">{{row.name}}</a></template></el-table-column><el-table-column label="擅长"><template #default="{row}"><el-tag v-for="t in row.tags" :key="t" size="small" style="margin-right:4px">{{t}}</el-tag></template></el-table-column><el-table-column prop="rating" label="评分" width="80"/><el-table-column prop="price" label="价格" width="120"/><el-table-column prop="slot" label="可预约" width="120"/><el-table-column label="操作" width="100"><template #default><el-button type="primary" link @click="router.push('/user/booking')">预约</el-button></template></el-table-column></el-table></el-card>
<div class="proto-section-title">平台保障</div><el-card><ul><li>咨询师入驻需平台资质审核，档案信息可查。</li><li>支付由平台担保，咨询完成后结算给咨询师。</li><li>支持订单投诉与平台介入处理。</li></ul></el-card>
</UserLayout></template>
