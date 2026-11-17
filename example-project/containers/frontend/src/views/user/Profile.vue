<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { profileService } from '@/services/profileService'
import { favoriteService } from '@/services/favoriteService'
import { agreementService } from '@/services/agreementService'
import { useAuthStore } from '@/stores/auth'
import { AGREEMENT_LABELS } from '@/constants/agreements'
import type { AgreementConsent, FavoriteItem } from '@/types'
import UserLayout from '@/layouts/UserLayout.vue'

const auth = useAuthStore()

const form = reactive({ nickname: '', avatarUrl: '', email: '', cityCode: '', locale: 'zh-CN' })
const saving = ref(false)
const favorites = ref<FavoriteItem[]>([])
const agreements = ref<AgreementConsent[]>([])
const consultantId = ref('stub-consultant-001')
const loading = ref(false)

async function loadAll() {
  loading.value = true
  try {
    const [me, favs, agrees] = await Promise.all([
      profileService.me(),
      favoriteService.list(),
      agreementService.list(),
    ])
    form.nickname = me.profile?.nickname || ''
    form.avatarUrl = me.profile?.avatarUrl || ''
    form.email = me.profile?.email || ''
    form.cityCode = me.profile?.cityCode || ''
    form.locale = me.profile?.locale || 'zh-CN'
    auth.setProfile(me.profile)
    favorites.value = favs
    agreements.value = agrees
  } catch (e: any) {
    ElMessage.warning(e.response?.data?.errorMessage || '加载个人中心失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    const updated = await profileService.updateProfile({
      nickname: form.nickname,
      avatarUrl: form.avatarUrl,
      email: form.email,
      cityCode: form.cityCode,
      locale: form.locale,
    })
    auth.setProfile(updated)
    ElMessage.success('资料已保存')
  } catch (e: any) {
    ElMessage.warning(e.response?.data?.errorMessage || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleAddFavorite() {
  if (!consultantId.value) {
    ElMessage.warning('请输入咨询师 ID')
    return
  }
  try {
    await favoriteService.add(consultantId.value)
    favorites.value = await favoriteService.list()
    ElMessage.success('收藏成功')
  } catch (e: any) {
    ElMessage.warning(e.response?.data?.errorMessage || '收藏失败')
  }
}

async function handleRemoveFavorite(id: string) {
  try {
    await ElMessageBox.confirm('确认取消该收藏？', '提示', { type: 'warning' })
  } catch {
    return
  }
  try {
    await favoriteService.remove(id)
    favorites.value = await favoriteService.list()
    ElMessage.success('已取消收藏')
  } catch (e: any) {
    ElMessage.warning(e.response?.data?.errorMessage || '取消收藏失败')
  }
}

function formatTime(value: string) {
  return new Date(value).toLocaleString()
}

onMounted(loadAll)
</script>

<template>
  <UserLayout>
    <div v-loading="loading">
      <h1 class="page-title">个人中心</h1>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-card class="card-gap">
            <template #header>个人资料</template>
            <el-form label-width="80px" @submit.prevent>
              <el-form-item label="手机号">
                <el-input :model-value="auth.user?.phone || ''" disabled id="profile-phone" />
              </el-form-item>
              <el-form-item label="昵称">
                <el-input v-model="form.nickname" id="profile-nickname" :disabled="loading" />
              </el-form-item>
              <el-form-item label="头像">
                <el-input v-model="form.avatarUrl" placeholder="头像地址" id="profile-avatar" :disabled="loading" />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="form.email" id="profile-email" :disabled="loading" />
              </el-form-item>
              <el-form-item label="城市">
                <el-input v-model="form.cityCode" placeholder="城市编码，如 310000" id="profile-city" :disabled="loading" />
              </el-form-item>
              <el-form-item label="语言">
                <el-input v-model="form.locale" id="profile-locale" :disabled="loading" />
              </el-form-item>
              <el-button type="primary" :loading="saving" :disabled="loading" id="profile-save" @click="handleSave">
                保存
              </el-button>
            </el-form>
          </el-card>

          <el-card>
            <template #header>协议同意记录</template>
            <div id="agreement-list">
            <el-table :data="agreements" size="small" empty-text="暂无协议同意记录">
              <el-table-column label="协议" width="120">
                <template #default="{ row }">{{ AGREEMENT_LABELS[row.agreementType] || row.agreementType }}</template>
              </el-table-column>
              <el-table-column prop="agreementVersion" label="版本" width="90" />
              <el-table-column label="同意时间">
                <template #default="{ row }">{{ formatTime(row.consentedAt) }}</template>
              </el-table-column>
              <el-table-column prop="sourceIp" label="来源 IP" />
            </el-table>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="card-gap">
            <template #header>我的咨询师</template>
            <div class="favorites__add">
              <el-input v-model="consultantId" placeholder="咨询师 ID" id="favorite-consultant-id" :disabled="loading" />
              <el-button id="favorite-add" :disabled="loading" @click="handleAddFavorite">收藏</el-button>
            </div>
            <div id="favorite-list">
            <el-table :data="favorites" size="small" empty-text="暂无收藏">
              <el-table-column prop="consultantId" label="咨询师" />
              <el-table-column label="收藏时间" width="180">
                <template #default="{ row }">{{ formatTime(row.createdAt) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button link type="danger" class="favorite-remove" @click="handleRemoveFavorite(row.consultantId)">
                    取消收藏
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </UserLayout>
</template>

<style scoped>
.page-title {
  margin: 0 0 16px;
}
.card-gap {
  margin-bottom: 16px;
}
.favorites__add {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
</style>
