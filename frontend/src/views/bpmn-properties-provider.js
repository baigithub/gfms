/**
 * BPMN 属性提供者
 * 为流程设计器提供自定义属性配置
 */
export default function PropertiesProvider(eventBus, translate, moddle) {
  this.getTabs = function(element) {
    // 只为用户任务显示自定义属性
    if (element.type !== 'bpmn:UserTask') {
      return []
    }

    return [
      {
        id: 'taskAssignment',
        label: translate('任务分配'),
        groups: [
          {
            id: 'assigneeConfig',
            label: translate('分配配置'),
            entries: [
              {
                id: 'assigneeType',
                label: translate('分配类型'),
                component: 'select',
                options: [
                  { value: 'initiator', label: translate('流程发起人') },
                  { value: 'candidateGroups', label: translate('候选组') },
                  { value: 'candidateUsers', label: translate('候选人') }
                ],
                modelProperty: 'assigneeType'
              },
              {
                id: 'candidateGroups',
                label: translate('候选组'),
                component: 'textfield',
                modelProperty: 'camunda:candidateGroups',
                get: function(element, node) {
                  const candidateGroups = element.businessObject.get('camunda:candidateGroups')
                  return { candidateGroups: candidateGroups || '' }
                },
                set: function(element, values, node) {
                  const modeling = eventBus.get('modeling')
                  modeling.updateProperties(element, {
                    'camunda:candidateGroups': values.candidateGroups || undefined
                  })
                  return {
                    camunda: {
                      candidateGroups: values.candidateGroups || undefined
                    }
                  }
                }
              },
              {
                id: 'assignee',
                label: translate('分配给'),
                component: 'textfield',
                modelProperty: 'camunda:assignee',
                get: function(element, node) {
                  const assignee = element.businessObject.get('camunda:assignee')
                  return { assignee: assignee || '' }
                },
                set: function(element, values, node) {
                  const modeling = eventBus.get('modeling')
                  modeling.updateProperties(element, {
                    'camunda:assignee': values.assignee || undefined
                  })
                  return {
                    camunda: {
                      assignee: values.assignee || undefined
                    }
                  }
                }
              }
            ]
          },
          {
            id: 'orgConfig',
            label: translate('机构配置'),
            entries: [
              {
                id: 'orgLevel',
                label: translate('机构层级'),
                component: 'select',
                options: [
                  { value: '1', label: translate('一级分行/总行') },
                  { value: '2', label: translate('二级分行') },
                  { value: '3', label: translate('支行') }
                ],
                get: function(element, node) {
                  const orgLevel = element.businessObject.get('camunda:orgLevel')
                  return { orgLevel: orgLevel || '1' }
                },
                set: function(element, values, node) {
                  const modeling = eventBus.get('modeling')
                  modeling.updateProperties(element, {
                    'camunda:orgLevel': values.orgLevel
                  })
                  return {
                    camunda: {
                      orgLevel: values.orgLevel
                    }
                  }
                }
              },
              {
                id: 'orgRelation',
                label: translate('机构关系'),
                component: 'select',
                options: [
                  { value: 'self', label: translate('当前机构') },
                  { value: 'parent', label: translate('父级机构') },
                  { value: 'ancestor', label: translate('上级机构') }
                ],
                get: function(element, node) {
                  const orgRelation = element.businessObject.get('camunda:orgRelation')
                  return { orgRelation: orgRelation || 'self' }
                },
                set: function(element, values, node) {
                  const modeling = eventBus.get('modeling')
                  modeling.updateProperties(element, {
                    'camunda:orgRelation': values.orgRelation
                  })
                  return {
                    camunda: {
                      orgRelation: values.orgRelation
                    }
                  }
                }
              }
            ]
          },
          {
            id: 'advanced',
            label: translate('高级设置'),
            entries: [
              {
                id: 'dueDate',
                label: translate('到期时间'),
                component: 'textfield',
                modelProperty: 'camunda:dueDate',
                get: function(element, node) {
                  const dueDate = element.businessObject.get('camunda:dueDate')
                  return { dueDate: dueDate || '' }
                },
                set: function(element, values, node) {
                  const modeling = eventBus.get('modeling')
                  modeling.updateProperties(element, {
                    'camunda:dueDate': values.dueDate || undefined
                  })
                  return {
                    camunda: {
                      dueDate: values.dueDate || undefined
                    }
                  }
                }
              },
              {
                id: 'priority',
                label: translate('优先级'),
                component: 'number',
                modelProperty: 'camunda:priority',
                get: function(element, node) {
                  const priority = element.businessObject.get('camunda:priority')
                  return { priority: priority || '50' }
                },
                set: function(element, values, node) {
                  const modeling = eventBus.get('modeling')
                  modeling.updateProperties(element, {
                    'camunda:priority': values.priority
                  })
                  return {
                    camunda: {
                      priority: values.priority
                    }
                  }
                }
              }
            ]
          }
        ]
      }
    ]
  }

  this.isAvailable = function(element) {
    return element.type === 'bpmn:UserTask'
  }
}

PropertiesProvider.$inject = ['eventBus', 'translate', 'moddle']