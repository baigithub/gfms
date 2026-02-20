<template>
  <div class="task-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon" color="#667eea"><Clock /></el-icon>
            <span class="card-title">待办任务</span>
            <el-tag type="info" size="small">{{ pagination.total }} 条记录</el-tag>
          </div>
          <div class="header-right">
            <el-button @click="loadData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        show-header
        style="width: 100%"
        class="modern-table"
      >
        <el-table-column type="index" label="序号" width="80" align="center">
          <template #default="{ $index }">
            <div class="index-badge">{{ $index + 1 }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="customer_name" label="客户名称" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="customer-name">
              <el-icon><User /></el-icon>
              {{ row.customer_name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="business_type" label="业务品种" width="150">
          <template #default="{ row }">
            <el-tag type="primary" effect="plain">{{ row.business_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="loan_account" label="贷款账号" width="150" />
        <el-table-column prop="loan_amount" label="放款金额(元)" width="140" align="right">
          <template #default="{ row }">
            <div class="amount-value">{{ formatAmount(row.loan_amount) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="disbursement_date" label="放款日" width="120" align="center">
          <template #default="{ row }">
            <div class="date-value">{{ formatDate(row.disbursement_date) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="绿色金融支持项目目录" min-width="250">
          <template #default="{ row }">
            <div class="project-category-wrap">
              <el-icon color="#4CAF50"><ElementPlus /></el-icon>
              <span>{{ formatGreenProjectCategory(row) }}</span>
            </div>
          </template>
        </el-table-column>        <el-table-column prop="deadline" label="截止日期" width="120" align="center">
          <template #default="{ row }">
            <el-tag
              :type="getDeadlineType(row.deadline)"
              size="small"
              effect="plain"
            >
              {{ row.deadline ? formatDate(row.deadline) : '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              @click="handleView(row)"
              class="action-button"
            >
              <el-icon><View /></el-icon>
              办理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getPendingTasks } from '@/api/green_finance'
import { useTabsStore } from '@/store/tabs'
import { Clock, Refresh, User, ElementPlus, View } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()
const tabsStore = useTabsStore()
const loading = ref(false)
const tableData = ref([])
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const formatAmount = (value) => {
  if (!value) return '0.00'
  return Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const formatDate = (value) => {
  return value ? dayjs(value).format('YYYY-MM-DD') : '-'
}

const formatGreenProjectCategory = (row) => {
  if (row.formatted_category) {
    return row.formatted_category
  }
  const parts = []
  if (row.project_category_large) {
    parts.push(row.project_category_large)
  }
  if (row.project_category_medium) {
    parts.push(row.project_category_medium)
  }
  if (row.project_category_small) {
    parts.push(row.project_category_small)
  }
  return parts.join('/') || '-'
}

const getDeadlineType = (deadline) => {
  if (!deadline) return 'info'
  const now = dayjs()
  const deadlineDate = dayjs(deadline)
  const daysDiff = deadlineDate.diff(now, 'day')
  
  if (daysDiff < 0) return 'danger'
  if (daysDiff <= 3) return 'warning'
  return 'success'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getPendingTasks({
      page: pagination.page,
      page_size: pagination.page_size
    })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    console.error('Failed to load tasks:', error)
  } finally {
    loading.value = false
  }
}

const handleView = (row) => {
  console.log('DEBUG: handleView called with row:', row)
  console.log('DEBUG: row.customer_name:', row.customer_name)
  console.log('DEBUG: row.task_id:', row.task_id)
  console.log('DEBUG: row.identification_id:', row.identification_id)
  
  const taskTitle = `任务详情 - ${row.customer_name}`
  // 使用task_id（workflow_task ID）而不是identification_id
  const taskPath = `/task-detail/${row.task_id}`
  console.log('DEBUG: taskPath:', taskPath)
  
  tabsStore.addTab({
    path: taskPath,
    title: taskTitle,
    query: { from: 'pending' }
  })
  
  router.push({
    path: taskPath,
    query: { from: 'pending' }
  })
}

onMounted(() => {
  loadData()
})

watch(() => route.query.t, () => {
  loadData()
})
</script>

<style scoped>
.task-page {
  padding: 0;
}

:deep(.el-card) {
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.el-card__body) {
  padding: 20px 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 20px;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
}

.header-right :deep(.el-button) {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
}

.modern-table {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table) {
  border-radius: 12px;
}

/* 隐藏表格空白填充行 */
:deep(.el-table__empty-block) {
  display: none;
}

:deep(.el-table .el-table__body-wrapper) {
  min-height: auto !important;
}

:deep(.el-table thead) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%) !important;
  display: table-header-group !important;
  visibility: visible !important;
}

:deep(.el-table th) {
  background: transparent !important;
  color: #303133 !important;
  font-weight: 600;
  font-size: 14px;
  padding: 16px 12px;
  display: table-cell !important;
  visibility: visible !important;
}

:deep(.el-table th .cell) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

:deep(.el-table tr) {
  transition: all 0.3s;
}

:deep(.el-table tr:hover > td) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%) !important;
}

:deep(.el-table__fixed-right) {
  position: sticky !important;
  right: 0 !important;
  z-index: 100 !important;
  background: white !important;
}

:deep(.el-table__fixed-right .el-table__fixed-body-wrapper) {
  z-index: 100 !important;
  background: white !important;
}

:deep(.el-table__fixed-right .el-table__fixed-header-wrapper) {
  z-index: 100 !important;
  background: white !important;
}

:deep(.el-table__fixed-right .el-table__fixed-right-patch) {
  width: 120px !important;
  background: white !important;
  z-index: 101 !important;
}

:deep(.el-table__fixed-right td) {
  background: white !important;
}

:deep(.el-table__fixed-right tr:hover > td) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%) !important;
}

:deep(.el-table td) {
  padding: 16px 12px;
  font-size: 14px;
  color: #000000;
}

.index-badge {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  margin: 0 auto;
}

.customer-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #000000;
}

.amount-value {
  font-weight: 600;
  color: #000000;
  font-family: 'Monaco', 'Menlo', monospace;
}

.date-value {
  color: #000000;
  font-size: 13px;
}

.project-category {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #000000;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  font-size: 14px;
}

:deep(.el-button--primary.is-link) {
  color: #667eea;
  font-weight: 500;
}

:deep(.el-button--primary.is-link:hover) {
  color: #764ba2;
}

:deep(.el-tag) {
  border-radius: 6px;
  padding: 4px 10px;
  font-weight: 500;
  font-size: 12px;
}

:deep(.el-tag--primary) {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
  color: #667eea;
}

:deep(.el-tag--success) {
  background: rgba(76, 175, 80, 0.1);
  border-color: rgba(76, 175, 80, 0.3);
  color: #4CAF50;
}

:deep(.el-tag--warning) {
  background: rgba(255, 152, 0, 0.1);
  border-color: rgba(255, 152, 0, 0.3);
  color: #FF9800;
}

:deep(.el-tag--danger) {
  background: rgba(244, 67, 54, 0.1);
  border-color: rgba(244, 67, 54, 0.3);
  color: #f44336;
}

:deep(.el-tag--info) {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
  color: #7f8c8d;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.el-pagination) {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-pagination .el-pager li) {
  border-radius: 8px;
  margin: 0 4px;
  font-weight: 500;
}

:deep(.el-pagination .el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

:deep(.el-pagination button) {
  border-radius: 8px;
}

:deep(.el-pagination .el-pagination__sizes .el-select .el-input .el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-loading-mask) {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
}

:deep(.el-loading-spinner .path) {
  stroke: #667eea;
}
</style>