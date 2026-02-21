<template>
  <div class="task-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon" color="#667eea"><Search /></el-icon>
            <span class="card-title">综合查询</span>
            <el-tag type="info" size="small">{{ pagination.total }} 条记录</el-tag>
          </div>
          <div class="header-right">
            <div class="export-group">
              <span class="export-label">导出数量:</span>
              <el-input-number 
                v-model="exportLimit" 
                :min="1" 
                :max="100000" 
                :step="1000"
                placeholder="导出数量"
                class="export-input"
                size="default"
                controls-position="right"
              />
              <span class="export-suffix">条</span>
            </div>
            <el-checkbox 
              v-model="exportOnlyComplete" 
              class="export-checkbox"
            >
              只导出有完整数据的记录
            </el-checkbox>
            <el-button type="success" @click="handleExport" :loading="exporting" class="export-button">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 查询表单 -->
      <div class="search-form-container">
        <el-collapse-transition>
          <div v-show="searchFormVisible">
            <el-form :inline="true" :model="searchForm" class="search-form">
              <el-row :gutter="28">
                <el-col :xs="24" :sm="12" :md="8" :lg="5" :xl="4">
                  <el-form-item label="客户名称">
                    <el-input 
                      v-model="searchForm.customer_name" 
                      placeholder="请输入客户名称" 
                      clearable 
                      class="search-input"
                    >
                      <template #prefix>
                        <el-icon><User /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8" :lg="5" :xl="4">
                  <el-form-item label="业务品种">
                    <el-select 
                      v-model="searchForm.business_type" 
                      placeholder="请选择业务品种" 
                      clearable 
                      class="search-input"
                    >
                      <el-option label="一般性固定资产贷款" value="一般性固定资产贷款" />
                      <el-option label="法人账户透支" value="法人账户透支" />
                      <el-option label="流动资金贷款" value="流动资金贷款" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8" :lg="5" :xl="4">
                  <el-form-item label="贷款账号">
                    <el-input 
                      v-model="searchForm.loan_account" 
                      placeholder="请输入贷款账号" 
                      clearable 
                      class="search-input"
                    >
                      <template #prefix>
                        <el-icon><Document /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8" :lg="5" :xl="4">
                  <el-form-item label="放款日期">
                    <el-date-picker
                      v-model="searchForm.loan_date_range"
                      type="daterange"
                      range-separator="至"
                      start-placeholder="开始日期"
                      end-placeholder="结束日期"
                      value-format="YYYY-MM-DD"
                      clearable
                      class="search-input"
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="8" :lg="4" :xl="4">
                  <el-form-item label="状态">
                    <el-select 
                      v-model="searchForm.status" 
                      placeholder="请选择状态" 
                      clearable 
                      class="search-input"
                    >
                      <el-option label="待处理" value="待处理" />
                      <el-option label="审核中" value="审核中" />
                      <el-option label="已办结" value="已办结" />
                      <el-option label="已撤回" value="已撤回" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </el-collapse-transition>
        
        <!-- 操作按钮栏 -->
        <div class="search-actions">
          <div class="action-buttons">
            <el-button type="primary" @click="handleSearch" :loading="loading" size="default">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="handleReset" size="default">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
            <el-button 
              text 
              type="primary" 
              @click="toggleSearchForm"
              class="toggle-button"
            >
              <el-icon>
                <component :is="searchFormVisible ? 'ArrowUp' : 'ArrowDown'" />
              </el-icon>
              {{ searchFormVisible ? '收起查询' : '展开查询' }}
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 查询结果表格 -->
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
        <el-table-column prop="loan_date" label="放款日期" width="120" align="center">
          <template #default="{ row }">
            <div class="date-value">{{ row.loan_date }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="plain">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignee_name" label="发起人" width="120">
          <template #default="{ row }">
            <div class="assignee-name">
              <el-icon><UserFilled /></el-icon>
              {{ row.assignee_name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" align="center">
          <template #default="{ row }">
            <div class="date-value">{{ row.created_at }}</div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewDetail(row)" class="action-button">
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
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>
    
    <!-- 任务详情对话框 -->
    <el-dialog 
      v-model="detailVisible" 
      title="任务详情" 
      width="900px" 
      :close-on-click-modal="false"
      class="detail-dialog"
    >
      <div class="detail-content">
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="任务编号">{{ detailData.task_id }}</el-descriptions-item>
          <el-descriptions-item label="任务类型">{{ detailData.task_key }}</el-descriptions-item>
          <el-descriptions-item label="客户名称">{{ detailData.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="业务品种">{{ detailData.business_type }}</el-descriptions-item>
          <el-descriptions-item label="贷款账号">{{ detailData.loan_account }}</el-descriptions-item>
          <el-descriptions-item label="放款金额">{{ formatAmount(detailData.loan_amount) }}</el-descriptions-item>
          <el-descriptions-item label="放款日期">{{ detailData.loan_date }}</el-descriptions-item>
          <el-descriptions-item label="绿色金融支持项目目录">{{ detailData.green_project_category }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(detailData.status)">{{ detailData.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发起人">{{ detailData.assignee_name }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detailData.created_at }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ detailData.completed_at || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">
          <span class="divider-title">
            <el-icon><List /></el-icon>
            审批记录
          </span>
        </el-divider>
        <el-table :data="detailData.workflow_history || []" stripe size="small" class="history-table">
          <el-table-column prop="node_name" label="审批节点" width="150" />
          <el-table-column prop="approver_name" label="审批人" width="120">
            <template #default="{ row }">
              <div class="approver-name">
                <el-icon><UserFilled /></el-icon>
                {{ row.approver_name }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small" effect="plain">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="comment" label="意见" min-width="200" show-overflow-tooltip />
          <el-table-column prop="created_at" label="处理时间" width="160" align="center" />
        </el-table>
        
        <el-divider content-position="left">
          <span class="divider-title">
            <el-icon><Paperclip /></el-icon>
            附件列表
          </span>
        </el-divider>
        <div v-if="detailData.attachments && detailData.attachments.length > 0">
          <el-table :data="detailData.attachments" stripe size="small" class="attachment-table">
            <el-table-column prop="task_name" label="所属节点" width="150" />
            <el-table-column prop="uploader_name" label="上传人" width="120">
              <template #default="{ row }">
                <div class="uploader-name">
                  <el-icon><UserFilled /></el-icon>
                  {{ row.uploader_name }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="original_filename" label="附件名称" min-width="200">
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
            <el-table-column prop="created_at" label="上传时间" width="160" align="center" />
          </el-table>
        </div>
        <el-empty v-else description="暂无附件" :image-size="60" />
        
        <el-divider content-position="left">
          <span class="divider-title">
            <el-icon><Clock /></el-icon>
            绿色分类变动轨迹
          </span>
        </el-divider>
        <el-timeline class="trace-timeline">
          <el-timeline-item
            v-for="(item, index) in detailData.workflow_history || []"
            :key="item.id"
            :timestamp="item.created_at"
            placement="top"
            :type="getTimelineType(item.status)"
          >
            <el-card shadow="never" class="trace-card">
              <div class="trace-header">
                <span class="trace-title">{{ item.node_name }}</span>
                <el-tag size="small" :type="getStatusType(item.status)" effect="plain">{{ item.status }}</el-tag>
              </div>
              <div class="trace-detail">
                <span class="trace-item">
                  <el-icon><UserFilled /></el-icon>
                  办理人: {{ item.approver_name }}
                </span>
              </div>
              <div v-if="item.comment" class="trace-comment">
                <span class="trace-item">
                  <el-icon><ChatDotRound /></el-icon>
                  意见: {{ item.comment }}
                </span>
              </div>
              <div class="trace-category" v-if="item.formatted_category">
                <div class="category-label">
                  <el-icon><ElementPlus /></el-icon>
                  绿色金融支持项目目录:
                </div>
                <div class="category-value">
                  {{ item.formatted_category }}
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-if="!detailData.workflow_history || detailData.workflow_history.length === 0" description="暂无分类变动轨迹" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Search, 
  Download, 
  User, 
  Document, 
  RefreshLeft, 
  View, 
  UserFilled,
  List,
  Paperclip,
  Clock,
  ChatDotRound,
  ElementPlus,
  ArrowUp,
  ArrowDown
} from '@element-plus/icons-vue'
import { searchTasks, exportTasks } from '@/api/green_finance'
import { useAuthStore } from '@/store/auth'
import dayjs from 'dayjs'

const loading = ref(false)
const exporting = ref(false)
const exportLimit = ref(10000)
const exportOnlyComplete = ref(false)
const searchFormVisible = ref(true)

const toggleSearchForm = () => {
  searchFormVisible.value = !searchFormVisible.value
}
const tableData = ref([])
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const searchForm = reactive({
  customer_name: '',
  business_type: '',
  loan_account: '',
  loan_date_range: [],
  status: ''
})

const detailVisible = ref(false)
const detailData = ref({})

const formatAmount = (value) => {
  if (!value) return '0.00'
  return Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
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
  if (status === '已完成' || status === '已办结') return 'success'
  if (status === '待处理') return 'primary'
  if (status === '已撤回') return 'info'
  return 'warning'
}

const getStatusType = (status) => {
  const typeMap = {
    '待处理': 'warning',
    '审核中': 'primary',
    '已办结': 'success',
    '已撤回': 'info',
    '已提交': 'info',
    '已完成': 'success',
    '驳回': 'danger',
    '办结': 'success'
  }
  return typeMap[status] || 'info'
}

const handleSearch = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (searchForm.customer_name) params.customer_name = searchForm.customer_name
    if (searchForm.business_type) params.business_type = searchForm.business_type
    if (searchForm.loan_account) params.loan_account = searchForm.loan_account
    if (searchForm.loan_date_range && searchForm.loan_date_range.length === 2) {
      params.loan_date_start = searchForm.loan_date_range[0]
      params.loan_date_end = searchForm.loan_date_range[1]
    }
    if (searchForm.status) params.status = searchForm.status
    const res = await searchTasks(params)
    tableData.value = res.data || []
    pagination.total = res.total || 0
  } catch (error) {
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  searchForm.customer_name = ''
  searchForm.business_type = ''
  searchForm.loan_account = ''
  searchForm.loan_date_range = []
  searchForm.status = ''
  pagination.page = 1
  loadData()
}

const handleExport = async () => {
  try {
    exporting.value = true
    const params = {}
    if (searchForm.customer_name) params.customer_name = searchForm.customer_name
    if (searchForm.business_type) params.business_type = searchForm.business_type
    if (searchForm.loan_account) params.loan_account = searchForm.loan_account
    if (searchForm.loan_date_range && searchForm.loan_date_range.length === 2) {
      params.loan_date_start = searchForm.loan_date_range[0]
      params.loan_date_end = searchForm.loan_date_range[1]
    }
    if (searchForm.status) params.status = searchForm.status
    
    console.log('导出参数:', params)
    params.limit = exportLimit.value
    params.only_complete = exportOnlyComplete.value
    console.log('导出参数(含limit和only_complete):', params)
    const blob = await exportTasks(params)
    console.log('导出响应:', blob)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `绿色金融任务导出_${dayjs().format('YYYYMMDD_HHmmss')}.csv`
    a.style.display = 'none'
    a.target = '_blank'
    a.rel = 'noopener noreferrer'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    console.error('错误详情:', error.response)
    
    // 尝试读取 blob 中的错误信息
    if (error.response?.data instanceof Blob) {
      const reader = new FileReader()
      reader.onload = () => {
        try {
          const errorData = JSON.parse(reader.result)
          console.error('错误信息:', errorData)
          console.error('错误详情数组:', errorData.detail)
          ElMessage.error(errorData.detail ? JSON.stringify(errorData.detail) : '导出失败')
        } catch (e) {
          console.error('无法解析错误信息:', reader.result)
          ElMessage.error('导出失败')
        }
      }
      reader.readAsText(error.response.data)
    } else {
      ElMessage.error(error.response?.data?.detail || '导出失败')
    }
  } finally {
    exporting.value = false
  }
}

const handleViewDetail = (row) => {
  detailData.value = { ...row }
  detailVisible.value = true
}

const loadData = async () => {
  handleSearch()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.task-page {
  padding: 32px;
  background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
  min-height: 100vh;
  position: relative;
}

.task-page::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 80% 50%, rgba(118, 75, 162, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

:deep(.el-card) {
  border-radius: 24px;
  border: 2px solid rgba(102, 126, 234, 0.12);
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px);
  position: relative;
  z-index: 1;
  overflow: hidden;
}

:deep(.el-card__header) {
  padding: 28px 32px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.12);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.04) 0%, rgba(118, 75, 162, 0.04) 100%);
}

:deep(.el-card__body) {
  padding: 32px;
  overflow-x: auto;
}

:deep(.el-table .el-table__fixed-right-patch) {
  width: 120px !important;
  background: transparent !important;
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

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.header-icon {
  font-size: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.3));
}

.card-title {
  font-size: 22px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.export-group {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 12px;
  border: 1.5px solid rgba(102, 126, 234, 0.15);
}

.export-label {
  font-size: 13px;
  color: #667eea;
  font-weight: 500;
}

.export-input {
  width: 120px !important;
}

:deep(.export-input .el-input__wrapper) {
  border-radius: 8px;
  border: 1.5px solid rgba(102, 126, 234, 0.2);
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

:deep(.export-input .el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.12);
}

:deep(.export-input .el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.export-suffix {
  font-size: 13px;
  color: #999;
  font-weight: 500;
}

.export-checkbox {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 500;
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.03);
  border-radius: 8px;
  border: 1.5px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.export-checkbox:hover {
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.2);
}

.export-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  border: none;
  background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
  box-shadow: 0 4px 16px rgba(0, 184, 148, 0.3);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.export-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.export-button:hover::before {
  left: 100%;
}

.export-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 184, 148, 0.4);
}

.export-button:active {
  transform: translateY(0);
}

.header-right :deep(.el-button:not(.export-button)) {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 500;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: none;
}

.header-right :deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.header-right :deep(.el-button--success) {
  background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
}

.header-right :deep(.el-button--success:hover) {
  background: linear-gradient(135deg, #00cec9 0%, #00b894 100%);
}

.header-right :deep(.el-input-number) {
  border-radius: 10px;
  border: 1.5px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.header-right :deep(.el-input-number:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.12);
}

.search-form-container {
  margin-bottom: 32px;
  padding: 32px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.95) 100%);
  border-radius: 24px;
  border: 2px solid rgba(102, 126, 234, 0.12);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.8);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.search-form-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.search-form {
  margin-bottom: 24px;
}

:deep(.search-form .el-row) {
  margin-bottom: 24px;
}

:deep(.search-form .el-row:last-child) {
  margin-bottom: 0;
}

:deep(.search-form .el-form-item) {
  margin-bottom: 0;
  width: 100%;
}

:deep(.search-form .el-form-item__label) {
  font-weight: 600;
  color: #2c3e50;
  padding-right: 16px;
  min-width: 90px;
  line-height: 40px;
  font-size: 14px;
  letter-spacing: 0.3px;
}

.search-input {
  width: 100%;
}

:deep(.search-input .el-input__wrapper),
:deep(.search-input .el-select .el-input__wrapper) {
  border-radius: 12px;
  padding: 10px 16px;
  border: 2px solid rgba(102, 126, 234, 0.18);
  background: rgba(255, 255, 255, 0.98);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  min-height: 44px;
}

:deep(.search-input .el-input__wrapper:hover),
:deep(.search-input .el-select .el-input__wrapper:hover) {
  border-color: #667eea;
  background: white;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

:deep(.search-input .el-input__wrapper.is-focus),
:deep(.search-input .el-select .el-input__wrapper.is-focus) {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.12), 0 6px 20px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

:deep(.search-input .el-input__inner) {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 500;
  height: 44px;
  line-height: 44px;
}

:deep(.search-input .el-input__prefix),
:deep(.search-input .el-input__suffix) {
  color: #667eea;
}

:deep(.search-input .el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.12), 0 6px 20px rgba(102, 126, 234, 0.15);
}

:deep(.search-input .el-date-editor) {
  width: 100%;
}

:deep(.search-input .el-date-editor .el-input__wrapper) {
  border-radius: 12px;
  border: 2px solid rgba(102, 126, 234, 0.18);
  background: rgba(255, 255, 255, 0.98);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  min-height: 44px;
  padding: 10px 16px;
}

:deep(.search-input .el-date-editor .el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

:deep(.search-input .el-date-editor .el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.12), 0 6px 20px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

:deep(.search-input .el-date-editor .el-range-input) {
  color: #2c3e50;
  font-weight: 500;
  font-size: 14px;
  height: 24px;
  line-height: 24px;
}

:deep(.search-input .el-date-editor .el-range-separator) {
  color: #667eea;
  font-weight: 600;
  font-size: 14px;
}

:deep(.search-input .el-date-editor .el-input__icon) {
  color: #667eea;
  font-size: 16px;
}

:deep(.search-input .el-input__inner::placeholder) {
  color: #999;
  font-weight: 400;
  font-size: 14px;
}

:deep(.search-input .el-input__inner::placeholder) {
  color: #999;
  font-weight: 400;
}

.search-actions {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
}

.action-buttons {
  display: flex;
  gap: 12px;
  align-items: center;
}

.toggle-button {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  padding: 10px 20px;
  border-radius: 10px;
  border: 2px solid rgba(102, 126, 234, 0.15);
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  transition: all 0.3s ease;
  cursor: pointer;
}

.toggle-button:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

:deep(.toggle-button .el-icon) {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.toggle-button:hover :deep(.toggle-button .el-icon) {
  transform: scale(1.1);
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
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.12);
  border: 2px solid rgba(102, 126, 234, 0.12);
}

:deep(.el-table) {
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.98);
}

:deep(.modern-table thead) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%) !important;
  display: table-header-group !important;
  visibility: visible !important;
}

