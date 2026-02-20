<template>
  <div class="workflow-management">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon" color="#667eea"><Operation /></el-icon>
            <span class="card-title">流程管理</span>
            <el-tag type="info" size="small">{{ definitions.length }} 个流程</el-tag>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="toDesigner">
              <el-icon><Plus /></el-icon>
              新建流程
            </el-button>
          </div>
        </div>
      </template>
      
      <el-collapse v-model="activeNames" accordion class="workflow-collapse">
        <el-collapse-item 
          v-for="group in groupedDefinitions" 
          :key="group.name"
          :name="group.name"
          class="collapse-item"
        >
          <template #title>
            <div class="group-title">
              <div class="group-icon">
                <el-icon><Management /></el-icon>
              </div>
              <div class="group-info">
                <span class="process-name">{{ group.name }}</span>
                <span class="process-count">{{ group.versions.length }} 个版本</span>
              </div>
            </div>
          </template>
          
          <el-table :data="group.versions" stripe class="workflow-table">
            <el-table-column prop="id" label="ID" width="80" align="center" />
            <el-table-column prop="key" label="流程键" width="180">
              <template #default="{ row }">
                <el-tag type="info" effect="plain" size="small">{{ row.key }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="流程名称" width="200">
              <template #default="{ row }">
                <div class="workflow-name">
                  <el-icon><FolderOpened /></el-icon>
                  {{ row.name }}
                </div>
              </template>
            </el-table-column>
            <el-table-column label="版本" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="primary" effect="plain" size="small">v{{ row.version }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" effect="plain">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="deployed_at" label="部署时间" width="180" align="center">
              <template #default="{ row }">
                <div class="date-value">{{ row.deployed_at }}</div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="300" fixed="right" align="center">
              <template #default="{ row }">
                <div class="action-buttons">
                  <el-button type="primary" link size="small" @click="viewWorkflow(row)">
                    <el-icon><View /></el-icon>
                    查看
                  </el-button>
                  <el-button type="primary" link size="small" @click="editWorkflow(row)">
                    <el-icon><Edit /></el-icon>
                    编辑
                  </el-button>
                  <el-button 
                    v-if="row.status === 'active'" 
                    type="warning" 
                    link 
                    size="small" 
                    @click="deactivateDefinition(row)"
                  >
                    <el-icon><VideoPause /></el-icon>
                    停用
                  </el-button>
                  <el-button 
                    v-if="row.status !== 'active'" 
                    type="success" 
                    link 
                    size="small" 
                    @click="activateDefinition(row)"
                  >
                    <el-icon><VideoPlay /></el-icon>
                    启用
                  </el-button>
                  <el-button type="danger" link size="small" @click="deleteWorkflow(row)">
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-collapse-item>
      </el-collapse>
    </el-card>
    
    <!-- 节点列表对话框 -->
    <el-dialog 
      v-model="nodesDialogVisible" 
      title="流程节点" 
      width="800px"
      class="nodes-dialog"
    >
      <el-table :data="nodes" stripe class="nodes-table">
        <el-table-column prop="sequence" label="顺序" width="80" align="center" />
        <el-table-column prop="node_id" label="节点ID" width="150">
          <template #default="{ row }">
            <el-tag type="info" effect="plain" size="small">{{ row.node_id }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="node_name" label="节点名称" width="200">
          <template #default="{ row }">
            <div class="node-name">
              <el-icon><ElementPlus /></el-icon>
              {{ row.node_name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="node_type" label="节点类型" width="120">
          <template #default="{ row }">
            <el-tag type="primary" effect="plain" size="small">{{ row.node_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_skip_if_empty" label="无人员跳过" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_skip_if_empty ? 'success' : 'danger'" effect="plain" size="small">
              {{ row.is_skip_if_empty ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Operation, 
  Plus, 
  Management, 
  FolderOpened, 
  View, 
  Edit, 
  VideoPause, 
  VideoPlay, 
  Delete,
  ElementPlus
} from '@element-plus/icons-vue'
import { getDefinitions, getTaskNodes, getDefinition, deleteDefinition, activate, deactivate } from '@/api/workflow'

const router = useRouter()

const definitions = ref([])
const groupedDefinitions = ref([])
const activeNames = ref([])
const nodes = ref([])
const nodesDialogVisible = ref(false)

const loadDefinitions = async () => {
  try {
    const res = await getDefinitions({ page: 1, page_size: 100 })
    definitions.value = res || []
    
    const groups = {}
    definitions.value.forEach(def => {
      if (!groups[def.name]) {
        groups[def.name] = {
          name: def.name,
          versions: []
        }
      }
      groups[def.name].versions.push(def)
    })
    
    groupedDefinitions.value = Object.values(groups).map(group => ({
      name: group.name,
      versions: group.versions.sort((a, b) => b.version - a.version)
    }))
    
    if (groupedDefinitions.value.length > 0) {
      activeNames.value = [groupedDefinitions.value[0].name]
    }
  } catch (error) {
    ElMessage.error('加载流程列表失败')
  }
}

const toDesigner = () => {
  router.push('/workflow/designer')
}

const viewWorkflow = (definition) => {
  router.push({
    path: '/workflow/designer',
    query: {
      mode: 'view',
      id: definition.id
    }
  })
}

const editWorkflow = async (definition) => {
  try {
    const detail = await getDefinition(definition.id)
    
    if (detail.instance_count && detail.instance_count > 0) {
      await ElMessageBox.confirm(
        `当前流程版本已绑定 ${detail.instance_count} 个流程实例，是否创建新版本？`,
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info',
          customClass: 'instance-bound-confirm'
        }
      )
      
      router.push({
        path: '/workflow/designer',
        query: {
          mode: 'new',
          copyFrom: definition.id
        }
      })
    } else {
      router.push({
        path: '/workflow/designer',
        query: {
          mode: 'edit',
          id: definition.id
        }
      })
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('获取流程定义详情失败')
    }
  }
}

const viewNodes = async (definition) => {
  try {
    const res = await getTaskNodes(definition.id)
    nodes.value = res || []
    nodesDialogVisible.value = true
  } catch (error) {
    ElMessage.error('加载节点列表失败')
  }
}

const deleteWorkflow = async (definition) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除流程 "${definition.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deleteDefinition(definition.id)
    ElMessage.success('流程删除成功')
    loadDefinitions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('流程删除失败')
    }
  }
}

const activateDefinition = async (definition) => {
  try {
    await ElMessageBox.confirm(
      `确定要启用流程 "${definition.name} v${definition.version}" 吗？这将停用同一名称下的其他启用版本。`,
      '启用确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    )
    
    await activate(definition.id)
    ElMessage.success('流程启用成功')
    loadDefinitions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('流程启用失败')
    }
  }
}

const deactivateDefinition = async (definition) => {
  try {
    await ElMessageBox.confirm(
      `确定要停用流程 "${definition.name} v${definition.version}" 吗？`,
      '停用确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await deactivate(definition.id)
    ElMessage.success('流程停用成功')
    loadDefinitions()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '流程停用失败')
    }
  }
}

const getStatusText = (status) => {
  const textMap = {
    'active': '已启用',
    'archived': '已停用'
  }
  return textMap[status] || status
}

onMounted(() => {
  loadDefinitions()
})
</script>

<style scoped>
.workflow-management {
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

.header-right :deep(.el-button) {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 8px;
}

.workflow-collapse {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.workflow-collapse .el-collapse-item) {
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
  transition: all 0.3s;
}

:deep(.workflow-collapse .el-collapse-item:hover) {
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

:deep(.workflow-collapse .el-collapse-item__header) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%);
  padding: 16px 20px;
  border-bottom: none;
  transition: all 0.3s;
}

:deep(.workflow-collapse .el-collapse-item__header:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
}

:deep(.workflow-collapse .el-collapse-item__wrap) {
  border-bottom: none;
  background: white;
}

:deep(.workflow-collapse .el-collapse-item__content) {
  padding: 0;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.group-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.group-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.process-name {
  font-weight: 600;
  font-size: 16px;
  color: #2c3e50;
}

.process-count {
  color: #7f8c8d;
  font-size: 13px;
}

.workflow-table {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.workflow-table) {
  border-radius: 12px;
}

:deep(.workflow-table thead) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%) !important;
  display: table-header-group !important;
  visibility: visible !important;
}

:deep(.workflow-table th) {
  background: transparent !important;
  color: #303133 !important;
  font-weight: 600;
  font-size: 14px;
  padding: 16px 12px;
  display: table-cell !important;
  visibility: visible !important;
}

:deep(.workflow-table th .cell) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

:deep(.workflow-table tr:hover > td) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%) !important;
}

