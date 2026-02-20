<template>
  <div class="system-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span class="card-title">机构管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增机构
          </el-button>
        </div>
      </template>
      
      <!-- 查询表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="机构名称">
          <el-input v-model="searchForm.name" placeholder="请输入机构名称" clearable />
        </el-form-item>
        <el-form-item label="机构代码">
          <el-input v-model="searchForm.code" placeholder="请输入机构代码" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" v-loading="loading" stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="机构名称" width="200" />
        <el-table-column prop="code" label="机构代码" width="120" />
        <el-table-column prop="level" label="机构层级" width="120">
          <template #default="{ row }">
            {{ row.level }} ({{ getLevelName(row.level) }})
          </template>
        </el-table-column>
        <el-table-column label="分级机构名称" width="150">
          <template #default="{ row }">
            {{ getParentOrgName(row.parent_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" min-width="200" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- 机构编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="orgForm" :rules="rules" ref="orgFormRef" label-width="100px">
        <el-form-item label="机构名称" prop="name">
          <el-input v-model="orgForm.name" />
        </el-form-item>
        <el-form-item label="机构代码" prop="code">
          <el-input v-model="orgForm.code" />
        </el-form-item>
        <el-form-item label="上级机构" prop="parent_id">
          <el-tree-select
            v-model="orgForm.parent_id"
            :data="orgTreeData"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="请选择上级机构"
            check-strictly
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="级别" prop="level">
          <el-select v-model="orgForm.level" placeholder="请选择级别" style="width: 100%">
            <el-option label="总行" :value="1" />
            <el-option label="分行" :value="2" />
            <el-option label="支行" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="orgForm.address" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="orgForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getOrganizations, createOrganization, updateOrganization, deleteOrganization } from '@/api/system'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const orgTreeData = ref([])
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const searchForm = reactive({
  name: '',
  code: ''
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增机构')
const isEdit = ref(false)
const orgFormRef = ref(null)

const orgForm = reactive({
  name: '',
  code: '',
  parent_id: null,
  level: 1,
  address: '',
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入机构名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入机构代码', trigger: 'blur' }],
  level: [{ required: true, message: '请选择级别', trigger: 'change' }]
}

const getLevelName = (level) => {
  const levelMap = {
    1: '总行',
    2: '分行',
    3: '支行'
  }
  return levelMap[level] || '-'
}

const getParentOrgName = (parentId) => {
  if (!parentId) return '-'
  const parent = tableData.value.find(o => o.id === parentId)
  return parent ? parent.name : '-'
}

const formatDateTime = (value) => {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const buildTreeData = (orgs) => {
  const map = {}
  const roots = []
  
  orgs.forEach(org => {
    map[org.id] = { ...org, children: [] }
  })
  
  orgs.forEach(org => {
    const node = map[org.id]
    if (org.parent_id && map[org.parent_id]) {
      map[org.parent_id].children.push(node)
    } else {
      roots.push(node)
    }
  })
  
  return roots
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (searchForm.name) {
      params.name = searchForm.name
    }
    if (searchForm.code) {
      params.code = searchForm.code
    }
    const res = await getOrganizations(params)
    tableData.value = res.data || []
    pagination.total = res.total || 0
    // 构建树形数据时需要全部数据
    if (searchForm.name === '' && searchForm.code === '') {
      const allOrgs = await getOrganizations({ page: 1, page_size: 1000 })
      orgTreeData.value = buildTreeData(allOrgs.data || [])
    }
  } catch (error) {
    console.error('Failed to load organizations:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadData()
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.code = ''
  loadData()
}

const handleAdd = () => {
  dialogTitle.value = '新增机构'
  isEdit.value = false
  Object.assign(orgForm, {
    name: '',
    code: '',
    parent_id: null,
    level: 1,
    address: '',
    is_active: true
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑机构'
  isEdit.value = true
  Object.assign(orgForm, {
    id: row.id,
    name: row.name,
    code: row.code,
    parent_id: row.parent_id,
    level: row.level,
    address: row.address,
    is_active: row.is_active
  })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除机构 "${row.name}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteOrganization(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const handleSubmit = async () => {
  if (!orgFormRef.value) return
  
  await orgFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await updateOrganization(orgForm.id, orgForm)
          ElMessage.success('更新成功')
        } else {
          await createOrganization(orgForm)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.search-form {
  margin-bottom: 20px;
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
</style>