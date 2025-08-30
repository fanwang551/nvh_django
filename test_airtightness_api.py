#!/usr/bin/env python3
"""
气密性API测试脚本
"""
import requests
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api/modal"

def test_vehicle_models():
    """测试获取车型列表"""
    print("=== 测试获取车型列表 ===")
    url = f"{BASE_URL}/vehicle-models/"
    
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"消息: {data.get('message')}")
            print(f"车型数量: {len(data.get('data', []))}")
            
            # 显示前几个车型
            vehicles = data.get('data', [])[:3]
            for vehicle in vehicles:
                print(f"  - ID: {vehicle['id']}, 名称: {vehicle['vehicle_model_name']}")
            
            return [v['id'] for v in data.get('data', [])]
        else:
            print(f"请求失败: {response.text}")
            return []
            
    except Exception as e:
        print(f"请求异常: {e}")
        return []

def test_airtightness_compare(vehicle_ids):
    """测试气密性数据对比"""
    print("\n=== 测试气密性数据对比 ===")
    url = f"{BASE_URL}/airtightness-data/compare/"
    
    # 选择前2个车型进行对比
    test_ids = vehicle_ids[:2] if len(vehicle_ids) >= 2 else vehicle_ids
    
    if not test_ids:
        print("没有可用的车型ID进行测试")
        return
    
    payload = {
        "vehicle_model_ids": ",".join(map(str, test_ids))
    }
    
    print(f"请求参数: {payload}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            print(f"消息: {data.get('message')}")
            
            result = data.get('data', {})
            vehicle_models = result.get('vehicle_models', [])
            leakage_data = result.get('leakage_data', [])
            
            print(f"对比车型数量: {len(vehicle_models)}")
            for vm in vehicle_models:
                print(f"  - {vm['name']} (测试日期: {vm.get('test_date', '未知')})")
            
            print(f"泄漏量数据分类数量: {len(leakage_data)}")
            for category in leakage_data:
                print(f"  - {category['category']}: {len(category['items'])} 项")
                for item in category['items'][:2]:  # 只显示前2项
                    print(f"    * {item['name']}: {item['values']}")
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

def main():
    """主测试函数"""
    print("开始测试气密性API...")
    
    # 测试获取车型列表
    vehicle_ids = test_vehicle_models()
    
    if vehicle_ids:
        # 测试气密性数据对比
        test_airtightness_compare(vehicle_ids)
    else:
        print("无法获取车型列表，跳过对比测试")
    
    print("\n测试完成！")

if __name__ == "__main__":
    main()