:deep(.workflow-table td) {
  padding: 16px 12px;
  font-size: 14px;
  color: #2c3e50;
}

.workflow-name,
.node-name {
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
  flex-wrap: wrap;
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

:deep(.el-button--warning.is-link) {
  color: #FF9800;
  font-weight: 500;
}

:deep(.el-button--warning.is-link:hover) {
  color: #F57C00;
}

:deep(.el-button--success.is-link) {
  color: #4CAF50;
  font-weight: 500;
}

:deep(.el-button--success.is-link:hover) {
  color: #388E3C;
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

:deep(.el-tag--info) {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
  color: #7f8c8d;
}

/* 对话框样式 */
:deep(.nodes-dialog) {
  border-radius: 16px;
}

:deep(.nodes-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.nodes-dialog .el-dialog__body) {
  padding: 24px;
}

.nodes-table {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.nodes-table thead) {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%) !important;
  display: table-header-group !important;
  visibility: visible !important;
}

:deep(.nodes-table th) {
  background: transparent !important;
  color: #303133 !important;
  font-weight: 600;
  font-size: 14px;
  padding: 16px 12px;
  display: table-cell !important;
  visibility: visible !important;
}

:deep(.nodes-table th .cell) {
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

:deep(.nodes-table td) {
  padding: 16px 12px;
  color: #2c3e50;
}
</style>

<style>
.instance-bound-confirm {
  border: 2px solid #667eea;
  border-radius: 16px;
}

.instance-bound-confirm .el-message-box__header {
  padding: 24px 24px 16px;
  display: flex;
  align-items: center;
}

.instance-bound-confirm .el-message-box__title {
  color: #667eea;
  font-weight: 600;
  font-size: 18px;
}

.instance-bound-confirm .el-message-box__status {
  color: #667eea;
  font-size: 28px;
  margin-right: 12px;
}

.instance-bound-confirm .el-message-box__message {
  padding: 20px 24px;
  color: #2c3e50;
  font-size: 15px;
  line-height: 1.6;
}

.instance-bound-confirm .el-message-box__btns {
  padding: 16px 24px 24px;
}

.instance-bound-confirm .el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 600;
}

.instance-bound-confirm .el-button--primary:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}
</style>