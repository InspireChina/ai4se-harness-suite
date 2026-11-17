<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authService } from '@/services/authService'
import { agreementService } from '@/services/agreementService'
import { useAuthStore } from '@/stores/auth'
import { AGREEMENT_VERSIONS } from '@/constants/agreements'
import UserLayout from '@/layouts/UserLayout.vue'

const router = useRouter()
const auth = useAuthStore()

const form = reactive({ phone: '', code: '', nickname: '', agree: false })
const sending = ref(false)
const loading = ref(false)
const sent = ref(false)

async function handleSendCode() {
  if (!form.phone) {
    ElMessage.warning('请输入手机号')
    return
  }
  sending.value = true
  try {
    await authService.sendSmsCode(form.phone)
    sent.value = true
    ElMessage.success('验证码已发送')
  } catch (e: any) {
    ElMessage.warning(e.response?.data?.errorMessage || '验证码发送失败')
  } finally {
    sending.value = false
  }
}

async function handleLogin() {
  if (!form.phone || !form.code) {
    ElMessage.warning('请输入手机号与验证码')
    return
  }
  if (!form.agree) {
    ElMessage.warning('请先阅读并同意《服务协议》与《隐私政策》')
    return
  }
  loading.value = true
  try {
    const res = await authService.smsLogin({
      phone: form.phone,
      code: form.code,
      nickname: form.nickname || undefined,
    })
    auth.setLogin(res)
    await recordAgreements()
    ElMessage.success('登录成功')
    router.push('/user/profile')
  } catch (e: any) {
    ElMessage.warning(e.response?.data?.errorMessage || '登录失败')
  } finally {
    loading.value = false
  }
}

/** 记录协议同意（按类型 + 版本幂等），失败不阻断登录。 */
async function recordAgreements() {
  try {
    await agreementService.consent('service', AGREEMENT_VERSIONS.service)
    await agreementService.consent('privacy', AGREEMENT_VERSIONS.privacy)
  } catch {
    // 协议中心（PLT）上线后由后端校验，此处仅尽力记录
  }
}
</script>

<template>
  <UserLayout>
    <div class="login">
      <el-card class="login__card">
        <template #header><strong>手机号登录 / 注册</strong></template>
        <el-form label-position="top" @submit.prevent>
          <el-form-item label="手机号">
            <el-input id="login-phone" v-model="form.phone" placeholder="11 位手机号" />
          </el-form-item>
          <el-form-item label="验证码">
            <div class="login__code">
              <el-input id="login-code" v-model="form.code" placeholder="6 位验证码" />
              <el-button :loading="sending" id="login-send-code" @click="handleSendCode">
                {{ sent ? '重新发送' : '获取验证码' }}
              </el-button>
            </div>
          </el-form-item>
          <el-form-item label="昵称（新用户可选）">
            <el-input id="login-nickname" v-model="form.nickname" placeholder="缺省由系统生成" />
          </el-form-item>
          <el-checkbox v-model="form.agree" class="login__agree">
            已阅读并同意《服务协议》与《隐私政策》
          </el-checkbox>
          <el-button
            type="primary"
            class="login__submit"
            :loading="loading"
            id="login-submit"
            @click="handleLogin"
          >
            登录 / 注册
          </el-button>
        </el-form>
      </el-card>
    </div>
  </UserLayout>
</template>

<style scoped>
.login {
  max-width: 420px;
  margin: 40px auto;
}
.login__code {
  display: flex;
  gap: 8px;
  width: 100%;
}
.login__submit {
  width: 100%;
  margin-top: 12px;
}
</style>
