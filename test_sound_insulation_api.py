#!/usr/bin/env python3
"""
测试隔声量API功能
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/sound-insulation"

def test_sound_insulation_apis():
    """测试隔声量相关API"""
    
    print("🚀 开始测试隔声量API功能...")
    
    # 1. 测试获取区域列表
    print(f"\n1️⃣ 测试获取区域列表")
    try:
        response = requests.get(f"{BASE_URL}/areas/")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            if data.get('success') and data.get('data'):
                areas = data['data']
                print(f"✅ 成功获取 {len(areas)} 个区域")
                
                # 选择第一个区域进行后续测试
                if areas:
                    area_id = areas[0]['id']
                    area_name = areas[0]['area_name']
                    print(f"📍 选择区域: {area_name} (ID: {area_id})")
                    
                    # 2. 测试根据区域获取车型
                    print(f"\n2️⃣ 测试根据区域获取车型列表")
                    try:
                        response = requests.get(f"{BASE_URL}/vehicles/", params={'area_id': area_id})
                        print(f"状态码: {response.status_code}")
                        
                        if response.status_code == 200:
                            data = response.json()
                            print(f"响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                            
                            if data.get('success') and data.get('data'):
                                vehicles = data['data']
                                print(f"✅ 成功获取 {len(vehicles)} 个车型")
                                
                                if len(vehicles) >= 2:
                                    # 选择前两个车型进行对比测试
                                    vehicle_ids = [str(v['id']) for v in vehicles[:2]]
                                    vehicle_names = [v['vehicle_model_name'] for v in vehicles[:2]]
                                    print(f"🚗 选择车型: {', '.join(vehicle_names)}")
                                    
                                    # 3. 测试隔声量对比
                                    print(f"\n3️⃣ 测试隔声量对比功能")
                                    try:
                                        compare_data = {
                                            'area_id': area_id,
                                            'vehicle_model_ids': ','.join(vehicle_ids)
                                        }
                                        
                                        response = requests.post(f"{BASE_URL}/compare/", 
                                                               json=compare_data,
                                                               headers={'Content-Type': 'application/json'})
                                        print(f"状态码: {response.status_code}")
                                        
                                        if response.status_code == 200:
                                            data = response.json()
                                            print(f"✅ 对比功能测试成功")
                                            
                                            if data.get('success') and data.get('data'):
                                                compare_results = data['data']
                                                print(f"📊 获取到 {len(compare_results)} 条对比数据")
                                                
                                                # 显示部分对比数据
                                                for result in compare_results:
                                                    print(f"   - {result['vehicle_model_name']}: {result['area_name']}")
                                                    freq_data = result['frequency_data']
                                                    sample_freqs = ['freq_1000', 'freq_2000', 'freq_4000']
                                                    for freq in sample_freqs:
                                                        value = freq_data.get(freq)
                                                        if value is not None:
                                                            print(f"     {freq}: {value} dB")
                                            else:
                                                print("⚠️ 未找到对比数据")
                                        else:
                                            print(f"❌ 对比功能测试失败: {response.text}")
                                    
                                    except Exception as e:
                                        print(f"❌ 对比功能测试异常: {str(e)}")
                                else:
                                    print("⚠️ 车型数量不足，无法进行对比测试")
                            else:
                                print("⚠️ 该区域暂无车型数据")
                        else:
                            print(f"❌ 获取车型列表失败: {response.text}")
                    
                    except Exception as e:
                        print(f"❌ 获取车型列表异常: {str(e)}")
            else:
                print("⚠️ 未获取到区域数据")
        else:
            print(f"❌ 获取区域列表失败: {response.text}")
    
    except Exception as e:
        print(f"❌ 获取区域列表异常: {str(e)}")
    
    print(f"\n✨ API测试完成！")


def test_error_cases():
    """测试错误情况"""
    print(f"\n🔍 测试错误处理...")
    
    # 测试无效区域ID
    print(f"\n测试无效区域ID")
    try:
        response = requests.get(f"{BASE_URL}/vehicles/", params={'area_id': 999})
        print(f"状态码: {response.status_code}")
        if response.status_code == 400:
            print("✅ 正确处理了无效区域ID")
        else:
            print(f"⚠️ 未预期的响应: {response.text}")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
    
    # 测试空参数
    print(f"\n测试空参数")
    try:
        response = requests.post(f"{BASE_URL}/compare/", 
                               json={},
                               headers={'Content-Type': 'application/json'})
        print(f"状态码: {response.status_code}")
        if response.status_code == 400:
            print("✅ 正确处理了空参数")
        else:
            print(f"⚠️ 未预期的响应: {response.text}")
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")


if __name__ == '__main__':
    test_sound_insulation_apis()
    test_error_cases()
