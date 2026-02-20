<template>
  <div class="workflow-designer-container">
    <div class="designer-header">
      <div class="header-left">
        <el-button @click="goBack" icon="ArrowLeft" circle />
        <h2 class="title">{{ mode === 'view' ? '查看流程' : (mode === 'new' ? '创建新版本' : '流程设计器') }}</h2>
      </div>
      <div class="header-info">
        <el-input 
          v-model="processName" 
          placeholder="请输入流程名称" 
          style="width: 300px; margin-right: 10px"
          :disabled="mode === 'view'"
        />
        <el-tag v-if="processVersion" type="info" style="margin-right: 10px">v{{ processVersion }}</el-tag>
      </div>
      <div class="header-actions" v-if="mode !== 'view'">
        <el-button @click="loadExample">加载示例</el-button>
        <el-button type="primary" @click="saveProcess">{{ mode === 'edit' ? '更新' : (mode === 'new' ? '保存为新版本' : '保存') }}</el-button>
        <el-button @click="exportBpmn">导出</el-button>
      </div>
    </div>
    
    <div class="designer-body">
      <!-- 左侧工具栏 -->
      <div class="left-toolbar">
        <div class="toolbar-title">工具</div>
        <div class="toolbar-content">
          <div class="tool-item" @click="activateTool('hand')" :class="{ active: currentTool === 'hand' }">
            <el-icon><Pointer /></el-icon>
            <span>选择</span>
          </div>
          <div class="tool-item" @click="activateTool('lasso')" :class="{ active: currentTool === 'lasso' }">
            <el-icon><Select /></el-icon>
            <span>框选</span>
          </div>
          <div class="tool-item" @click="activateTool('space')" :class="{ active: currentTool === 'space' }">
            <el-icon><Rank /></el-icon>
            <span>空间</span>
          </div>
          <div class="tool-item" @click="activateTool('global-connect')" :class="{ active: currentTool === 'global-connect' }">
            <el-icon><Connection /></el-icon>
            <span>连接</span>
          </div>
          <div class="tool-divider"></div>
          <div class="toolbar-section-title">元素</div>
          <div class="tool-item" @click="addStartEvent">
            <el-icon><VideoPlay /></el-icon>
            <span>开始事件</span>
          </div>
          <div class="tool-item" @click="addEndEvent">
            <el-icon><VideoPause /></el-icon>
            <span>结束事件</span>
          </div>
          <div class="tool-item" @click="addUserTask">
            <el-icon><User /></el-icon>
            <span>用户任务</span>
          </div>
          <div class="tool-item" @click="addExclusiveGateway">
            <el-icon><Share /></el-icon>
            <span>排他网关</span>
          </div>
          <div class="tool-item" @click="addParallelGateway">
            <el-icon><Share /></el-icon>
            <span>并行网关</span>
          </div>
          <div class="tool-item" @click="addServiceTask">
            <el-icon><Setting /></el-icon>
            <span>服务任务</span>
          </div>
        </div>
      </div>
      
      <!-- 中间设计区域 -->
      <div class="canvas-wrapper">
        <div class="canvas-container" ref="canvasContainer"></div>
      </div>
      
      <!-- 右侧属性栏 -->
      <div class="right-panel">
        <div class="panel-title">属性</div>
        <div class="panel-content">
          <el-empty v-if="!selectedElement" description="请选择一个元素" />
          <div v-else class="properties-form">
            <el-form :model="elementProperties" label-width="90px" size="small">
              <el-form-item label="ID">
                <el-input v-model="elementProperties.id" disabled />
              </el-form-item>
              <el-form-item label="类型">
                <el-input v-model="elementProperties.typeName" disabled />
              </el-form-item>
              <el-form-item label="名称">
                <el-input v-model="elementProperties.name" :disabled="mode === 'view'" @change="updateElementName" />
              </el-form-item>
              
              <!-- 用户任务特有属性 -->
              <template v-if="elementProperties.type === 'bpmn:UserTask' || elementProperties.type === 'bpmn:Task'">
                <el-form-item label="候选组">
                  <el-select 
                    v-model="elementProperties.candidateGroups" 
                    multiple 
                    placeholder="选择角色"
                    style="width: 100%"
                    :disabled="mode === 'view'"
                    @change="updateCandidateGroups"
                  >
                    <el-option 
                      v-for="role in roles" 
                      :key="role.id" 
                      :label="role.name" 
                      :value="role.name" 
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="适用机构">
                  <el-checkbox-group 
                    v-model="elementProperties.orgLevels"
                    :disabled="mode === 'view'"
                    @change="updateCustomProperties"
                  >
                    <el-checkbox value="1">总行</el-checkbox>
                    <el-checkbox value="2">分行</el-checkbox>
                    <el-checkbox value="3">支行</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </template>
              
              <!-- 排他网关特有属性 -->
              <template v-if="elementProperties.type === 'bpmn:ExclusiveGateway'">
                <el-form-item label="条件变量">
                  <el-input 
                    v-model="elementProperties.conditionVariable" 
                    placeholder="例如: parentOrgType"
                    :disabled="mode === 'view'"
                  />
                </el-form-item>
                <el-form-item label="条件表达式">
                  <el-input 
                    v-model="elementProperties.conditionExpression" 
                    type="textarea" 
                    :rows="3"
                    placeholder="例如: ${parentOrgType == 2}"
                    :disabled="mode === 'view'"
                    @change="updateConditionExpression"
                  />
                </el-form-item>
                <el-divider />
                <el-form-item label="分支说明">
                  <el-alert 
                    title="网关分支条件" 
                    type="info" 
                    :closable="false"
                    show-icon
                  >
                    <template #default>
                      <div style="font-size: 12px; line-height: 1.6;">
                        <p>• 使用 ${变量名} 访问流程变量</p>
                        <p>• 例如: ${parentOrgType == 2} 表示父级机构为分行</p>
                        <p>• 可用变量: initiator(发起人), parentOrgType(父级机构类型)</p>
                      </div>
                    </template>
                  </el-alert>
                </el-form-item>
              </template>
              
              <!-- 连线特有属性 -->
              <template v-if="elementProperties.type === 'bpmn:SequenceFlow'">
                <el-form-item label="条件表达式">
                  <el-input 
                    v-model="elementProperties.conditionExpression" 
                    type="textarea" 
                    :rows="3"
                    placeholder="输入条件表达式，例如: ${parentOrgType == 2}"
                    :disabled="mode === 'view'"
                    @change="updateConditionExpression"
                  />
                </el-form-item>
                <el-form-item label="条件说明">
                  <el-alert 
                    title="分支条件" 
                    type="info" 
                    :closable="false"
                    show-icon
                  >
                    <template #default>
                      <div style="font-size: 12px; line-height: 1.6;">
                        <p>• 使用 ${变量名} 访问流程变量</p>
                        <p>• 常用变量: parentOrgType(父级机构类型)</p>
                        <p>• 机构类型: 1=总行, 2=分行, 3=支行</p>
                        <p>• 示例: ${parentOrgType == 2} 走分行审批</p>
                      </div>
                    </template>
                  </el-alert>
                </el-form-item>
              </template>
            </el-form>
          </div>
        </div>
      </div>
    </div>
    
    <el-dialog v-model="dialogVisible" title="流程信息" width="500px">
      <el-form :model="processInfo" label-width="100px">
        <el-form-item label="流程键">
          <el-input v-model="processInfo.key" placeholder="例如: green_identification" />
        </el-form-item>
        <el-form-item label="流程名称">
          <el-input v-model="processInfo.name" placeholder="例如: 绿色贷款认定流程" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="processInfo.description" type="textarea" placeholder="流程描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmProcessInfo">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, markRaw } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Pointer, Select, Rank, Connection, VideoPlay, VideoPause, User, Share, Setting, ArrowLeft } from '@element-plus/icons-vue'
