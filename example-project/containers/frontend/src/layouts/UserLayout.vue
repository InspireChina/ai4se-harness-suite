<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const displayName = computed(() => auth.profile?.nickname || auth.user?.phone || '未登录')

function handleLogout() {
  auth.logout()
  router.push('/user/login')
}
</script>

<template>
  <div class="layout">
    <header class="layout__header">
      <div class="layout__brand">咨询预约平台</div>
      <nav class="layout__nav">
        <router-link to="/">首页</router-link>
        <router-link to="/user/profile">个人中心</router-link>
      </nav>
      <div class="layout__user">
        <template v-if="auth.isLoggedIn">
          <span class="layout__name">{{ displayName }}</span>
          <el-button link type="primary" @click="handleLogout">退出</el-button>
        </template>
        <router-link v-else to="/user/login">登录 / 注册</router-link>
      </div>
    </header>
    <main class="layout__main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  background: #f5f7fa;
}
.layout__header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 24px;
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}
.layout__brand {
  font-weight: 600;
  font-size: 18px;
}
.layout__nav {
  display: flex;
  gap: 16px;
  flex: 1;
}
.layout__nav a {
  color: #606266;
  text-decoration: none;
}
.layout__nav a.router-link-active {
  color: #409eff;
}
.layout__user {
  display: flex;
  align-items: center;
  gap: 8px;
}
.layout__name {
  color: #606266;
}
.layout__main {
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px;
}
</style>
