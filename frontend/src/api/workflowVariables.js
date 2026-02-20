import request from '@/utils/request'

// 获取流程变量列表
export function getVariables(params) {
  return request.get('/workflow-variables', { params })
}

// 创建流程变量
export function createVariable(data) {
  return request.post('/workflow-variables', data)
}

// 更新流程变量
export function updateVariable(id, data) {
  return request.put(`/workflow-variables/${id}`, data)
}

// 删除流程变量
export function deleteVariable(id) {
  return request.delete(`/workflow-variables/${id}`)
}

// 获取流程变量详情
export function getVariable(id) {
  return request.get(`/workflow-variables/${id}`)
}