import BpmnModeler from 'bpmn-js/lib/Modeler'
import camundaModdleDescriptor from 'camunda-bpmn-moddle/resources/camunda'
import {
  createDefinition,
  updateDefinition,
  getDefinitions,
  getDefinition,
  createTaskNodes,
  getTaskNodes
} from '@/api/workflow'
import { getRoles } from '@/api/system'

const canvasContainer = ref(null)
let bpmnModeler = null
const dialogVisible = ref(false)
const selectedElement = ref(null)
const currentTool = ref('hand')
const mode = ref('new') // new, view, edit
const definitionId = ref(null)
const processName = ref('')
const processVersion = ref(null)

const route = useRoute()
const router = useRouter()

const processInfo = ref({
  key: '',
  name: '',
  description: ''
})

const elementProperties = ref({
  id: '',
  name: '',
  type: '',
  typeName: '',
  candidateGroups: [],
  conditionExpression: '',
  parentOrgType: '',
  orgLevels: []
})

const roles = ref([])

// 示例 BPMN XML
const exampleBpmn = `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                 xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                 xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                 xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                 xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                 id="Definitions_1"
                 targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="false">
    <bpmn:startEvent id="StartEvent_1" />
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_1" />
    <bpmn:userTask id="Task_1" name="客户经理提交" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="Task_1" targetRef="Task_2" />
    <bpmn:userTask id="Task_2" name="二级分行审核" />
    <bpmn:sequenceFlow id="Flow_3" sourceRef="Task_2" targetRef="Task_3" />
    <bpmn:userTask id="Task_3" name="一级分行复核" />
    <bpmn:sequenceFlow id="Flow_4" sourceRef="Task_3" targetRef="EndEvent_1" />
    <bpmn:endEvent id="EndEvent_1" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent_2" bpmnElement="StartEvent_1">
        <dc:Bounds x="100" y="100" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="_BPMNShape_Task_3" bpmnElement="Task_1">
        <dc:Bounds x="180" y="78" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="_BPMNShape_Task_4" bpmnElement="Task_2">
        <dc:Bounds x="330" y="78" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="_BPMNShape_Task_5" bpmnElement="Task_3">
        <dc:Bounds x="480" y="78" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="_BPMNShape_EndEvent_2" bpmnElement="EndEvent_1">
        <dc:Bounds x="630" y="100" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="BPMNEdge_SequenceFlow_1" bpmnElement="Flow_1">
        <di:waypoint x="136" y="118" />
        <di:waypoint x="180" y="118" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="BPMNEdge_SequenceFlow_2" bpmnElement="Flow_2">
        <di:waypoint x="280" y="118" />
        <di:waypoint x="330" y="118" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="BPMNEdge_SequenceFlow_3" bpmnElement="Flow_3">
        <di:waypoint x="430" y="118" />
        <di:waypoint x="480" y="118" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="BPMNEdge_SequenceFlow_4" bpmnElement="Flow_4">
        <di:waypoint x="580" y="118" />
        <di:waypoint x="630" y="118" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`

