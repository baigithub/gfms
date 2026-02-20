import request from '@/utils/request'

// ==================== 操作日志 ====================

/**
 * 获取操作日志列表
 */
export function getOperationLogs(params) {
  return request({
    url: '/logs/operations',
    method: 'get',
    params
  })
}

/**
 * 删除操作日志
 */
export function deleteOperationLog(id) {
  return request({
    url: `/logs/operations/${id}`,
    method: 'delete'
  })
}

/**
 * 批量删除操作日志
 */
export function batchDeleteOperationLogs(logIds) {
  return request({
    url: '/logs/operations',
    method: 'delete',
    data: logIds
  })
}

// ==================== 登录日志 ====================

/**
 * 获取登录日志列表
 */
export function getLoginLogs(params) {
  return request({
    url: '/logs/logins',
    method: 'get',
    params
  })
}

/**
 * 删除登录日志
 */
export function deleteLoginLog(id) {
  return request({
    url: `/logs/logins/${id}`,
    method: 'delete'
  })
}

/**
 * 批量删除登录日志
 */
export function batchDeleteLoginLogs(logIds) {
  return request({
    url: '/logs/logins',
    method: 'delete',
    data: logIds
  })
}

// ==================== 异常日志 ====================

/**
 * 获取异常日志列表
 */
export function getExceptionLogs(params) {
  return request({
    url: '/logs/exceptions',
    method: 'get',
    params
  })
}

/**
 * 获取异常日志详情
 */
export function getExceptionLogDetail(id) {
  return request({
    url: `/logs/exceptions/${id}`,
    method: 'get'
  })
}

/**
 * 标记异常日志为已解决
 */
export function resolveExceptionLog(id, data) {
  return request({
    url: `/logs/exceptions/${id}/resolve`,
    method: 'patch',
    params: data
  })
}

/**
 * 删除异常日志
 */
export function deleteExceptionLog(id) {
  return request({
    url: `/logs/exceptions/${id}`,
    method: 'delete'
  })
}

/**
 * 批量删除异常日志
 */
export function batchDeleteExceptionLogs(logIds) {
  return request({
    url: '/logs/exceptions',
    method: 'delete',
    data: logIds
  })
}

// ==================== 统计信息 ====================

/**
 * 获取日志统计信息
 */
export function getLogStatistics() {
  return request({
    url: '/logs/statistics',
    method: 'get'
  })
}