<template>
  <div class="task-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon" color="#667eea"><DocumentChecked /></el-icon>
            <span class="card-title">办结任务</span>
            <el-tag type="success" size="small">{{ pagination.total }} 条记录</el-tag>
          </div>
          <div class="header-right">
            <el-button @click="loadData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 查询表单 -->
      <div class="search-form-container">
        <el-form :model="queryForm" inline class="query-form">
          <el-form-item label="客户名称">
            <el-input 
              v-model="queryForm.customer_name" 
              placeholder="请输入" 
              clearable 
              class="modern-input"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="业务品种">
            <el-select 
              v-model="queryForm.business_type" 
              placeholder="请选择" 
              clearable 
              class="modern-input"
            >
              <el-option label="一般性固定资产贷款" value="一般性固定资产贷款" />
              <el-option label="法人账户透支" value="法人账户透支" />
            </el-select>
          </el-form-item>
          <el-form-item label="贷款账号">
            <el-input 
              v-model="queryForm.loan_account" 
              placeholder="请输入" 
              clearable 
              class="modern-input"
            >
              <template #prefix>
                <el-icon><Document /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="发起人">
            <el-input 
              v-model="queryForm.initiator" 
              placeholder="请输入" 
              clearable 
              class="modern-input"
            >
              <template #prefix>
                <el-icon><UserFilled /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="项目目录">
            <el-input 
              v-model="queryForm.project_category" 
              placeholder="请输入" 
              clearable 
              class="modern-input"
            >
              <template #prefix>
                <el-icon><ElementPlus /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="放款日期">
            <el-date-picker
              v-model="disbursementDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              class="modern-input"
            />
          </el-form-item>
          <el-form-item label="办结时间">
            <el-date-picker
              v-model="completedDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              class="modern-input"
            />
          </el-form-item>
          <el-form-item label="截止日期">
            <el-date-picker
              v-model="deadlineDateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              class="modern-input"
            />
          </el-form-item>
          <el-form-item class="search-buttons">
            <el-button type="primary" @click="handleQuery" :loading="loading">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
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
            <div class="date-value">{{ row.deadline ? formatDate(row.deadline) : '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="success" effect="plain">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="initiator_name" label="发起人" width="120">
          <template #default="{ row }">
            <div class="assignee-name">
              <el-icon><UserFilled /></el-icon>
              {{ row.initiator_name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="completed_at" label="办结时间" width="160" align="center">
          <template #default="{ row }">
            <div class="date-value">{{ formatDateTime(row.completed_at) }}</div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)" class="action-button">
              <el-icon><View /></el-icon>
              查看
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
    
    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="任务详情"
      width="900px"
      class="detail-dialog"
    >
      <div class="detail-content">
        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="业务信息" name="business">
            <el-descriptions :column="2" border class="detail-descriptions">
              <el-descriptions-item label="贷款编号">{{ currentTask.loan_code }}</el-descriptions-item>
              <el-descriptions-item label="客户名称">{{ currentTask.customer_name }}</el-descriptions-item>
              <el-descriptions-item label="业务品种">{{ currentTask.business_type }}</el-descriptions-item>
              <el-descriptions-item label="贷款账号">{{ currentTask.loan_account }}</el-descriptions-item>
              <el-descriptions-item label="放款金额">{{ formatAmount(currentTask.loan_amount) }}</el-descriptions-item>
              <el-descriptions-item label="放款日期">{{ formatDate(currentTask.disbursement_date) }}</el-descriptions-item>
              <el-descriptions-item label="绿色金融支持项目目录" :span="2">
                <div class="category-display">
                  <el-icon color="#4CAF50"><ElementPlus /></el-icon>
                  {{ currentTask.formatted_category || formatCategory(currentTask) }}
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="ESG风险等级">{{ currentTask.esg_risk_level }}</el-descriptions-item>
              <el-descriptions-item label="ESG表现等级">{{ currentTask.esg_performance_level }}</el-descriptions-item>
              <el-descriptions-item label="办结时间" :span="2">{{ formatDateTime(currentTask.completed_at) }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          
          <el-tab-pane label="审批记录" name="approval">
            <el-timeline class="timeline-container">
              <el-timeline-item
                v-for="item in workflowHistory"
                :key="item.id"
                :timestamp="formatDateTime(item.completed_at || item.started_at)"
                placement="top"
              >
                <el-card shadow="never" class="timeline-card">
                  <div class="timeline-content">
                    <div class="timeline-header">
                      <span class="timeline-title">{{ item.task_name }}</span>
                      <el-tag :type="getStatusType(item.status)" size="small" effect="plain">
                        {{ item.status }}
                      </el-tag>
                    </div>
                    <div class="timeline-detail">
                      <span class="timeline-item">
                        <el-icon><UserFilled /></el-icon>
                        审批人: {{ item.assignee_name }}
                      </span>
                      <span class="timeline-item">
                        <el-icon><OfficeBuilding /></el-icon>
                        岗位: {{ item.position_name }}
                      </span>
                    </div>
                    <div v-if="item.approval_result" class="timeline-result">
                      <span>审批结果: </span>
                      <span :class="item.approval_result === '同意' ? 'result-agree' : 'result-disagree'">
                        {{ item.approval_result }}
                      </span>
                    </div>
                    <div v-if="item.comment" class="timeline-comment">
                      <span class="timeline-item">
                        <el-icon><ChatDotRound /></el-icon>
                        意见: {{ item.comment }}
                      </span>
                    </div>
                    <div v-if="item.reason" class="timeline-reason">
                      <span class="timeline-item">
                        <el-icon><Warning /></el-icon>
                        原因: {{ item.reason }}
                      </span>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-tab-pane>
          
          <el-tab-pane label="流程跟踪" name="flow">
            <FlowChart :workflow-history="workflowHistory" :process-definition-id="processDefinitionId" />
          </el-tab-pane>
          
          <el-tab-pane label="附件列表" name="attachments">
            <el-table 
              :data="currentTask.attachments || []" 
              stripe 
              size="small" 
              class="attachment-table"
            >
              <el-table-column prop="task_name" label="所属节点" width="150" />
              <el-table-column prop="uploader_name" label="上传人" width="120">
                <template #default="{ row }">
                  <div class="uploader-name">
                    <el-icon><UserFilled /></el-icon>
                    {{ row.uploader_name }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="original_filename" label="附件名称">
                <template #default="{ row }">
                  <el-button type="primary" link @click="handleDownloadAttachment(row)" class="file-link">
                    <el-icon><Download /></el-icon>
                    {{ row.original_filename }}
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column prop="file_size" label="文件大小" width="100" align="right">
                <template #default="{ row }">
                  {{ formatFileSize(row.file_size) }}
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="上传时间" width="150" align="center">
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <el-tab-pane label="绿色分类变动轨迹" name="category-trace">
            <el-timeline class="timeline-container">
              <el-timeline-item
                v-for="item in workflowHistory"
                :key="item.id"
                :timestamp="formatDateTime(item.completed_at || item.started_at)"
                placement="top"
              >
                <el-card shadow="never" class="timeline-card">
                  <div class="timeline-content">
                    <div class="timeline-header">
                      <span class="timeline-title">{{ item.task_name }}</span>
                      <el-tag :type="getStatusType(item.status)" size="small" effect="plain">
                        {{ item.status }}
                      </el-tag>
                    </div>
                    <div class="trace-category">
                      <div class="category-label">
                        <el-icon color="#4CAF50"><ElementPlus /></el-icon>
                        绿色金融支持项目目录:
                      </div>
                      <div class="category-value">
                        {{ item.formatted_category || '暂无分类信息' }}
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  DocumentChecked, 
  Refresh, 
  User, 
  Document, 
  UserFilled,
  ElementPlus,
  Search,
  RefreshLeft,
  View,
  OfficeBuilding,
  ChatDotRound,
  Warning,
  Download
} from '@element-plus/icons-vue'
import FlowChart from '@/components/FlowChart.vue'
import { getArchivedTasks, getTaskDetail, getWorkflowHistory, getWorkflowInstance } from '@/api/green_finance'
import dayjs from 'dayjs'
import { useAuthStore } from '@/store/auth'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const queryForm = reactive({
  customer_name: '',
  business_type: '',
  loan_account: '',
  initiator: '',
  project_category: ''
})

const disbursementDateRange = ref([])
const completedDateRange = ref([])
const deadlineDateRange = ref([])

const dialogVisible = ref(false)
const activeTab = ref('business')
const currentTask = ref({})
const workflowHistory = ref([])
const components = {
  FlowChart
}
const processDefinitionId = ref(null)

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

const formatDateTime = (value) => {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const getStatusType = (status) => {
  const typeMap = {
    '待处理': 'warning',
    '已完成': 'success',
    '已撤回': 'info'
  }
  return typeMap[status] || 'info'
}

const formatGreenProjectCategory = (row) => {
  if (row.formatted_category) {
    return row.formatted_category
  }
  const parts = []
  if (row.project_category_large) parts.push(row.project_category_large)
  if (row.project_category_medium) parts.push(row.project_category_medium)
  if (row.project_category_small) parts.push(row.project_category_small)
  return parts.join('/') || '-'
}

const formatCategory = (task) => {
  const parts = []
  if (task.project_category_large_code && task.project_category_large) {
    parts.push(`${task.project_category_large_code} ${task.project_category_large}`)
  } else if (task.project_category_large) {
    parts.push(task.project_category_large)
  }
  
  if (task.project_category_medium_code && task.project_category_medium) {
    parts.push(`${task.project_category_medium_code} ${task.project_category_medium}`)
  } else if (task.project_category_medium) {
    parts.push(task.project_category_medium)
  }
  
  if (task.project_category_small_code && task.project_category_small) {
    parts.push(`${task.project_category_small_code} ${task.project_category_small}`)
  } else if (task.project_category_small) {
    parts.push(task.project_category_small)
  }
  
  return parts.join('/') || '-'
}

const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const getFlowActiveStep = () => {
  if (!currentTask.value) return 0
  
  const status = currentTask.value.status
  if (status === '办结' || status === '已完成') {
    return 5
  }
  
  if (workflowHistory.value && workflowHistory.value.length > 0) {
    const allTaskKeys = ['manager_identification', 'branch_review', 'first_approval', 'final_review']
    const allCompleted = allTaskKeys.every(key => 
      workflowHistory.value.some(t => t.task_key === key && t.status === '已完成')
    )
    
    if (allCompleted) return 5
    
    const completedTasks = workflowHistory.value.filter(t => t.status === '已完成')
    if (completedTasks.length === 3) return 3
    if (completedTasks.length === 2) return 2
    if (completedTasks.length === 1) return 1
  }
  
  return 0
}

const handleDownloadAttachment = async (attachment) => {
  try {
    const authStore = useAuthStore()
    const token = authStore.token
    
    if (!token) {
      ElMessage.error('未登录,请先登录')
      return
    }
    
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
    const url = `${baseUrl}${attachment.download_url}`
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`下载失败: ${response.status}`)
    }
    
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = attachment.original_filename
    a.style.display = 'none'
    a.target = '_blank'
    a.rel = 'noopener noreferrer'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(downloadUrl)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

const buildQueryParams = () => {
  const params = {
    page: pagination.page,
    page_size: pagination.page_size
  }
  
  if (queryForm.customer_name) params.customer_name = queryForm.customer_name
  if (queryForm.business_type) params.business_type = queryForm.business_type
  if (queryForm.loan_account) params.loan_account = queryForm.loan_account
  if (queryForm.initiator) params.initiator = queryForm.initiator
  if (queryForm.project_category) params.project_category = queryForm.project_category
  
  if (disbursementDateRange.value && disbursementDateRange.value.length === 2) {
    params.disbursement_date_start = disbursementDateRange.value[0]
    params.disbursement_date_end = disbursementDateRange.value[1]
  }
  
  if (completedDateRange.value && completedDateRange.value.length === 2) {
    params.completed_date_start = completedDateRange.value[0]
    params.completed_date_end = completedDateRange.value[1]
  }
  
  if (deadlineDateRange.value && deadlineDateRange.value.length === 2) {
    params.deadline_start = deadlineDateRange.value[0]
    params.deadline_end = deadlineDateRange.value[1]
  }
  
  return params
}

const loadData = async () => {
  loading.value = true
  try {
    const params = buildQueryParams()
    const res = await getArchivedTasks(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    console.error('Failed to load tasks:', error)
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  Object.assign(queryForm, {
    customer_name: '',
    business_type: '',
    loan_account: '',
    initiator: '',
    project_category: ''
  })
  disbursementDateRange.value = []
  completedDateRange.value = []
  deadlineDateRange.value = []
  pagination.page = 1
  loadData()
}

const handleView = async (row) => {
  try {
    const [detail, history] = await Promise.all([
      getTaskDetail(row.task_id),
      getWorkflowHistory(row.identification_id)
    ])
    currentTask.value = detail
    workflowHistory.value = history
    
    // 获取工作流实例信息（包含process_definition_id）
    try {
      const instance = await getWorkflowInstance(row.identification_id)
      processDefinitionId.value = instance?.process_definition_id || null
    } catch (error) {
      console.warn('获取工作流实例失败:', error)
      processDefinitionId.value = null
    }
    
    dialogVisible.value = true
    activeTab.value = 'business'
  } catch (error) {
    ElMessage.error('获取任务详情失败')
  }
}

onMounted(() => {
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
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.header-right :deep(.el-button) {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
}

.search-form-container {
  margin-bottom: 24px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 16px;
  border: 1px solid rgba(102, 126, 234, 0.15);
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.08);
}

.query-form {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

:deep(.query-form .el-form-item) {
  margin-bottom: 0;
  display: inline-flex;
  align-items: center;
}

:deep(.query-form .el-form-item__label) {
  font-weight: 500;
  color: #2c3e50;
  padding-right: 12px;
  min-width: 80px;
  text-align: right;
  line-height: 42px;
}

.modern-input {
  width: 220px;
}

:deep(.modern-input .el-input__wrapper) {
  border-radius: 10px;
  padding: 8px 14px;
  border: 1.5px solid rgba(102, 126, 234, 0.2);
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  min-height: 42px;
  align-items: center;
}

:deep(.modern-input .el-input__wrapper:hover) {
  border-color: #667eea;
  background: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.12);
}

:deep(.modern-input .el-input__wrapper.is-focus) {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
}

:deep(.modern-input .el-select .el-input__wrapper) {
  cursor: pointer;
  min-height: 42px;
  height: 42px;
  align-items: center;
}

:deep(.modern-input .el-date-editor) {
  width: 220px;
  height: 42px;
}

:deep(.modern-input .el-date-editor .el-input__wrapper) {
  min-height: 42px;
  height: 42px;
  align-items: center;
}

:deep(.modern-input .el-date-editor .el-range-input) {
  height: 24px;
  line-height: 24px;
}

:deep(.modern-input .el-date-editor .el-range-separator) {
  line-height: 24px;
}

:deep(.modern-input .el-date-editor .el-input__icon) {
  line-height: 24px;
}

.search-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-left: auto;
}

.search-buttons :deep(.el-button) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 500;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  height: 42px;
  line-height: 1;
}

.search-buttons :deep(.el-button:hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.search-buttons :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.search-buttons :deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.modern-table {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table) {
  border-radius: 12px;
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
  color: #2c3e50;
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

.customer-name,
.assignee-name,
.uploader-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.amount-value {
  font-weight: 600;
  color: #2E8B57;
  font-family: 'Monaco', 'Menlo', monospace;
}

.date-value {
  color: #7f8c8d;
  font-size: 13px;
}

.project-category {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #2c3e50;
}

.action-button,
.file-link {
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

/* 对话框样式 */
:deep(.detail-dialog) {
  border-radius: 16px;
}

:deep(.detail-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.detail-dialog .el-dialog__body) {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

.detail-content {
  display: flex;
  flex-direction: column;
}

.detail-tabs {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.detail-tabs .el-tabs__header) {
  margin: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  padding: 0 20px;
}

:deep(.detail-tabs .el-tabs__nav-wrap::after) {
  display: none;
}

:deep(.detail-tabs .el-tabs__item) {
  height: 48px;
  line-height: 48px;
  font-weight: 500;
  color: #2c3e50;
}

:deep(.detail-tabs .el-tabs__item.is-active) {
  color: #667eea;
  font-weight: 600;
}

.detail-descriptions {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.detail-descriptions .el-descriptions__label) {
  background: rgba(102, 126, 234, 0.05);
  font-weight: 500;
  color: #2c3e50;
  padding: 16px;
}

:deep(.detail-descriptions .el-descriptions__content) {
  padding: 16px;
  color: #2c3e50;
}

.category-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.timeline-container {
  padding-left: 20px;
}

.timeline-card {
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s;
}

.timeline-card:hover {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.timeline-content {
  padding: 12px 0;
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.timeline-title {
  font-weight: 600;
  font-size: 15px;
  color: #2c3e50;
}

.timeline-detail {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.timeline-result,
.timeline-comment,
.timeline-reason {
  font-size: 13px;
  margin-bottom: 8px;
}

.timeline-result span:first-child {
  color: #7f8c8d;
}

.result-agree {
  color: #4CAF50;
  font-weight: 600;
}

.result-disagree {
  color: #f44336;
  font-weight: 600;
}

.flow-chart {
  padding: 40px 20px;
}

:deep(.flow-chart .el-step.is-finish .el-step__icon) {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  border-color: transparent;
}

:deep(.flow-chart .el-step.is-finish .el-step__icon.is-text) {
  color: white;
}

:deep(.flow-chart .el-step__line-inner.is-success) {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
}

:deep(.flow-chart .el-step.is-finish .el-step__title) {
  color: #4CAF50;
  font-weight: 600;
}

:deep(.flow-chart .el-step.is-finish .el-step__description) {
  color: #4CAF50;
}

.attachment-table {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.attachment-table th) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%) !important;
  color: #303133 !important;
  font-weight: 600;
  padding: 16px 12px;
}

:deep(.attachment-table th .cell) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

:deep(.attachment-table td) {
  padding: 16px 12px;
  color: #2c3e50;
}

.trace-category {
  margin-top: 12px;
  padding: 12px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%);
  border-radius: 8px;
  border-left: 3px solid #667eea;
}

.category-label {
  font-size: 12px;
  color: #667eea;
  font-weight: 600;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.category-value {
  font-size: 13px;
  color: #2c3e50;
  line-height: 1.6;
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