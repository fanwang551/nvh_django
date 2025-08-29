#!/usr/bin/env python3
"""
NVH模态数据对比功能API测试脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api/modal"

def test_api_endpoints():
    """测试所有新增的API接口"""
    
    print("🚀 开始测试NVH模态数据对比功能API接口...")
    print("=" * 60)
    
    # 1. 测试获取零件列表
    print("\n1️⃣ 测试获取零件列表")
    try:
        response = requests.get(f"{BASE_URL}/components/")
        if response.status_code == 200:
            data = response.json()
            components = data.get('data', [])
            print(f"✅ 成功获取 {len(components)} 个零件")
            if components:
                component_id = components[0]['id']
                component_name = components[0]['component_name']
                print(f"   示例零件: {component_name} (ID: {component_id})")
            else:
                print("❌ 没有找到零件数据")
                return
        else:
            print(f"❌ 获取零件列表失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 2. 测试获取相关车型
    print(f"\n2️⃣ 测试获取零件 '{component_name}' 的相关车型")
    try:
        response = requests.get(f"{BASE_URL}/modal-data/related-vehicles/", 
                              params={'component_id': component_id})
        if response.status_code == 200:
            data = response.json()
            vehicles = data.get('data', [])
            print(f"✅ 成功获取 {len(vehicles)} 个相关车型")
            vehicle_ids = [str(v['id']) for v in vehicles[:2]]  # 取前2个车型
            vehicle_names = [v['vehicle_model_name'] for v in vehicles[:2]]
            print(f"   示例车型: {', '.join(vehicle_names)}")
        else:
            print(f"❌ 获取相关车型失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 3. 测试获取测试状态
    print(f"\n3️⃣ 测试获取测试状态选项")
    try:
        response = requests.get(f"{BASE_URL}/modal-data/test-statuses/", 
                              params={
                                  'component_id': component_id,
                                  'vehicle_model_ids': ','.join(vehicle_ids)
                              })
        if response.status_code == 200:
            data = response.json()
            test_statuses = data.get('data', [])
            print(f"✅ 成功获取 {len(test_statuses)} 个测试状态")
            print(f"   测试状态: {', '.join(test_statuses)}")
            selected_status = test_statuses[0] if test_statuses else None
        else:
            print(f"❌ 获取测试状态失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 4. 测试获取振型类型
    print(f"\n4️⃣ 测试获取振型类型选项")
    try:
        response = requests.get(f"{BASE_URL}/modal-data/mode-types/", 
                              params={
                                  'component_id': component_id,
                                  'vehicle_model_ids': ','.join(vehicle_ids),
                                  'test_statuses': selected_status
                              })
        if response.status_code == 200:
            data = response.json()
            mode_types = data.get('data', [])
            print(f"✅ 成功获取 {len(mode_types)} 个振型类型")
            print(f"   振型类型: {', '.join(mode_types[:3])}...")  # 只显示前3个
            selected_modes = mode_types[:2]  # 选择前2个振型进行对比
        else:
            print(f"❌ 获取振型类型失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 5. 测试模态数据对比
    print(f"\n5️⃣ 测试模态数据对比功能")
    try:
        compare_data = {
            'component_id': component_id,
            'vehicle_model_ids': ','.join(vehicle_ids),
            'test_statuses': selected_status,
            'mode_types': ','.join(selected_modes)
        }
        
        response = requests.post(f"{BASE_URL}/modal-data/compare/", 
                               json=compare_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            data = response.json()
            compare_result = data.get('data', [])
            print(f"✅ 成功获取 {len(compare_result)} 条对比数据")
            
            # 显示对比结果摘要
            if compare_result:
                print("\n📊 对比结果摘要:")
                for item in compare_result[:5]:  # 只显示前5条
                    print(f"   {item['display_name']} - {item['mode_type']}: {item['frequency']} Hz")
                if len(compare_result) > 5:
                    print(f"   ... 还有 {len(compare_result) - 5} 条数据")
        else:
            print(f"❌ 模态数据对比失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🎉 所有API接口测试完成！功能正常工作！")
    print("\n💡 提示: 现在可以在浏览器中访问 http://localhost:5175 测试前端界面")

if __name__ == "__main__":
    test_api_endpoints()
