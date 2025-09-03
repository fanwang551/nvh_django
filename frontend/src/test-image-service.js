// 测试图片服务的简单脚本
import { getImageUrl, getApiBaseUrl } from '@/utils/imageService'

console.log('=== 图片服务测试 ===')
console.log('API Base URL:', getApiBaseUrl())
console.log('环境变量 VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)

// 测试不同类型的路径
const testPaths = [
  '/media/images/test.jpg',
  'media/images/test.jpg',
  'http://example.com/test.jpg',
  'https://example.com/test.jpg',
  '',
  null,
  undefined
]

testPaths.forEach(path => {
  console.log(`输入: ${path} -> 输出: ${getImageUrl(path)}`)
})
