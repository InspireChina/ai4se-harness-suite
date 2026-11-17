<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = withDefaults(
  defineProps<{
    who?: string
    authAction?: string
    authTo?: string
  }>(),
  {
    who: '138****6688',
    authAction: '退出',
    authTo: '/user/login',
  },
)

const route = useRoute()
const router = useRouter()
const active = computed(() => route.path)

function go(path: string) {
  router.push(path)
}
</script>

<template>
  <header class="proto-topbar">
    <div class="proto-brand" @click="go('/')">咨询师预约平台</div>
    <el-menu mode="horizontal" :ellipsis="false" :default-active="active" style="flex: 1; border: none" router>
      <el-menu-item index="/user">首页</el-menu-item>
      <el-menu-item index="/user/search">找咨询师</el-menu-item>
      <el-menu-item index="/user/my-orders">我的预约</el-menu-item>
      <el-menu-item index="/user/profile">个人中心</el-menu-item>
    </el-menu>
    <div>
      <span style="color: #909399; margin-right: 8px">{{ props.who }}</span>
      <el-button link type="primary" @click="go(props.authTo)">{{ props.authAction }}</el-button>
    </div>
  </header>
  <main class="proto-main">
    <slot />
  </main>
</template>
