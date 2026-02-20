<template>
  <div class="dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎回来，{{ authStore.user?.real_name }} 👋</h1>
        <p class="welcome-subtitle">绿色金融管理系统 · 实时数据监控</p>
      </div>
      <div class="welcome-actions">
        <el-button type="primary" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>
    
    <!-- 核心指标卡片 -->
    <div class="stats-cards">
      <el-card shadow="never" class="stat-card main-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="48"><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色贷款</div>
            <div class="stat-value">{{ formatAmount(stats.green_loan_balance) }}</div>
            <div class="stat-sub">
              <span class="stat-item">
                <el-icon :size="14"><User /></el-icon>
                客户数: {{ stats.customer_count }}个
              </span>
              <span class="growth" :class="{ negative: stats.growth_rate < 0 }">
                <el-icon :size="14"><component :is="stats.growth_rate >= 0 ? 'TrendCharts' : 'Bottom'" /></el-icon>
                {{ Math.abs(stats.growth_rate) }}%
              </span>
            </div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="never" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon investment">
            <el-icon :size="36"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色投资</div>
            <div class="stat-value">{{ formatAmount(stats.green_investment) }}</div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="never" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon leasing">
            <el-icon :size="36"><Briefcase /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色租赁</div>
            <div class="stat-value">{{ formatAmount(stats.green_leasing) }}</div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="never" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon wealth">
            <el-icon :size="36"><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色理财</div>
            <div class="stat-value">{{ formatAmount(stats.green_wealth_management) }}</div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="never" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon underwriting">
            <el-icon :size="36"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色承销</div>
            <div class="stat-value">{{ formatAmount(stats.green_underwriting) }}</div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 待办事项 -->
    <el-card shadow="never" class="todo-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon class="header-icon"><List /></el-icon>
            <span class="card-title">待办事项</span>
            <el-tag type="info" size="small">{{ todos.length }} 项</el-tag>
          </div>
          <el-button text type="primary" @click="handleTodoClick('all')">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
      
      <div v-if="todos.length === 0" class="empty-state">
        <el-empty description="暂无待办事项" />
      </div>
      
      <div v-else class="todo-list">
        <div
          v-for="todo in todos"
          :key="todo.category"
          class="todo-item"
          @click="handleTodoClick(todo.category)"
        >
          <div class="todo-info">
            <div class="todo-icon">
              <el-icon><CircleCheckFilled /></el-icon>
            </div>
            <div class="todo-content">
              <div class="todo-title">{{ todo.category }}</div>
              <div class="todo-desc">点击查看详情</div>
            </div>
          </div>
          <div class="todo-count">
            <el-tag :type="getCountType(todo.count)" size="large" effect="dark">
              {{ todo.count }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { getDashboard } from '@/api/green_finance'
import { 
  Money, 
  TrendCharts, 
  Briefcase, 
  Wallet, 
  Document, 
  List, 
  CircleCheckFilled,
  Refresh,
  User,
  Bottom,
  ArrowRight
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)

const stats = ref({
  green_loan_balance: 0,
  customer_count: 0,
  green_loan_ratio: 0,
  growth_rate: 0,
  green_investment: 0,
  green_leasing: 0,
  green_wealth_management: 0,
  green_underwriting: 0
})

const todos = ref([])

const formatAmount = (value) => {
  if (value === null || value === undefined || value === '') return '0.00万亿元'
  const numValue = typeof value === 'string' ? parseFloat(value) : Number(value)
  if (isNaN(numValue)) return '0.00万亿元'
  const trillionValue = numValue / 10000
  const formatted = trillionValue.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
  return `${formatted}万亿元`
}

const getCountType = (count) => {
  if (count >= 10) return 'danger'
  if (count >= 5) return 'warning'
  return 'success'
}

const loadDashboard = async () => {
  try {
    loading.value = true
    const data = await getDashboard()
    stats.value = data.stats
    todos.value = data.todos || []
  } catch (error) {
    console.error('Failed to load dashboard:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadDashboard()
}

const handleTodoClick = (category) => {
  router.push('/green-identify/pending')
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.welcome-content {
  flex: 1;
}

.welcome-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: 0.5px;
}

.welcome-subtitle {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
  font-weight: 400;
}

.welcome-actions :deep(.el-button) {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s;
}

.welcome-actions :deep(.el-button:hover) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-card {
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.stat-card.main-card {
  grid-column: span 2;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.main-card .stat-label,
.stat-card.main-card .stat-value,
.stat-card.main-card .stat-sub {
  color: white;
}

.stat-card.main-card .stat-icon {
  background: rgba(255, 255, 255, 0.2);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 8px;
}

.stat-icon {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(46, 139, 87, 0.1) 0%, rgba(76, 175, 80, 0.1) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2E8B57;
  flex-shrink: 0;
}

.stat-icon.investment {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(102, 187, 106, 0.1) 100%);
  color: #4CAF50;
}

.stat-icon.leasing {
  background: linear-gradient(135deg, rgba(102, 187, 106, 0.1) 0%, rgba(129, 199, 132, 0.1) 100%);
  color: #66BB6A;
}

.stat-icon.wealth {
  background: linear-gradient(135deg, rgba(129, 199, 132, 0.1) 0%, rgba(165, 214, 167, 0.1) 100%);
  color: #81C784;
}

.stat-icon.underwriting {
  background: linear-gradient(135deg, rgba(165, 214, 167, 0.1) 0%, rgba(200, 230, 201, 0.1) 100%);
  color: #A5D6A7;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2E8B57;
  margin-bottom: 12px;
  line-height: 1.2;
}

.stat-sub {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #95a5a6;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.growth {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #4CAF50;
  font-weight: 600;
  padding: 4px 8px;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 6px;
}

.growth.negative {
  color: #f44336;
  background: rgba(244, 67, 54, 0.1);
}

/* 待办事项卡片 */
.todo-card {
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.todo-card .el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

:deep(.todo-card .el-card__body) {
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
  color: #667eea;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.empty-state {
  padding: 40px 0;
}

.todo-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s;
  cursor: pointer;
}

.todo-item:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
}

.todo-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.todo-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #2E8B57 0%, #4CAF50 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(46, 139, 87, 0.3);
}

.todo-content {
  display: flex;
  flex-direction: column;
}

.todo-title {
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.todo-desc {
  font-size: 12px;
  color: #95a5a6;
}

.todo-count :deep(.el-tag) {
  font-size: 16px;
  font-weight: 700;
  padding: 8px 16px;
  border-radius: 8px;
}

:deep(.el-tag--success) {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  border-color: #4CAF50;
}

:deep(.el-tag--warning) {
  background: linear-gradient(135deg, #FF9800 0%, #FFB74D 100%);
  border-color: #FF9800;
}

:deep(.el-tag--danger) {
  background: linear-gradient(135deg, #f44336 0%, #EF5350 100%);
  border-color: #f44336;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-card.main-card {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    padding: 24px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .stat-card.main-card {
    grid-column: span 1;
  }
  
  .todo-list {
    grid-template-columns: 1fr;
  }
}
</style>