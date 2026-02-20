import request from '@/utils/request'

// 流程定义
export function createDefinition(data) {
  return request.post('/workflow/definitions', data)
}

export function getDefinitions(params) {
  return request.get('/workflow/definitions', { params })
}

export function getDefinition(id) {
  return request.get(`/workflow/definitions/${id}`)
}

export function getDefinitionById(id) {
  return request.get(`/workflow/definitions/${id}`)
}

export function updateDefinition(id, data) {
  return request.put(`/workflow/definitions/${id}`, data)
}

export function deleteDefinition(id) {
  return request.delete(`/workflow/definitions/${id}`)
}

export function activate(id) {
  return request.post(`/workflow/definitions/${id}/activate`)
}

export function deactivate(id) {
  return request.post(`/workflow/definitions/${id}/deactivate`)
}

export function createTaskNodes(definitionId, nodes) {
  return request.post(`/workflow/definitions/${definitionId}/nodes`, nodes)
}

export function getTaskNodes(definitionId) {
  return request.get(`/workflow/definitions/${definitionId}/nodes`)
}

// 流程实例
export function startInstance(data) {
  return request.post('/workflow/instances', data)
}

export function getInstances(params) {
  return request.get('/workflow/instances', { params })
}

export function getInstance(instanceId) {
  return request.get(`/workflow/instances/${instanceId}`)
}

export function getInstanceTasks(instanceId) {
  return request.get(`/workflow/instances/${instanceId}/tasks`)
}

export function deleteInstance(instanceId) {
  return request.delete(`/workflow/instances/${instanceId}`)
}

// 绿色金融工作流实例
export function getGreenFinanceInstances(params) {
  return request.get('/workflow-instances', { params })
}

export function deleteGreenFinanceInstance(instanceId) {
  return request.delete(`/workflow-instances/${instanceId}`)
}

export function getGreenFinanceInstanceTasks(instanceId) {
  return request.get(`/workflow-instances/${instanceId}/tasks`)
}

// 任务
export function getMyTasks() {
  return request.get('/workflow/tasks/my-tasks')
}

export function completeTask(taskId, data) {
  return request.post(`/workflow/tasks/${taskId}/complete`, data)
}