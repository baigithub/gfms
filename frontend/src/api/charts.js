import request from '@/utils/request'

// 获取最近12个月认定绿色贷款余额趋势
export function getLoanBalanceTrend() {
  return request({
    url: '/charts/loan-balance-trend',
    method: 'get'
  })
}

// 获取最近12个月放款金额趋势
export function getDisbursementTrend() {
  return request({
    url: '/charts/disbursement-trend',
    method: 'get'
  })
}

// 获取截止当前时点绿色大类占比
export function getGreenCategoryDistribution() {
  return request({
    url: '/charts/green-category-distribution',
    method: 'get'
  })
}