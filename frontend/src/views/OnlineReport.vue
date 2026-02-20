<template>
  <div class="online-report-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon" color="#667eea"><DataAnalysis /></el-icon>
            <span class="card-title">在线报表</span>
            <el-tag type="info" size="small">{{ pagination.total }} 条记录</el-tag>
          </div>
          <div class="header-right">
            <el-button @click="loadData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
            <el-button type="success" @click="exportExcel">
              <el-icon><Download /></el-icon>
              导出报表
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 查询条件 -->
      <div class="filter-bar">
        <el-form :inline="true" :model="searchForm" size="small">
          <el-form-item label="一级分行">
            <el-input v-model="searchForm.level1_branch" placeholder="请输入" clearable style="width: 150px" />
          </el-form-item>
          <el-form-item label="二级分行">
            <el-input v-model="searchForm.level2_branch" placeholder="请输入" clearable style="width: 150px" />
          </el-form-item>
          <el-form-item label="支行">
            <el-input v-model="searchForm.branch" placeholder="请输入" clearable style="width: 150px" />
          </el-form-item>
          <el-form-item label="贷款账号">
            <el-input v-model="searchForm.loan_account" placeholder="请输入" clearable style="width: 150px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon><RefreshRight /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 在线Excel容器 -->
      <div id="luckysheet" class="luckysheet-container"></div>
      
      <!-- 分页 -->
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[20, 50, 100, 200, 500, 1000]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          small
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download, DataAnalysis, RefreshRight } from '@element-plus/icons-vue'
import { getOnlineReport } from '@/api/green_finance'
import * as XLSX from 'xlsx'
import luckysheet from 'luckysheet'
import 'luckysheet/dist/css/luckysheet.css'
import 'luckysheet/dist/plugins/plugins.css'

