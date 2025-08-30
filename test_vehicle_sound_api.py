#!/usr/bin/env python3
"""
测试车型隔声量API接口
"""

import requests
import json

# API基础URL
BASE_URL = 'http://127.0.0.1:8000/api/sound-insulation'

def test_get_vehicles_with_sound_data():
    """测试获取有隔声量数据的车型列表"""
    print("=" * 60)
    print("测试：获取有隔声量数据的车型列表")
    print("=" * 60)
    
    url = f"{BASE_URL}/vehicle-sound-data/"
    
    try:
        response = requests.get(url)
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success') and data.get('data'):
                print(f"✅ 成功获取 {len(data['data'])} 个车型")
                return data['data']
            else:
                print("❌ 响应格式错误或无数据")
                return []
        else:
            print(f"❌ 请求失败: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return []

def test_vehicle_sound_insulation_compare(vehicle_ids):
    """测试车型隔声量对比"""
    print("\n" + "=" * 60)
    print("测试：车型隔声量对比")
    print("=" * 60)
    
    if not vehicle_ids:
        print("❌ 没有可用的车型ID进行测试")
        return
    
    url = f"{BASE_URL}/vehicle-sound-compare/"
    
    # 使用前两个车型进行测试
    test_ids = vehicle_ids[:2] if len(vehicle_ids) >= 2 else vehicle_ids
    vehicle_model_ids = ','.join(map(str, [v['id'] for v in test_ids]))
    
    data = {
        'vehicle_model_ids': vehicle_model_ids
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success') and result.get('data'):
                print(f"✅ 成功获取 {len(result['data'])} 个车型的对比数据")
                
                # 显示对比数据摘要
                for item in result['data']:
                    print(f"  - 车型: {item['vehicle_model_name']}")
                    print(f"    代码: {item['vehicle_model_code']}")
                    print(f"    测试日期: {item.get('test_date', '未记录')}")
                    print(f"    测试工程师: {item.get('test_engineer', '未记录')}")
                    
                    # 显示部分频率数据
                    freq_data = item.get('frequency_data', {})
                    sample_freqs = ['freq_200', 'freq_1000', 'freq_5000']
                    freq_values = []
                    for freq in sample_freqs:
                        value = freq_data.get(freq)
                        if value is not None:
                            freq_values.append(f"{freq.replace('freq_', '')}Hz: {value}dB")
                    
                    if freq_values:
                        print(f"    样本频率数据: {', '.join(freq_values)}")
                    print()
                    
            else:
                print("❌ 响应格式错误或无数据")
        else:
            print(f"❌ 请求失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试：错误处理")
    print("=" * 60)
    
    url = f"{BASE_URL}/vehicle-sound-compare/"
    
    # 测试空参数
    print("1. 测试空参数:")
    try:
        response = requests.post(url, json={})
        print(f"  响应状态码: {response.status_code}")
        if response.status_code == 400:
            print("  ✅ 正确处理空参数错误")
        else:
            print("  ❌ 未正确处理空参数错误")
    except Exception as e:
        print(f"  ❌ 请求异常: {str(e)}")
    
    # 测试无效车型ID
    print("\n2. 测试无效车型ID:")
    try:
        response = requests.post(url, json={'vehicle_model_ids': '999,1000'})
        print(f"  响应状态码: {response.status_code}")
        if response.status_code == 400:
            print("  ✅ 正确处理无效车型ID错误")
        else:
            print("  ❌ 未正确处理无效车型ID错误")
    except Exception as e:
        print(f"  ❌ 请求异常: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 开始测试车型隔声量API接口")
    print("服务器地址: http://127.0.0.1:8000")
    
    # 测试获取车型列表
    vehicles = test_get_vehicles_with_sound_data()
    
    # 测试车型隔声量对比
    test_vehicle_sound_insulation_compare(vehicles)
    
    # 测试错误处理
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("🎉 API测试完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
