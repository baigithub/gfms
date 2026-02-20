<template>
  <div class="system-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">角色管理</span>
          <el-button type="primary" size="small" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增角色
          </el-button>
        </div>
      </template>
      
      <el-table :data="tableData" v-loading="loading" stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button v-if="!isSuperAdmin(row)" type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button v-if="!isSuperAdmin(row)" type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 查看/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
      :class="{ 'view-mode': dialogMode === 'view' }"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
        :disabled="dialogMode === 'view'"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        
        <el-form-item label="菜单权限" prop="permissions">
          <el-tree
            ref="permissionTreeRef"
            :data="menuTree"
            :props="treeProps"
            node-key="id"
            show-checkbox
            :key="formData.id || 'new'"
            :default-checked-keys="checkedPermissions"
            :default-expanded-keys="[1, 2, 3]"
            :default-expand-all="true"
            :check-strictly="dialogMode === 'view'"
            @check="handleCheckChange"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <span class="node-label">{{ node.label }}</span>
              </span>
            </template>
          </el-tree>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer" v-show="dialogMode !== 'view'">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </div>
        <div class="dialog-footer" v-show="dialogMode === 'view'">
          <el-button @click="dialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getRoles, getRoleDetail, updateRole, deleteRole } from '@/api/system'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogMode = ref('add') // add, edit, view
const dialogTitle = ref('')
const formRef = ref(null)
const permissionTreeRef = ref(null)

const formData = reactive({
  id: null,
  name: '',
  description: '',
  permissions: []
})

const checkedPermissions = ref([])

// 菜单权限树形数据
const menuTree = [
  {
    id: 1,
    label: '工作台',
    children: [
      { id: 'dashboard', label: '首页' }
    ]
  },
  {
    id: 2,
    label: '绿色认定',
    children: [
      { id: 'green-identify-pending', label: '待办任务' },
      { id: 'green-identify-completed', label: '已办任务' },
      { id: 'green-identify-archived', label: '办结任务' },
      { id: 'green-identify-query', label: '综合查询' }
    ]
  },
  {
    id: 3,
    label: '系统管理',
    children: [
      { id: 'system-user', label: '用户管理' },
      { id: 'system-role', label: '角色管理' },
      { id: 'system-org', label: '机构管理' }
    ]
  },
  {
    id: 4,
    label: '流程管理',
    children: [
      { id: 'workflow-management', label: '流程管理' },
      { id: 'workflow-instances', label: '流程实例' }
    ]
  }
]

const treeProps = {
  children: 'children',
  label: 'label'
}

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' }
  ]
}

const formatDateTime = (value) => {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-'
}

// 判断是否为超级管理员角色
const isSuperAdmin = (role) => {
  return role.name === '超级管理员'
}

// 获取所有菜单权限key
const getAllMenuKeys = () => {
  const allKeys = []
  menuTree.forEach(menu => {
    if (menu.children) {
      menu.children.forEach(child => {
        allKeys.push(child.id)
      })
    }
  })
  return allKeys
}

const handleCheckChange = (data, checkedInfo) => {
  if (dialogMode.value === 'view') {
    // 查看模式下，阻止勾选状态改变
    if (permissionTreeRef.value) {
      permissionTreeRef.value.setCheckedKeys(checkedPermissions.value)
    }
  }
}

const loadData = async () => {
  loading.value = true
  try {
    tableData.value = await getRoles()
  } catch (error) {
    console.error('Failed to load roles:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogMode.value = 'add'
  dialogTitle.value = '新增角色'
  resetForm()
  dialogVisible.value = true
}

const handleView = async (row) => {
  dialogMode.value = 'view'
  dialogTitle.value = '查看角色'
  try {
    // 先重置checkedPermissions
    checkedPermissions.value = []
    
    const role = await getRoleDetail(row.id)
    formData.id = role.id
    formData.name = role.name
    formData.description = role.description || ''
    
    // 如果是超级管理员，默认全部选中
    if (isSuperAdmin(role)) {
      checkedPermissions.value = getAllMenuKeys()
      formData.permissions = checkedPermissions.value
    } else {
      formData.permissions = role.permissions || []
      checkedPermissions.value = formData.permissions
    }
    
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取角色详情失败')
  }
}

const handleEdit = async (row) => {
  dialogMode.value = 'edit'
  dialogTitle.value = '编辑角色'
  try {
    // 先重置checkedPermissions
    checkedPermissions.value = []
    
    const role = await getRoleDetail(row.id)
    formData.id = role.id
    formData.name = role.name
    formData.description = role.description || ''
    formData.permissions = role.permissions || []
    
    // 设置选中的权限
    checkedPermissions.value = formData.permissions
    
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取角色详情失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除角色"${row.name}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 获取选中的权限（只获取叶子节点）
    const checkedKeys = permissionTreeRef.value.getCheckedKeys()
    // 过滤掉父节点（数字类型），只保留叶子节点（字符串类型）
    const leafKeys = checkedKeys.filter(key => typeof key === 'string')
    formData.permissions = leafKeys
    
    console.log('提交的权限:', formData.permissions)
    
    await updateRole(formData.id, formData)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存失败')
    }
  }
}

const resetForm = () => {
  formData.id = null
  formData.name = ''
  formData.description = ''
  formData.permissions = []
  checkedPermissions.value = []
  if (formRef.value) {
    formRef.value.resetFields()
  }
  // 重置树的选择状态
  if (permissionTreeRef.value) {
    permissionTreeRef.value.setCheckedKeys([])
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.system-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-tree) {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
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

:deep(.el-table td) {
  padding: 16px 12px;
  font-size: 14px;
  color: #2c3e50;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 8px;
}

.node-label {
  margin-left: 8px;
}

/* 查看模式下禁用勾选框 */
.view-mode :deep(.el-tree .el-checkbox) {
  pointer-events: none !important;
  cursor: not-allowed !important;
}

.view-mode :deep(.el-tree .el-checkbox__input) {
  pointer-events: none !important;
  cursor: not-allowed !important;
}

.view-mode :deep(.el-tree .el-checkbox__inner) {
  background-color: #edf2fc !important;
  border-color: #dcdfe6 !important;
  cursor: not-allowed !important;
}

.view-mode :deep(.el-tree .el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #a8abb2 !important;
  border-color: #a8abb2 !important;
}

.view-mode :deep(.el-tree .el-checkbox__input.is-checked .el-checkbox__inner::after) {
  border-color: #fff !important;
}
</style>