const loadRoles = async () => {
  try {
    const response = await getRoles()
    console.log('角色数据:', response)
    
    // 处理不同的响应格式
    if (Array.isArray(response)) {
      roles.value = response
    } else if (response.data && Array.isArray(response.data)) {
      roles.value = response.data
    } else if (response.items && Array.isArray(response.items)) {
      roles.value = response.items
    } else {
      roles.value = []
    }
    
    console.log('加载的角色列表:', roles.value)
  } catch (error) {
    console.error('加载角色失败:', error)
    roles.value = []
  }
}

const loadWorkflowDefinition = async (defId, mode) => {
  console.log('loadWorkflowDefinition 开始:', defId, mode)
  try {
    console.log('调用 getDefinition API...')
    const response = await getDefinition(defId)
    console.log('getDefinition 响应:', response)
    console.log('响应的所有键:', Object.keys(response))
    console.log('bpmn_xml 字段:', response.bpmn_xml)
    
    const definition = response
    
    // 设置流程信息
    processName.value = definition.name
    processVersion.value = definition.version
    
    // 只有在编辑模式下才设置 definitionId，新建模式下不设置
    if (mode === 'edit') {
      definitionId.value = defId
    } else {
      definitionId.value = null
    }
    
    processInfo.value = {
      key: definition.key,
      name: definition.name,
      description: definition.description || ''
    }
    
    console.log('流程信息:', processInfo.value)
    console.log('流程版本:', processVersion.value)
    console.log('definitionId.value:', definitionId.value)
    
    // 加载 BPMN XML
    if (definition.bpmn_xml) {
      console.log('开始 importXML，BPMN 长度:', definition.bpmn_xml.length)
      console.log('BPMN XML 片段:', definition.bpmn_xml.substring(0, 500))
      
      // 检查XML中是否包含候选组
      const hasCandidateGroups = definition.bpmn_xml.includes('candidateGroups')
      console.log('BPMN XML中是否包含candidateGroups标签:', hasCandidateGroups)
      
      // 提取所有包含candidateGroups的片段
      const candidateGroupsMatches = definition.bpmn_xml.match(/<[^>]*candidateGroups[^>]*>.*?<\/[^>]*candidateGroups[^>]*>/gi)
      console.log('BPMN XML中的candidateGroups片段:', candidateGroupsMatches)
      
      await bpmnModeler.importXML(definition.bpmn_xml)
      console.log('importXML 完成')
      bpmnModeler.get('canvas').zoom('fit-viewport')
      console.log('画布缩放完成')
      
      // 检查加载后的元素
      const elementRegistry = bpmnModeler.get('elementRegistry')
      const elements = elementRegistry.getAll()
      console.log('加载的元素数量:', elements.length)
      
      // 检查用户任务元素
      const userTasks = elements.filter(el => el.type === 'bpmn:Task' || el.type === 'bpmn:UserTask')
      console.log('用户任务数量:', userTasks.length)
      userTasks.forEach(task => {
        const bo = task.businessObject
        console.log('任务:', task.id, bo.name)
        console.log('  - candidateGroups:', bo.candidateGroups)
        console.log('  - candidateGroups类型:', typeof bo.candidateGroups)
        console.log('  - businessObject所有属性:', Object.keys(bo))
        console.log('  - $attrs:', bo.$attrs)
      })
      
      if (mode === 'view') {
        // 查看模式：禁用编辑功能
        ElMessage.info('查看模式：无法编辑流程')
      } else if (mode === 'new') {
        ElMessage.success('流程已加载，保存后将创建新版本')
      } else {
        ElMessage.success('流程加载成功')
      }
    } else {
      console.error('流程定义中没有 BPMN XML')
      ElMessage.error('流程定义中没有 BPMN XML')
    }
  } catch (error) {
    console.error('加载流程定义失败:', error)
    ElMessage.error('加载流程定义失败: ' + (error.message || '未知错误'))
  }
}

