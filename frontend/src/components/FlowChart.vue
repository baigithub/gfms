<template>
  <div class="flow-chart-container">
    <div class="flow-chart">
      <div class="flow-rows">
                      <div
                        v-for="(row, rowIndex) in flowRows"
                        :key="rowIndex"
                        class="flow-row"
                        :class="{ 'row-all-finished': isRowAllFinished(row) }"
                      >
                        <div
                          v-for="(step, colIndex) in row"
                          :key="step.code || colIndex"
                          class="flow-node"
                          :class="{ 
                            'node-finished': step.status === 'finish',
                            'node-clickable': hasMultipleOperations(step.code),
                            'node-right-edge': rowIndex % 2 === 1 && colIndex === 0,
                            'node-last-in-row': colIndex === row.length - 1
                          }"
                          :data-code="step.code"
                          :data-status="step.status"
                          @click="handleNodeClick(step.code)"
                        >
                          <div class="flow-node-icon">
                            <el-icon v-if="step.status === 'finish'"><CircleCheckFilled /></el-icon>
                            <el-icon v-else><Clock /></el-icon>
                            <div v-if="hasMultipleOperations(step.code)" class="operation-count">
                              {{ getNodeOperationCount(step.code) }}
                            </div>
                          </div>
                          <div class="flow-node-title">{{ step.title }}</div>
                          <!-- 单次操作显示办理人和时间 -->
                          <div v-if="hasSingleOperation(step.code)" class="flow-node-info">
                            由 {{ getSingleOperation(step.code).assignee_name }} 于 {{ formatDateTime(getSingleOperation(step.code).completed_at || getSingleOperation(step.code).started_at) }} 办理完成
                          </div>
                          
                          <!-- 节点之间的连接线 -->
                          <div
                            v-if="colIndex < row.length - 1"
                            class="connection-line"
                            :class="getConnectionStatus(step, row[colIndex + 1])"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
    <!-- 节点操作历史对话框 -->
    <el-dialog
      v-model="nodeHistoryDialogVisible"
      title="节点操作历史"
      width="700px"
      class="node-history-dialog"
      :close-on-click-modal="false"
    >
      <div class="node-history-content">
        <el-timeline>
          <el-timeline-item
                          v-for="(item, index) in currentNodeHistory"
                          :key="item.id"
                          :timestamp="formatDateTime(item.completed_at || item.started_at)"
                          placement="top"
                          :type="getTimelineType(item.status)"
                        >
                          <el-card shadow="hover" class="history-card">
                            <div class="history-header">
                              <span class="history-title">第 {{ index + 1 }} 次操作</span>
                              <el-tag :type="getStatusType(item.status)" size="small" effect="dark">
                                {{ item.status }}
                              </el-tag>
                            </div>              <div class="history-detail">
                <div class="detail-item">
                  <el-icon class="detail-icon"><User /></el-icon>
                  <span>办理人: {{ item.assignee_name }}</span>
                </div>
                <div class="detail-item">
                  <el-icon class="detail-icon"><Position /></el-icon>
                  <span>岗位: {{ item.position_name }}</span>
                </div>
              </div>
              <div v-if="item.approval_result" class="history-result">
                <span class="result-label">审批结果: </span>
                <span :class="item.approval_result === '同意' ? 'result-agree' : 'result-disagree'">
                  {{ item.approval_result }}
                </span>
              </div>
              <div v-if="item.comment" class="history-comment">
                <span class="comment-label">意见: </span>
                <span>{{ item.comment }}</span>
              </div>
              <div v-if="item.reason" class="history-reason">
                <span class="reason-label">原因: </span>
                <span>{{ item.reason }}</span>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="nodeHistoryDialogVisible = false" size="large">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { CircleCheckFilled, Clock, User, Position } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const props = defineProps({
  workflowHistory: {
    type: Array,
    default: () => []
  },
  processDefinitionId: {
    type: [Number, null],
    default: null
  }
})

const nodeHistoryDialogVisible = ref(false)
const currentNodeHistory = ref([])
const activeProcessDefinition = ref(null) // 当前启用的流程定义

