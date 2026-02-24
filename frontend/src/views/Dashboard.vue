<template>
  <div class="dashboard">
    <!-- 系统公告轮播图 -->
    <div 
      class="announcement-banner" 
      v-if="announcements.length > 0"
      @mouseenter="isPaused = true"
      @mouseleave="isPaused = false"
    >
      <transition name="slide-fade">
        <div class="banner-item" :key="currentIndex">
          <img :src="currentAnnouncement.cover_image" class="banner-image" alt="公告封面" />
          <div class="banner-content">
            <div class="banner-tag">系统公告</div>
            <h3 class="banner-title">{{ currentAnnouncement.title }}</h3>
            <p class="banner-summary">{{ currentAnnouncement.summary }}</p>
          </div>
        </div>
      </transition>
      <div class="banner-dots">
        <span 
          v-for="(ann, index) in announcements" 
          :key="index"
          :class="['dot', { active: index === currentIndex }]"
          @click="goToSlide(index)"
        ></span>
      </div>
      <div class="banner-navigation">
        <button class="nav-btn prev" @click="prevSlide">
          <el-icon><ArrowLeft /></el-icon>
        </button>
        <button class="nav-btn next" @click="nextSlide">
          <el-icon><ArrowRight /></el-icon>
        </button>
      </div>
      <div class="banner-progress">
        <div 
          class="progress-bar" 
          :style="{ width: ((currentIndex + 1) / announcements.length * 100) + '%' }"
        ></div>
      </div>
    </div>
    
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">
          <span class="greeting">早上好</span>
          {{ authStore.user?.real_name }} 👋
        </h1>
        <p class="welcome-subtitle">绿色金融管理系统 · 智能数据看板</p>
        <div class="welcome-stats">
          <div class="mini-stat">
            <el-icon><Document /></el-icon>
            <span>{{ todos.length }} 项待办</span>
          </div>
          <div class="mini-stat">
            <el-icon><Money /></el-icon>
            <span>{{ formatCompactAmount(stats.green_loan_balance) }}</span>
          </div>
        </div>
      </div>
      <div class="welcome-actions">
        <el-button type="primary" @click="refreshData" :loading="loading" class="refresh-btn">
          <el-icon class="btn-icon"><Refresh /></el-icon>
          刷新数据
        </el-button>
      </div>
    </div>
    
    <!-- 核心指标卡片 -->
    <div class="stats-cards">
      <el-card shadow="hover" class="stat-card main-card">
        <div class="stat-content">
          <div class="stat-icon-wrapper">
            <div class="stat-icon">
              <el-icon :size="40"><Money /></el-icon>
            </div>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色贷款余额</div>
            <div class="stat-value">{{ formatAmount(stats.green_loan_balance) }}</div>
            <div class="stat-metrics">
              <div class="metric-item">
                <span class="metric-label">客户数</span>
                <span class="metric-value">{{ stats.customer_count }}</span>
              </div>
              <div class="metric-divider"></div>
              <div class="metric-item">
                <span class="metric-label">增长率</span>
                <span class="metric-value" :class="{ negative: stats.growth_rate < 0, positive: stats.growth_rate >= 0 }">
                  <el-icon :size="12"><component :is="stats.growth_rate >= 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                  {{ Math.abs(stats.growth_rate) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon-wrapper investment">
            <div class="stat-icon">
              <el-icon :size="32"><TrendCharts /></el-icon>
            </div>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色投资</div>
            <div class="stat-value">{{ formatAmount(stats.green_investment) }}</div>
            <div class="stat-trend up">
              <el-icon><ArrowUp /></el-icon>
              持续增长
            </div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon-wrapper leasing">
            <div class="stat-icon">
              <el-icon :size="32"><Briefcase /></el-icon>
            </div>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色租赁</div>
            <div class="stat-value">{{ formatAmount(stats.green_leasing) }}</div>
            <div class="stat-trend up">
              <el-icon><ArrowUp /></el-icon>
              稳健发展
            </div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon-wrapper wealth">
            <div class="stat-icon">
              <el-icon :size="32"><Wallet /></el-icon>
            </div>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色理财</div>
            <div class="stat-value">{{ formatAmount(stats.green_wealth_management) }}</div>
            <div class="stat-trend up">
              <el-icon><ArrowUp /></el-icon>
              快速增长
            </div>
          </div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon-wrapper underwriting">
            <div class="stat-icon">
              <el-icon :size="32"><Document /></el-icon>
            </div>
          </div>
          <div class="stat-info">
            <div class="stat-label">绿色承销</div>
            <div class="stat-value">{{ formatAmount(stats.green_underwriting) }}</div>
            <div class="stat-trend up">
              <el-icon><ArrowUp /></el-icon>
              持续发力
            </div>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 数据图表区域 -->
    <div class="charts-section">
      <el-card shadow="hover" class="chart-card">
        <template #header>
          <div class="chart-header">
            <div class="chart-title-wrapper">
              <el-icon class="chart-icon"><TrendCharts /></el-icon>
              <span class="chart-title">最近12个月认定绿色贷款余额趋势</span>
            </div>
          </div>
        </template>
        <div ref="loanBalanceChartRef" class="chart-container"></div>
      </el-card>
      
      <el-card shadow="hover" class="chart-card">
        <template #header>
          <div class="chart-header">
            <div class="chart-title-wrapper">
              <el-icon class="chart-icon"><Money /></el-icon>
              <span class="chart-title">最近12个月放款金额趋势</span>
            </div>
          </div>
        </template>
        <div ref="disbursementChartRef" class="chart-container"></div>
      </el-card>
      
      <el-card shadow="hover" class="chart-card full-width">
        <template #header>
          <div class="chart-header">
            <div class="chart-title-wrapper">
              <el-icon class="chart-icon"><Document /></el-icon>
              <span class="chart-title">截止当前时点绿色大类占比</span>
            </div>
          </div>
        </template>
        <div ref="categoryChartRef" class="chart-container"></div>
      </el-card>
    </div>
    
    <!-- 待办事项 -->
    <el-card shadow="hover" class="todo-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <div class="header-icon-wrapper">
              <el-icon class="header-icon"><List /></el-icon>
            </div>
            <div class="header-text">
              <span class="card-title">待办事项</span>
              <span class="card-subtitle">您有 {{ todos.length }} 项待处理任务</span>
            </div>
          </div>
          <el-button text type="primary" @click="handleTodoClick('all')" class="view-all-btn">
            查看全部
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
      
      <div v-if="todos.length === 0" class="empty-state">
        <el-empty description="暂无待办事项" :image-size="120">
          <template #description>
            <p class="empty-text">太棒了！所有任务已完成</p>
          </template>
        </el-empty>
      </div>
      
      <div v-else class="todo-list">
        <div
          v-for="todo in todos"
          :key="todo.category"
          class="todo-item"
          @click="handleTodoClick(todo.category)"
        >
          <div class="todo-left">
            <div class="todo-icon">
              <el-icon><CircleCheckFilled /></el-icon>
            </div>
            <div class="todo-content">
              <div class="todo-title">{{ todo.category }}</div>
              <div class="todo-desc">点击查看详情并处理</div>
            </div>
          </div>
          <div class="todo-count">
            <el-tag :type="getCountType(todo.count)" size="large" effect="dark" class="count-tag">
              {{ todo.count }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { getDashboard } from '@/api/green_finance'
import { getScrollAnnouncements } from '@/api/announcement'
import { 
  getLoanBalanceTrend,
  getDisbursementTrend,
  getGreenCategoryDistribution
} from '@/api/charts'
import * as echarts from 'echarts'
import { 
  Money, 
  TrendCharts, 
  Briefcase, 
  Wallet, 
  Document, 
  List, 
  CircleCheckFilled,
  Refresh,
  ArrowRight,
  ArrowLeft,
  ArrowUp,
  ArrowDown
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

// 公告轮播相关
const announcements = ref([])
const currentIndex = ref(0)
let rotationTimer = null
const isPaused = ref(false)

const currentAnnouncement = computed(() => {
  return announcements.value[currentIndex.value] || {}
})

// 图表相关
const loanBalanceChartRef = ref(null)
const disbursementChartRef = ref(null)
const categoryChartRef = ref(null)
let loanBalanceChart = null
let disbursementChart = null
let categoryChart = null

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

const formatCompactAmount = (value) => {
  if (value === null || value === undefined || value === '') return '0亿'
  const numValue = typeof value === 'string' ? parseFloat(value) : Number(value)
  if (isNaN(numValue)) return '0亿'
  const billionValue = numValue / 100000000
  return `${billionValue.toFixed(2)}亿`
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

// 加载公告数据
const loadAnnouncements = async () => {
  try {
    const response = await getScrollAnnouncements()
    announcements.value = Array.isArray(response) ? response : []
    if (announcements.value.length > 0) {
      startBannerRotation()
    }
  } catch (error) {
    console.error('加载公告失败:', error)
  }
}

// 开始轮播
const startBannerRotation = () => {
  if (rotationTimer) clearInterval(rotationTimer)
  rotationTimer = setInterval(() => {
    if (!isPaused.value) {
      currentIndex.value = (currentIndex.value + 1) % announcements.value.length
    }
  }, 3000)
}

// 切换到下一张
const nextSlide = () => {
  currentIndex.value = (currentIndex.value + 1) % announcements.value.length
}

// 切换到上一张
const prevSlide = () => {
  currentIndex.value = (currentIndex.value - 1 + announcements.value.length) % announcements.value.length
}

// 跳转到指定页
const goToSlide = (index) => {
  currentIndex.value = index
}

// 加载图表数据
const loadCharts = async () => {
  await nextTick()
  console.log('开始加载图表...')
  
  // 初始化贷款余额趋势图表
  if (loanBalanceChartRef.value) {
    console.log('加载贷款余额图表')
    loadLoanBalanceChart()
  } else {
    console.error('贷款余额图表容器未找到')
  }
  
  // 初始化放款金额趋势图表
  if (disbursementChartRef.value) {
    console.log('加载放款金额图表')
    loadDisbursementChart()
  } else {
    console.error('放款金额图表容器未找到')
  }
  
  // 初始化绿色大类占比图表
  if (categoryChartRef.value) {
    console.log('加载绿色大类占比图表')
    loadCategoryChart()
  } else {
    console.error('绿色大类占比图表容器未找到')
  }
}

// 贷款余额趋势图表
const loadLoanBalanceChart = async () => {
  try {
    console.log('获取贷款余额趋势数据...')
    const data = await getLoanBalanceTrend()
    console.log('贷款余额趋势数据:', data)
    
    if (loanBalanceChart) {
      loanBalanceChart.dispose()
    }
    
    console.log('初始化echarts实例')
    loanBalanceChart = echarts.init(loanBalanceChartRef.value)
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params) => {
          const value = params[0].value
          return `${params[0].name}<br/>贷款余额: ${value.toFixed(2)}万亿元`
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.months || [],
        axisLabel: {
          rotate: 45,
          fontSize: 11
        }
      },
      yAxis: {
        type: 'value',
        name: '万亿元',
        axisLabel: {
          formatter: '{value}'
        }
      },
      series: [{
        name: '贷款余额',
        type: 'bar',
        data: data.balances || [],
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: '#4CAF50'
            }, {
              offset: 1, color: '#81C784'
            }]
          }
        },
        barWidth: '50%'
      }]
    }
    
    console.log('设置贷款余额图表配置')
    loanBalanceChart.setOption(option)
    console.log('贷款余额图表加载完成')
    
    window.addEventListener('resize', () => loanBalanceChart.resize())
  } catch (error) {
    console.error('加载贷款余额趋势图表失败:', error)
  }
}