const initModeler = async () => {
  console.log('开始初始化 BPMN Modeler...')
  
  if (!canvasContainer.value) {
    console.error('canvasContainer 不存在')
    ElMessage.error('画布容器未找到，请刷新页面重试')
    return
  }

  try {
    console.log('创建 BPMN Modeler...')
    bpmnModeler = new BpmnModeler({
      container: canvasContainer.value,
      moddleExtensions: {
        camunda: camundaModdleDescriptor
      }
    })
    console.log('BPMN Modeler 创建成功')

    // 等待 BPMN Modeler 完全初始化
    await new Promise(resolve => setTimeout(resolve, 100))

    // 监听元素选择事件
    const eventBus = bpmnModeler.get('eventBus')
    eventBus.on('selection.changed', (e) => {
      console.log('selection.changed 事件触发:', e)
      const newSelection = e.newSelection
      console.log('newSelection:', newSelection)
      if (newSelection && newSelection.length > 0) {
        const element = newSelection[0]
        console.log('选中的元素:', element.id, element.type)
        selectedElement.value = markRaw(element)
        updatePropertiesPanel(element)
      } else {
        console.log('取消选择')
        selectedElement.value = null
        elementProperties.value = {
          id: '',
          name: '',
          type: '',
          typeName: '',
          candidateGroups: [],
          conditionExpression: '',
          conditionVariable: '',
          parentOrgType: '',
          orgLevels: []
        }
      }
    })

    // 检查 URL 参数，决定加载哪个流程
    const urlMode = route.query.mode
    const urlDefinitionId = route.query.id
    const copyFrom = route.query.copyFrom
    
    console.log('初始化时路由参数:', { urlMode, urlDefinitionId, copyFrom })
    
    // 更新 mode 值
    if (urlMode && (urlMode === 'view' || urlMode === 'edit' || urlMode === 'new')) {
      mode.value = urlMode
      console.log('设置模式为:', mode.value)
    }
    
    console.log('URL 参数:', { mode: mode.value, definitionId: urlDefinitionId, copyFrom })
    
    if (copyFrom) {
      // 从现有流程复制创建新版本
      console.log('从现有流程复制创建新版本:', copyFrom)
      await loadWorkflowDefinition(copyFrom, 'new')
      ElMessage.info('已加载流程定义，保存后将创建新版本')
    } else if (urlDefinitionId && (mode.value === 'view' || mode.value === 'edit')) {
      // 加载现有流程
      console.log('加载现有流程:', urlDefinitionId, '模式:', mode.value)
      await loadWorkflowDefinition(urlDefinitionId, mode.value)
    } else {
      // 加载示例流程
      console.log('加载示例流程...')
      try {
        console.log('exampleBpmn 长度:', exampleBpmn.length)
        await bpmnModeler.importXML(exampleBpmn)
        console.log('importXML 完成')
        
        const canvas = bpmnModeler.get('canvas')
        canvas.zoom('fit-viewport')
        console.log('示例流程加载成功')
        ElMessage.success('示例流程加载成功')
      } catch (error) {
        console.error('加载示例失败:', error)
        ElMessage.error('加载示例失败: ' + error.message)
      }
    }
  } catch (error) {
    console.error('BPMN Modeler 初始化失败:', error)
    ElMessage.error('BPMN Modeler 初始化失败: ' + error.message)
  }
}

const activateTool = (toolType) => {
  currentTool.value = toolType
  // TODO: 实现 BPMN 工具激活逻辑
}

const addStartEvent = () => {
  if (!bpmnModeler) return
  const modeling = bpmnModeler.get('modeling')
  const elementFactory = bpmnModeler.get('elementFactory')
  const elementRegistry = bpmnModeler.get('elementRegistry')
  
  const shape = elementFactory.createShape({ type: 'bpmn:StartEvent' })
  modeling.createShape(shape, { x: 300, y: 200 })
}

const addEndEvent = () => {
  if (!bpmnModeler) return
  const modeling = bpmnModeler.get('modeling')
  const elementFactory = bpmnModeler.get('elementFactory')
  
  const shape = elementFactory.createShape({ type: 'bpmn:EndEvent' })
  modeling.createShape(shape, { x: 600, y: 200 })
}

const addUserTask = () => {
  if (!bpmnModeler) return
  const modeling = bpmnModeler.get('modeling')
  const elementFactory = bpmnModeler.get('elementFactory')
  const moddle = bpmnModeler.get('moddle')
  
  // 创建用户任务并设置默认名称
  const shape = elementFactory.createShape({ 
    type: 'bpmn:UserTask',
    businessObject: moddle.create('bpmn:UserTask', {
      name: '用户任务'
    })
  })
  modeling.createShape(shape, { x: 450, y: 180 })
}

const addExclusiveGateway = () => {
  if (!bpmnModeler) return
  const modeling = bpmnModeler.get('modeling')
  const elementFactory = bpmnModeler.get('elementFactory')
  
  const shape = elementFactory.createShape({ type: 'bpmn:ExclusiveGateway' })
  modeling.createShape(shape, { x: 450, y: 200 })
}

const addParallelGateway = () => {
  if (!bpmnModeler) return
  const modeling = bpmnModeler.get('modeling')
  const elementFactory = bpmnModeler.get('elementFactory')
  
  const shape = elementFactory.createShape({ type: 'bpmn:ParallelGateway' })
  modeling.createShape(shape, { x: 450, y: 200 })
}

