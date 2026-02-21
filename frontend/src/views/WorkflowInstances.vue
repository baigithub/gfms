<template>
  <div class="workflow-instances">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon" color="#667eea"><Operation /></el-icon>
            <span class="card-title">流程实例</span>
            <el-tag type="info" size="small">{{ instances.length }} 个实例</el-tag>
          </div>
          <div class="header-right">
            <el-select 
              v-model="workflowType" 
              placeholder="工作流类型" 
              class="modern-select"
              @change="loadInstances"
            >
              <el-option label="通用工作流" value="general" />
              <el-option label="绿色金融工作流" value="green_finance" />
            </el-select>
            <el-select 
              v-model="statusFilter" 
              placeholder="状态" 
              class="modern-select"
              @change="loadInstances"
            >
              <el-option label="全部" value="" />
              <el-option label="审批中" value="running" />
              <el-option label="已完成" value="completed" />
              <el-option label="已终止" value="terminated" />
              <el-option label="退回" value="returned" />
              <el-option label="撤回" value="withdrawn" />
              <el-option label="分配" value="assigned" />
              <el-option label="已办结" value="已办结" />
            </el-select>
            <el-button @click="loadInstances">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="instances" 
        stripe
        class="modern-table"
      >
        <el-table-column prop="customer_name" label="客户名称" width="150">
          <template #default="{ row }">
            <div class="customer-name">
              <el-icon><User /></el-icon>
              {{ row.customer_name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="loan_account" label="贷款账号" width="180">
          <template #default="{ row }">
            <div class="loan-account">
              <el-icon><Document /></el-icon>
              {{ row.loan_account }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="instance_key" label="实例键" width="150">
          <template #default="{ row }">
            <el-tag type="info" effect="plain" size="small">{{ row.instance_key }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="business_key" label="业务键" width="150">
          <template #default="{ row }">
            <el-tag type="primary" effect="plain" size="small">{{ row.business_key }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="definition.name" label="流程名称" width="200">
          <template #default="{ row }">
            <div class="workflow-name">
              <el-icon><FolderOpened /></el-icon>
              {{ row.definition?.name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="流程版本" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="success" effect="plain" size="small">v{{ row.definition?.version }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="plain" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="started_at" label="开始时间" width="180" align="center">
          <template #default="{ row }">
            <div class="date-value">{{ row.started_at }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="completed_at" label="完成时间" width="180" align="center">
          <template #default="{ row }">
            <div class="date-value">{{ row.completed_at || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" link size="small" @click="viewDetail(row)">
                <el-icon><View /></el-icon>
                查看详情
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          small
        />
      </div>

      <el-empty v-if="instances.length === 0" description="暂无流程实例" />
    </el-card>
    
    <!-- 实例详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      title="实例详情" 
      width="900px"
      class="instance-dialog"
    >
      <div class="instance-detail-content">
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="实例键">{{ currentInstance?.instance_key }}</el-descriptions-item>
          <el-descriptions-item label="业务键">{{ currentInstance?.business_key }}</el-descriptions-item>
          <el-descriptions-item label="流程名称">{{ currentInstance?.definition?.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentInstance?.status)" effect="plain">
              {{ getStatusText(currentInstance?.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ currentInstance?.started_at }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ currentInstance?.completed_at || '-' }}</el-descriptions-item>
        </el-descriptions>
        
        <el-divider content-position="left">
          <span class="divider-title">
            <el-icon><List /></el-icon>
            任务记录
          </span>
        </el-divider>
        
        <el-table :data="tasks" stripe size="small" class="tasks-table">
          <el-table-column prop="task_name" label="任务名称" width="200">
            <template #default="{ row }">
              <div class="task-name">
                <el-icon><ElementPlus /></el-icon>
                {{ row.task_name }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="assignee_name" label="处理人" width="120">
            <template #default="{ row }">
              <div class="assignee-name">
                <el-icon><UserFilled /></el-icon>
                {{ row.assignee_name }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getTaskStatusType(row.status)" effect="plain" size="small">
                {{ getTaskStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="started_at" label="开始时间" width="180" align="center">
            <template #default="{ row }">
              <div class="date-value">{{ row.started_at }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="completed_at" label="完成时间" width="180" align="center">
            <template #default="{ row }">
              <div class="date-value">{{ row.completed_at || '-' }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="comment" label="处理意见" min-width="200" show-overflow-tooltip />
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Operation, 
  Refresh, 
  User, 
  Document, 
  FolderOpened, 
  View, 
  Delete,
  List,
  ElementPlus,
  UserFilled
} from '@element-plus/icons-vue'
import { 
  getInstances, 
  getInstanceTasks, 
  deleteInstance, 
  getGreenFinanceInstances, 
  deleteGreenFinanceInstance, 
  getGreenFinanceInstanceTasks 
} from '@/api/workflow'

const instances = ref([])
const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0
})
const tasks = ref([])
const statusFilter = ref('')
const workflowType = ref('green_finance')
const detailDialogVisible = ref(false)
const currentInstance = ref(null)

const loadInstances = async () => {
  try {
    const params = { 
      page: pagination.value.page, 
      page_size: pagination.value.page_size 
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    let res
    if (workflowType.value === 'green_finance') {
      res = await getGreenFinanceInstances(params)
    } else {
      res = await getInstances(params)
    }
    instances.value = res.data || []
    pagination.value.total = res.total || 0
  } catch (error) {
    console.error('Failed to load instances:', error)
    ElMessage.error('加载实例列表失败')
  }
}

const viewDetail = async (instance) => {
  currentInstance.value = instance
  try {
    let res
    if (workflowType.value === 'green_finance') {
      res = await getGreenFinanceInstanceTasks(instance.id)
    } else {
      res = await getInstanceTasks(instance.id)
    }
    tasks.value = res || []
    detailDialogVisible.value = true
  } catch (error) {
    console.error('Failed to load tasks:', error)
    ElMessage.error('加载任务记录失败')
  }
}

const handleDelete = async (instance) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除流程实例 "${instance.instance_key}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    if (workflowType.value === 'green_finance') {
      await deleteGreenFinanceInstance(instance.id)
    } else {
      await deleteInstance(instance.id)
    }
    ElMessage.success('流程实例删除成功')
    loadInstances()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('流程实例删除失败')
    }
  }
}

const handlePageChange = (page) => {
  pagination.value.page = page
  loadInstances()
}

const handleSizeChange = (size) => {
  pagination.value.page_size = size
  pagination.value.page = 1
  loadInstances()
}

const getStatusType = (status) => {
  const typeMap = {
    'running': 'warning',
    'completed': 'success',
    'terminated': 'danger',
    'returned': 'warning',
    'withdrawn': 'info',
    'assigned': 'primary',
    '已办结': 'success'
  }
  return typeMap[status] || ''
}

const getStatusText = (status) => {
  const textMap = {
    'running': '审批中',
    'completed': '已完成',
    'terminated': '已终止',
    'returned': '退回',
    'withdrawn': '撤回',
    'assigned': '分配',
    '已办结': '已办结'
  }
  return textMap[status] || status
}

const getTaskStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'completed': 'success',
    'skipped': 'info',
    'cancelled': 'danger'
  }
  return typeMap[status] || ''
}

const getTaskStatusText = (status) => {
  const textMap = {
    'pending': '待处理',
    'completed': '已完成',
    'skipped': '已跳过',
    'cancelled': '已取消'
  }
  return textMap[status] || status
}

onMounted(() => {
  loadInstances()
})
</script>

<style scoped>
.workflow-instances {
  height: 100%;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.modern-select {
  width: 150px;
}

:deep(.modern-select .el-input__wrapper) {
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

:deep(.modern-select .el-input__wrapper:hover) {
  border-color: #667eea;
}

:deep(.modern-select .el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

:deep(.header-right .el-button) {
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

:deep(.modern-table) {
  border-radius: 12px;
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

:deep(.modern-table tr:hover > td) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%) !important;
}

:deep(.modern-table td) {
  padding: 16px 12px;
  font-size: 14px;
  color: #2c3e50;
}

.customer-name,
.loan-account,
.workflow-name,
.task-name,
.assignee-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.date-value {
  color: #7f8c8d;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-buttons :deep(.el-button) {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  font-size: 13px;
}

:deep(.el-button--primary.is-link) {
  color: #667eea;
  font-weight: 500;
}

:deep(.el-button--primary.is-link:hover) {
  color: #764ba2;
}

:deep(.el-button--danger.is-link) {
  color: #f44336;
  font-weight: 500;
}

:deep(.el-button--danger.is-link:hover) {
  color: #d32f2f;
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

/* 对话框样式 */
:deep(.instance-dialog) {
  border-radius: 16px;
}

:deep(.instance-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.instance-dialog .el-dialog__body) {
  padding: 24px;
}

.instance-detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

:deep(.el-divider) {
  margin: 0;
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

.tasks-table {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.tasks-table th) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%) !important;
  color: #303133 !important;
  font-weight: 600;
  padding: 16px 12px;
}

:deep(.tasks-table th .cell) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

:deep(.tasks-table td) {
  padding: 16px 12px;
  color: #2c3e50;
}

:deep(.el-loading-mask) {
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
}

:deep(.el-loading-spinner .path) {
  stroke: #667eea;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 20px 0 0 0;
}
</style>