// 根据流程定义ID或工作流历史生成流程步骤定义
const getFlowStepDefinitions = () => {
  // 优先使用流程定义中的节点信息
  if (activeProcessDefinition.value && activeProcessDefinition.value.nodes && activeProcessDefinition.value.nodes.length > 0) {
    const flowStepDefinitions = [
      { title: '开始', description: '客户经理发起认定', code: 'start' }
    ]
    
    // 按照流程定义中的顺序添加任务节点
    activeProcessDefinition.value.nodes.forEach(node => {
      if (node.type === 'task') {
        flowStepDefinitions.push({
          title: node.name,
          description: node.name,
          code: node.task_key || node.name
        })
      }
    })
    
    flowStepDefinitions.push({
      title: '结束',
      description: '流程完成',
      code: 'end'
    })
    
    return flowStepDefinitions
  }
  // 如果没有流程定义但有工作流历史，从历史中提取节点
  else if (props.workflowHistory && props.workflowHistory.length > 0 && props.processDefinitionId) {
    const taskKeys = new Set()
    const taskNames = {}
    
    props.workflowHistory.forEach(item => {
      if (item.task_key && item.task_name) {
        taskKeys.add(item.task_key)
        taskNames[item.task_key] = item.task_name
      }
    })
    
    const flowStepDefinitions = [
      { title: '开始', description: '客户经理发起认定', code: 'start' }
    ]
    
    const sortedTaskKeys = Array.from(taskKeys).sort((a, b) => {
      const aItem = props.workflowHistory.find(i => i.task_key === a)
      const bItem = props.workflowHistory.find(i => i.task_key === b)
      return (aItem?.started_at || 0) - (bItem?.started_at || 0)
    })
    
    sortedTaskKeys.forEach(taskKey => {
      flowStepDefinitions.push({
        title: taskNames[taskKey] || taskKey,
        description: taskNames[taskKey] || taskKey,
        code: taskKey
      })
    })
    
    flowStepDefinitions.push({
      title: '结束',
      description: '流程完成',
      code: 'end'
    })
    
    return flowStepDefinitions
  } else {
    // 没有工作流历史或未绑定流程版本，显示当前启用版本的流程节点
    // 如果有activeProcessDefinition，使用它；否则使用默认的v5流程节点
    if (activeProcessDefinition.value && activeProcessDefinition.value.nodes) {
      const flowStepDefinitions = [
        { title: '开始', description: '客户经理发起认定', code: 'start' }
      ]
      
      // 按照流程定义中的顺序添加任务节点
      activeProcessDefinition.value.nodes.forEach(node => {
        if (node.type === 'task') {
          flowStepDefinitions.push({
            title: node.name,
            description: node.name,
            code: node.task_key || node.name
          })
        }
      })
      
      flowStepDefinitions.push({
        title: '结束',
        description: '流程完成',
        code: 'end'
      })
      
      return flowStepDefinitions
    } else {
      // 默认v5流程节点（向后兼容）
      return [
        { title: '开始', description: '客户经理发起认定', code: 'start' },
        { title: '客户经理提交', description: '填写认定信息', code: 'manager_identification' },
        { title: '二级分行认定', description: '二级分行绿色金融管理部门审核', code: 'branch_review' },
        { title: '一级分行认定', description: '一级分行审批', code: 'first_approval' },
        { title: '一级分行复核', description: '最终复核', code: 'final_review' },
        { title: '结束', description: '流程完成', code: 'end' }
      ]
    }
  }
}

// 将节点名称映射到 task_key（与后端保持一致）
const mapNodeNameToTaskKey = (nodeName) => {
  if (!nodeName) return ''
  if (nodeName.includes('客户经理')) return 'manager_identification'
  if (nodeName.includes('二级分行')) return 'branch_review'
  if (nodeName.includes('一级分行') && nodeName.includes('复核')) return 'final_review'
  if (nodeName.includes('一级分行')) return 'first_approval'
  if (nodeName.includes('复核')) return 'final_review'
  return nodeName.toLowerCase().replace(/\s+/g, '_')
}

