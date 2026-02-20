<template>
  <div class="log-exception-container">
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="异常模块">
              <el-input v-model="searchForm.exception_module" placeholder="请输入异常模块" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-form-item label="解决状态">
              <el-select v-model="searchForm.is_resolved" placeholder="请选择解决状态" clearable style="width: 100%">
                <el-option label="未解决" :value="0" />
                <el-option label="已解决" :value="1" />
              </el-select>
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
        <el-table-column prop="exception_time" label="发生时间" width="180" align="center" />
        <el-table-column prop="exception_module" label="异常模块" width="120" align="center" />
        <el-table-column prop="exception_interface" label="异常接口" width="200" show-overflow-tooltip />
        <el-table-column prop="exception_type" label="异常类型" width="150" show-overflow-tooltip />
        <el-table-column prop="exception_message" label="异常消息" width="200" show-overflow-tooltip />
        <el-table-column prop="user_name" label="用户姓名" width="100" align="center" />
        <el-table-column prop="user_account" label="用户账号" width="120" align="center" />
        <el-table-column prop="ip_address" label="IP地址" width="120" align="center" />
        <el-table-column prop="is_resolved" label="解决状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_resolved === 1 ? 'success' : 'warning'">
              {{ row.is_resolved === 1 ? '已解决' : '未解决' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleViewDetail(row)">
              查看详情
            </el-button>
            <el-button
              v-if="row.is_resolved === 0"
              type="success"
              size="small"
              @click="handleResolve(row)"
            >
              标记解决
            </el-button>
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

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="异常日志详情"
      width="800px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="异常模块">{{ currentDetail.exception_module }}</el-descriptions-item>
        <el-descriptions-item label="异常接口">{{ currentDetail.exception_interface }}</el-descriptions-item>
        <el-descriptions-item label="异常类型">{{ currentDetail.exception_type }}</el-descriptions-item>
        <el-descriptions-item label="异常消息">{{ currentDetail.exception_message }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">{{ currentDetail.request_method }}</el-descriptions-item>
        <el-descriptions-item label="请求URL">{{ currentDetail.request_url }}</el-descriptions-item>
        <el-descriptions-item label="用户姓名">{{ currentDetail.user_name }}</el-descriptions-item>
        <el-descriptions-item label="用户账号">{{ currentDetail.user_account }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentDetail.ip_address }}</el-descriptions-item>
        <el-descriptions-item label="发生时间">{{ currentDetail.exception_time }}</el-descriptions-item>
        <el-descriptions-item label="解决状态">
          <el-tag :type="currentDetail.is_resolved === 1 ? 'success' : 'warning'">
            {{ currentDetail.is_resolved === 1 ? '已解决' : '未解决' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="解决时间">{{ currentDetail.resolved_time || '-' }}</el-descriptions-item>
        <el-descriptions-item label="堆栈信息" :span="2">
          <el-input
            v-model="currentDetail.stack_trace"
            type="textarea"
            :rows="10"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item label="请求参数" :span="2">
          <el-input
            v-model="currentDetail.request_params"
            type="textarea"
            :rows="5"
            readonly
          />
        </el-descriptions-item>
        <el-descriptions-item label="解决备注" :span="2">
          {{ currentDetail.resolved_note || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 标记解决对话框 -->
    <el-dialog
      v-model="resolveDialogVisible"
      title="标记异常为已解决"
      width="500px"
    >
      <el-form :model="resolveForm" label-width="100px">
        <el-form-item label="解决备注">
          <el-input
            v-model="resolveForm.resolved_note"
            type="textarea"
            :rows="4"
            placeholder="请输入解决备注（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmResolve">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Delete } from '@element-plus/icons-vue'
import { getExceptionLogs, getExceptionLogDetail, deleteExceptionLog, batchDeleteExceptionLogs, resolveExceptionLog } from '@/api/log'
import { useAuthStore } from '@/store/auth'

const loading = ref(false)
const tableData = ref([])
const selectedIds = ref([])
const detailDialogVisible = ref(false)
const resolveDialogVisible = ref(false)
const currentDetail = ref({})
const currentResolveId = ref(null)

const authStore = useAuthStore()

const searchForm = reactive({
  exception_module: '',
  is_resolved: null,
  start_time: '',
  end_time: ''
})

const resolveForm = reactive({
  resolved_note: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 获取异常日志列表
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    const response = await getExceptionLogs(params)
    tableData.value = response.data
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('获取异常日志失败')
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
  searchForm.exception_module = ''
  searchForm.is_resolved = null
  searchForm.start_time = ''
  searchForm.end_time = ''
  pagination.page = 1
  fetchData()
}

// 查看详情
const handleViewDetail = async (row) => {
  try {
    const detail = await getExceptionLogDetail(row.id)
    currentDetail.value = detail
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
    console.error(error)
  }
}

// 标记解决
const handleResolve = (row) => {
  currentResolveId.value = row.id
  resolveForm.resolved_note = ''
  resolveDialogVisible.value = true
}

// 确认解决
const handleConfirmResolve = async () => {
  try {
    await resolveExceptionLog(currentResolveId.value, {
      resolved_note: resolveForm.resolved_note,
      current_user_id: authStore.user.id
    })
    ElMessage.success('标记成功')
    resolveDialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error('标记失败')
    console.error(error)
  }
}

// 删除单条
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条日志吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteExceptionLog(id)
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
    
    await batchDeleteExceptionLogs(selectedIds.value)
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
.log-exception-container {
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

:deep(.el-descriptions__label) {
  background: #fafafa;
  font-weight: 500;
  color: #606266;
}

:deep(.el-descriptions__content) {
  color: #606266;
}

:deep(.el-textarea__inner) {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
}
</style>