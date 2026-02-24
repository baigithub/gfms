<template>
  <div class="layout-container">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <div class="logo-icon">
          <el-icon :size="28" color="white"><ElementPlus /></el-icon>
        </div>
        <div class="logo-text">
          <span class="logo-title">绿色金融</span>
          <span class="logo-subtitle">Green Finance</span>
        </div>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="false"
        :unique-opened="true"
        router
        background-color="transparent"
        text-color="rgba(255, 255, 255, 0.8)"
        active-text-color="#ffffff"
      >
        <el-menu-item v-if="hasMenuPermission('/dashboard') || authStore.user?.is_superuser" index="/dashboard">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-sub-menu v-if="greenIdentifyMenus.length > 0 || authStore.user?.is_superuser" index="green-identify">
          <template #title>
            <el-icon><ElementPlus /></el-icon>
            <span>绿色认定</span>
          </template>
          <el-menu-item
            v-for="menu in greenIdentifyMenus"
            :key="menu.path"
            :index="menu.path"
          >
            {{ menu.label }}
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu v-if="systemMenus.length > 0 || authStore.user?.is_superuser" index="system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item
            v-for="menu in systemMenus"
            :key="menu.path"
            :index="menu.path"
          >
            {{ menu.label }}
          </el-menu-item>
          
          <!-- 日志管理子菜单 -->
          <el-sub-menu v-if="logMenus.length > 0 || authStore.user?.is_superuser" index="log">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>日志管理</span>
            </template>
            <el-menu-item
              v-for="menu in logMenus"
              :key="menu.path"
              :index="menu.path"
            >
              {{ menu.label }}
            </el-menu-item>
          </el-sub-menu>
        </el-sub-menu>
        
        <el-sub-menu v-if="workflowMenus.length > 0 || authStore.user?.is_superuser" index="workflow">
          <template #title>
            <el-icon><Operation /></el-icon>
            <span>流程管理</span>
          </template>
          <el-menu-item
            v-for="menu in workflowMenus"
            :key="menu.path"
            :index="menu.path"
          >
            {{ menu.label }}
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <div class="main-container">
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item to="/">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentTitle">{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <div class="header-item">
            <el-icon :size="18" color="#667eea"><Bell /></el-icon>
          </div>
          <el-dropdown @command="handleUserCommand">
            <div class="user-info">
              <div class="user-avatar">
                <el-avatar :size="36" :icon="UserFilled" />
              </div>
              <div class="user-details">
                <div class="user-name">{{ authStore.user?.real_name }}</div>
                <div class="user-role">{{ authStore.user?.role_name || '用户' }}</div>
              </div>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <div class="tabs-container">
        <el-tabs
          v-model="tabsStore.activeTab"
          type="card"
          closable
          @tab-remove="handleTabRemove"
          @tab-click="handleTabClick"
        >
          <el-tab-pane
            v-for="tab in tabsStore.tabs"
            :key="tab.path"
            :label="tab.title"
            :name="tab.path"
          >
            <template #label>
              <el-dropdown
                trigger="contextmenu"
                @command="(cmd) => handleTabCommand(cmd, tab.path)"
              >
                <span class="tab-label">{{ tab.title }}</span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="close">关闭</el-dropdown-item>
                    <el-dropdown-item command="closeOthers">关闭其他</el-dropdown-item>
                    <el-dropdown-item command="closeLeft">关闭左侧</el-dropdown-item>
                    <el-dropdown-item command="closeRight">关闭右侧</el-dropdown-item>
                    <el-dropdown-item command="closeAll">关闭全部</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" :key="route.fullPath" />
          </keep-alive>
        </router-view>
      </el-main>
    </div>
  </div>
</template>

<script setup>
import { computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ElementPlus, 
  House, 
  Setting, 
  Operation, 
  UserFilled, 
  User,
  Bell,
  ArrowDown,
  SwitchButton,
  Document
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/auth'
import { useTabsStore } from '@/store/tabs'
import { logout } from '@/api/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const tabsStore = useTabsStore()

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title)