:deep(.modern-table th) {
  background: transparent !important;
  color: #303133 !important;
  font-weight: 600;
  font-size: 14px;
  padding: 16px 12px;
  display: table-cell !important;
  visibility: visible !important;
}

:deep(.modern-table th .cell) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

:deep(.el-table tr:hover > td) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%) !important;
  transform: scale(1.005);
  transition: all 0.3s ease;
}

:deep(.el-table td) {
  padding: 20px 18px;
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
  gap: 24px;
}

.detail-descriptions {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.detail-descriptions .el-descriptions__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
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

:deep(.el-divider) {
  margin: 16px 0;
}

:deep(.el-divider__text) {
  background: transparent;
  padding: 0;
}

.divider-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.history-table,
.attachment-table {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.history-table th),
:deep(.attachment-table th) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%) !important;
  color: #303133 !important;
  font-weight: 600;
  padding: 16px 12px;
}

:deep(.history-table th .cell),
:deep(.attachment-table th .cell) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

:deep(.history-table td),
:deep(.attachment-table td) {
  padding: 16px 12px;
  color: #2c3e50;
}

.trace-timeline {
  padding-left: 20px;
}

.trace-card {
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s;
}

.trace-card:hover {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
  transform: translateY(-2px);
}

.trace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.trace-title {
  font-weight: 600;
  font-size: 15px;
  color: #2c3e50;
}