// 放款金额趋势图表
const loadDisbursementChart = async () => {
  try {
    console.log('获取放款金额趋势数据...')
    const data = await getDisbursementTrend()
    console.log('放款金额趋势数据:', data)
    
    if (disbursementChart) {
      disbursementChart.dispose()
    }
    
    console.log('初始化放款金额echarts实例')
    disbursementChart = echarts.init(disbursementChartRef.value)
    
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params) => {
          const value = params[0].value
          return `${params[0].name}<br/>放款金额: ${value.toFixed(2)}万亿元`
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.months || [],
        axisLabel: {
          rotate: 45,
          fontSize: 11
        }
      },
      yAxis: {
        type: 'value',
        name: '万亿元',
        axisLabel: {
          formatter: '{value}'
        }
      },
      series: [{
        name: '放款金额',
        type: 'bar',
        data: data.amounts || [],
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0, color: '#667eea'
            }, {
              offset: 1, color: '#764ba2'
            }]
          }
        },
        barWidth: '50%'
      }]
    }
    
    disbursementChart.setOption(option)
    
    window.addEventListener('resize', () => disbursementChart.resize())
  } catch (error) {
    console.error('加载放款金额趋势图表失败:', error)
  }
}

// 绿色大类占比图表
const loadCategoryChart = async () => {
  try {
    console.log('获取绿色大类占比数据...')
    const data = await getGreenCategoryDistribution()
    console.log('绿色大类占比数据:', data)
    
    if (categoryChart) {
      categoryChart.dispose()
    }
    
    console.log('初始化绿色大类占比echarts实例')
    categoryChart = echarts.init(categoryChartRef.value)
    
    const colors = ['#4CAF50', '#66BB6A', '#81C784', '#A5D6A7', '#C8E6C9', '#667eea', '#764ba2']
    
    const option = {
      tooltip: {
        trigger: 'item',
        formatter: (params) => {
          return `${params.name}<br/>余额: ${params.value.toFixed(2)}万亿元<br/>占比: ${params.percent}%`
        }
      },
      legend: {
        orient: 'vertical',
        right: '10%',
        top: 'center'
      },
      series: [{
        name: '绿色大类',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: (data.categories || []).map((cat, index) => ({
          name: cat,
          value: data.balances[index] || 0
        }))
      }]
    }
    
    categoryChart.setOption(option)
    
    window.addEventListener('resize', () => categoryChart.resize())
  } catch (error) {
    console.error('加载绿色大类占比图表失败:', error)
  }
}