const addServiceTask = () => {
  if (!bpmnModeler) return
  const modeling = bpmnModeler.get('modeling')
  const elementFactory = bpmnModeler.get('elementFactory')
  
  const shape = elementFactory.createShape({ type: 'bpmn:ServiceTask' })
  modeling.createShape(shape, { x: 450, y: 180 })
}

const updatePropertiesPanel = (element) => {
  const businessObject = element.businessObject
  
  console.log('updatePropertiesPanel - 元素ID:', element.id)
  console.log('updatePropertiesPanel - businessObject类型:', businessObject.$type)
  console.log('updatePropertiesPanel - businessObject的所有属性:', Object.keys(businessObject))
  console.log('updatePropertiesPanel - candidateGroups原始值:', businessObject.candidateGroups)
  console.log('updatePropertiesPanel - candidateGroups类型:', typeof businessObject.candidateGroups)
  
  // 尝试从扩展元素中获取候选组
  let candidateGroupsFromExtension = []
  console.log('检查extensionElements:', businessObject.extensionElements)
  if (businessObject.extensionElements) {
    console.log('extensionElements存在，类型:', typeof businessObject.extensionElements)
    const values = businessObject.extensionElements.values || []
    console.log('extensionElements.values:', values)
    console.log('extensionElements.values类型:', typeof values)
    if (Array.isArray(values)) {
      console.log('extensionElements.values是数组，长度:', values.length)
      values.forEach((item, index) => {
        console.log(`extensionElement项[${index}]:`, item.$type, item)
        if (item.$type === 'camunda:Properties') {
          console.log('找到camunda:Properties')
          const properties = item.values || []
          console.log('properties:', properties)
          properties.forEach((prop, propIndex) => {
            console.log(`property[${propIndex}]:`, prop.name, '=', prop.value)
          })
        }
      })
    }
  } else {
    console.log('extensionElements不存在或为null')
  }
  
  const typeMap = {
    'bpmn:StartEvent': '开始事件',
    'bpmn:EndEvent': '结束事件',
    'bpmn:UserTask': '用户任务',
    'bpmn:Task': '用户任务',
    'bpmn:ServiceTask': '服务任务',
    'bpmn:ExclusiveGateway': '排他网关',
    'bpmn:ParallelGateway': '并行网关',
    'bpmn:SequenceFlow': '连线'
  }
  
  // 从扩展属性中读取自定义属性
  let parentOrgType = ''
  let orgLevels = []
  
  if (businessObject.extensionElements) {
    const values = businessObject.extensionElements.values || []
    values.forEach(item => {
      if (item.$type === 'camunda:Properties') {
        const properties = item.values || []
        properties.forEach(prop => {
          if (prop.name === 'parentOrgType') {
            parentOrgType = prop.value || ''
          } else if (prop.name === 'orgLevels') {
            try {
              orgLevels = JSON.parse(prop.value || '[]')
            } catch (e) {
              orgLevels = []
            }
          }
        })
      }
    })
  }
  
  // 处理候选组：确保始终是数组格式
  let candidateGroups = []
  
  console.log('读取候选组 - 步骤1: 检查 businessObject.candidateGroups')
  console.log('  businessObject.candidateGroups:', businessObject.candidateGroups)
  
  // 首先尝试从 businessObject 的直接属性获取
  if (businessObject.candidateGroups) {
    if (Array.isArray(businessObject.candidateGroups)) {
      candidateGroups = [...businessObject.candidateGroups]
      console.log('  从数组获取:', candidateGroups)
    } else if (typeof businessObject.candidateGroups === 'string') {
      candidateGroups = businessObject.candidateGroups.split(',').map(g => g.trim()).filter(g => g)
      console.log('  从字符串获取:', candidateGroups)
    }
  }
  
  console.log('读取候选组 - 步骤2: 检查 extensionElements')
  
  // 如果没有找到，尝试从 extensionElements 中获取
  if (candidateGroups.length === 0 && businessObject.extensionElements) {
    const values = businessObject.extensionElements.values || []
    console.log('  extensionElements.values:', values)
    console.log('  values 类型:', typeof values)
    console.log('  是否为数组:', Array.isArray(values))
    console.log('  values.length:', values.length)
    console.log('  values的所有键:', values.length > 0 ? Object.keys(values[0]) : 'N/A')
    
    if (Array.isArray(values)) {
      for (let i = 0; i < values.length; i++) {
        const item = values[i]
        console.log(`  values[${i}]:`, item.$type, item)
        console.log(`    item.values:`, item.values)
        console.log(`    item.values.length:`, item.values ? item.values.length : 'N/A')
        if (item.$type === 'camunda:Properties') {
          const properties = item.values || []
          console.log(`    camunda:Properties.values:`, properties)
          console.log(`    properties.length:`, properties.length)
          if (Array.isArray(properties)) {
            for (let j = 0; j < properties.length; j++) {
              const prop = properties[j]
              console.log(`      property[${j}]:`, prop.name, '=', prop.value)
              if (prop.name === 'candidateGroups' && prop.value) {
                candidateGroups = prop.value.split(',').map(g => g.trim()).filter(g => g)
                console.log('      找到候选组:', candidateGroups)
                break
              }
            }
          }
          if (candidateGroups.length > 0) break
        }
      }
    }
  }
  
  console.log('最终候选组:', candidateGroups)
  
  elementProperties.value = {
    id: element.id,
    name: businessObject.name || '',
    type: businessObject.$type,
    typeName: typeMap[businessObject.$type] || businessObject.$type,
    candidateGroups: candidateGroups,
    conditionExpression: businessObject.conditionExpression?.body || '',
    conditionVariable: '',
    parentOrgType: parentOrgType,
    orgLevels: orgLevels
  }
}

