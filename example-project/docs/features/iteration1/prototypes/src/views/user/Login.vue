<script setup lang="ts">
import { reactive,ref } from 'vue'
import { useRouter } from 'vue-router'
import UserLayout from '@/layouts/UserLayout.vue'
const router=useRouter(); const sent=ref(false); const form=reactive({phone:'',code:'',agree:false})
</script>
<template><UserLayout who="未登录" auth-action="登录" auth-to="/user/login"><div style="max-width:420px;margin:40px auto"><el-card><template #header><strong>手机号登录 / 注册</strong></template><el-form label-position="top"><el-form-item label="手机号"><el-input v-model="form.phone" placeholder="11 位手机号"/></el-form-item><el-form-item label="验证码"><div style="display:flex;gap:8px;width:100%"><el-input v-model="form.code" placeholder="6 位验证码"/><el-button @click="sent=true">{{sent?'已发送':'获取验证码'}}</el-button></div></el-form-item><el-checkbox v-model="form.agree">已阅读并同意《服务协议》与《隐私政策》</el-checkbox><el-button type="primary" style="width:100%;margin-top:12px" @click="router.push('/user')">登录 / 注册</el-button></el-form></el-card></div></UserLayout></template>