onMounted(() => {
  loadDashboard()
  loadAnnouncements()
  loadCharts()
})

onUnmounted(() => {
  if (rotationTimer) {
    clearInterval(rotationTimer)
  }
  
  if (loanBalanceChart) {
    loanBalanceChart.dispose()
  }
  if (disbursementChart) {
    disbursementChart.dispose()
  }
  if (categoryChart) {
    categoryChart.dispose()
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 28px;
  padding: 4px;
}

/* 公告轮播图 */
.announcement-banner {
  position: relative;
  width: 100%;
  height: 380px;
  overflow: hidden;
  border-radius: 24px;
  background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  transition: box-shadow 0.4s ease;
}

.announcement-banner:hover {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.16);
}

.banner-item {
  width: 100%;
  height: 100%;
  position: relative;
}

.banner-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 8s ease-out;
}

.banner-item .banner-image {
  animation: imageZoom 8s ease-out infinite;
}

@keyframes imageZoom {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.08);
  }
  100% {
    transform: scale(1);
  }
}

.banner-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 32px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.85) 0%, rgba(0, 0, 0, 0.6) 40%, transparent 100%);
  color: white;
}

.banner-tag {
  display: inline-block;
  padding: 8px 20px;
  background: linear-gradient(135deg, #00bcd4 0%, #26c6da 100%);
  border-radius: 24px;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 4px 12px rgba(0, 188, 212, 0.4);
  animation: tagPulse 3s ease-in-out infinite;
}

@keyframes tagPulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(0, 188, 212, 0.4);
  }
  50% {
    box-shadow: 0 6px 20px rgba(0, 188, 212, 0.6);
  }
}

