import request from './index'

export const getDashboard = () => {
  return request({
    url: '/dashboard',
    method: 'get'
  })
}

export const getPendingTasks = (params) => {
  return request({
    url: '/tasks/pending',
    method: 'get',
    params
  })
}

export const getCompletedTasks = (params) => {
  return request({
    url: '/tasks/completed',
    method: 'get',
    params
  })
}

export const getArchivedTasks = (params) => {
  return request({
    url: '/tasks/archived',
    method: 'get',
    params
  })
}

export const getTaskDetail = (taskId) => {
  return request({
    url: `/tasks/${taskId}`,
    method: 'get'
  })
}

export const completeTask = (taskId, data) => {
  return request({
    url: `/tasks/${taskId}/complete`,
    method: 'post',
    data
  })
}

export const withdrawTask = (taskId) => {
  return request({
    url: `/tasks/${taskId}/withdraw`,
    method: 'post'
  })
}

export const getWorkflowHistory = (id) => {
  return request({
    url: `/identifications/${id}/workflow`,
    method: 'get',
    params: {
      t: Date.now() // 添加时间戳强制不使用缓存
    }
  })
}

export const getWorkflowInstance = (id) => {
  return request({
    url: `/identifications/${id}/workflow-instance`,
    method: 'get'
  })
}

export const searchTasks = (params) => {
  return request({
    url: '/tasks/search',
    method: 'get',
    params
  })
}

export const exportTasks = (params) => {
  return request({
    url: '/tasks/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

export const getGreenCategories = () => {
  return request({
    url: '/green-categories',
    method: 'get'
  })
}

export const updateTaskCategory = (taskId, data) => {
  return request({
    url: `/tasks/${taskId}/category`,
    method: 'put',
    data
  })
}

export const saveTask = (taskId, data) => {
  return request({
    url: `/tasks/${taskId}/save`,
    method: 'post',
    data
  })
}

export const returnTask = (taskId, data) => {
  return request({
    url: `/tasks/${taskId}/return`,
    method: 'post',
    data
  })
}

export const getOnlineReport = (params) => {
  return request({
    url: '/tasks/online-report',
    method: 'get',
    params
  })
}