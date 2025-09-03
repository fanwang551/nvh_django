#!/usr/bin/env python3
"""
API性能测试脚本
"""

import time
import requests
import json
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nvh_backend.settings')
django.setup()

from apps.modal.models import VehicleModel

def test_api_performance():
    """测试API性能"""
    url = 'http://127.0.0.1:8000/api/modal/vehicle-models/'
    
    print('🔍 开始API性能测试...')
    print(f'测试URL: {url}')
    print('-' * 50)
    
    # 先检查数据库中的数据量
    vehicle_count = VehicleModel.objects.count()
    active_vehicle_count = VehicleModel.objects.filter(status='active').count()
    print(f'数据库中车型总数: {vehicle_count}')
    print(f'激活状态车型数: {active_vehicle_count}')
    print('-' * 50)
    
    # 进行5次测试
    total_time = 0
    success_count = 0
    
    for i in range(5):
        start_time = time.time()
        try:
            response = requests.get(url, timeout=30)
            end_time = time.time()
            response_time = end_time - start_time
            total_time += response_time
            
            print(f'测试 {i+1}: {response_time:.3f}秒 - 状态码: {response.status_code}')
            
            if response.status_code == 200:
                success_count += 1
                if i == 0:  # 只在第一次显示响应数据量
                    data = response.json()
                    if 'data' in data:
                        print(f'   返回数据量: {len(data["data"])} 条记录')
                        print(f'   响应体大小: {len(response.text)} 字符')
                        # 显示第一条数据的结构
                        if data["data"]:
                            first_record = data["data"][0]
                            print(f'   单条记录字段: {list(first_record.keys())}')
            else:
                print(f'   错误响应: {response.text[:200]}...')
                
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f'测试 {i+1}: {response_time:.3f}秒 - 错误: {str(e)}')
    
    if success_count > 0:
        avg_time = total_time / success_count
        print('-' * 50)
        print(f'成功测试次数: {success_count}/5')
        print(f'平均响应时间: {avg_time:.3f}秒')
        print(f'总测试时间: {total_time:.3f}秒')
        
        # 性能分析
        if avg_time > 5.0:
            print('⚠️  性能警告: 响应时间超过5秒，存在严重性能问题！')
        elif avg_time > 2.0:
            print('⚠️  性能警告: 响应时间超过2秒，需要优化')
        elif avg_time > 1.0:
            print('ℹ️  性能提示: 响应时间超过1秒，建议优化')
        else:
            print('✅ 性能良好: 响应时间在可接受范围内')
    else:
        print('❌ 所有测试都失败了')

def test_database_query_performance():
    """测试数据库查询性能"""
    print('\n🔍 开始数据库查询性能测试...')
    print('-' * 50)
    
    # 测试原始查询
    start_time = time.time()
    queryset = VehicleModel.objects.filter(status='active').order_by('id')
    vehicles = list(queryset)  # 强制执行查询
    end_time = time.time()
    
    print(f'数据库查询时间: {end_time - start_time:.3f}秒')
    print(f'查询到的记录数: {len(vehicles)}')
    
    # 测试序列化性能
    from apps.modal.serializers import VehicleModelSerializer
    
    start_time = time.time()
    serializer = VehicleModelSerializer(vehicles, many=True)
    serialized_data = serializer.data  # 强制执行序列化
    end_time = time.time()
    
    print(f'序列化时间: {end_time - start_time:.3f}秒')
    print(f'序列化后数据大小: {len(str(serialized_data))} 字符')

if __name__ == '__main__':
    test_api_performance()
    test_database_query_performance()
