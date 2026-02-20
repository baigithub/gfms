<template>
  <div class="login-container">
    <div class="login-background">
      <div class="background-pattern"></div>
      <div class="brand-container">
        <div class="green-logo">
          <div class="logo-circle">
            <el-icon :size="56" color="white"><ElementPlus /></el-icon>
          </div>
        </div>
        <div class="background-text">
          <h1>绿色金融</h1>
          <p>Green Finance Management System</p>
          <div class="tagline">智能 · 高效 · 可持续</div>
        </div>
      </div>
    </div>
    
    <div class="login-form-container">
      <div class="login-form">
        <div class="form-header">
          <div class="header-icon">
            <el-icon :size="32" color="#667eea"><ElementPlus /></el-icon>
          </div>
          <h2>绿色金融管理系统</h2>
          <p>登录您的账户</p>
        </div>
        
        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="rules"
          label-position="top"
          size="large"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="请输入登录账号"
              :prefix-icon="User"
              class="modern-input"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入登录密码"
              :prefix-icon="Lock"
              show-password
              class="modern-input"
            />
          </el-form-item>
          
          <el-form-item prop="captcha">
            <div class="captcha-container">
              <el-input
                v-model="loginForm.captcha"
                placeholder="请输入验证码"
                :prefix-icon="Key"
                class="modern-input captcha-input"
                @keyup.enter="handleLogin"
              />
              <div class="captcha-code" @click="refreshCaptcha" title="点击刷新验证码">
                {{ captchaCode }}
              </div>
            </div>
          </el-form-item>
          
          <el-form-item>
            <el-button
              type="primary"
              :loading="loading"
              @click="handleLogin"
              class="login-button"
            >
              <template v-if="!loading">
                <el-icon class="button-icon"><ElementPlus /></el-icon>
              </template>
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="form-footer">
          <div class="footer-divider"></div>
          <p class="footer-text">© 2025 绿色金融管理系统 · 技术支持</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Key, ElementPlus } from '@element-plus/icons-vue'
import { login } from '@/api/auth'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref(null)
const loading = ref(false)
const captchaCode = ref('D2CIK')
const lastLoginTime = ref(0)
const LOGIN_COOLDOWN = 5000 // 5秒冷却时间

const loginForm = reactive({
  username: '',
  password: '',
  captcha: ''
})

const refreshCaptcha = () => {
  const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
  let result = ''
  for (let i = 0; i < 5; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaCode.value = result
}

const rules = {
  username: [
    { required: true, message: '请输入登录账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入登录密码', trigger: 'blur' }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  // 检查登录间隔
  const now = Date.now()
  if (now - lastLoginTime.value < LOGIN_COOLDOWN) {
    const remainingTime = Math.ceil((LOGIN_COOLDOWN - (now - lastLoginTime.value)) / 1000)
    ElMessage.warning(`请等待 ${remainingTime} 秒后再试`)
    return
  }

  try {
    await loginFormRef.value.validate()
    lastLoginTime.value = Date.now()
    loading.value = true
    
    const res = await login(loginForm)
    
    authStore.setToken(res.access_token)
    authStore.setUser(res.user)
    authStore.setPermissions(res.user.permissions || [])
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    if (error !== false) {
      // 判断错误类型并显示具体提示
      const errorMessage = error.response?.data?.detail || error.message || '登录失败'
      
      if (errorMessage.includes('验证码')) {
        ElMessage.error('验证码错误，请重新输入')
        refreshCaptcha()
        loginForm.captcha = ''
      } else if (errorMessage.includes('用户名或密码错误')) {
        ElMessage.error('用户名或密码错误')
        loginForm.password = ''
        refreshCaptcha()
        loginForm.captcha = ''
      } else {
        ElMessage.error(errorMessage)
        refreshCaptcha()
        loginForm.captcha = ''
      }
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.login-background {
  flex: 4;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(135deg, #8A7FE9 0%, #6B4ABF 100%);
  overflow: hidden;
}

.background-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  animation: pattern-move 20s ease-in-out infinite alternate;
}

@keyframes pattern-move {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(1.2);
  }
}

.brand-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 40px;
  z-index: 1;
  animation: fadeInUp 1s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.green-logo {
  animation: logoGlow 3s ease-in-out infinite;
}

@keyframes logoGlow {
  0%, 100% {
    filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
  }
  50% {
    filter: drop-shadow(0 0 30px rgba(255, 255, 255, 0.5));
  }
}

.logo-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(20px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.background-text {
  text-align: center;
  z-index: 1;
  color: white;
  animation: fadeInUp 1s ease-out 0.3s backwards;
}

.background-text h1 {
  font-size: 72px;
  font-weight: 800;
  margin: 0 0 20px 0;
  letter-spacing: 6px;
  text-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.background-text p {
  font-size: 20px;
  font-weight: 300;
  margin: 0 0 32px 0;
  opacity: 0.95;
  letter-spacing: 2px;
  font-family: 'Inter', 'Helvetica Neue', sans-serif;
}

.tagline {
  font-size: 22px;
  font-weight: 500;
  opacity: 0.9;
  letter-spacing: 12px;
  margin-top: 40px;
  position: relative;
  display: inline-block;
  padding: 12px 32px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.tagline::before,
.tagline::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 80px;
  height: 2px;
  background: rgba(255, 255, 255, 0.4);
}

.tagline::before {
  left: -100px;
}

.tagline::after {
  right: -100px;
}

.login-form-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  position: relative;
}

.login-form {
  width: 460px;
  background: white;
  border-radius: 20px;
  padding: 48px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  z-index: 10;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.header-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.form-header h2 {
  color: #2c3e50;
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: 0.5px;
}

.form-header p {
  color: #7f8c8d;
  font-size: 14px;
  font-weight: 400;
  margin: 0;
}

:deep(.modern-input .el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 16px;
  border: 2px solid #e0e6ed;
  transition: all 0.3s ease;
  background: #fafbfc;
}

:deep(.modern-input .el-input__wrapper:hover) {
  border-color: #667eea;
  background: white;
}

:deep(.modern-input .el-input__wrapper.is-focus) {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

:deep(.modern-input .el-input__inner) {
  font-size: 15px;
  color: #2c3e50;
}

.captcha-container {
  display: flex;
  gap: 12px;
  align-items: center;
}

.captcha-input {
  flex: 1;
}

.captcha-code {
  width: 120px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  color: white;
  letter-spacing: 3px;
  border-radius: 12px;
  user-select: none;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.captcha-code:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
}

.login-button {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(102, 126, 234, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.button-icon {
  margin-right: 8px;
  font-size: 18px;
}

.form-footer {
  margin-top: 32px;
  padding-top: 24px;
}

.footer-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, #e0e6ed 50%, transparent 100%);
  margin-bottom: 16px;
}

.footer-text {
  color: #95a5a6;
  font-size: 12px;
  text-align: center;
  margin: 0;
  font-weight: 400;
}

:deep(.el-form-item__content) {
  flex-direction: column;
}

:deep(.el-form-item__error) {
  padding-top: 4px;
}

:deep(.el-icon) {
  font-size: 18px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-background {
    flex: 2;
  }
  
  .background-text h1 {
    font-size: 48px;
  }
  
  .background-text p {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }
  
  .login-background {
    flex: 1;
    min-height: 300px;
  }
  
  .background-text h1 {
    font-size: 36px;
  }
  
  .background-text p {
    font-size: 14px;
  }
  
  .login-form {
    width: 90%;
    padding: 32px 24px;
  }
  
  .form-header h2 {
    font-size: 24px;
  }
}
</style>