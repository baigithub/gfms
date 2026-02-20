<template>
  <div class="workflow-variables">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon" color="#667eea"><Key /></el-icon>
            <span class="card-title">流程变量管理</span>
            <el-tag type="info" size="small">{{ variables.length }} 个变量</el-tag>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新建变量
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="search-form-container">
        <el-form :inline="true" :model="queryForm" class="search-form">
          <el-form-item label="流程类型">
            <el-select 
              v-model="queryForm.workflowType" 
              placeholder="请选择流程类型" 
              clearable 
              class="modern-input"
              @change="loadVariables"
            >
              <el-option 
                v-for="definition in definitions" 
                :key="definition.id" 
                :label="definition.name" 
                :value="definition.id" 
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <el-table 
        :data="variables" 
        stripe 
        v-loading="loading"
        class="modern-table"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="definition_name" label="流程类型" width="200">
          <template #default="{ row }">
            <div class="workflow-name">
              <el-icon><FolderOpened /></el-icon>
              {{ row.definition_name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="variable_name" label="变量名称" width="180">
          <template #default="{ row }">
            <div class="variable-name">
              <el-icon><Edit /></el-icon>
              {{ row.variable_name }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="variable_key" label="变量键" width="180">
          <template #default="{ row }">
            <el-tag type="info" effect="plain" size="small">{{ row.variable_key }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="variable_type" label="变量类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.variable_type)" effect="plain" size="small">
              {{ getTypeText(row.variable_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="default_value" label="默认值" width="150">
          <template #default="{ row }">
            <div class="default-value">{{ row.default_value || '-' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="required" label="必填" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.required ? 'success' : 'info'" effect="plain" size="small">
              {{ row.required ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" link size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!loading && variables.length === 0" description="暂无流程变量" />
    </el-card>
    
    <!-- 新建/编辑变量对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogMode === 'add' ? '新建流程变量' : '编辑流程变量'" 
      width="600px"
      class="variable-dialog"
    >
      <el-form 
        :model="variableForm" 
        :rules="rules" 
        ref="variableFormRef" 
        label-width="100px"
        class="variable-form"
      >
        <el-form-item label="流程类型" prop="definition_id">
          <el-select 
            v-model="variableForm.definition_id" 
            placeholder="请选择流程类型" 
            class="modern-input"
          >
            <el-option 
              v-for="definition in definitions" 
              :key="definition.id" 
              :label="definition.name" 
              :value="definition.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="变量名称" prop="variable_name">
          <el-input 
            v-model="variableForm.variable_name" 
            placeholder="请输入变量名称"
            class="modern-input"
          >
            <template #prefix>
              <el-icon><Edit /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="变量键" prop="variable_key">
          <el-input 
            v-model="variableForm.variable_key" 
            placeholder="请输入变量键（英文）"
            class="modern-input"
          >
            <template #prefix>
              <el-icon><Key /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="变量类型" prop="variable_type">
          <el-select 
            v-model="variableForm.variable_type" 
            placeholder="请选择变量类型" 
            class="modern-input"
          >
            <el-option label="字符串" value="string" />
            <el-option label="数字" value="number" />
            <el-option label="布尔值" value="boolean" />
            <el-option label="数组" value="array" />
            <el-option label="对象" value="object" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="默认值" prop="default_value">
          <el-input 
            v-model="variableForm.default_value" 
            placeholder="请输入默认值"
            class="modern-input"
          >
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="variableForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入变量描述"
            class="modern-input"
          />
        </el-form-item>
        
        <el-form-item label="必填">
          <el-switch v-model="variableForm.required" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Key, 
  Plus, 
  FolderOpened, 
  Edit, 
  Delete, 
  Document 
} from '@element-plus/icons-vue'
import { getDefinitions } from '@/api/workflow'
import { getVariables, createVariable, updateVariable, deleteVariable } from '@/api/workflowVariables'

const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('add')
const variableFormRef = ref(null)

const definitions = ref([])
const variables = ref([])

const queryForm = reactive({
  workflowType: ''
})

const variableForm = reactive({
  definition_id: '',
  variable_name: '',
  variable_key: '',
  variable_type: 'string',
  default_value: '',
  description: '',
  required: false
})

const rules = {
  definition_id: [{ required: true, message: '请选择流程类型', trigger: 'change' }],
  variable_name: [{ required: true, message: '请输入变量名称', trigger: 'blur' }],
  variable_key: [
    { required: true, message: '请输入变量键', trigger: 'blur' },
    { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '变量键只能包含字母、数字和下划线，且必须以字母或下划线开头', trigger: 'blur' }
  ],
  variable_type: [{ required: true, message: '请选择变量类型', trigger: 'change' }]
}

const loadDefinitions = async () => {
  try {
    const res = await getDefinitions({ page: 1, page_size: 100 })
    const definitionMap = new Map()
    if (res && res.length > 0) {
      res.forEach(def => {
        if (!definitionMap.has(def.name) || def.version > definitionMap.get(def.name).version) {
          definitionMap.set(def.name, def)
        }
      })
      definitions.value = Array.from(definitionMap.values())
    } else {
      definitions.value = []
    }
  } catch (error) {
    console.error('加载流程定义失败:', error)
  }
}

const loadVariables = async () => {
  loading.value = true
  try {
    const params = {}
    if (queryForm.workflowType) {
      params.definition_id = queryForm.workflowType
    }
    const res = await getVariables(params)
    variables.value = res || []
  } catch (error) {
    console.error('加载流程变量失败:', error)
    ElMessage.error('加载流程变量失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogMode.value = 'add'
  Object.assign(variableForm, {
    definition_id: queryForm.workflowType || '',
    variable_name: '',
    variable_key: '',
    variable_type: 'string',
    default_value: '',
    description: '',
    required: false
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogMode.value = 'edit'
  Object.assign(variableForm, {
    id: row.id,
    definition_id: row.definition_id,
    variable_name: row.variable_name,
    variable_key: row.variable_key,
    variable_type: row.variable_type,
    default_value: row.default_value,
    description: row.description,
    required: row.required
  })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该流程变量吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteVariable(row.id)
      ElMessage.success('删除成功')
      loadVariables()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  try {
    await variableFormRef.value.validate()
    
    const data = { ...variableForm }
    if (dialogMode.value === 'edit') {
      await updateVariable(data.id, data)
      ElMessage.success('更新成功')
    } else {
      await createVariable(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadVariables()
  } catch (error) {
    if (error !== false) {
      console.error('提交失败:', error)
      ElMessage.error('提交失败')
    }
  }
}

const getTypeText = (type) => {
  const typeMap = {
    string: '字符串',
    number: '数字',
    boolean: '布尔值',
    array: '数组',
    object: '对象'
  }
  return typeMap[type] || type
}

const getTypeColor = (type) => {
  const colorMap = {
    string: 'primary',
    number: 'success',
    boolean: 'warning',
    array: 'info',
    object: 'danger'
  }
  return colorMap[type] || ''
}

onMounted(() => {
  loadDefinitions()
  loadVariables()
})
</script>

<style scoped>
.workflow-variables {
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

.search-form-container {
  margin-bottom: 24px;
  padding: 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
}

.search-form {
  display: flex;
  gap: 16px;
}

:deep(.search-form .el-form-item) {
  margin-bottom: 0;
}

.modern-input {
  width: 200px;
}

:deep(.modern-input .el-input__wrapper) {
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

:deep(.modern-input .el-input__wrapper:hover) {
  border-color: #667eea;
}

:deep(.modern-input .el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

:deep(.modern-input .el-select .el-input__wrapper) {
  cursor: pointer;
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

.workflow-name,
.variable-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.default-value {
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
:deep(.variable-dialog) {
  border-radius: 16px;
}

:deep(.variable-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.variable-dialog .el-dialog__body) {
  padding: 24px;
}

.variable-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #2c3e50;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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