// 菜单权限映射
const menuPermissions = {
  '/dashboard': 'dashboard',
  '/green-identify/pending': 'green-identify-pending',
  '/green-identify/completed': 'green-identify-completed',
  '/green-identify/archived': 'green-identify-archived',
  '/green-identify/query': 'green-identify-query',
  '/green-identify/online-report': 'green-identify-query',
  '/system/user': 'system-user',
  '/system/role': 'system-role',
  '/system/org': 'system-org',
  '/system/log/operation': 'system-log-operation',
  '/system/log/login': 'system-log-login',
  '/system/log/exception': 'system-log-exception',
  '/workflow/management': 'workflow-management',
  '/workflow/instances': 'workflow-instances'
}

// 检查是否有菜单权限
const hasMenuPermission = (path) => {
  const permission = menuPermissions[path]
  if (!permission) return true
  return authStore.permissions?.includes(permission) || authStore.user?.is_superuser
}

// 计算绿色认定子菜单
const greenIdentifyMenus = computed(() => {
  const menus = [
    { path: '/green-identify/pending', label: '待办任务', permission: 'green-identify-pending' },
    { path: '/green-identify/completed', label: '已办任务', permission: 'green-identify-completed' },
    { path: '/green-identify/archived', label: '办结任务', permission: 'green-identify-archived' },
    { path: '/green-identify/query', label: '综合查询', permission: 'green-identify-query' },
    { path: '/green-identify/online-report', label: '在线报表', permission: 'green-identify-query' }
  ]
  return menus.filter(m => authStore.permissions?.includes(m.permission) || authStore.user?.is_superuser)
})

// 计算系统管理子菜单
const systemMenus = computed(() => {
  const menus = [
    { path: '/system/user', label: '用户管理', permission: 'system-user' },
    { path: '/system/announcement', label: '公告管理', permission: 'system-announcement' },
    { path: '/system/role', label: '角色管理', permission: 'system-role' },
    { path: '/system/org', label: '机构管理', permission: 'system-org' }
  ]
  return menus.filter(m => authStore.permissions?.includes(m.permission) || authStore.user?.is_superuser)
})

// 计算日志管理子菜单
const logMenus = computed(() => {
  const menus = [
    { path: '/system/log/operation', label: '操作日志', permission: 'system-log-operation' },
    { path: '/system/log/login', label: '登录日志', permission: 'system-log-login' },
    { path: '/system/log/exception', label: '异常日志', permission: 'system-log-exception' }
  ]
  return menus.filter(m => authStore.permissions?.includes(m.permission) || authStore.user?.is_superuser)
})

// 计算流程管理子菜单
const workflowMenus = computed(() => {
  const menus = [
    { path: '/workflow/management', label: '流程管理', permission: 'workflow-management' },
    { path: '/workflow/instances', label: '流程实例', permission: 'workflow-instances' },
    { path: '/workflow/variables', label: '流程变量', permission: 'workflow-variables' }
  ]
  return menus.filter(m => authStore.permissions?.includes(m.permission) || authStore.user?.is_superuser)
})

// 监听路由变化，添加页签
watch(() => route.path, (newPath) => {
  if (newPath && !route.meta.hidden) {
    tabsStore.addTab(route)
  }
}, { immediate: true })

// 处理页签关闭
const handleTabRemove = (path) => {
  tabsStore.removeTab(path)
  if (tabsStore.activeTab !== path) {
    router.push(tabsStore.activeTab)
  }
}

// 处理页签点击
const handleTabClick = (tab) => {
  const tabPath = tab.props.name
  const [path, queryString] = tabPath.split('?')
  if (queryString) {
    const params = new URLSearchParams(queryString)
    const query = Object.fromEntries(params)
    router.push({ path, query })
  } else {
    router.push(path)
  }
}

// 处理右键菜单命令
const handleTabCommand = (command, path) => {
  switch (command) {
    case 'close':
      tabsStore.removeTab(path)
      break
    case 'closeOthers':
      tabsStore.closeOtherTabs(path)
      break
    case 'closeLeft':
      tabsStore.closeLeftTabs(path)
      break
    case 'closeRight':
      tabsStore.closeRightTabs(path)
      break
    case 'closeAll':
      tabsStore.closeAllTabs()
      break
  }
}

