/**
 * 图片服务工具类
 * 统一管理图片URL生成和处理逻辑
 */

import { ElMessage } from 'element-plus'

/**
 * 获取API基础URL
 * 从环境变量中读取，支持开发和生产环境切换
 */
const getApiBaseUrl = () => {
  return import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
}

/**
 * 生成完整的图片URL
 * @param {string} filePath - 图片文件路径（相对路径）
 * @returns {string} 完整的图片URL
 */
export const getImageUrl = (filePath) => {
  // 如果没有文件路径，返回空字符串
  if (!filePath) {
    return ''
  }

  // 如果已经是完整的URL（http或https开头），直接返回
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath
  }

  // 如果是相对路径（以/开头），拼接API基础URL
  if (filePath.startsWith('/')) {
    return `${getApiBaseUrl()}${filePath}`
  }

  // 如果是相对路径但不以/开头，添加/再拼接
  return `${getApiBaseUrl()}/${filePath}`
}

/**
 * 图片加载错误处理
 * @param {Event} event - 图片加载错误事件
 * @param {Object} options - 配置选项
 * @param {boolean} options.showMessage - 是否显示错误消息，默认true
 * @param {string} options.fallbackSrc - 备用图片地址
 */
export const handleImageError = (event, options = {}) => {
  const { showMessage = true, fallbackSrc = '' } = options
  
  console.error('图片加载失败:', event.target.src)
  
  // 显示错误消息
  if (showMessage) {
    ElMessage.error('图片加载失败')
  }
  
  // 设置备用图片
  if (fallbackSrc && event.target) {
    event.target.src = fallbackSrc
  }
}

/**
 * 预加载图片
 * @param {string} imageSrc - 图片地址
 * @returns {Promise} 预加载Promise
 */
export const preloadImage = (imageSrc) => {
  return new Promise((resolve, reject) => {
    if (!imageSrc) {
      reject(new Error('图片地址为空'))
      return
    }

    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error(`图片预加载失败: ${imageSrc}`))
    img.src = getImageUrl(imageSrc)
  })
}

/**
 * 批量预加载图片
 * @param {Array<string>} imageSrcs - 图片地址数组
 * @returns {Promise<Array>} 预加载结果数组
 */
export const preloadImages = async (imageSrcs) => {
  if (!Array.isArray(imageSrcs) || imageSrcs.length === 0) {
    return []
  }

  const promises = imageSrcs.map(src => 
    preloadImage(src).catch(error => {
      console.warn('图片预加载失败:', error.message)
      return null
    })
  )

  return Promise.all(promises)
}

/**
 * 检查图片是否存在
 * @param {string} imageSrc - 图片地址
 * @returns {Promise<boolean>} 图片是否存在
 */
export const checkImageExists = async (imageSrc) => {
  try {
    await preloadImage(imageSrc)
    return true
  } catch {
    return false
  }
}

// 导出默认对象，包含所有方法
export default {
  getImageUrl,
  handleImageError,
  preloadImage,
  preloadImages,
  checkImageExists,
  getApiBaseUrl
}
