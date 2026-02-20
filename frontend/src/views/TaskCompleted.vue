<template>
  <div class="task-page">
    <el-card shadow="hover" class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <div class="header-icon">
              <el-icon size="24"><CircleCheckFilled /></el-icon>
            </div>
            <div class="header-content">
              <span class="card-title">已办任务</span>
              <span class="card-subtitle">查看所有已完成的任务</span>
            </div>
          </div>
        </div>
      </template>

      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        show-header
        class="modern-table"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266', fontWeight: '600' }"
        :cell-style="{ padding: '16px 0' }"
      >
        <el-table-column type="index" label="序号" width="80" align="center">
          <template #default="{ $index }">
            <div class="index-badge">{{ $index + 1 }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="customer_name" label="客户名称" min-width="150">
          <template #default="{ row }">
            <div class="customer-name">{{ row.customer_name }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="business_type" label="业务品种" width="150">
          <template #default="{ row }">
            <el-tag type="success" effect="plain" size="small">{{ row.business_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="loan_account" label="贷款账号" width="150">
          <template #default="{ row }">
            <div class="loan-account">{{ row.loan_account }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="loan_amount" label="放款金额(元)" width="140">
          <template #default="{ row }">
            <div class="amount-value">{{ formatAmount(row.loan_amount) }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="disbursement_date" label="放款日" width="120">
          <template #default="{ row }">
            <div class="date-value">{{ formatDate(row.disbursement_date) }}</div>
          </template>
        </el-table-column>
<el-table-column label="绿色金融支持项目目录" min-width="200">
  <template #default="{ row }">
    <div class="project-category-wrap">
      <el-icon color="#4CAF50"><ElementPlus /></el-icon>
      <span>{{ formatGreenProjectCategory(row) }}</span>
    </div>
  </template>
</el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small" effect="dark">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
                        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" link size="small" @click="handleView(row)">
                <el-icon class="btn-icon"><View /></el-icon>
                查看
              </el-button>
              <el-button 
                type="warning" 
                link 
                size="small" 
                @click="handleWithdraw(row)"
                :disabled="!canWithdraw(row)"
              >
                <el-icon class="btn-icon"><RefreshLeft /></el-icon>
                撤回
              </el-button>
            </div>
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
          class="modern-pagination"
        />
      </div>
    </el-card>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="任务详情"
      width="900px"
      class="modern-dialog"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="activeTab" class="modern-tabs">
        <el-tab-pane label="业务信息" name="business">
          <el-descriptions :column="2" border class="modern-descriptions">
            <el-descriptions-item label="贷款编号">{{ currentTask.loan_code }}</el-descriptions-item>
            <el-descriptions-item label="客户名称">{{ currentTask.customer_name }}</el-descriptions-item>
            <el-descriptions-item label="业务品种">{{ currentTask.business_type }}</el-descriptions-item>
            <el-descriptions-item label="贷款账号">{{ currentTask.loan_account }}</el-descriptions-item>
            <el-descriptions-item label="放款金额">{{ formatAmount(currentTask.loan_amount) }}</el-descriptions-item>
            <el-descriptions-item label="放款日期">{{ formatDate(currentTask.disbursement_date) }}</el-descriptions-item>
            <el-descriptions-item label="绿色金融支持项目目录" :span="2">{{ formatGreenProjectCategory(currentTask) }}</el-descriptions-item>
            <el-descriptions-item label="ESG风险等级">{{ currentTask.esg_risk_level }}</el-descriptions-item>
            <el-descriptions-item label="ESG表现等级">{{ currentTask.esg_performance_level }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="审批记录" name="approval">
          <div class="timeline-container">
            <el-timeline>
              <el-timeline-item
                v-for="item in workflowHistory"
                :key="item.id"
                :timestamp="formatDateTime(item.completed_at || item.started_at)"
                placement="top"
                :type="getTimelineType(item.status)"
              >
                <el-card shadow="hover" class="timeline-card">
                  <div class="timeline-content">
                    <div class="timeline-header">
                      <span class="timeline-title">{{ item.task_name }}</span>
                      <el-tag :type="getStatusType(item.status)" size="small" effect="dark">
                        {{ item.status }}
                      </el-tag>
                    </div>
                    <div class="timeline-detail">
                      <div class="detail-item">
                        <el-icon class="detail-icon"><User /></el-icon>
                        <span>审批人: {{ item.assignee_name }}</span>
                      </div>
                      <div class="detail-item">
                        <el-icon class="detail-icon"><Position /></el-icon>
                        <span>岗位: {{ item.position_name }}</span>
                      </div>
                    </div>
                    <div v-if="item.approval_result" class="timeline-result">
                      <span class="result-label">审批结果: </span>
                      <span :class="item.approval_result === '同意' ? 'result-agree' : 'result-disagree'">
                        {{ item.approval_result }}
                      </span>
                    </div>
                    <div v-if="item.comment" class="timeline-comment">
                      <span class="comment-label">意见: </span>
                      <span>{{ item.comment }}</span>
                    </div>
                    <div v-if="item.reason" class="timeline-reason">
                      <span class="reason-label">原因: </span>
                      <span>{{ item.reason }}</span>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-if="!workflowHistory || workflowHistory.length === 0" description="暂无审批记录" :image-size="80" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="流程跟踪" name="flow">
          <FlowChart :workflow-history="workflowHistory" />
        </el-tab-pane>

        <el-tab-pane label="附件列表" name="attachments">
          <div class="attachments-container">
            <el-table :data="currentTask.attachments || []" stripe size="large" v-if="currentTask.attachments && currentTask.attachments.length > 0" class="modern-table">
              <el-table-column prop="task_name" label="所属节点" width="150" />
              <el-table-column prop="uploader_name" label="上传人" width="120" />
              <el-table-column prop="original_filename" label="附件名称" min-width="200">
                <template #default="{ row }">
                  <el-button type="primary" link size="default" @click="handleDownloadAttachment(row)" class="file-link">
                    <el-icon class="file-icon"><Document /></el-icon>
                    {{ row.original_filename }}
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column prop="file_size" label="文件大小" width="100">
                <template #default="{ row }">
                  {{ formatFileSize(row.file_size) }}
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="上传时间" width="160" />
            </el-table>
            <el-empty v-else description="暂无附件" :image-size="80" />
          </div>
        </el-tab-pane>

        <el-tab-pane label="绿色分类变动轨迹" name="category-trace">
          <div class="category-trace-container">
            <div class="category-trace">
              <el-timeline>
                <el-timeline-item
                  v-for="(item, index) in workflowHistory"
                  :key="item.id"
                  :timestamp="formatDateTime(item.completed_at || item.started_at)"
                  placement="top"
                  :type="getTimelineType(item.status)"
                >
                  <el-card shadow="hover" class="trace-card">
                    <div class="trace-header">
                      <span class="trace-title">{{ item.task_name }}</span>
                      <el-tag size="small" effect="dark">{{ item.status }}</el-tag>
                    </div>
                    <div class="trace-detail">
                      <div class="detail-item">
                        <el-icon class="detail-icon"><User /></el-icon>
                        <span>办理人: {{ item.assignee_name }}</span>
                      </div>
                      <div v-if="item.assignee_username" class="detail-item">
                        <el-icon class="detail-icon"><UserFilled /></el-icon>
                        <span>账号: {{ item.assignee_username }}</span>
                      </div>
                    </div>
                    <div v-if="item.formatted_category" class="trace-category">
                      <div class="category-label">
                        <el-icon><FolderOpened /></el-icon>
                        <span>绿色金融支持项目目录:</span>
                      </div>
                      <div class="category-value">{{ item.formatted_category }}</div>
                    </div>
                    <div v-else class="trace-category-empty">
                      <el-icon><Folder /></el-icon>
                      <span>暂无分类信息</span>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
              <el-empty v-if="!workflowHistory || workflowHistory.length === 0" description="暂无分类变动轨迹" :image-size="80" />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false" size="large">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheckFilled, View, User, Position, Document, UserFilled, FolderOpened, Folder, Clock, RefreshLeft } from '@element-plus/icons-vue'
import FlowChart from '@/components/FlowChart.vue'
import { useRouter, useRoute } from 'vue-router'
import { getCompletedTasks, getTaskDetail, getWorkflowHistory, withdrawTask } from '@/api/green_finance'
import dayjs from 'dayjs'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const dialogVisible = ref(false)
const activeTab = ref('business')
const currentTask = ref({})
const workflowHistory = ref([])
const nodeHistoryDialogVisible = ref(false)
const currentNodeHistory = ref([])
const components = {
  FlowChart
}

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

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
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

const getTimelineType = (status) => {
  if (status === '已完成') return 'success'
  if (status === '待处理') return 'primary'
  if (status === '已撤回') return 'info'
  return 'warning'
}

const getStatusType = (status) => {
  const typeMap = {
    '待办': 'warning',
    '已办': 'primary',
    '办结': 'success',
    '驳回': 'danger',
    '撤回': 'info'
  }
  return typeMap[status] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCompletedTasks({
      page: pagination.page,
      page_size: pagination.page_size
    })
    tableData.value = res.items
    pagination.total = res.total

    // 获取所有任务的工作流历史记录
    allWorkflowHistory.value.clear()
    for (const task of res.items) {
      try {
        const identificationId = task.identification_id || task.id
        const history = await getWorkflowHistory(identificationId)
        allWorkflowHistory.value.set(identificationId, history)
      } catch (error) {
        console.error(`获取任务 ${task.identification_id} 的工作流历史失败:`, error)
      }
    }
  } catch (error) {
    console.error('Failed to load tasks:', error)
  } finally {
    loading.value = false
  }
}


// 存储所有任务的工作流历史记录
const allWorkflowHistory = ref(new Map())

// 判断是否可以撤回
const canWithdraw = (row) => {
  // 只有"办理中"状态的任务可以撤回（已办结的任务已经完成整个流程，不能撤回）
  if (row.status !== '办理中') {
      return false
  }

  // 获取该任务的工作流历史记录
  const identificationId = row.identification_id || row.id
  const history = allWorkflowHistory.value.get(identificationId)

  if (!history || history.length === 0) {
      return false
  }

  // 获取当前已完成任务的节点
  const completedTasks = history.filter(item => item.status === '已完成')
  if (completedTasks.length === 0) {
      return false
  }

  // 获取最后一个已完成任务的节点
  const lastCompletedTask = completedTasks[completedTasks.length - 1]
  const currentTaskKey = lastCompletedTask.task_key

  // 定义节点顺序
  const nodeOrder = ['manager_identification', 'branch_review', 'first_approval', 'final_review']
  const currentIndex = nodeOrder.indexOf(currentTaskKey)

  // 如果是最后一个节点，不能撤回
  if (currentIndex === -1 || currentIndex >= nodeOrder.length - 1) {
      return false
  }

  // 获取下一个节点的task_key
  const nextTaskKey = nodeOrder[currentIndex + 1]

  // 检查下一个节点是否有"待处理"状态的记录
  const nextPendingTasks = history.filter(item => item.task_key === nextTaskKey && item.status === '待处理')

  // 只有当下一个节点有"待处理"状态的记录时，才能撤回
  return nextPendingTasks.length > 0
}

// 处理撤回
const handleWithdraw = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确定要撤回此任务吗？撤回后任务将出现在您的待办任务列表中。',
      '撤回确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    loading.value = true
    await withdrawTask(row.task_id || row.id)
    ElMessage.success('任务已撤回到待办任务列表')
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('撤回任务失败:', error)
      ElMessage.error(error.response?.data?.detail || '撤回任务失败')
    }
  } finally {
    loading.value = false
  }
}

const handleView = async (row) => {
  try {
    console.log('handleView called with row:', row)
    console.log('row.task_id:', row.task_id)
    console.log('row.identification_id:', row.identification_id)
    const [detail, history] = await Promise.all([
      getTaskDetail(row.task_id),
      getWorkflowHistory(row.identification_id)
    ])
    console.log('detail:', detail)
    console.log('detail.attachments:', detail.attachments)
    console.log('detail.attachments type:', typeof detail.attachments)
    console.log('detail.attachments length:', detail.attachments ? detail.attachments.length : 0)
    console.log('history:', history)
    currentTask.value = detail
    workflowHistory.value = history
    console.log('currentTask.value after assignment:', currentTask.value)
    console.log('currentTask.value.attachments after assignment:', currentTask.value.attachments)
    dialogVisible.value = true
    activeTab.value = 'business'
  } catch (error) {
    console.error('获取任务详情失败:', error)
    ElMessage.error('获取任务详情失败')
  }
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
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  min-height: 100vh;
}

.main-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: none;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.card-subtitle {
  font-size: 13px;
  color: #7f8c8d;
  font-weight: 400;
}

.modern-table {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
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
  font-weight: 600;
  color: #2c3e50;
}

.loan-account {
  font-family: 'Courier New', monospace;
  color: #34495e;
  font-size: 13px;
  letter-spacing: 0.5px;
}

.amount-value {
  font-weight: 700;
  color: #27ae60;
  font-size: 15px;
}

.date-value {
  color: #7f8c8d;
  font-size: 14px;
}

.category-value {
  color: #2c3e50;
  font-size: 13px;
  line-height: 1.5;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}


.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.action-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}
.action-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.btn-icon {
  font-size: 16px;
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
  background: rgba(102, 126, 234, 0.1) !important;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  padding: 16px;
  background: #fafbfc;
  border-radius: 8px;
}

.modern-pagination {
  font-weight: 500;
}

.modern-dialog {
  border-radius: 16px;
  overflow: hidden;
}

.modern-tabs {
  padding: 24px;
}

.modern-descriptions {
  border-radius: 8px;
  overflow: hidden;
}

.timeline-container,
.attachments-container,
.category-trace-container {
  padding: 24px;
  background: #fafbfc;
  border-radius: 8px;
  min-height: 400px;
}

.timeline-card,
.trace-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.timeline-card:hover,
.trace-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.timeline-content {
  padding: 8px 0;
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ecf0f1;
}

.timeline-title {
  font-weight: 700;
  font-size: 16px;
  color: #2c3e50;
}

.timeline-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #7f8c8d;
}

.detail-icon {
  font-size: 16px;
  color: #667eea;
}

.timeline-result,
.timeline-comment,
.timeline-reason {
  font-size: 13px;
  color: #2c3e50;
  margin-top: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.result-label,
.comment-label,
.reason-label {
  font-weight: 600;
  color: #34495e;
  margin-right: 4px;
}

.result-agree {
  color: #27ae60;
  font-weight: 700;
}

.result-disagree {
  color: #e74c3c;
  font-weight: 700;
}

.flow-chart-container {
  padding: 40px 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  border-radius: 12px;
}

:deep(.modern-table) {
  border-radius: 12px;
  overflow: hidden;
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

.flow-chart {
  padding: 32px 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  position: relative;
}

.flow-rows {
  display: flex;
  flex-direction: column;
  gap: 80px;
  position: relative;
}

.flow-row {
  display: flex;
  justify-content: center;
  gap: 80px;
  position: relative;
}

.flow-row::after {
  content: '';
  position: absolute;
  top: 28px;
  left: 50px;
  right: 50px;
  height: 4px;
  background: linear-gradient(90deg, transparent 0%, #e0e6ed 10%, #e0e6ed 90%, transparent 100%);
  z-index: 0;
  opacity: 0.5;
}

.flow-row.row-all-finished::after {
  background: linear-gradient(90deg, transparent 0%, #67C23A 10%, #67C23A 90%, transparent 100%);
}

.flow-row.row-reverse {
  flex-direction: row-reverse;
}

/* 偶数行右侧节点的竖直连接线 */
.flow-row.row-reverse .flow-node.node-right-edge::before {
  content: '';
  position: absolute;
  right: 70px;
  top: 56px;
  width: 4px;
  height: 40px;
  background: linear-gradient(180deg, #67C23A 0%, #67C23A 60%, transparent 100%);
  z-index: 0;
}

.flow-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  width: 140px;
  position: relative;
  z-index: 1;
  cursor: default;
}

.flow-node.node-clickable {
  cursor: pointer;
}

.flow-node.node-clickable:hover {
  transform: scale(1.05);
}

.flow-node-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  background: linear-gradient(135deg, #e0e6ed 0%, #cfd8dc 100%);
  color: #909399;
  margin-bottom: 12px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 3px solid #e0e6ed;
  position: relative;
}

.operation-count {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: white;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.4);
  border: 2px solid white;
}

.node-finished .flow-node-icon {
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.4);
  border: 3px solid #67C23A;
  animation: pulse-green 2s ease-in-out infinite;
}

@keyframes pulse-green {
  0%, 100% {
    box-shadow: 0 4px 16px rgba(103, 194, 58, 0.4);
  }
  50% {
    box-shadow: 0 4px 24px rgba(103, 194, 58, 0.6);
  }
}

.flow-node-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
  line-height: 1.4;
}

.flow-node-desc {
  font-size: 12px;
  color: #7f8c8d;
  line-height: 1.4;
}

.file-link {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.file-link:hover {
  background: rgba(102, 126, 234, 0.1);
}

.file-icon {
  font-size: 16px;
}

.trace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ecf0f1;
}

.trace-title {
  font-weight: 700;
  font-size: 15px;
  color: #2c3e50;
}

.trace-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.trace-category {
  margin-top: 16px;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.category-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #667eea;
  font-weight: 600;
  margin-bottom: 8px;
}

.category-label .el-icon {
  font-size: 16px;
}

.category-value {
  font-size: 14px;
  color: #2c3e50;
  line-height: 1.6;
  padding-left: 22px;
}

.trace-category-empty {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 13px;
  color: #95a5a6;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  background: #fafbfc;
  border-top: 1px solid #ecf0f1;
}

/* 滚动条美化 */
:deep(.el-table__body-wrapper::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-track) {
  background: #f1f1f1;
  border-radius: 4px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb) {
  background: #c1c1c1;
  border-radius: 4px;
}

:deep(.el-table__body-wrapper::-webkit-scrollbar-thumb:hover) {
  background: #a8a8a6;
}
</style>