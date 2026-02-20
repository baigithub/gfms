<template>
  <div class="log-operation-container">
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="操作人账号">
              <el-input v-model="searchForm.operator_account" placeholder="请输入操作人账号" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="操作菜单">
              <el-input v-model="searchForm.operation_menu" placeholder="请输入操作菜单" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="开始时间">
              <el-date-picker
                v-model="searchForm.start_time"
                type="datetime"
                placeholder="选择开始时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                clearable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="结束时间">
              <el-date-picker
                v-model="searchForm.end_time"
                type="datetime"
                placeholder="选择结束时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                clearable
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="24" class="button-group">
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
            <el-button 
              type="danger" 
              @click="handleBatchDelete" 
              :disabled="selectedIds.length === 0"
            >
              <el-icon><Delete /></el-icon>
              批量删除
            </el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table
        :data="tableData"
        border
        stripe
        @selection-change="handleSelectionChange"
        v-loading="loading"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="operation_time" label="操作时间" width="180" align="center" />
        <el-table-column prop="operator_name" label="操作人姓名" width="120" align="center" />
        <el-table-column prop="operator_account" label="操作人账号" width="120" align="center" />
        <el-table-column prop="operation_menu" label="操作菜单" width="150" align="center" />
        <el-table-column prop="request_url" label="请求接口" width="200" show-overflow-tooltip />
        <el-table-column prop="request_duration" label="请求耗时" width="100" align="center">
          <template #default="{ row }">
            <span class="duration-text">{{ row.request_duration ? row.request_duration.toFixed(3) + '秒' : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="120" align="center" />
        <el-table-column prop="status_code" label="状态码" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status_code === 200 ? 'success' : 'danger'">
              {{ row.status_code }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="handleDelete(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Delete } from '@element-plus/icons-vue'
import { getOperationLogs, deleteOperationLog, batchDeleteOperationLogs } from '@/api/log'

const loading = ref(false)
const tableData = ref([])
const selectedIds = ref([])

const searchForm = reactive({
  operator_account: '',
  operation_menu: '',
  start_time: '',
  end_time: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 获取操作日志列表
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    const response = await getOperationLogs(params)
    tableData.value = response.data
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('获取操作日志失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 查询
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchForm.operator_account = ''
  searchForm.operation_menu = ''
  searchForm.start_time = ''
  searchForm.end_time = ''
  pagination.page = 1
  fetchData()
}

// 删除单条
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条日志吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteOperationLog(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.length} 条日志吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await batchDeleteOperationLogs(selectedIds.value)
    ElMessage.success('批量删除成功')
    selectedIds.value = []
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除失败')
      console.error(error)
    }
  }
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedIds.value = selection.map(item => item.id)
}

// 分页变化
const handlePageChange = (page) => {
  pagination.page = page
  fetchData()
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  pagination.page = 1
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.log-operation-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.search-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.search-form {
  padding: 8px 0;
}

.search-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.search-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.button-group {
  text-align: right;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
  margin-top: 8px;
}

.button-group .el-button {
  margin-left: 8px;
}

.button-group .el-button:first-child {
  margin-left: 0;
}

.table-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.table-card :deep(.el-card__body) {
  padding: 0;
}

:deep(.el-table) {
  border-radius: 8px;
}

:deep(.el-table__header th) {
  background: #fafafa;
  color: #303133;
  font-weight: 600;
  font-size: 14px;
  padding: 14px 12px;
}

:deep(.el-table__body tr) {
  transition: background-color 0.2s;
}

:deep(.el-table__body tr:hover) {
  background-color: #f5f7fa;
}

:deep(.el-table__body td) {
  padding: 14px 12px;
  font-size: 14px;
  color: #606266;
}

.duration-text {
  font-family: 'Courier New', monospace;
  font-weight: 500;
  color: #409eff;
}

:deep(.el-tag) {
  padding: 4px 10px;
  font-weight: 500;
  font-size: 13px;
  border-radius: 4px;
}

.pagination {
  margin-top: 16px;
  padding: 16px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
  background-color: #409eff;
  color: white;
}
</style>