const updateElementName = () => {
  if (!selectedElement.value) return
  
  const modeling = bpmnModeler.get('modeling')
  modeling.updateProperties(selectedElement.value, {
    name: elementProperties.value.name
  })
}

const updateCandidateGroups = () => {
  if (!selectedElement.value) return
  
  const modeling = bpmnModeler.get('modeling')
  const moddle = bpmnModeler.get('moddle')
  
  // 创建普通数组，避免Vue代理冲突
  const groups = elementProperties.value.candidateGroups || []
  const candidateGroupsValue = groups.map(g => String(g)).join(',')
  
  // 使用 setTimeout 避免响应式冲突
  setTimeout(() => {
    try {
      const element = selectedElement.value
      const businessObject = element.businessObject
      
      // 获取或创建 extensionElements
      let extensionElements = businessObject.extensionElements
      if (!extensionElements) {
        extensionElements = moddle.create('bpmn:ExtensionElements')
        businessObject.extensionElements = extensionElements
      }
      
      // 查找或创建 camunda:Properties
      let camundaProperties = null
      const values = extensionElements.get('values') || []
      for (const item of values) {
        if (item.$type === 'camunda:Properties') {
          camundaProperties = item
          break
        }
      }
      
      if (!camundaProperties) {
        camundaProperties = moddle.create('camunda:Properties')
        values.push(camundaProperties)
        extensionElements.set('values', values)
      }
      
      // 查找或创建 candidateGroups 属性
      const properties = camundaProperties.get('values') || []
      let candidateGroupsProperty = null
      for (const prop of properties) {
        if (prop.name === 'candidateGroups') {
          candidateGroupsProperty = prop
          break
        }
      }
      
      if (candidateGroupsProperty) {
        candidateGroupsProperty.value = candidateGroupsValue || ''
      } else {
        candidateGroupsProperty = moddle.create('camunda:Property', {
          name: 'candidateGroups',
          value: candidateGroupsValue || ''
        })
        properties.push(candidateGroupsProperty)
      }
      
      camundaProperties.set('values', properties)
      
      // 同时也设置到 businessObject 的直接属性上（用于回显）
      businessObject.candidateGroups = candidateGroupsValue || undefined
      
      // 触发更新事件
      const eventBus = bpmnModeler.get('eventBus')
      eventBus.fire('element.changed', { element })
      eventBus.fire('propertiesPanel.changed', { element })
      
      console.log('候选组已更新:', candidateGroupsValue)
    } catch (error) {
      console.error('更新候选组失败:', error)
      console.error('错误堆栈:', error.stack)
    }
  }, 0)
}

const updateConditionExpression = () => {
  if (!selectedElement.value) return
  
  const modeling = bpmnModeler.get('modeling')
  const moddle = bpmnModeler.get('moddle')
  
  // 创建条件表达式对象
  const conditionExpression = moddle.create('bpmn:FormalExpression', {
    body: elementProperties.value.conditionExpression
  })
  
  modeling.updateProperties(selectedElement.value, {
    conditionExpression: conditionExpression
  })
}

const updateCustomProperties = () => {
  if (!selectedElement.value) return
  
  // 使用 setTimeout 避免响应式冲突
  setTimeout(() => {
    try {
      const moddle = bpmnModeler.get('moddle')
      const businessObject = selectedElement.value.businessObject
      
      // 创建 extensionElements
      const extensionElements = moddle.create('bpmn:ExtensionElements')
      const values = []
      
      // 添加 parentOrgType 属性
      if (elementProperties.value.parentOrgType) {
        const properties = moddle.create('camunda:Properties', {
          values: [
            moddle.create('camunda:Property', {
              name: 'parentOrgType',
              value: elementProperties.value.parentOrgType
            })
          ]
        })
        values.push(properties)
      }
      
      // 添加 orgLevels 属性
      if (elementProperties.value.orgLevels && elementProperties.value.orgLevels.length > 0) {
        const properties = moddle.create('camunda:Properties', {
          values: [
            moddle.create('camunda:Property', {
              name: 'orgLevels',
              value: JSON.stringify(elementProperties.value.orgLevels)
            })
          ]
        })
        values.push(properties)
      }
      
      // 设置 values
      Object.defineProperty(extensionElements, 'values', {
        value: values,
        writable: true,
        configurable: true
      })
      
      // 设置 extensionElements
      Object.defineProperty(businessObject, 'extensionElements', {
        value: extensionElements,
        writable: true,
        configurable: true
      })
      
      // 触发更新
      const eventBus = bpmnModeler.get('eventBus')
      eventBus.fire('element.changed', { element: selectedElement.value })
      
    } catch (error) {
      console.error('更新自定义属性失败:', error)
    }
  }, 0)
}

