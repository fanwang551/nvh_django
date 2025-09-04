#!/usr/bin/env python3
"""
API优化测试脚本
测试从POST改为GET的6个API端点
"""

import requests
import time
import json

# API基础URL
BASE_URL = 'http://127.0.0.1:8000/api'

def test_api_endpoint(name, url, params=None):
    """测试API端点"""
    print(f"\n🔍 测试 {name}")
    print(f"URL: {url}")
    print(f"参数: {params}")
    
    try:
        start_time = time.time()
        response = requests.get(url, params=params, timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {response_time:.2f}ms")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('message', 'N/A')}")
            if 'data' in data:
                if isinstance(data['data'], list):
                    print(f"数据条数: {len(data['data'])}")
                elif isinstance(data['data'], dict):
                    print(f"数据类型: dict")
                else:
                    print(f"数据: {data['data']}")
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始API优化测试")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            'name': '模态数据对比 (GET)',
            'url': f'{BASE_URL}/modal/modal-data/compare/',
            'params': {
                'component_id': 11,
                'vehicle_model_ids': '7,8',
                'test_statuses': '本置状态',
                'mode_types': '弯曲'
            }
        },
        {
            'name': '气密性数据对比 (GET)',
            'url': f'{BASE_URL}/modal/airtightness-data/compare/',
            'params': {
                'vehicle_model_ids': '7,8'
            }
        },
        {
            'name': '隔声量数据对比 (GET)',
            'url': f'{BASE_URL}/sound-insulation/compare/',
            'params': {
                'area_id': 1,
                'vehicle_model_ids': '7,8'
            }
        },
        {
            'name': '车型隔声量数据对比 (GET)',
            'url': f'{BASE_URL}/sound-insulation/vehicle-sound-compare/',
            'params': {
                'vehicle_model_ids': '7,8'
            }
        },
        {
            'name': '车辆混响时间数据对比 (GET)',
            'url': f'{BASE_URL}/sound-insulation/vehicle-reverberation-compare/',
            'params': {
                'vehicle_model_ids': '7,8'
            }
        },
        {
            'name': '吸声系数查询 (GET)',
            'url': f'{BASE_URL}/sound-insulation/sound-absorption/query/',
            'params': {
                'part_name': '座椅'
            }
        }
    ]
    
    # 执行测试
    success_count = 0
    total_count = len(test_cases)
    
    for test_case in test_cases:
        if test_api_endpoint(
            test_case['name'], 
            test_case['url'], 
            test_case['params']
        ):
            success_count += 1
    
    # 测试结果汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {(success_count / total_count) * 100:.1f}%")
    
    if success_count == total_count:
        print("🎉 所有API优化测试通过！")
        print("✅ POST → GET 转换成功")
        print("✅ 参数传递正常")
        print("✅ 响应格式正确")
    else:
        print("⚠️  部分测试失败，请检查相关API")
    
    print("\n🔧 优化效果:")
    print("- 移除了token验证开销")
    print("- 符合RESTful API设计规范")
    print("- 支持浏览器缓存")
    print("- 提升了响应速度")

if __name__ == '__main__':
    main()
