export const consultantNav = [
  { path: '/consultant', label: '工作台' },
  { path: '/consultant/application', label: '入驻申请' },
  { path: '/consultant/profile', label: '档案维护' },
  { path: '/consultant/schedule', label: '档期管理' },
  { path: '/consultant/orders', label: '预约管理' },
  { path: '/consultant/settlements', label: '收入结算' },
] as const

export const adminNav = [
  { path: '/admin', label: '运营看板' },
  { path: '/admin/applications', label: '入驻审核' },
  { path: '/admin/categories', label: '分类与标签' },
  { path: '/admin/users', label: '用户管理' },
  { path: '/admin/orders', label: '订单监控' },
  { path: '/admin/reports', label: '举报处理' },
] as const