// 移除 watch，改为手动调用

const loadExample = async () => {
  processInfo.value = {
    key: 'green_identification',
    name: '绿色贷款认定流程',
    description: '绿色贷款认定审批流程'
  }
  
  try {
    await bpmnModeler.importXML(exampleBpmn)
    bpmnModeler.get('canvas').zoom('fit-viewport')
    ElMessage.success('示例流程加载成功')
  } catch (error) {
    console.error('加载示例失败:', error)
    ElMessage.error('加载示例失败')
  }
}

// 从 BPMN 模型中提取任务节点信息
const extractTaskNodes = () => {
  if (!bpmnModeler) return []
  
  const elementRegistry = bpmnModeler.get('elementRegistry')
  const elements = elementRegistry.getAll()
  
  console.log('所有元素类型:', elements.map(el => ({ id: el.id, type: el.type, name: el.businessObject?.name })))
  
  const taskNodes = []
  let sequence = 0
  
  // 找到所有用户任务（包括bpmn:Task和bpmn:UserTask）
  const userTasks = elements.filter(element => {
    return element.type === 'bpmn:UserTask' || element.type === 'bpmn:Task'
  })
  
  console.log('找到的用户任务数量:', userTasks.length)
  
  userTasks.forEach(task => {
    const businessObject = task.businessObject
    sequence++
    
    console.log('处理任务:', businessObject.id, businessObject.name, '候选组:', businessObject.candidateGroups)
    
    // 提取候选组
    let candidateGroups = []
    if (businessObject.candidateGroups) {
      if (typeof businessObject.candidateGroups === 'string') {
        candidateGroups = businessObject.candidateGroups.split(',').map(g => g.trim())
      } else if (Array.isArray(businessObject.candidateGroups)) {
        candidateGroups = [...businessObject.candidateGroups]
      }
    }
    
    // 查找角色ID
    let roleId = null
    if (candidateGroups.length > 0) {
      const role = roles.value.find(r => candidateGroups.includes(r.name))
      if (role) {
        roleId = role.id
      }
    }
    
    // 提取机构层级
    let orgLevel = null
    if (businessObject.extensionElements) {
      const values = businessObject.extensionElements.values || []
      values.forEach(item => {
        if (item.$type === 'camunda:Properties') {
          const properties = item.values || []
          properties.forEach(prop => {
            if (prop.name === 'orgLevels') {
              try {
                const orgLevels = JSON.parse(prop.value || '[]')
                if (orgLevels.length > 0) {
                  orgLevel = orgLevels.join(',')
                }
              } catch (e) {
                console.error('解析机构层级失败:', e)
              }
            }
          })
        }
      })
    }
    
    taskNodes.push({
      node_id: businessObject.id,
      node_name: businessObject.name || '',
      node_type: 'UserTask',
      role_id: roleId,
      org_level: orgLevel,
      is_skip_if_empty: true,
      sequence: sequence
    })
  })
  
  return taskNodes
}

