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
  // 优先使用环境变量；否则回退到当前页面来源，便于同网段访问和vite代理
  return import.meta.env.VITE_API_BASE_URL || (typeof window !== 'undefined' ? window.location.origin : '')
}

/**
 * 生成完整的图片URL
 * @param {string} filePath - 图片文件路径（相对路径）
 * @returns {string} 完整的图片URL
 */
export const getImageUrl = (filePath) => {
  // 如果没有文件路径，直接返回空字符串，交给上层通过 v-if 显示“无图”
  if (!filePath) {
    return ''
  }

  // 兼容后端传入非字符串类型（如数字、数组等），避免出现 startsWith 报错
  let path = typeof filePath === 'string' ? filePath : String(filePath)

  // 如果转换后仍然是空字符串或无效值，直接返回空字符串
  if (!path || typeof path !== 'string') {
    return ''
  }

  // 统一使用正斜杠，避免 Windows 路径分隔符影响 URL
  path = path.replace(/\\/g, '/')

  // 对包含中文或特殊字符的文件名做安全编码，只编码最后一段文件名，避免路径被整体编码
  const encodePathFileName = (rawPath) => {
    const segments = rawPath.split('/')
    if (!segments.length) return ''

    const fileName = segments.pop()
    if (!fileName) {
      return segments.join('/')
    }

    let encodedFileName
    try {
      // 先尝试解码，防止已经编码的路径被二次编码
      encodedFileName = encodeURIComponent(decodeURIComponent(fileName))
    } catch {
      encodedFileName = encodeURIComponent(fileName)
    }

    return [...segments, encodedFileName].join('/')
  }

  // 如果已经是完整的URL（http或https开头），直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) {
    try {
      const url = new URL(path)
      url.pathname = encodePathFileName(url.pathname)
      return url.toString()
    } catch {
      // 如果 URL 解析失败，退回到简单编码策略
      return encodePathFileName(path)
    }
  }

  // 如果是以/开头的相对路径，直接返回，让前端同源或网关代理处理（如Vite/Nginx的 /media 反代）
  if (path.startsWith('/')) {
    return `/${encodePathFileName(path.replace(/^\/+/, ''))}`
  }

  // 若是常见静态相对路径（不以/开头），补上前导/ 以便同源代理
  if (path.startsWith('media/') || path.startsWith('static/')) {
    return `/${encodePathFileName(path)}`
  }

  // 其他相对路径：拼接后端基础地址，并对文件名做编码
  const encodedRelativePath = encodePathFileName(path)
  return `${getApiBaseUrl()}/${encodedRelativePath}`
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
