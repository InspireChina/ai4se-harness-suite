<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps<{
  title: string
  who: string
  base: '/consultant' | '/admin'
  items: { path: string; label: string }[]
}>()

const route = useRoute()
const router = useRouter()
const active = computed(() => route.path)

function go(path: string) {
  router.push(path)
}
</script>

<template>
  <div class="proto-layout">
    <aside class="proto-aside">
      <h2>{{ props.title }}</h2>
      <el-menu
        background-color="#001529"
        text-color="#fff"
        active-text-color="#409eff"
        :default-active="active"
        router
      >
        <el-menu-item v-for="item in props.items" :key="item.path" :index="item.path">
          <span>{{ item.label }}</span>
        </el-menu-item>
      </el-menu>
      <p class="muted">{{ props.who }}</p>
      <p class="muted" style="cursor: pointer" @click="go('/')">← 返回入口</p>
    </aside>
    <main class="proto-main">
      <slot />
    </main>
  </div>
</template>