const saveProcess = async () => {
  try {
    console.log('saveProcess 开始执行')
    console.log('当前模式:', mode.value)
    console.log('definitionId:', definitionId.value)
    console.log('processName:', processName.value)
    
    // 验证候选组是否正确保存
    if (bpmnModeler) {
      const elementRegistry = bpmnModeler.get('elementRegistry')
      const elements = elementRegistry.getAll()
      const userTasks = elements.filter(el => el.type === 'bpmn:Task' || el.type === 'bpmn:UserTask')
      console.log('保存前验证候选组:')
      userTasks.forEach(task => {
        console.log(`  ${task.businessObject.name}: candidateGroups =`, task.businessObject.candidateGroups)
      })
    }
    
    if (!processName.value.trim()) {
      ElMessage.warning('请输入流程名称')
      return
    }

    if (!bpmnModeler) {
      ElMessage.error('流程设计器未初始化，请刷新页面重试')
      return
    }

    const { xml } = await bpmnModeler.saveXML({ format: true })
    console.log('BPMN XML 长度:', xml.length)
    
    // 如果角色列表为空，尝试重新加载
    if (roles.value.length === 0) {
      console.log('角色列表为空，尝试重新加载...')
      await loadRoles()
    }
    
    // 提取任务节点信息
    const taskNodes = extractTaskNodes()
    console.log('提取的任务节点:', taskNodes)
    
    let savedDefinitionId = null
    
    if (mode.value === 'edit' && definitionId.value) {
      // 编辑模式：尝试更新现有版本
      console.log('尝试更新现有流程版本:', definitionId.value)
      console.log('调用 updateDefinition API')
      try {
        const result = await updateDefinition(definitionId.value, {
          bpmn_xml: xml
        })
        console.log('updateDefinition 完成，返回结果:', result)
        savedDefinitionId = definitionId.value
        
        // 更新任务节点
        if (taskNodes.length > 0) {
          console.log('调用 createTaskNodes API，参数:', taskNodes)
          const nodesResult = await createTaskNodes(definitionId.value, taskNodes)
          console.log('createTaskNodes 完成，返回结果:', nodesResult)
        }
        
        ElMessage.success('流程更新成功')
      } catch (updateError) {
        // 如果是因为有流程实例而无法更新，则创建新版本
        if (updateError.response?.status === 400 && 
            updateError.response?.data?.detail?.includes('已绑定')) {
          console.log('流程已绑定实例，创建新版本')
          ElMessage.info('流程已绑定实例，正在创建新版本...')
          
          const processKey = processName.value.trim().replace(/\s+/g, '_').toLowerCase()
          const definitionData = {
            key: processKey,
            name: processName.value.trim(),
            description: '',
            bpmn_xml: xml
          }
          
          const result = await createDefinition(definitionData)
          console.log('createDefinition 完成，返回结果:', result)
          savedDefinitionId = result.id
          
          // 创建任务节点
          if (taskNodes.length > 0) {
            console.log('调用 createTaskNodes API，参数:', taskNodes)
            await createTaskNodes(savedDefinitionId, taskNodes)
            console.log('createTaskNodes 完成')
          }
          
          ElMessage.success('新版本创建成功')
        } else {
          // 其他错误，直接抛出
          throw updateError
        }
      }
    } else {
      // 新建模式：创建新版本
      console.log('新建模式，创建新版本')
      const processKey = processName.value.trim().replace(/\s+/g, '_').toLowerCase()
      
      const definitionData = {
        key: processKey,
        name: processName.value.trim(),
        description: '',
        bpmn_xml: xml
      }
      
      console.log('保存流程数据:', definitionData)
      const result = await createDefinition(definitionData)
      console.log('createDefinition 完成，返回结果:', result)
      savedDefinitionId = result.id
      
      // 创建任务节点
      if (taskNodes.length > 0) {
        console.log('调用 createTaskNodes API，参数:', taskNodes)
        await createTaskNodes(savedDefinitionId, taskNodes)
        console.log('createTaskNodes 完成')
      }
      
      ElMessage.success('流程保存成功')
    }
  } catch (error) {
    console.error('保存流程失败:', error)
    console.error('错误详情:', error.response?.data)
    console.error('错误详情数组:', error.response?.data?.detail)
    
    // 处理错误信息
    if (error.response && error.response.status === 400) {
      const errorMessage = error.response.data.detail || '保存失败'
      ElMessage.error('保存流程失败: ' + errorMessage)
    } else if (error.response && error.response.status === 422) {
      const errorDetails = error.response.data.detail
      if (Array.isArray(errorDetails)) {
        const errorMessages = errorDetails.map(err => err.msg || err.message || JSON.stringify(err)).join('; ')
        ElMessage.error('保存流程失败: ' + errorMessages)
      } else {
        ElMessage.error('保存流程失败: ' + (errorDetails || '验证错误'))
      }
    } else if (error.response && error.response.status === 500) {
      ElMessage.error('保存流程失败: 服务器内部错误')
    } else {
      ElMessage.error('保存流程失败: ' + (error.message || '未知错误'))
    }
  }
}

const exportBpmn = () => {
  try {
    const { xml } = bpmnModeler.saveXML({ format: true })
    
    const blob = new Blob([xml], { type: 'application/xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = (processInfo.value.name || 'workflow') + '.bpmn'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    ElMessage.success('流程导出成功')
  } catch (error) {
    console.error('导出流程失败:', error)
    ElMessage.error('导出流程失败')
  }
}

const goBack = () => {
  router.push('/workflow/management')
}

const confirmProcessInfo = () => {
  ElMessage.success('流程信息已保存')
  dialogVisible.value = false
}

onMounted(() => {
  loadRoles()
  initModeler()
})

onBeforeUnmount(() => {
  if (bpmnModeler) {
    bpmnModeler.destroy()
  }
})
</script>

<style scoped>
.workflow-designer-container {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.designer-header {
  background: white;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-info {
  display: flex;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.designer-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 左侧工具栏 */
.left-toolbar {
  width: 200px;
  background: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.toolbar-title {
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  border-bottom: 1px solid #f0f0f0;
}

.toolbar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.toolbar-section-title {
  padding: 12px 8px 8px;
  font-size: 12px;
  font-weight: 600;
  color: #999;
}

.tool-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 8px 0;
}

.tool-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
  color: #666;
}

.tool-item:hover {
  background: #f5f5f5;
}

.tool-item.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.tool-item .el-icon {
  font-size: 16px;
}

/* 中间设计区域 */
.canvas-wrapper {
  flex: 1;
  background: #fff;
  position: relative;
  overflow: hidden;
}

.canvas-container {
  width: 100%;
  height: 100%;
}

/* 隐藏 BPMN.js 默认的工具栏 */
.canvas-container :deep(.djs-palette) {
  display: none !important;
}

/* 右侧属性栏 */
.right-panel {
  width: 300px;
  background: white;
  border-left: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.panel-title {
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  border-bottom: 1px solid #f0f0f0;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.properties-form {
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
  
  :deep(.el-form-item__label) {
    font-size: 13px;
    color: #666;
  }
}
</style>