.banner-title {
  margin: 0 0 12px 0;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.3;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
  animation: titleSlide 0.6s ease-out;
}

@keyframes titleSlide {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.banner-summary {
  margin: 0;
  font-size: 16px;
  opacity: 0.95;
  line-height: 1.6;
  max-width: 600px;
  animation: summarySlide 0.6s ease-out 0.1s backwards;
}

@keyframes summarySlide {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 0.95;
    transform: translateY(0);
  }
}

.banner-dots {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
  z-index: 2;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.dot:hover {
  background: rgba(255, 255, 255, 0.8);
  transform: scale(1.2);
}

.dot.active {
  background: white;
  width: 36px;
  border-radius: 6px;
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.6);
}

.dot.active::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00bcd4;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.5);
    opacity: 0.5;
  }
}

.banner-navigation {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
  pointer-events: none;
}

.nav-btn {
  pointer-events: auto;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  color: white;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.35);
  border-color: rgba(255, 255, 255, 0.6);
  transform: scale(1.15);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.nav-btn:active {
  transform: scale(1.05);
}

.slide-fade-enter-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateX(-40px);
}

.banner-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  z-index: 3;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #00bcd4 0%, #26c6da 100%);
  transition: width 0.3s ease;
  box-shadow: 0 0 10px rgba(0, 188, 212, 0.5);
}

