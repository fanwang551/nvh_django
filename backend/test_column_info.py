#!/usr/bin/env python3
"""
测试NOT NULL字段标记功能
"""

import os
import sys
import pymysql

# 添加Django项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nvh_backend.settings')

# 导入Django配置
import django
django.setup()

from django.conf import settings


def test_column_info():
    """测试获取列信息功能"""
    try:
        db_config = settings.DATABASES['default']
        connection = pymysql.connect(
            host=db_config['HOST'],
            port=int(db_config['PORT']),
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            database=db_config['NAME'],
            charset='utf8mb4'
        )
        
        print("🔍 测试获取表字段约束信息...")
        
        # 测试几个表的字段信息
        test_tables = ['vehicle_models', 'vehicle_suspension_isolation_tests', 'suspension_isolation_data']
        
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            all_tables = [table[0] for table in cursor.fetchall()]
            
            for table_name in test_tables:
                if table_name in all_tables:
                    print(f"\n📋 表: {table_name}")
                    cursor.execute(f"DESCRIBE `{table_name}`")
                    column_info = cursor.fetchall()
                    
                    print("字段信息:")
                    for col in column_info:
                        field_name = col[0]
                        field_type = col[1]
                        null_allowed = col[2]
                        key = col[3]
                        default = col[4]
                        
                        is_not_null = null_allowed == 'NO'
                        null_status = "NOT NULL" if is_not_null else "允许NULL"
                        
                        print(f"  - {field_name:20} {field_type:20} {null_status}")
                else:
                    print(f"⚠️  表 {table_name} 不存在")
        
        connection.close()
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")


if __name__ == "__main__":
    test_column_info()