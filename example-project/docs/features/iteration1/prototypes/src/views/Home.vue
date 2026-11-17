<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const cards = [
  {
    title: '终端用户端',
    desc: '检索、预约、订单与评价',
    href: '/user',
    links: [
      { href: '/user/search', label: '检索咨询师' },
      { href: '/user/booking', label: '预约下单' },
      { href: '/user/my-orders', label: '我的预约' },
      { href: '/user/login', label: '登录注册' },
    ],
  },
  {
    title: '咨询师端',
    desc: '入驻、档期、履约与结算',
    href: '/consultant',
    links: [
      { href: '/consultant/application', label: '入驻申请' },
      { href: '/consultant/schedule', label: '档期管理' },
      { href: '/consultant/orders', label: '预约管理' },
      { href: '/consultant/settlements', label: '收入结算' },
    ],
  },
  {
    title: '管理端',
    desc: '看板、审核、分类与治理',
    href: '/admin',
    links: [
      { href: '/admin/applications', label: '入驻审核' },
      { href: '/admin/categories', label: '分类标签' },
      { href: '/admin/users', label: '用户管理' },
      { href: '/admin/reports', label: '举报处理' },
    ],
  },
]
</script>

<template>
  <main class="proto-main" style="max-width: 960px; margin: 0 auto">
    <h1 class="proto-page-title">咨询师预约平台 · 原型入口</h1>
    <p class="proto-page-desc">iteration1 · Vite + Vue 3 + Element Plus demo</p>
    <el-row :gutter="16">
      <el-col v-for="card in cards" :key="card.title" :span="8">
        <el-card class="proto-card-gap">
          <template #header><strong>{{ card.title }}</strong></template>
          <p style="color: #909399; margin-top: 0">{{ card.desc }}</p>
          <el-button type="primary" @click="router.push(card.href)">进入</el-button>
          <ul style="padding-left: 18px; margin: 12px 0 0">
            <li v-for="l in card.links" :key="l.href">
              <a class="proto-link" href="#" @click.prevent="router.push(l.href)">{{ l.label }}</a>
            </li>
          </ul>
        </el-card>
      </el-col>
    </el-row>
  </main>
</template>