/* 欢迎区域 */
.welcome-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40px 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24px;
  color: white;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.25);
  position: relative;
  overflow: hidden;
}

.welcome-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.welcome-section::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%);
  border-radius: 50%;
}

.welcome-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.welcome-title {
  font-size: 34px;
  font-weight: 700;
  margin: 0 0 12px 0;
  letter-spacing: 0.3px;
  line-height: 1.3;
}

.greeting {
  display: block;
  font-size: 18px;
  font-weight: 500;
  opacity: 0.9;
  margin-bottom: 6px;
}

.welcome-subtitle {
  font-size: 15px;
  opacity: 0.9;
  margin: 0 0 24px 0;
  font-weight: 400;
  letter-spacing: 0.5px;
}

.welcome-stats {
  display: flex;
  gap: 24px;
}

.mini-stat {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  font-size: 14px;
  font-weight: 600;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
}

.mini-stat:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.welcome-actions {
  position: relative;
  z-index: 1;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 14px 28px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.refresh-btn .btn-icon {
  margin-right: 6px;
}

/* 图表区域 */
.charts-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-card {
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  background: white;
}

.chart-card.full-width {
  grid-column: span 2;
}

.chart-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
}

:deep(.chart-card .el-card__header) {
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(to right, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%);
}

:deep(.chart-card .el-card__body) {
  padding: 24px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chart-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-icon {
  font-size: 20px;
  color: #667eea;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: 0.3px;
}

.chart-container {
  width: 100%;
  height: 320px;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.stat-card {
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  background: white;
}

.stat-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.stat-card.main-card {
  grid-column: span 2;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.main-card .stat-label,
.stat-card.main-card .stat-value,
.stat-card.main-card .metric-label,
.stat-card.main-card .metric-value,
.stat-card.main-card .stat-trend {
  color: white;
}

.stat-card.main-card .metric-item {
  border-color: rgba(255, 255, 255, 0.2);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
}

.stat-icon-wrapper {
  flex-shrink: 0;
}

.stat-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(46, 139, 87, 0.12) 0%, rgba(76, 175, 80, 0.12) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2E8B57;
  box-shadow: 0 4px 16px rgba(46, 139, 87, 0.15);
}

.stat-icon-wrapper.investment .stat-icon {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.12) 0%, rgba(102, 187, 106, 0.12) 100%);
  color: #4CAF50;
  box-shadow: 0 4px 16px rgba(76, 175, 80, 0.15);
}

.stat-icon-wrapper.leasing .stat-icon {
  background: linear-gradient(135deg, rgba(102, 187, 106, 0.12) 0%, rgba(129, 199, 132, 0.12) 100%);
  color: #66BB6A;
  box-shadow: 0 4px 16px rgba(102, 187, 106, 0.15);
}

.stat-icon-wrapper.wealth .stat-icon {
  background: linear-gradient(135deg, rgba(129, 199, 132, 0.12) 0%, rgba(165, 214, 167, 0.12) 100%);
  color: #81C784;
  box-shadow: 0 4px 16px rgba(129, 199, 132, 0.15);
}

