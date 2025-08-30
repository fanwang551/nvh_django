#!/usr/bin/env python3
"""
测试前端页面访问
"""

import requests
import time

def test_frontend_access():
    """测试前端页面是否可以访问"""
    print("=" * 60)
    print("测试前端页面访问")
    print("=" * 60)
    
    frontend_url = 'http://localhost:5177'
    
    try:
        print(f"正在测试前端服务: {frontend_url}")
        response = requests.get(frontend_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ 前端服务正常运行")
            print(f"响应状态码: {response.status_code}")
            print(f"页面标题: {response.text[:200]}...")
        else:
            print(f"❌ 前端服务响应异常: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到前端服务，请确保前端服务正在运行")
    except requests.exceptions.Timeout:
        print("❌ 前端服务响应超时")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def test_api_connectivity():
    """测试API连通性"""
    print("\n" + "=" * 60)
    print("测试API连通性")
    print("=" * 60)
    
    api_url = 'http://127.0.0.1:8000/api/sound-insulation/vehicle-sound-data/'
    
    try:
        print(f"正在测试API接口: {api_url}")
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API接口正常工作")
                print(f"获取到 {len(data.get('data', []))} 个车型数据")
            else:
                print("❌ API响应格式异常")
        else:
            print(f"❌ API响应异常: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端API，请确保后端服务正在运行")
    except requests.exceptions.Timeout:
        print("❌ API响应超时")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始测试前端和API连通性")
    
    # 测试前端页面访问
    test_frontend_access()
    
    # 测试API连通性
    test_api_connectivity()
    
    print("\n" + "=" * 60)
    print("📋 访问信息")
    print("=" * 60)
    print("前端地址: http://localhost:5177")
    print("后端地址: http://127.0.0.1:8000")
    print("功能路径: 业务中心 → 车型隔声量查询")
    print("直接访问: http://localhost:5177/business/vehicle-sound-insulation-query")
    print("\n🎉 测试完成！")

if __name__ == '__main__':
    main()