const loading = ref(false)
const tableData = ref([])
const searchForm = reactive({
  level1_branch: '',
  level2_branch: '',
  branch: '',
  loan_account: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

let luckysheetInstance = null

// 获取报表数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    if (searchForm.level1_branch) params.level1_branch = searchForm.level1_branch
    if (searchForm.level2_branch) params.level2_branch = searchForm.level2_branch
    if (searchForm.branch) params.branch = searchForm.branch
    if (searchForm.loan_account) params.loan_account = searchForm.loan_account
    
    const response = await getOnlineReport(params)
    tableData.value = response.data
    pagination.total = response.total
    await nextTick()
    renderExcel(response.data)
  } catch (error) {
    ElMessage.error('获取报表数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 渲染Excel数据
const renderExcel = (data) => {
  if (!data || data.length === 0) {
    ElMessage.warning('暂无数据')
    return
  }
  
  if (luckysheetInstance) {
    try {
      luckysheet.destroy()
    } catch (e) {
      console.warn('销毁luckysheet实例失败:', e)
    }
    luckysheetInstance = null
  }
  
  // 准备表头 - 使用简单字符串格式
  const headerRow = [
    '序号', '一级分行', '二级分行', '支行', '贷款账号', '放款金额(万元)',
    '绿色大类', '绿色中类', '绿色小类', '发起人', '客户名称',
    '业务品种', '放款日期', '状态', '创建时间', '完成时间'
  ]
  
  // 准备数据行 - 使用简单的值格式，贷款账号强制为字符串
  const dataRows = data.map((item, index) => {
    const loanAmount = item.loan_amount ? Number(item.loan_amount) / 10000 : 0
    // 贷款账号转换为字符串，并添加单引号前缀防止科学计数法
    const loanAccount = item.loan_account ? `'${String(item.loan_account)}` : ''
    
    return [
      index + 1,  // 序号：数字
      item.level1_branch || '-',
      item.level2_branch || '-',
      item.branch || '-',
      loanAccount,  // 贷款账号：文本（带单引号前缀）
      loanAmount,  // 放款金额：数字
      item.green_large || '',
      item.green_medium || '',
      item.green_small || '',
      item.initiator || '',
      item.customer_name || '',
      item.business_type || '',
      item.loan_date || '',
      item.status || '',
      item.created_at || '',
      item.completed_at || ''
    ]
  })
  
  const excelData = [headerRow, ...dataRows]
  
  // 获取容器宽度
  const containerWidth = document.getElementById('luckysheet')?.offsetWidth || 1200
  const rowHeaderWidth = 46  // 行号列宽度
  const availableWidth = containerWidth - rowHeaderWidth - 20  // 减去行号和边距
  
  // 动态计算列宽
  const calculateColumnWidth = (colIndex) => {
    let maxWidth = 0
    // 临时创建 canvas 来计算文本宽度
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    ctx.font = '13px Arial'  // luckysheet 默认字体
    
    // 遍历所有行，计算该列的最大宽度
    for (let i = 0; i < excelData.length; i++) {
      const cell = excelData[i][colIndex]
      if (!cell) continue
      
      // 处理对象格式和简单值格式
      let value = ''
      if (typeof cell === 'object' && cell.v !== undefined) {
        value = String(cell.v)
      } else {
        value = String(cell)
      }
      
      const textWidth = ctx.measureText(value).width
      
      if (textWidth > maxWidth) {
        maxWidth = textWidth
      }
    }
    
    // 加上一些内边距
    const padding = 20
    return Math.max(60, maxWidth + padding)
  }
  
  // 计算所有列的宽度
  const columnWidths = []
  let totalWidth = 0
  for (let i = 0; i < 16; i++) {
    const width = calculateColumnWidth(i)
    columnWidths.push(width)
    totalWidth += width
  }
  
  // 如果总宽度超过可用宽度，按比例缩放
  let scale = 1
  if (totalWidth > availableWidth) {
    scale = availableWidth / totalWidth
  }
  
  // 生成动态列宽配置
  const dynamicColumnLen = {}
  for (let i = 0; i < 16; i++) {
    dynamicColumnLen[i] = Math.floor(columnWidths[i] * scale)
  }
  
  const options = {
    container: 'luckysheet',
    title: '在线报表',
    lang: 'zh',
    showinfobar: false,
    showsheetbar: false,
    showstatisticBar: false,
    sheetFormulaBar: false,
    enableAddRow: false,
    enableAddBackTop: false,
    userInfo: false,
    showConfigWindowResize: false,
    forceCalculation: false,
    rowHeaderWidth: 46,
    columnHeaderHeight: 35,
    defaultColWidth: 150,
    row: {
      len: data.length + 1,
      height: 30
    },
    column: {
      len: 16
    },
    cellUpdateBefore: (range, oldValue, newValue, isRefresh) => {
      return false
    },
    data: [{
      name: 'Sheet1',
      color: '',
      status: 1,
      order: 0,
      data: excelData,
      config: {
        columnlen: dynamicColumnLen,  // 使用动态计算的列宽
        rowlen: {
          0: 40  // 表头行高
        },
        merge: {},
        // 设置单元格对齐
        luckysheet_defaultCell: {
          align: 'center',
          vAlign: 'middle'
        }
      },
      index: 0
    }]
  }
  
  try {
    luckysheet.create(options)
    luckysheetInstance = luckysheet
  } catch (e) {
    console.error('创建Excel失败:', e)
    ElMessage.error('Excel组件加载失败')
  }
}

// 查询
const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchForm.level1_branch = ''
  searchForm.level2_branch = ''
  searchForm.branch = ''
  searchForm.loan_account = ''
  pagination.page = 1
  fetchData()
}

// 加载数据
const loadData = () => {
  fetchData()
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

// 导出Excel
const exportExcel = () => {
  try {
    // 准备表头
    const headers = [
      '序号', '一级分行', '二级分行', '支行', '贷款账号', '放款金额(万元)',
      '绿色大类', '绿色中类', '绿色小类', '发起人', '客户名称',
      '业务品种', '放款日期', '状态', '创建时间', '完成时间'
    ]
    
    // 准备数据行
    const rows = tableData.value.map((item, index) => [
      index + 1,
      item.level1_branch || '-',
      item.level2_branch || '-',
      item.branch || '-',
      item.loan_account || '',
      item.loan_amount ? (Number(item.loan_amount) / 10000).toFixed(2) : '',
      item.green_large || '',
      item.green_medium || '',
      item.green_small || '',
      item.initiator || '',
      item.customer_name || '',
      item.business_type || '',
      item.loan_date || '',
      item.status || '',
      item.created_at || '',
      item.completed_at || ''
    ])
    
    // 创建工作簿
    const wb = XLSX.utils.book_new()
    
    // 创建工作表
    const ws = XLSX.utils.aoa_to_sheet([headers, ...rows])
    
    // 设置列宽
    ws['!cols'] = [
      { wch: 8 },   // 序号
      { wch: 20 },  // 一级分行
      { wch: 20 },  // 二级分行
      { wch: 20 },  // 支行
      { wch: 25 },  // 贷款账号
      { wch: 15 },  // 放款金额(万元)
      { wch: 15 },  // 绿色大类
      { wch: 20 },  // 绿色中类
      { wch: 20 },  // 绿色小类
      { wch: 12 },  // 发起人
      { wch: 25 },  // 客户名称
      { wch: 25 },  // 业务品种
      { wch: 15 },  // 放款日期
      { wch: 12 },  // 状态
      { wch: 20 },  // 创建时间
      { wch: 20 }   // 完成时间
    ]
    
    // 设置单元格样式：所有列居中
    const range = XLSX.utils.decode_range(ws['!ref'])
    for (let R = range.s.r; R <= range.e.r; ++R) {
      for (let C = range.s.c; C <= range.e.c; ++C) {
        const cellAddress = XLSX.utils.encode_cell({ r: R, c: C })
        if (!ws[cellAddress]) continue
        if (!ws[cellAddress].s) ws[cellAddress].s = {}
        ws[cellAddress].s.alignment = { horizontal: 'center' }
      }
    }
    
    // 设置表头样式
    for (let C = range.s.c; C <= range.e.c; ++C) {
      const address = XLSX.utils.encode_cell({ r: 0, c: C })
      if (!ws[address]) continue
      ws[address].s.font = { bold: true }
      ws[address].s.fill = { fgColor: { rgb: "D3D3D3" } }
    }
    
    // 添加工作表到工作簿
    XLSX.utils.book_append_sheet(wb, ws, '在线报表')
    
    // 导出文件
    XLSX.writeFile(wb, `在线报表_${new Date().getTime()}.xlsx`)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error(error)
  }
}

onMounted(() => {
  fetchData()
})

onBeforeUnmount(() => {
  if (luckysheetInstance) {
    try {
      luckysheet.destroy()
    } catch (e) {
      console.warn('销毁luckysheet实例失败:', e)
    }
  }
})
</script>

<style scoped>
.online-report-container {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  color: #303133;
}

.header-right {
  display: flex;
  gap: 12px;
}

.filter-bar {
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.luckysheet-container {
  width: 100%;
  height: 600px;
  margin-bottom: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}
</style>

<style>
/* luckysheet自定义样式 */
.luckysheet-info {
  display: none !important;
}

.luckysheet-sheet-area {
  display: none !important;
}

.luckysheet-wa-editor {
  display: none !important;
}

.luckysheet-bottom-controll-row {
  display: none !important;
}
</style>