.stat-icon-wrapper.underwriting .stat-icon {
  background: linear-gradient(135deg, rgba(165, 214, 167, 0.12) 0%, rgba(200, 230, 201, 0.12) 100%);
  color: #A5D6A7;
  box-shadow: 0 4px 16px rgba(165, 214, 167, 0.15);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 10px;
  font-weight: 500;
  letter-spacing: 0.3px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2E8B57;
  margin-bottom: 16px;
  line-height: 1.2;
}

.stat-metrics {
  display: flex;
  align-items: center;
  gap: 20px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 14px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.stat-card.main-card .metric-item {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.2);
}

.metric-label {
  font-size: 11px;
  opacity: 0.8;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}

.metric-value.positive {
  color: #4CAF50;
}

.metric-value.negative {
  color: #f44336;
}

.metric-divider {
  width: 1px;
  height: 40px;
  background: rgba(0, 0, 0, 0.1);
}

.stat-card.main-card .metric-divider {
  background: rgba(255, 255, 255, 0.3);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  padding: 8px 14px;
  background: rgba(76, 175, 80, 0.1);
  border-radius: 10px;
  color: #4CAF50;
}

.stat-trend.up {
  background: rgba(76, 175, 80, 0.1);
}

/* 待办事项卡片 */
.todo-card {
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  background: white;
}

:deep(.todo-card .el-card__header) {
  padding: 24px 28px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: linear-gradient(to right, rgba(102, 126, 234, 0.02) 0%, rgba(118, 75, 162, 0.02) 100%);
}

:deep(.todo-card .el-card__body) {
  padding: 24px 28px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
}

.header-icon {
  font-size: 20px;
  color: white;
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 0.3px;
}

.card-subtitle {
  font-size: 13px;
  color: #7f8c8d;
  font-weight: 500;
}

.view-all-btn {
  font-size: 14px;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: 10px;
  transition: all 0.3s;
}

.view-all-btn:hover {
  background: rgba(102, 126, 234, 0.1);
}

.empty-state {
  padding: 60px 0;
}

.empty-text {
  font-size: 15px;
  color: #7f8c8d;
  margin-top: 16px;
}

.todo-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.04) 0%, rgba(118, 75, 162, 0.04) 100%);
  border-radius: 16px;
  border: 1.5px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.todo-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(to bottom, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s;
}

.todo-item:hover::before {
  opacity: 1;
}

.todo-item:hover {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-color: rgba(102, 126, 234, 0.25);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(102, 126, 234, 0.15);
}

.todo-left {
  display: flex;
  align-items: center;
  gap: 18px;
  flex: 1;
}

.todo-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: linear-gradient(135deg, #2E8B57 0%, #4CAF50 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 22px;
  box-shadow: 0 6px 16px rgba(46, 139, 87, 0.3);
  flex-shrink: 0;
  transition: all 0.3s;
}

.todo-item:hover .todo-icon {
  transform: scale(1.1);
  box-shadow: 0 8px 20px rgba(46, 139, 87, 0.4);
}

.todo-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.todo-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: 0.2px;
}

.todo-desc {
  font-size: 13px;
  color: #7f8c8d;
}

.todo-count {
  flex-shrink: 0;
}

.count-tag {
  font-size: 18px;
  font-weight: 700;
  padding: 10px 20px;
  border-radius: 12px;
  border: none;
}

:deep(.el-tag--success) {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  border-color: #4CAF50;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

:deep(.el-tag--warning) {
  background: linear-gradient(135deg, #FF9800 0%, #FFB74D 100%);
  border-color: #FF9800;
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

:deep(.el-tag--danger) {
  background: linear-gradient(135deg, #f44336 0%, #EF5350 100%);
  border-color: #f44336;
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .stats-cards {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .stat-card.main-card {
    grid-column: span 3;
  }
}

@media (max-width: 1024px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    padding: 32px 24px;
  }
  
  .welcome-stats {
    justify-content: center;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-card.main-card {
    grid-column: span 2;
  }
  
  .todo-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .welcome-title {
    font-size: 26px;
  }
  
  .greeting {
    font-size: 16px;
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
  
  .announcement-banner {
    height: 280px;
  }
  
  .banner-title {
    font-size: 20px;
  }
  
  .banner-summary {
    font-size: 13px;
  }
}
</style>