// 获取当前启用的流程定义
const fetchActiveProcessDefinition = async () => {
  try {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    const headers = {
      'Content-Type': 'application/json'
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    const response = await fetch('/api/workflow/definitions?name=绿色认定&status=active&page=1&page_size=1', {
      headers: headers
    })
    
    if (!response.ok) {
      console.warn('获取流程定义失败:', response.status, response.statusText)
      return
    }
    
    const data = await response.json()
    if (data && data.length > 0) {
      const activeDef = data[0]
      // 解析BPMN XML获取节点信息
      if (activeDef.bpmn_xml) {
        const parser = new DOMParser()
        const xmlDoc = parser.parseFromString(activeDef.bpmn_xml, 'text/xml')
        const nodes = []
        
        // 提取用户任务节点（使用通配符命名空间）
        const userTasks = xmlDoc.getElementsByTagNameNS('*', 'userTask')
        console.log('找到userTask节点数量:', userTasks.length)
        
        for (let i = 0; i < userTasks.length; i++) {
          const task = userTasks[i]
          const taskName = task.getAttribute('name') || task.getAttribute('id')
          const taskId = task.getAttribute('id')
          // 使用与后端一致的映射函数
          const taskKey = mapNodeNameToTaskKey(taskName)
          console.log(`节点${i}: id=${taskId}, name=${taskName}, task_key=${taskKey}`)
          nodes.push({
            id: taskId,
            name: taskName,
            type: 'task',
            task_key: taskKey
          })
        }
        
        activeProcessDefinition.value = {
          id: activeDef.id,
          version: activeDef.version,
          name: activeDef.name,
          nodes: nodes
        }
        console.log('获取到当前启用流程定义:', activeProcessDefinition.value)
      }
    }
  } catch (error) {
    console.warn('获取当前启用流程定义失败:', error)
  }
}

// 组件挂载时获取当前启用的流程定义
onMounted(() => {
  if (!props.processDefinitionId) {
    fetchActiveProcessDefinition()
  }
})

const flowSteps = computed(() => {
  if (!props.workflowHistory && !props.processDefinitionId && !activeProcessDefinition.value) {
    return []
  }

  const flowStepDefinitions = getFlowStepDefinitions()
  const steps = []

  flowStepDefinitions.forEach(stepDef => {
    // 查找对应的工作流历史记录
    const historyItem = props.workflowHistory?.find(item => item.task_key === stepDef.code)
    
    let status = 'wait'
    if (stepDef.code === 'start') {
      status = 'finish'
    } else if (stepDef.code === 'end') {
      // 结束节点的状态：检查实际经过的节点是否都完成了
      // 只检查有历史记录的节点（跳过的节点不检查）
      const nodesWithHistory = steps.filter(s => s.code !== 'start' && s.code !== 'end' && 
        props.workflowHistory?.some(item => item.task_key === s.code))
      const allFinishedNodes = nodesWithHistory.every(s => s.status === 'finish')
      // 如果有实际经过的节点且都完成了，则结束节点也完成
      status = nodesWithHistory.length > 0 && allFinishedNodes ? 'finish' : 'wait'
    } else if (historyItem) {
      // 检查该节点是否有已完成记录
      const nodeHistoryItems = props.workflowHistory?.filter(item => item.task_key === stepDef.code)
      const hasCompleted = nodeHistoryItems.some(item => item.status === '已完成')
      // 只有当节点有已完成记录时，才显示为完成状态
      // 如果只有暂存或待处理记录，则显示为等待状态
      status = hasCompleted ? 'finish' : 'wait'
    }

    steps.push({
      title: stepDef.title,
      description: stepDef.description,
      code: stepDef.code,
      status: status
    })
  })

  return steps
})

// 按照单行布局组织节点：所有6个节点在一行显示
const flowRows = computed(() => {
  if (flowSteps.value.length === 0) return []

  const rows = []
  // 所有节点放在一行
  rows.push(flowSteps.value)

  return rows
})

// 检查一行是否所有节点都已完成
const isRowAllFinished = (row) => {
  return row && row.length > 0 && row.every(step => step.status === 'finish')
}

// 检查两个节点之间的连线状态
const getConnectionStatus = (currentStep, nextStep) => {
  if (currentStep.status === 'finish' && nextStep.status === 'finish') {
    return 'finished'
  }
  return 'pending'
}

// 检查节点是否有多次操作
const hasMultipleOperations = (taskKey) => {
  if (!taskKey || taskKey === 'start' || taskKey === 'end') return false
  
  // 获取该节点的所有记录
  const nodeHistory = props.workflowHistory.filter(item => item.task_key === taskKey)
  
  // 如果该节点只有"已撤回"记录，说明这是被撤回的节点，不显示徽章
  if (nodeHistory.length > 0 && nodeHistory.every(item => item.status === '已撤回')) {
    return false
  }
  
  // 获取该节点的记录数量（排除"已撤回"记录）
  const nodeCount = nodeHistory.filter(item => item.status !== '已撤回').length
  
  // 获取从该节点撤回的记录数量（下一个节点的"已撤回"记录）
  const withdrawnCount = props.workflowHistory.filter(item => 
    item.status === '已撤回' && isWithdrawnFromCurrentNode(taskKey, item.task_key)
  ).length
  
  return (nodeCount + withdrawnCount) > 1
}

// 获取节点的操作次数
const getNodeOperationCount = (taskKey) => {
  if (!taskKey || taskKey === 'start' || taskKey === 'end') return 0
  
  // 获取该节点的所有记录
  const nodeHistory = props.workflowHistory.filter(item => item.task_key === taskKey)
  
  // 如果该节点只有"已撤回"记录，说明这是被撤回的节点，返回0
  if (nodeHistory.length > 0 && nodeHistory.every(item => item.status === '已撤回')) {
    return 0
  }
  
  // 获取该节点的记录数量（排除"已撤回"记录）
  const nodeCount = nodeHistory.filter(item => item.status !== '已撤回').length
  
  // 获取从该节点撤回的记录数量（下一个节点的"已撤回"记录）
  const withdrawnCount = props.workflowHistory.filter(item => 
    item.status === '已撤回' && isWithdrawnFromCurrentNode(taskKey, item.task_key)
  ).length
  
  return nodeCount + withdrawnCount
}

// 检查撤回记录是否应该显示在当前节点（即当前节点是撤回发起的节点）
const isWithdrawnFromCurrentNode = (currentTaskKey, withdrawnTaskKey) => {
  // 定义节点顺序
  const nodeOrder = ['manager_identification', 'branch_review', 'first_approval', 'final_review']
  const currentIndex = nodeOrder.indexOf(currentTaskKey)
  const withdrawnIndex = nodeOrder.indexOf(withdrawnTaskKey)
  // 撤回的记录应该是下一个节点的"已撤回"状态，表示从当前节点撤回的
  return withdrawnIndex === currentIndex + 1
}

// 检查节点是否只有一次操作且已完成
const hasSingleOperation = (taskKey) => {
  if (!taskKey || taskKey === 'start' || taskKey === 'end') return false
  
  const nodeHistory = props.workflowHistory.filter(item => item.task_key === taskKey)
  
  // 如果该节点只有"已撤回"记录，说明这是被撤回的节点，不显示办理完成信息
  if (nodeHistory.length > 0 && nodeHistory.every(item => item.status === '已撤回')) {
    return false
  }
  
  // 获取该节点的记录数量（排除"已撤回"记录）
  const nodeCount = nodeHistory.filter(item => item.status !== '已撤回').length
  const withdrawnCount = props.workflowHistory.filter(item => 
    item.status === '已撤回' && isWithdrawnFromCurrentNode(taskKey, item.task_key)
  ).length
  
  // 只有当节点有1条记录且状态为"已完成"，且没有撤回记录时才显示办理完成信息
  return nodeCount === 1 && nodeHistory.filter(item => item.status === '已完成').length === 1 && withdrawnCount === 0
}

// 获取单次操作的信息
const getSingleOperation = (taskKey) => {
  if (!taskKey || taskKey === 'start' || taskKey === 'end') return null
  
  const nodeHistory = props.workflowHistory.filter(item => item.task_key === taskKey)
  
  // 如果该节点只有"已撤回"记录，说明这是被撤回的节点，不显示单次操作信息
  if (nodeHistory.length > 0 && nodeHistory.every(item => item.status === '已撤回')) {
    return null
  }
  
  const withdrawnCount = props.workflowHistory.filter(item => 
    item.status === '已撤回' && isWithdrawnFromCurrentNode(taskKey, item.task_key)
  ).length
  
  // 如果有撤回记录，不显示单次操作信息
  if (withdrawnCount > 0) return null
  
  // 返回该节点的第一条非"已撤回"记录
  const nonWithdrawnHistory = nodeHistory.filter(item => item.status !== '已撤回')
  return nonWithdrawnHistory.length > 0 ? nonWithdrawnHistory[0] : null
}

// 点击节点查看详细操作记录
const handleNodeClick = (taskKey) => {
  if (!hasMultipleOperations(taskKey)) return
  
  // 获取该节点的所有记录
  const nodeHistory = props.workflowHistory.filter(item => item.task_key === taskKey)
  
  // 如果该节点只有"已撤回"记录，说明这是被撤回的节点，不允许点击
  if (nodeHistory.length > 0 && nodeHistory.every(item => item.status === '已撤回')) {
    return
  }
  
  // 获取该节点的记录（排除"已撤回"记录）
  const nonWithdrawnHistory = nodeHistory.filter(item => item.status !== '已撤回')
  
  // 获取从该节点撤回的记录（下一个节点的"已撤回"记录）
  const withdrawnHistory = props.workflowHistory.filter(item => 
    item.status === '已撤回' && isWithdrawnFromCurrentNode(taskKey, item.task_key)
  )
  
  // 合并所有记录并按时间正序排列（最早的在前）
  const allHistory = [...nonWithdrawnHistory, ...withdrawnHistory].sort((a, b) => {
    const timeA = new Date(a.started_at || a.completed_at).getTime()
    const timeB = new Date(b.started_at || b.completed_at).getTime()
    return timeA - timeB
  })
  
  currentNodeHistory.value = allHistory
  nodeHistoryDialogVisible.value = true
}

const formatDateTime = (value) => {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const getTimelineType = (status) => {
  if (status === '已完成') return 'success'
  if (status === '待处理') return 'primary'
  if (status === '已撤回') return 'info'
  return 'warning'
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
</script>

<style scoped>
.flow-chart-container {
  padding: 40px 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  border-radius: 12px;
  overflow: visible;
}

.flow-chart {
  padding: 32px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  position: relative;
  width: 100%;
  min-height: 150px;
}

.flow-rows {
  display: flex;
  flex-direction: column;
  gap: 80px;
  position: relative;
  min-width: fit-content;
}

.flow-row {
  display: flex;
  justify-content: space-between;
  gap: 0;
  position: relative;
  flex-wrap: nowrap;
  width: 100%;
  padding: 0;
}

/* 第一行左对齐 */
.flow-row:nth-child(1) {
  justify-content: space-between;
}

.flow-row::after {
  display: none;
}

.flow-row.row-all-finished::after {
  display: none;
}

.flow-node {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  min-width: 0;
  max-width: none;
  z-index: 1;
  margin: 0;
  flex: 1;
}

.flow-node.node-clickable {
  cursor: pointer;
}

.flow-node.node-clickable:hover {
  transform: scale(1.05);
}

/* 节点之间的连接线 */
.connection-line {
  position: absolute;
  top: 32px;
  left: calc(100% - 40px);
  width: calc(50% + 30px);
  height: 2px;
  z-index: 0;
  background: #e0e6ed;
}

.connection-line.finished {
  background: #67C23A;
}

.flow-node-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: linear-gradient(135deg, #e0e6ed 0%, #cfd8dc 100%);
  color: #909399;
  margin-bottom: 8px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid #e0e6ed;
  position: relative;
  flex-shrink: 0;
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
  border: 2px solid #67C23A;
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
  text-align: center;
  width: 100%;
}

.flow-node-info {
  font-size: 12px;
  color: #606266;
  line-height: 1.4;
  text-align: center;
  width: 100%;
  margin-top: 4px;
  padding: 2px 4px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  border-radius: 4px;
  font-weight: 500;
}

.flow-node-desc {
  font-size: 12px;
  color: #7f8c8d;
  line-height: 1.4;
}

.node-history-dialog {
  border-radius: 16px;
  overflow: hidden;
}

.node-history-content {
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
}

.history-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.history-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ecf0f1;
}

.history-title {
  font-weight: 700;
  font-size: 14px;
  color: #667eea;
}

.history-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.history-result,
.history-comment,
.history-reason {
  font-size: 13px;
  color: #2c3e50;
  margin-top: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  padding: 16px 24px;
  background: #fafbfc;
  border-top: 1px solid #ecf0f1;
}
</style>