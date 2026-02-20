import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台', permission: 'dashboard' }
      },
      {
        path: 'task-detail/:id',
        name: 'TaskDetail',
        component: () => import('@/views/TaskDetail.vue'),
        meta: { title: '任务详情', hidden: true }
      },
      {
        path: 'green-identify',
        name: 'GreenIdentify',
        redirect: '/green-identify/pending',
        meta: { title: '绿色认定' },
        children: [
          {
            path: 'pending',
            name: 'TaskPending',
            component: () => import('@/views/TaskPending.vue'),
            meta: { title: '待办任务', permission: 'green-identify-pending' }
          },
          {
            path: 'completed',
            name: 'TaskCompleted',
            component: () => import('@/views/TaskCompleted.vue'),
            meta: { title: '已办任务', permission: 'green-identify-completed' }
          },
          {
            path: 'archived',
            name: 'TaskArchived',
            component: () => import('@/views/TaskArchived.vue'),
            meta: { title: '办结任务', permission: 'green-identify-archived' }
          },
          {
            path: 'query',
            name: 'TaskQuery',
            component: () => import('@/views/TaskQuery.vue'),
            meta: { title: '综合查询', permission: 'green-identify-query' }
          },
          {
            path: 'online-report',
            name: 'OnlineReport',
            component: () => import('@/views/OnlineReport.vue'),
            meta: { title: '在线报表', permission: 'green-identify-query' }
          }
        ]
      },
      {
        path: 'system',
        name: 'System',
        component: () => import('@/views/System.vue'),
        meta: { title: '系统管理' },
        redirect: '/system/user',
        children: [
          {
            path: 'user',
            name: 'SystemUser',
            component: () => import('@/views/SystemUser.vue'),
            meta: { title: '用户管理', permission: 'system-user' }
          },
          {
            path: 'role',
            name: 'SystemRole',
            component: () => import('@/views/SystemRole.vue'),
            meta: { title: '角色管理', permission: 'system-role' }
          },
          {
            path: 'org',
            name: 'SystemOrg',
            component: () => import('@/views/SystemOrg.vue'),
            meta: { title: '机构管理', permission: 'system-org' }
          },
          {
            path: 'log',
            name: 'Log',
            redirect: '/system/log/operation',
            meta: { title: '日志管理' },
            children: [
              {
                path: 'operation',
                name: 'LogOperation',
                component: () => import('@/views/LogOperation.vue'),
                meta: { title: '操作日志', permission: 'system-log-operation' }
              },
              {
                path: 'login',
                name: 'LogLogin',
                component: () => import('@/views/LogLogin.vue'),
                meta: { title: '登录日志', permission: 'system-log-login' }
              },
              {
                path: 'exception',
                name: 'LogException',
                component: () => import('@/views/LogException.vue'),
                meta: { title: '异常日志', permission: 'system-log-exception' }
              }
            ]
          }
        ]
      },
      {
        path: 'workflow',
        name: 'Workflow',
        redirect: '/workflow/management',
        meta: { title: '流程管理' },
        children: [
          {
            path: 'designer',
            name: 'WorkflowDesigner',
            component: () => import('@/views/WorkflowDesigner.vue'),
            meta: { title: '流程设计器', hidden: true }
          },
          {
            path: 'management',
            name: 'WorkflowManagement',
            component: () => import('@/views/WorkflowManagement.vue'),
            meta: { title: '流程管理', permission: 'workflow-management' }
          },
          {
            path: 'instances',
            name: 'WorkflowInstances',
            component: () => import('@/views/WorkflowInstances.vue'),
            meta: { title: '流程实例', permission: 'workflow-instances' }
          },
          {
            path: 'variables',
            name: 'WorkflowVariables',
            component: () => import('@/views/WorkflowVariables.vue'),
            meta: { title: '流程变量', permission: 'workflow-variables' }
          }
        ]
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    // 检查权限（超级管理员跳过权限检查）
    if (to.meta.requiresAuth && !authStore.user?.is_superuser && to.meta.permission) {
      const hasPermission = authStore.permissions?.includes(to.meta.permission)
      if (!hasPermission) {
        // 没有权限，跳转到登录页
        next('/login')
        return
      }
    }
    // 如果已认证，重置无操作计时器
    if (authStore.isAuthenticated) {
      authStore.resetInactivityTimer()
    }
    next()
  }
})

export default router