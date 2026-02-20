<template>
  <div class="task-detail-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">任务详情 - {{ taskDetail.customer_name }}</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="业务信息" name="business">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="贷款编号">{{ taskDetail.loan_code }}</el-descriptions-item>
            <el-descriptions-item label="客户名称">{{ taskDetail.customer_name }}</el-descriptions-item>
            <el-descriptions-item label="业务品种">{{ taskDetail.business_type }}</el-descriptions-item>
            <el-descriptions-item label="贷款账号">{{ taskDetail.loan_account }}</el-descriptions-item>
            <el-descriptions-item label="放款金额">{{ formatAmount(taskDetail.loan_amount) }}</el-descriptions-item>
            <el-descriptions-item label="放款日期">{{ formatDate(taskDetail.disbursement_date) }}</el-descriptions-item>
            <el-descriptions-item label="绿色金融支持项目目录" :span="2">
              <el-cascader
                v-model="selectedCategory"
                :options="categoryOptions"
                :props="cascaderProps"
                placeholder="请选择绿色金融支持项目目录"
                clearable
                filterable
                @change="handleCategoryChange"
                style="width: 100%"
              />
            </el-descriptions-item>
            <el-descriptions-item label="任务办理截止日期">{{ taskDetail.deadline ? formatDate(taskDetail.deadline) : '-' }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(taskDetail.status)" size="small">
                {{ taskDetail.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="发起人">{{ taskDetail.initiator_name }}</el-descriptions-item>
            <el-descriptions-item label="发起时间">{{ formatDateTime(taskDetail.started_at) }}</el-descriptions-item>
            <el-descriptions-item label="完成时间" :span="2">{{ taskDetail.completed_at ? formatDateTime(taskDetail.completed_at) : '-' }}</el-descriptions-item>
            <el-descriptions-item label="机构" :span="2">{{ taskDetail.org_name || '-' }}</el-descriptions-item>
          </el-descriptions>

          <!-- 材料上传 -->
          <div class="upload-section">
            <div class="section-title">材料上传</div>
            <el-upload
              v-model:file-list="fileList"
              :action="uploadUrl"
              :headers="uploadHeaders"
              :on-success="handleUploadSuccess"
              :on-remove="handleRemove"
              :on-preview="handlePreview"
              :on-change="handleFileChange"
              :limit="10"
              :before-upload="beforeUpload"
              :auto-upload="true"
              multiple
              list-type="text"
            >
              <el-button type="primary" size="small">
                <el-icon><UploadFilled /></el-icon>
                选择文件
              </el-button>
              <template #tip>
                <div class="el-upload__tip">
                  支持 jpg、png、pdf、doc、docx、xls、xlsx 格式，单个文件不超过10MB，最多上传10个文件
                </div>
              </template>
            </el-upload>
            
            <!-- 已上传文件列表 -->
            <div v-if="fileList.length > 0" class="uploaded-files">
              <div class="files-title">已上传文件 ({{ fileList.length }})</div>
              <div class="files-list">
                <div
                  v-for="(file, index) in fileList"
                  :key="index"
                  class="file-item"
                >
                  <el-icon><Document /></el-icon>
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  <el-button
                    type="danger"
                    link
                    size="small"
                    @click="handleRemove(file)"
                  >
                    删除
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 办理意见 -->
          <div class="opinion-section">
            <div class="section-title">办理意见</div>
            <el-input
              v-model="processingOpinion"
              type="textarea"
              :rows="4"
              placeholder="请输入办理意见"
              maxlength="500"
              show-word-limit
            />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="审批记录" name="approval">
          <div v-loading="historyLoading">
            <el-timeline v-if="workflowHistory.length > 0">
              <el-timeline-item
                v-for="item in workflowHistory"
                :key="item.id"
                :timestamp="formatDateTime(item.completed_at || item.started_at)"
                placement="top"
              >
                <el-card>
                  <div class="timeline-content">
                    <div class="timeline-header">
                      <span class="timeline-title">{{ item.task_name }}</span>
                      <el-tag :type="getStatusType(item.status)" size="small">
                        {{ item.status }}
                      </el-tag>
                    </div>
                    <div class="timeline-detail">
                      <span>审批人: {{ item.assignee_name }}</span>
                      <span v-if="item.assignee_username">账号: {{ item.assignee_username }}</span>
                      <span>岗位: {{ item.position_name }}</span>
                    </div>
                    <div v-if="item.approval_result" class="timeline-result">
                      <span>审批结果: </span>
                      <span :class="item.approval_result === '同意' ? 'result-agree' : 'result-disagree'">
                        {{ item.approval_result }}
                      </span>
                    </div>
                    <div v-if="item.comment" class="timeline-comment">
                      <span>意见: {{ item.comment }}</span>
                    </div>
                    <div v-if="item.reason" class="timeline-reason">
                      <span>原因: {{ item.reason }}</span>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无审批记录" />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="流程跟踪" name="flow">
          <FlowChart :workflow-history="workflowHistory" />
        </el-tab-pane>
        
        <el-tab-pane label="绿色分类变动轨迹" name="category-trace">
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
                    <el-tag size="small">{{ item.status }}</el-tag>
                  </div>
                  <div class="trace-detail">
                    <span>办理人: {{ item.assignee_name }}</span>
                    <span v-if="item.assignee_username">账号: {{ item.assignee_username }}</span>
                  </div>
                  <div v-if="item.formatted_category" class="trace-category">
                    <div class="category-label">绿色金融支持项目目录:</div>
                    <div class="category-value">{{ item.formatted_category }}</div>
                  </div>
                  <div v-else class="trace-category-empty">
                    <span>暂无分类信息</span>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-if="!workflowHistory || workflowHistory.length === 0" description="暂无分类变动轨迹" />
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="附件列表" name="attachments">
          <div class="attachments-section">
            <el-table :data="taskDetail.attachments || []" stripe size="small">
              <el-table-column prop="task_name" label="所属节点" width="150" />
              <el-table-column prop="uploader_name" label="上传人" width="120" />
              <el-table-column prop="original_filename" label="附件名称" min-width="200">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="handleDownloadAttachment(row)">
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
            <el-empty v-if="!taskDetail.attachments || taskDetail.attachments.length === 0" description="暂无附件" :image-size="60" />
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <div class="page-actions">
        <el-button @click="goBack">关闭</el-button>
        <el-button type="info" plain @click="handleSave">
          <el-icon><Document /></el-icon>
          暂存
        </el-button>
        <el-button v-if="canReturn" type="warning" @click="showReturnDialog">退回</el-button>
        <el-button type="primary" @click="showApprovalDialog">提交审批</el-button>
      </div>
    </el-card>
    
    <!-- 审批对话框 -->
    <el-dialog
      v-model="approvalDialogVisible"
      title="任务审批"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="approval-message">您是否确认提交？</div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="approvalDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleCompleteTask">确定</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 退回对话框 -->
    <el-dialog
      v-model="returnDialogVisible"
      title="任务退回"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form label-width="100px">
        <el-form-item label="退回到">
          <el-select v-model="returnForm.return_to_node" placeholder="请选择退回节点" style="width: 100%">
            <el-option
              v-for="node in returnOptions"
              :key="node.value"
              :label="node.label"
              :value="node.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="退回意见">
          <el-input
            v-model="returnForm.comment"
            type="textarea"
            :rows="4"
            placeholder="请输入退回意见"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="returnDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleReturnTask">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Document, SuccessFilled, Loading, Clock } from '@element-plus/icons-vue'
import FlowChart from '@/components/FlowChart.vue'
import { getTaskDetail, getWorkflowHistory, completeTask, withdrawTask, getGreenCategories, updateTaskCategory, saveTask, returnTask } from '@/api/green_finance'
import { useAuthStore } from '@/store/auth'
import { useTabsStore } from '@/store/tabs'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const tabsStore = useTabsStore()

const taskId = computed(() => route.params.id)

const taskDetail = ref({})
const workflowHistory = ref([])
const components = {
  FlowChart
}
const activeTab = ref('business')
const historyLoading = ref(false)

// 绿色项目目录选择
const selectedCategory = ref([])
const categoryOptions = ref([])
const cascaderProps = {
  value: 'value',
  label: 'label',
  children: 'children',
  emitPath: true,
  checkStrictly: false
}

// 办理意见
const processingOpinion = ref('')

// 材料上传
const fileList = ref([])
const currentTaskId = ref(null)

const uploadUrl = computed(() => {
  // 优先使用当前待处理任务的ID，如果没有则使用identification_id
  const id = currentTaskId.value || taskId.value
  return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/files/upload?task_id=${id}`
})
const uploadHeaders = computed(() => {
  return {
    'Authorization': `Bearer ${authStore.token}`
  }
})

const approvalDialogVisible = ref(false)
const approvalForm = reactive({
  approval_result: '同意',
  comment: '',
  reason: ''
})

const returnDialogVisible = ref(false)
const returnForm = reactive({
  return_to_node: '',
  comment: ''
})

// 根据当前节点判断是否可以退回
const canReturn = computed(() => {
  if (!workflowHistory.value || workflowHistory.value.length === 0) return false
  
  // 获取当前待处理的任务
  const currentTask = workflowHistory.value.find(item => item.status === '待处理')
  if (!currentTask) return false
  
  const taskKey = currentTask.task_key
  
  // 客户经理不能退回
  if (taskKey === 'manager_identification') return false
  
  // 其他节点可以退回
  return true
})

// 根据当前节点判断是否可以撤回
const canWithdraw = computed(() => {
  if (!workflowHistory.value || workflowHistory.value.length === 0) return false
  
  // 获取当前待处理的任务
  const currentTask = workflowHistory.value.find(item => item.status === '待处理')
  if (!currentTask) return false
  
  const taskKey = currentTask.task_key
  
  // 客户经理（第一个节点）不能撤回
  if (taskKey === 'manager_identification') return false
  
  // 一级分行绿色金融复核岗不能撤回
  if (taskKey === 'final_review') return false
  
  // 其他节点可以撤回
  return true
})

// 根据当前节点获取可退回的节点选项
const returnOptions = computed(() => {
  if (!workflowHistory.value || workflowHistory.value.length === 0) return []
  
  // 获取当前待处理的任务
  const currentTask = workflowHistory.value.find(item => item.status === '待处理')
  if (!currentTask) return []
  
  const taskKey = currentTask.task_key
  
  const optionsMap = {
    'branch_review': [
      { value: 'manager_identification', label: '客户经理认定' }
    ],
    'first_approval': [
      { value: 'manager_identification', label: '客户经理认定' },
      { value: 'branch_review', label: '二级分行绿色金融管理岗' }
    ],
    'final_review': [
      { value: 'manager_identification', label: '客户经理认定' },
      { value: 'branch_review', label: '二级分行绿色金融管理岗' },
      { value: 'first_approval', label: '一级分行绿色金融管理岗' }
    ]
  }
  
  return optionsMap[taskKey] || []
})

const currentStep = computed(() => {
  if (!workflowHistory.value || workflowHistory.value.length === 0) return 0
  
  const lastTask = workflowHistory.value[workflowHistory.value.length - 1]
  if (lastTask.approval_result === '同意') {
    if (lastTask.task_key === 'manager_identification') return 1
    if (lastTask.task_key === 'branch_review') return 2
    if (lastTask.task_key === 'first_approval') return 3
    if (lastTask.task_key === 'final_review') return 4
  }
  return 1
})

const flowSteps = computed(() => {
  // 定义基础流程节点
  const baseSteps = [
    { title: '开始', description: '客户经理发起认定', task_key: 'start' },
    { title: '客户经理认定', description: '填写认定信息', task_key: 'manager_identification' },
    { title: '二级分行绿色金融管理岗', description: '绿色金融管理部门审核', task_key: 'branch_review' },
    { title: '一级分行绿色金融管理岗', description: '一级分行审批', task_key: 'first_approval' },
    { title: '一级分行绿色金融复核岗', description: '最终复核', task_key: 'final_review' },
    { title: '结束', description: '流程完成', task_key: 'end' }
  ]
  
  if (!workflowHistory.value || workflowHistory.value.length === 0) {
    return baseSteps.map((step, index) => ({
      ...step,
      status: index === 0 ? 'finish' : (index === 1 ? 'process' : 'wait'),
      lineColor: 'black'
    }))
  }
  
  // 动态生成流程节点
  const steps = []
  let currentTaskKey = null
  
  // 按时间顺序处理每个任务
  const sortedHistory = [...workflowHistory.value].sort((a, b) => 
    new Date(a.started_at) - new Date(b.started_at)
  )
  
  console.log('DEBUG flowSteps: sortedHistory', sortedHistory)
  
  // 添加开始节点
  steps.push({
    ...baseSteps[0],
    status: 'finish',
    lineColor: 'black'
  })
  
  // 为每个任务创建节点
  sortedHistory.forEach((task, index) => {
    const stepInfo = baseSteps.find(s => s.task_key === task.task_key)
    if (!stepInfo) return
    
    const isCompleted = task.status === '已完成'
    const isPending = task.status === '待处理' || task.status === '暂存'
    
    // 检查是否有退回操作（下一个任务的task_key比当前任务的task_key小）
    let lineColor = 'black'
    if (index < sortedHistory.length - 1) {
      const nextTask = sortedHistory[index + 1]
      const currentIndex = baseSteps.findIndex(s => s.task_key === task.task_key)
      const nextIndex = baseSteps.findIndex(s => s.task_key === nextTask.task_key)
      
      console.log(`DEBUG flowSteps: task ${task.task_key} -> next ${nextTask.task_key}, currentIndex=${currentIndex}, nextIndex=${nextIndex}`)
      
      // 如果是退回（返回到前面的节点）
      if (nextIndex < currentIndex && nextIndex > 0) {
        lineColor = '#67C23A' // 浅绿色
        console.log(`DEBUG flowSteps: 退回操作，设置连线颜色为浅绿色`)
      }
    }
    
    steps.push({
      title: stepInfo.title,
      description: stepInfo.description,
      task_key: task.task_key,
      status: isCompleted ? 'finish' : (isPending ? 'process' : 'wait'),
      lineColor: lineColor,
      taskData: task
    })
    
    if (isPending) {
      currentTaskKey = task.task_key
    }
  })
  
  // 如果最后一个任务已完成且是复核岗，添加结束节点
  const lastTask = sortedHistory[sortedHistory.length - 1]
  if (lastTask && lastTask.status === '已完成' && lastTask.task_key === 'final_review') {
    steps.push({
      ...baseSteps[baseSteps.length - 1],
      status: 'finish',
      lineColor: 'black'
    })
  }
  
  console.log('DEBUG flowSteps: final steps', steps)
  return steps
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

const formatDateTime = (value) => {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const calculateDuration = (startTime, endTime) => {
  if (!startTime || !endTime) return '-'
  
  const start = dayjs(startTime)
  const end = dayjs(endTime)
  const diff = end.diff(start, 'second')
  
  if (diff < 60) {
    return `${diff}秒`
  } else if (diff < 3600) {
    const minutes = Math.floor(diff / 60)
    const seconds = diff % 60
    return seconds > 0 ? `${minutes}分${seconds}秒` : `${minutes}分钟`
  } else if (diff < 86400) {
    const hours = Math.floor(diff / 3600)
    const minutes = Math.floor((diff % 3600) / 60)
    return minutes > 0 ? `${hours}小时${minutes}分` : `${hours}小时`
  } else {
    const days = Math.floor(diff / 86400)
    const hours = Math.floor((diff % 86400) / 3600)
    return hours > 0 ? `${days}天${hours}小时` : `${days}天`
  }
}

const formatGreenProjectCategory = (row) => {
  if (row.formatted_category) {
    return row.formatted_category
  }
  // 兼容旧数据
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

const getStatusType = (status) => {
  const typeMap = {
    '待处理': 'warning',
    '已完成': 'success',
    '已撤回': 'info',
    '已退回': 'warning',
    '暂存': 'info'
  }
  return typeMap[status] || 'info'
}

const loadData = async () => {
  try {
    const detail = await getTaskDetail(taskId.value)
    taskDetail.value = detail
    
    // 使用identification_id获取工作流历史
    const history = await getWorkflowHistory(detail.id)
    workflowHistory.value = history
    
    // 获取当前待处理任务
    const currentTask = history.find(item => item.status === '待处理')
    
    // 设置当前待处理任务的ID（用于附件上传）
    if (currentTask) {
      currentTaskId.value = currentTask.id
    }
    
    // 获取当前待处理任务的办理意见并回显
    if (currentTask && currentTask.comment) {
      processingOpinion.value = currentTask.comment
    }
    
    // 回显当前任务的分类信息（优先使用当前任务的分类，如果没有则使用上一已完成节点的分类）
    if (currentTask) {
      if (currentTask.formatted_category || currentTask.project_category_large) {
        // 使用当前任务的分类信息
        detail.project_category_large = currentTask.project_category_large || detail.project_category_large
        detail.project_category_medium = currentTask.project_category_medium || detail.project_category_medium
        detail.project_category_small = currentTask.project_category_small || detail.project_category_small
        detail.formatted_category = currentTask.formatted_category || detail.formatted_category
      } else if (!detail.project_category_large && !detail.project_category_medium && !detail.project_category_small) {
        // 如果当前任务没有分类信息，且identification也没有分类信息，则使用上一已完成节点的分类
        const previousTasks = history.filter(item => 
          item.id < currentTask.id && item.status === '已完成'
        )
        if (previousTasks.length > 0) {
          // 取最近的一个已完成的任务
          const latestPrevious = previousTasks[previousTasks.length - 1]
          if (latestPrevious.formatted_category) {
            detail.project_category_large = latestPrevious.project_category_large
            detail.project_category_medium = latestPrevious.project_category_medium
            detail.project_category_small = latestPrevious.project_category_small
            detail.formatted_category = latestPrevious.formatted_category
          }
        }
      }
    }
    
    // 回显当前任务的附件
    if (currentTask && detail.attachments) {
      fileList.value = detail.attachments
        .filter(attachment => attachment.task_id === currentTask.id)
        .map(attachment => ({
          name: attachment.original_filename,
          size: attachment.file_size,
          url: attachment.download_url,
          uid: attachment.id
        }))
    }
    
    // 调试：打印任务详情数据
    console.log('任务详情数据:', detail)
    console.log('附件数据:', detail.attachments)
    
    // 调试：打印流程跟踪数据
    
        console.log('流程跟踪数据:', history)
    
        history.forEach(item => {
    
          console.log(`任务${item.id}:`, {
    
            task_name: item.task_name,
    
            status: item.status,
    
            assignee_name: item.assignee_name,
    
            assignee_username: item.assignee_username,
    
            formatted_category: item.formatted_category,
    
            completed_at: item.completed_at
    
          })
    
        })
    
        
    
        // 设置当前选中的分类（根据上个节点的绿色分类）
    
        if (detail.project_category_small || detail.project_category_medium || detail.project_category_large) {
    
          // 先加载绿色分类选项
    
          await loadGreenCategories()
    
          
          // 优先使用后端返回的code字段，如果没有则使用名称匹配
          const codes = []
          
          if (detail.project_category_large_code) {
            codes.push(detail.project_category_large_code)
            if (detail.project_category_medium_code) {
              codes.push(detail.project_category_medium_code)
              if (detail.project_category_small_code) {
                codes.push(detail.project_category_small_code)
              }
            }
          }
          
          // 如果没有code字段，使用名称匹配作为备选
          if (codes.length === 0) {
            const findCategoryCodes = (largeName, mediumName = null, smallName = null) => {
              // 查找大类（label格式为"code name"，所以需要检查label是否包含name）
              const largeOption = categoryOptions.value.find(opt => opt.label.includes(largeName))
              if (!largeOption) return null
              
              const result = [largeOption.value]
              
              if (mediumName && largeOption.children) {
                const mediumOption = largeOption.children.find(opt => opt.label.includes(mediumName))
                if (mediumOption) {
                  result.push(mediumOption.value)
                  
                  if (smallName && mediumOption.children) {
                    const smallOption = mediumOption.children.find(opt => opt.label.includes(smallName))
                    if (smallOption) {
                      result.push(smallOption.value)
                    }
                  }
                }
              }
              
              return result
            }
            
            const nameCodes = findCategoryCodes(
              detail.project_category_large,
              detail.project_category_medium,
              detail.project_category_small
            )
            
            if (nameCodes) {
              selectedCategory.value = nameCodes
            }
          } else {
            selectedCategory.value = codes
          }
        }
    
      } catch (error) {
    
        ElMessage.error('获取任务详情失败')
    
      }
    
    }

const loadGreenCategories = async () => {
  try {
    const categories = await getGreenCategories()
    categoryOptions.value = buildCategoryTree(categories)
  } catch (error) {
    console.error('加载绿色项目目录失败:', error)
  }
}

const buildCategoryTree = (categories) => {
  // 构建三级级联选择器数据结构
  const tree = []
  const largeMap = new Map()
  
  // 第一遍：收集所有大类
  categories.forEach(cat => {
    if (!largeMap.has(cat.large_code)) {
      largeMap.set(cat.large_code, {
        value: cat.large_code,
        label: `${cat.large_code} ${cat.large_name}`,
        children: []
      })
    }
  })
  
  // 第二遍：添加中类到大类
  const mediumMap = new Map()
  categories.forEach(cat => {
    const large = largeMap.get(cat.large_code)
    if (large) {
      const mediumKey = `${cat.large_code}-${cat.medium_code}`
      if (!mediumMap.has(mediumKey)) {
        const medium = {
          value: cat.medium_code,
          label: `${cat.medium_code} ${cat.medium_name}`,
          children: []
        }
        large.children.push(medium)
        mediumMap.set(mediumKey, medium)
      }
    }
  })
  
  // 第三遍：添加小类到中类
  categories.forEach(cat => {
    if (cat.small_code) {
      const mediumKey = `${cat.large_code}-${cat.medium_code}`
      const medium = mediumMap.get(mediumKey)
      if (medium) {
        medium.children.push({
          value: cat.small_code,
          label: `${cat.small_code} ${cat.small_name}`
        })
      }
    }
  })
  
  return Array.from(largeMap.values())
}

const handleCategoryChange = async (value) => {
  if (!value || value.length === 0) {
    return
  }
  
  console.log('handleCategoryChange - selected value:', value)
  
  try {
    // 构建更新数据
    const updateData = {
      project_category_large: '',
      project_category_medium: '',
      project_category_small: ''
    }
    
    // 查找对应的名称
    const allCategories = await getGreenCategories()
    
    // 查找大类名称
    const largeCategory = allCategories.find(c => c.large_code === value[0])
    if (largeCategory) {
      updateData.project_category_large = largeCategory.large_name
      console.log('找到大类:', largeCategory.large_code, largeCategory.large_name)
    }
    
    // 查找中类名称 - 确保只匹配正确的记录（同时匹配 large_code 和 medium_code）
    if (value[1]) {
      const mediumCategory = allCategories.find(c => 
        c.large_code === value[0] && 
        c.medium_code === value[1]
      )
      if (mediumCategory) {
        updateData.project_category_medium = mediumCategory.medium_name
        console.log('找到中类:', mediumCategory.medium_code, mediumCategory.medium_name)
      }
    }
    
    // 查找小类名称 - 确保只匹配正确的记录（同时匹配所有三个 code）
    if (value[2]) {
      const smallCategory = allCategories.find(c => 
        c.large_code === value[0] && 
        c.medium_code === value[1] && 
        c.small_code === value[2]
      )
      if (smallCategory) {
        updateData.project_category_small = smallCategory.small_name
        console.log('找到小类:', smallCategory.small_code, smallCategory.small_name)
      }
    }
    
    console.log('准备更新的数据:', updateData)
    
    // 调用API更新
    await updateTaskCategory(taskId.value, updateData)
    ElMessage.success('绿色金融支持项目目录已更新')
    
    // 更新taskDetail中的分类信息，避免重新加载导致分类被覆盖
    if (updateData.project_category_large) {
      taskDetail.value.project_category_large = updateData.project_category_large
    }
    if (updateData.project_category_medium) {
      taskDetail.value.project_category_medium = updateData.project_category_medium
    }
    if (updateData.project_category_small) {
      taskDetail.value.project_category_small = updateData.project_category_small
    }
    
    // 重新加载任务详情以确保数据一致性
    await loadData()
  } catch (error) {
    console.error('更新分类失败:', error)
    ElMessage.error('更新绿色金融支持项目目录失败')
  }
}

const goBack = () => {
  // 返回上一页或待办列表
  if (route.query.from === 'pending') {
    router.push('/green-identify/pending')
  } else {
    router.back()
  }
}

const showApprovalDialog = () => {
  approvalDialogVisible.value = true
}

const handleCompleteTask = async () => {
  try {
    // 准备提交的数据，包括绿色分类
    const submitData = {
      approval_result: '同意',
      comment: processingOpinion.value || '',
      reason: ''
    }
    
    // 添加绿色分类信息
    if (selectedCategory.value && selectedCategory.value.length > 0) {
      try {
        const allCategories = await getGreenCategories()
        
        // 查找大类名称
        const largeCategory = allCategories.find(c => c.large_code === selectedCategory.value[0])
        if (largeCategory) {
          submitData.project_category_large = largeCategory.large_name
        }
        
        // 查找中类名称
        if (selectedCategory.value[1]) {
          const mediumCategory = allCategories.find(c => 
            c.large_code === selectedCategory.value[0] && c.medium_code === selectedCategory.value[1]
          )
          if (mediumCategory) {
            submitData.project_category_medium = mediumCategory.medium_name
          }
        }
        
        // 查找小类名称
        if (selectedCategory.value[2]) {
          const smallCategory = allCategories.find(c => 
            c.large_code === selectedCategory.value[0] && 
            c.medium_code === selectedCategory.value[1] && 
            c.small_code === selectedCategory.value[2]
          )
          if (smallCategory) {
            submitData.project_category_small = smallCategory.small_name
          }
        }
      } catch (error) {
        console.error('获取分类信息失败:', error)
      }
    }
    
    // 获取当前待处理任务的ID
    const history = await getWorkflowHistory(taskDetail.value.id)
    console.log('DEBUG: handleCompleteTask - history:', history)
    console.log('DEBUG: handleCompleteTask - taskDetail.value.id:', taskDetail.value.id)
    
    // 查找状态为"待处理"或"暂存"的任务
    const currentTask = history.find(item => item.status === '待处理' || item.status === '暂存')
    console.log('DEBUG: handleCompleteTask - currentTask:', currentTask)
    
    if (currentTask) {
      console.log('DEBUG: handleCompleteTask - currentTask.id:', currentTask.id)
      await completeTask(currentTask.id, submitData)
      ElMessage.success('任务已完成')
      approvalDialogVisible.value = false
    } else {
      ElMessage.error('找不到当前待处理任务')
      return
    }
    
    // 关闭当前页签
    tabsStore.removeTab(route.path)
    
    // 刷新待办任务列表（通过导航到待办列表触发）
    // 添加时间戳强制刷新
    setTimeout(() => {
      router.push({
        path: '/green-identify/pending',
        query: { t: Date.now() }  // 添加时间戳强制刷新
      })
    }, 500)
  } catch (error) {
    ElMessage.error('任务完成失败')
  }
}

const handleWithdraw = async () => {
  try {
    await ElMessageBox.confirm('确定要撤回此任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await withdrawTask(taskId.value)
    ElMessage.success('任务已撤回')
    // 返回待办列表
    setTimeout(() => {
      if (route.query.from === 'pending') {
        router.push('/green-identify/pending')
      } else {
        router.back()
      }
    }, 1000)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('任务撤回失败')
    }
  }
}

const handleSave = async () => {
  try {
    // 优先使用用户选择的分类，如果没有则使用taskDetail的分类（可能包含默认分类）
    let projectCategoryLarge = taskDetail.value.project_category_large
    let projectCategoryMedium = taskDetail.value.project_category_medium
    let projectCategorySmall = taskDetail.value.project_category_small
    
    // 如果用户选择了分类，使用用户选择的分类
    if (selectedCategory.value && selectedCategory.value.length > 0) {
      try {
        const allCategories = await getGreenCategories()
        
        // 查找大类名称
        const largeCategory = allCategories.find(c => c.large_code === selectedCategory.value[0])
        if (largeCategory) {
          projectCategoryLarge = largeCategory.large_name
        }
        
        // 查找中类名称
        if (selectedCategory.value[1]) {
          const mediumCategory = allCategories.find(c => 
            c.large_code === selectedCategory.value[0] && c.medium_code === selectedCategory.value[1]
          )
          if (mediumCategory) {
            projectCategoryMedium = mediumCategory.medium_name
          }
        }
        
        // 查找小类名称
        if (selectedCategory.value[2]) {
          const smallCategory = allCategories.find(c => 
            c.large_code === selectedCategory.value[0] && 
            c.medium_code === selectedCategory.value[1] && 
            c.small_code === selectedCategory.value[2]
          )
          if (smallCategory) {
            projectCategorySmall = smallCategory.small_name
          }
        }
      } catch (error) {
        console.error('获取分类信息失败:', error)
      }
    }
    
    // 保存绿色分类和意见
    const saveData = {
      project_category_large: projectCategoryLarge,
      project_category_medium: projectCategoryMedium,
      project_category_small: projectCategorySmall,
      comment: processingOpinion.value
    }
    
    // 获取当前待处理任务的ID
    console.log('DEBUG: taskDetail.value:', taskDetail.value)
    console.log('DEBUG: taskDetail.value.id:', taskDetail.value.id)
    
    const history = await getWorkflowHistory(taskDetail.value.id)
    // 查找状态为"待处理"或"暂存"的任务
    const currentTask = history.find(item => item.status === '待处理' || item.status === '暂存')
    console.log('DEBUG: currentTask:', currentTask)
    
    if (currentTask) {
      await saveTask(currentTask.id, saveData)
      ElMessage.success('任务已暂存')
      
      // 重新加载数据
      await loadData()
    } else {
      ElMessage.error('找不到当前待处理任务')
    }
  } catch (error) {
    ElMessage.error('任务暂存失败')
  }
}

const showReturnDialog = () => {
  returnForm.return_to_node = ''
  returnForm.comment = ''
  returnDialogVisible.value = true
}

const handleReturnTask = async () => {
  if (!returnForm.return_to_node) {
    ElMessage.warning('请选择退回节点')
    return
  }
  
  try {
    await returnTask(taskId.value, {
      return_to_node: returnForm.return_to_node,
      comment: returnForm.comment
    })
    ElMessage.success('任务已退回')
    returnDialogVisible.value = false
    
    // 关闭当前页签
    tabsStore.removeTab(route.path)
    
    // 刷新待办任务列表
    setTimeout(() => {
      router.push({
        path: '/green-identify/pending',
        query: { t: Date.now() }
      })
    }, 500)
  } catch (error) {
    ElMessage.error('任务退回失败')
  }
}

// 文件上传成功
const handleUploadSuccess = (response, file) => {
  if (response.code === 0 || response.success) {
    ElMessage.success('文件上传成功')
    
    // 更新文件列表，使用后端返回的数据
    if (response.data) {
      const uploadedFile = {
        name: response.data.original_filename || file.name,
        size: response.data.size || file.size,
        url: response.data.url,
        uid: file.uid,
        status: 'success',
        response: response
      }
      
      // 确保fileList中有这个文件
      const existingIndex = fileList.value.findIndex(f => f.uid === file.uid)
      if (existingIndex >= 0) {
        fileList.value[existingIndex] = uploadedFile
      } else {
        fileList.value.push(uploadedFile)
      }
    }
  } else {
    ElMessage.error(response.message || '文件上传失败')
    fileList.value = fileList.value.filter(f => f.uid !== file.uid)
  }
}

// 移除文件
const handleRemove = (file) => {
  // 从fileList中移除文件
  fileList.value = fileList.value.filter(f => f.uid !== file.uid)
  ElMessage.success('文件已移除')
}

// 预览文件
const handlePreview = (file) => {
  if (file.url) {
    window.open(file.url, '_blank')
  } else if (file.response && file.response.url) {
    window.open(file.response.url, '_blank')
  } else {
    ElMessage.warning('无法预览该文件')
  }
}

// 上传前验证
const beforeUpload = (file) => {
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'image/jpeg',
    'image/png'
  ]
  
  const isAllowedType = allowedTypes.includes(file.type)
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isAllowedType) {
    ElMessage.error('只支持 pdf、doc、docx、xls、xlsx、jpg、png 格式的文件!')
    return false
  }
  
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  
  return true
}

// 文件状态改变
const handleFileChange = (file, fileList) => {
  // 更新fileList
  if (file.status !== 'fail') {
    // 更新fileList，保留正确的文件数据
    const updatedList = fileList.map(f => {
      return {
        name: f.name,
        size: f.size,
        uid: f.uid,
        status: f.status,
        url: f.url,
        response: f.response
      }
    })
    fileList.value = updatedList
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const getTimelineType = (status) => {
  if (status === '已完成') return 'success'
  if (status === '待处理') return 'primary'
  if (status === '已撤回') return 'info'
  return 'warning'
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
    
    // 使用fetch下载文件,携带认证token
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!response.ok) {
      throw new Error(`下载失败: ${response.status}`)
    }
    
    // 创建blob并下载
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
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

onMounted(() => {
  loadData()
  loadGreenCategories()
})
</script>

<style scoped>
.task-detail-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.opinion-section {
  margin-top: 24px;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.upload-section {
  margin-top: 24px;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 4px;
  max-width: 300px;
}

.uploaded-files {
  margin-top: 16px;
  border-top: 1px solid #e0e0e0;
  padding-top: 12px;
}

.files-title {
  font-size: 13px;
  font-weight: bold;
  color: #666;
  margin-bottom: 8px;
}

.files-list {
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background-color: white;
  border-radius: 4px;
  margin-bottom: 6px;
  font-size: 12px;
  transition: background-color 0.2s;
}

.file-item:hover {
  background-color: #f0f0f0;
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #333;
}

.file-size {
  color: #999;
  font-size: 11px;
  min-width: 50px;
  text-align: right;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 12px;
}

.page-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.approval-message {
  text-align: center;
  font-size: 16px;
  color: #333;
  padding: 20px 0;
}

:deep(.el-timeline-item__timestamp) {
  color: #999;
  font-size: 12px;
}

:deep(.el-timeline-item__wrapper) {
  padding-left: 28px;
}

:deep(.el-upload__tip) {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

:deep(.upload-section .el-upload-list) {
  max-height: 200px;
  overflow-y: auto;
}

.timeline-content {
  padding: 10px 0;
}

.timeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.timeline-title {
  font-weight: bold;
  font-size: 14px;
}

.timeline-detail {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.timeline-result {
  font-size: 13px;
  margin-bottom: 5px;
}

.result-agree {
  color: #4CAF50;
  font-weight: bold;
}

.result-disagree {
  color: #f44336;
  font-weight: bold;
}

.timeline-comment,
.timeline-reason {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.flow-chart {
  padding: 40px 20px;
}

:deep(.el-descriptions__label) {
  background-color: #f5f7fa;
  font-weight: bold;
}

.category-display {
  line-height: 1.8;
}

.formatted-category {
  color: #303133;
  font-weight: 500;
  font-size: 14px;
  white-space: pre-line;
}

.category-trace {
  padding: 20px;
}

.trace-card {
  margin-bottom: 10px;
}

.trace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.trace-title {
  font-weight: bold;
  font-size: 14px;
}

.trace-detail {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}

.trace-category {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.category-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.category-value {
  font-size: 13px;
  color: #303133;
  line-height: 1.5;
}

.trace-category-empty {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
  color: #909399;
  font-size: 12px;
}

.attachments-section {
  padding: 10px 0;
}

/* 自定义流程图样式 */
.custom-flow {
  padding: 40px 20px;
  overflow-x: auto;
}

.flow-path {
  position: relative;
  min-width: fit-content;
}

.flow-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.flow-node {
  position: absolute;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 150px;
  text-align: center;
}

.node-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  font-size: 20px;
  background-color: #f5f7fa;
  color: #909399;
  border: 2px solid #dcdfe6;
}

.node-finish .node-icon {
  background-color: #67C23A;
  color: white;
  border-color: #67C23A;
}

.node-process .node-icon {
  background-color: #409EFF;
  color: white;
  border-color: #409EFF;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
}

.node-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.node-desc {
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.node-info {
  font-size: 11px;
  color: #909399;
}

.plain-category {
  color: #909399;
  font-style: italic;
  font-size: 14px;
}

.flow-chart {
  padding: 40px 20px;
}

/* 将当前处理节点改为绿色 */
:deep(.el-step.is-process .el-step__head.is-process) {
  color: #67C23A;
  border-color: #67C23A;
}

:deep(.el-step.is-process .el-step__line.is-process) {
  background-color: #67C23A;
}

:deep(.el-step.is-process .el-step__title.is-process) {
  color: #67C23A;
}

:deep(.el-step.is-process .el-step__description.is-process) {
  color: #67C23A;
}

.flow-info {
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.flow-item {
  padding: 10px 0;
  border-bottom: 1px solid #e4e7ed;
}

.flow-item:last-child {
  border-bottom: none;
}

.flow-item-title {
  font-weight: bold;
  font-size: 14px;
  color: #303133;
  margin-bottom: 5px;
}

.flow-item-info {
  font-size: 12px;
  color: #909399;
}

.flow-item-duration {
  color: #409EFF;
  font-weight: 500;
}
</style>