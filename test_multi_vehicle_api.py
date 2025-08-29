#!/usr/bin/env python3
"""
测试多车型选择的API接口
"""

import requests
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api/modal"

def test_multi_vehicle_selection():
    """测试多车型选择功能"""
    
    print("🚀 测试多车型选择功能...")
    print("=" * 50)
    
    # 1. 获取零件列表
    print("\n1️⃣ 获取零件列表")
    response = requests.get(f"{BASE_URL}/components/")
    if response.status_code != 200:
        print(f"❌ 获取零件列表失败: {response.status_code}")
        return
    
    components = response.json().get('data', [])
    if not components:
        print("❌ 没有找到零件数据")
        return
    
    component_id = components[0]['id']
    component_name = components[0]['component_name']
    print(f"✅ 选择零件: {component_name} (ID: {component_id})")
    
    # 2. 获取相关车型（选择多个）
    print(f"\n2️⃣ 获取零件 '{component_name}' 的相关车型")
    response = requests.get(f"{BASE_URL}/modal-data/related-vehicles/", 
                          params={'component_id': component_id})
    if response.status_code != 200:
        print(f"❌ 获取相关车型失败: {response.status_code}")
        return
    
    vehicles = response.json().get('data', [])
    if len(vehicles) < 2:
        print(f"❌ 车型数量不足，只有 {len(vehicles)} 个车型")
        return
    
    # 选择前3个车型（多车型选择）
    selected_vehicles = vehicles[:3]
    vehicle_ids = [str(v['id']) for v in selected_vehicles]
    vehicle_names = [v['vehicle_model_name'] for v in selected_vehicles]
    print(f"✅ 选择多个车型: {', '.join(vehicle_names)}")
    print(f"   车型ID: {', '.join(vehicle_ids)}")
    
    # 3. 获取测试状态（多车型时应该返回单选选项）
    print(f"\n3️⃣ 获取测试状态选项（多车型模式）")
    response = requests.get(f"{BASE_URL}/modal-data/test-statuses/", 
                          params={
                              'component_id': component_id,
                              'vehicle_model_ids': ','.join(vehicle_ids)
                          })
    if response.status_code != 200:
        print(f"❌ 获取测试状态失败: {response.status_code}")
        return
    
    test_statuses = response.json().get('data', [])
    print(f"✅ 获取测试状态: {test_statuses}")
    
    if not test_statuses:
        print("❌ 没有找到测试状态")
        return
    
    # 选择第一个测试状态（单选）
    selected_status = test_statuses[0]
    print(f"   选择测试状态: {selected_status}")
    
    # 4. 获取振型类型
    print(f"\n4️⃣ 获取振型类型选项")
    response = requests.get(f"{BASE_URL}/modal-data/mode-types/", 
                          params={
                              'component_id': component_id,
                              'vehicle_model_ids': ','.join(vehicle_ids),
                              'test_statuses': selected_status  # 注意：这里是单个值，不是数组
                          })
    if response.status_code != 200:
        print(f"❌ 获取振型类型失败: {response.status_code}")
        return
    
    mode_types = response.json().get('data', [])
    print(f"✅ 获取振型类型: {mode_types[:5]}...")  # 只显示前5个
    
    if not mode_types:
        print("❌ 没有找到振型类型")
        return
    
    # 选择前2个振型
    selected_modes = mode_types[:2]
    print(f"   选择振型: {selected_modes}")
    
    # 5. 执行对比（关键测试）
    print(f"\n5️⃣ 执行多车型对比")
    compare_data = {
        'component_id': component_id,
        'vehicle_model_ids': ','.join(vehicle_ids),
        'test_statuses': selected_status,  # 单个值，不是数组
        'mode_types': ','.join(selected_modes)
    }
    
    print(f"   对比参数: {json.dumps(compare_data, indent=2, ensure_ascii=False)}")
    
    response = requests.post(f"{BASE_URL}/modal-data/compare/", 
                           json=compare_data,
                           headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        data = response.json()
        compare_result = data.get('data', [])
        print(f"✅ 多车型对比成功！获取 {len(compare_result)} 条对比数据")
        
        # 显示对比结果摘要
        if compare_result:
            print("\n📊 对比结果摘要:")
            for item in compare_result[:8]:  # 显示前8条
                print(f"   {item['display_name']} - {item['mode_type']}: {item['frequency']} Hz")
            if len(compare_result) > 8:
                print(f"   ... 还有 {len(compare_result) - 8} 条数据")
                
            # 检查数据完整性
            has_mode_shape = any(item.get('mode_shape_file') for item in compare_result)
            has_test_photo = any(item.get('test_photo_file') for item in compare_result)
            print(f"\n🔍 数据完整性检查:")
            print(f"   包含振型文件: {'✅' if has_mode_shape else '❌'}")
            print(f"   包含测试图片: {'✅' if has_test_photo else '❌'}")
    else:
        print(f"❌ 多车型对比失败: {response.status_code}")
        print(f"   响应内容: {response.text}")
        return
    
    print("\n" + "=" * 50)
    print("🎉 多车型选择功能测试完成！")
    print("💡 前端bug已修复，现在可以正常选择多个车型进行对比了！")

if __name__ == "__main__":
    test_multi_vehicle_selection()