// 处理用户下拉菜单命令
const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await logout()
        authStore.logout()
        tabsStore.closeAllTabs()
        ElMessage.success('退出成功')
        router.push('/login')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('退出失败')
        }
      }
      break
  }
}

onMounted(() => {
  if (route.path && !route.meta.hidden) {
    tabsStore.addTab(route)
  }
})
</script>

<style scoped>
.layout-container {
  display: flex;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.sidebar {
  background: linear-gradient(180deg, #0A6633 0%, #0d5a2e 100%);
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 100;
}

.sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 10% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 90% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1;
}

.logo-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 18px;
  font-weight: 700;
  color: white;
  letter-spacing: 0.5px;
  line-height: 1.2;
}

.logo-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 400;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

:deep(.el-menu) {
  border: none;
  padding: 8px 0;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  margin: 0 12px;
  border-radius: 8px;
  padding: 0 16px;
  height: 44px;
  line-height: 44px;
  transition: all 0.3s ease;
  margin-bottom: 4px;
}

:deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.8);
}

:deep(.el-menu-item .el-icon),
:deep(.el-sub-menu__title .el-icon) {
  margin-right: 10px;
  font-size: 18px;
}

:deep(.el-menu-item span),
:deep(.el-sub-menu__title span) {
  font-size: 14px;
  font-weight: 500;
}

:deep(.el-sub-menu__title:hover),
:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: white;
  transform: translateX(2px);
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%) !important;
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

:deep(.el-sub-menu .el-menu-item) {
  background-color: transparent !important;
  margin-left: 24px;
  margin-right: 12px;
  padding-left: 20px;
}

:deep(.el-sub-menu .el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-sub-menu .el-menu-item.is-active) {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%) !important;
}

:deep(.el-sub-menu .el-sub-menu__title .el-sub-menu__icon-arrow) {
  color: rgba(255, 255, 255, 0.6);
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.header-left {
  flex: 1;
}

:deep(.el-breadcrumb) {
  font-size: 14px;
}

:deep(.el-breadcrumb__inner) {
  color: #667eea;
  font-weight: 500;
  transition: color 0.3s;
}

:deep(.el-breadcrumb__inner:hover) {
  color: #764ba2;
}

:deep(.el-breadcrumb__separator) {
  color: #c0c4cc;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-item {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.header-item:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 12px;
  transition: all 0.3s;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.user-info:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.user-avatar {
  position: relative;
}

.user-avatar::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  background: #52c41a;
  border: 2px solid white;
  border-radius: 50%;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.2;
}

.user-role {
  font-size: 12px;
  color: #95a5a6;
  font-weight: 400;
  line-height: 1.2;
}

.dropdown-icon {
  color: #95a5a6;
  transition: transform 0.3s;
  font-size: 14px;
}

.user-info:hover .dropdown-icon {
  transform: rotate(180deg);
}

:deep(.el-dropdown-menu__item) {
  padding: 10px 16px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
}

.tabs-container {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 8px 24px 0;
}

.tabs-container :deep(.el-tabs--card) {
  border: none;
}

.tabs-container :deep(.el-tabs__nav) {
  border: none !important;
}

.tabs-container :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.tabs-container :deep(.el-tabs--card > .el-tabs__header) {
  border: none;
  margin: 0;
}

.tabs-container :deep(.el-tabs--card > .el-tabs__header .el-tabs__item) {
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px 8px 0 0;
  margin-right: 8px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  color: #667eea;
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s;
  border-bottom: none;
}

.tabs-container :deep(.el-tabs--card > .el-tabs__header .el-tabs__item:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #764ba2;
  transform: translateY(-2px);
}

.tabs-container :deep(.el-tabs--card > .el-tabs__header .el-tabs__item.is-active) {
  background: linear-gradient(135deg, #a5b4fc 0%, #c4b5fd 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  border-bottom: none;
}

.tabs-container :deep(.el-tabs--card > .el-tabs__header .el-tabs__item .el-icon-close) {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  transition: all 0.3s;
  margin-left: 8px;
  font-size: 12px;
}

.tabs-container :deep(.el-tabs--card > .el-tabs__header .el-tabs__item .el-icon-close:hover) {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.main-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  position: relative;
}

.main-content::-webkit-scrollbar {
  width: 8px;
}

.main-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

.main-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}
</style>