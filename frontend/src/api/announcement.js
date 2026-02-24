import request from '@/utils/request'

export function getAnnouncements(params) {
  return request({
    url: '/announcements',
    method: 'get',
    params
  })
}

export function getAnnouncement(id) {
  return request({
    url: `/announcements/${id}`,
    method: 'get'
  })
}

export function createAnnouncement(data) {
  return request({
    url: '/announcements/',
    method: 'post',
    data
  })
}

export function updateAnnouncement(id, data) {
  return request({
    url: `/announcements/${id}`,
    method: 'put',
    data
  })
}

export function deleteAnnouncement(id) {
  return request({
    url: `/announcements/${id}`,
    method: 'delete'
  })
}

export function uploadCoverImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/announcements/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getScrollAnnouncements() {
  return request({
    url: '/announcements/scroll/active',
    method: 'get'
  })
}