.trace-detail,
.trace-comment {
  display: flex;
  gap: 6px;
  font-size: 13px;
  color: #7f8c8d;
  margin-bottom: 8px;
}

.trace-item {
  display: flex;
  align-items: center;
  gap: 6px;
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

.search-form-transition {
  transition: all 0.3s ease;
}

.pagination-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 36px 28px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.9) 100%);
  border-radius: 16px;
  margin-top: 32px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.08);
}

:deep(.el-pagination) {
  display: flex;
  align-items: center;
  gap: 10px;
}

:deep(.el-pagination button) {
  border-radius: 10px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  background: rgba(255, 255, 255, 0.98);
  color: #2c3e50;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 40px;
  height: 40px;
}

:deep(.el-pagination button:hover) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

:deep(.el-pagination button:disabled) {
  background: #f5f5f5;
  color: #c0c4cc;
  border-color: #e4e7ed;
  transform: none;
  box-shadow: none;
}

:deep(.el-pager li) {
  border-radius: 10px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  background: rgba(255, 255, 255, 0.98);
  color: #2c3e50;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-width: 40px;
  height: 40px;
}

:deep(.el-pager li:hover) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

:deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.index-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 700;
  font-size: 15px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

:deep(.el-table tr:hover .index-badge) {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.customer-name,
.assignee-name {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2c3e50;
  font-weight: 600;
  font-size: 14px;
}

:deep(.el-tag) {
  border-radius: 8px;
  padding: 6px 14px;
  font-weight: 600;
  font-size: 13px;
  border: 2px solid;
  transition: all 0.3s ease;
}

:deep(.el-tag--primary) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: rgba(102, 126, 234, 0.3);
  color: #667eea;
}

:deep(.el-tag--success) {
  background: linear-gradient(135deg, rgba(0, 184, 148, 0.1) 0%, rgba(0, 206, 201, 0.1) 100%);
  border-color: rgba(0, 184, 148, 0.3);
  color: #00b894;
}

:deep(.el-tag--warning) {
  background: linear-gradient(135deg, rgba(255, 165, 0, 0.1) 0%, rgba(255, 193, 7, 0.1) 100%);
  border-color: rgba(255, 165, 0, 0.3);
  color: #ffa500;
}

:deep(.el-tag--danger) {
  background: linear-gradient(135deg, rgba(255, 99, 71, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
  border-color: rgba(255, 99, 71, 0.3);
  color: #ff6347;
}

:deep(.el-tag--info) {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1) 0%, rgba(100, 181, 246, 0.1) 100%);
  border-color: rgba(52, 152, 219, 0.3);
  color: #3498db;
}

.amount-value,
.date-value {
  color: #5a6c7d;
  font-weight: 600;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  font-size: 14px;
}

.action-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-size: 14px;
}

.action-button:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}
</style>