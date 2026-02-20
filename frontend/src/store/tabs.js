import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTabsStore = defineStore('tabs', () => {
  const tabs = ref([
    {
      name: 'Dashboard',
      title: '工作台',
      path: '/dashboard'
    }
  ])
  
  const activeTab = ref('/dashboard')
  
  // 添加页签
  function addTab(route) {
    // 支持自定义标题和query参数
    const title = route.title || route.meta?.title || '未知'
    const path = route.path
    const query = route.query || {}
    
    // 检查是否已存在（包含query参数）
    const pathWithQuery = Object.keys(query).length > 0 
      ? `${path}?${new URLSearchParams(query).toString()}`
      : path
      
    const existTab = tabs.value.find(tab => tab.path === pathWithQuery || tab.path === path)
    
    if (!existTab) {
      tabs.value.push({
        name: route.name || route.path,
        title: title,
        path: pathWithQuery,
        originalPath: path
      })
    }
    activeTab.value = pathWithQuery
  }
  
  // 移除页签
  function removeTab(path) {
    const index = tabs.value.findIndex(tab => tab.path === path)
    if (index !== -1) {
      tabs.value.splice(index, 1)
      
      // 如果关闭的是当前激活的页签，切换到前一个或后一个
      if (activeTab.value === path && tabs.value.length > 0) {
        const newIndex = Math.max(0, index - 1)
        activeTab.value = tabs.value[newIndex].path
      }
    }
  }
  
  // 关闭其他页签
  function closeOtherTabs(path) {
    const currentTab = tabs.value.find(tab => tab.path === path)
    if (currentTab) {
      tabs.value = [currentTab]
      activeTab.value = path
    }
  }
  
  // 关闭所有页签（保留首页）
  function closeAllTabs() {
    const dashboardTab = tabs.value.find(tab => tab.path === '/dashboard')
    tabs.value = dashboardTab ? [dashboardTab] : []
    activeTab.value = '/dashboard'
  }
  
  // 关闭左侧页签
  function closeLeftTabs(path) {
    const index = tabs.value.findIndex(tab => tab.path === path)
    if (index > 0) {
      tabs.value = tabs.value.slice(index)
    }
  }
  
  // 关闭右侧页签
  function closeRightTabs(path) {
    const index = tabs.value.findIndex(tab => tab.path === path)
    if (index !== -1) {
      tabs.value = tabs.value.slice(0, index + 1)
    }
  }
  
  // 设置激活页签
  function setActiveTab(path) {
    activeTab.value = path
  }
  
  return {
    tabs,
    activeTab,
    addTab,
    removeTab,
    closeOtherTabs,
    closeAllTabs,
    closeLeftTabs,
    closeRightTabs,
    setActiveTab
  }
})