import request from './index'

export const getUsers = (params) => {
  return request({
    url: '/system/users',
    method: 'get',
    params
  })
}

export const createUser = (data) => {
  return request({
    url: '/system/users',
    method: 'post',
    data
  })
}

export const updateUser = (userId, data) => {
  return request({
    url: `/system/users/${userId}`,
    method: 'put',
    data
  })
}

export const deleteUser = (userId) => {
  return request({
    url: `/system/users/${userId}`,
    method: 'delete'
  })
}

export const resetUserPassword = (userId) => {
  return request({
    url: `/system/users/${userId}/reset-password`,
    method: 'post'
  })
}

export const getRoles = () => {
  return request({
    url: '/system/roles',
    method: 'get'
  })
}

export const createRole = (data) => {
  return request({
    url: '/system/roles',
    method: 'post',
    data
  })
}

export const updateRole = (roleId, data) => {
  return request({
    url: `/system/roles/${roleId}`,
    method: 'put',
    data
  })
}

export const deleteRole = (roleId) => {
  return request({
    url: `/system/roles/${roleId}`,
    method: 'delete'
  })
}

export const getRoleDetail = (roleId) => {
  return request({
    url: `/system/roles/${roleId}`,
    method: 'get'
  })
}

export const getOrganizations = async (params) => {
  const response = await request({
    url: '/system/organizations',
    method: 'get',
    params
  })
  return response
}

export const createOrganization = (data) => {
  return request({
    url: '/system/organizations',
    method: 'post',
    data
  })
}

export const updateOrganization = (orgId, data) => {
  return request({
    url: `/system/organizations/${orgId}`,
    method: 'put',
    data
  })
}

export const deleteOrganization = (orgId) => {
  return request({
    url: `/system/organizations/${orgId}`,
    method: 'delete'
  })
}