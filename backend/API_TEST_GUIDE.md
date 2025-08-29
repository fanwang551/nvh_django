# NVH 模态数据查询 API 测试指南

## 服务器信息
- **基础URL**: `http://127.0.0.1:8000`
- **认证方式**: Bearer Token (OIDC)
- **响应格式**: JSON

## API 接口列表

### 1. 获取车型列表
**接口**: `GET /api/modal/vehicle-models/`

**功能**: 获取所有激活状态的车型列表，支持分页和搜索

**请求参数**:
- `page`: 页码 (可选，默认1)
- `page_size`: 每页数量 (可选，默认10)
- `search`: 搜索关键词 (可选，支持车型名称和代码搜索)

**请求示例**:
```
GET /api/modal/vehicle-models/?page=1&page_size=10&search=BMW
```

**响应示例**:
```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        "count": 3,
        "next": null,
        "previous": null,
        "current": 1,
        "max_page": 1,
        "results": [
            {
                "id": 1,
                "cle_model_code": "BMW_X5_2023",
                "vehicle_model_name": "BMW X5 2023款",
                "vin": "WBAFR9C50DD123456",
                "drive_type": "AWD",
                "configuration": "xDrive40i 豪华套装",
                "production_year": 2023,
                "status": "active",
                "created_at": "2025-08-27T14:44:35.123456Z",
                "updated_at": "2025-08-27T14:44:35.123456Z"
            }
        ]
    },
    "success": true
}
```

### 2. 获取零件列表
**接口**: `GET /api/modal/components/`

**功能**: 获取零件列表，支持按车型筛选、分页和搜索

**请求参数**:
- `vehicle_model_id`: 车型ID (可选，用于级联查询)
- `page`: 页码 (可选，默认1)
- `page_size`: 每页数量 (可选，默认10)
- `search`: 搜索关键词 (可选，支持零件名称、代码、分类搜索)

**请求示例**:
```
GET /api/modal/components/?vehicle_model_id=1&page=1&page_size=10
```

**响应示例**:
```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        "count": 3,
        "next": null,
        "previous": null,
        "current": 1,
        "max_page": 1,
        "results": [
            {
                "id": 1,
                "component_name": "发动机悬置",
                "category": "动力总成",
                "component_brand": "Continental",
                "component_model": "EM-2023-001",
                "component_code": "ENG_MOUNT_001",
                "created_at": "2025-08-27T14:44:35.123456Z",
                "updated_at": "2025-08-27T14:44:35.123456Z"
            }
        ]
    },
    "success": true
}
```

### 3. 查询模态数据
**接口**: `GET /api/modal/modal-data/`

**功能**: 根据车型和零件查询模态数据，支持分页和多种筛选条件

**请求参数**:
- `vehicle_model_id`: 车型ID (必填)
- `component_id`: 零件ID (可选)
- `page`: 页码 (可选，默认1)
- `page_size`: 每页数量 (可选，默认10)
- `freq_min`: 最小频率 (可选)
- `freq_max`: 最大频率 (可选)
- `test_type`: 测试类型 (可选)

**请求示例**:
```
GET /api/modal/modal-data/?vehicle_model_id=1&component_id=1&freq_min=20&freq_max=100
```

**响应示例**:
```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        "count": 3,
        "next": null,
        "previous": null,
        "current": 1,
        "max_page": 1,
        "results": [
            {
                "id": 1,
                "test_project": 1,
                "test_project_code": "TEST_BMW_X5_2023_ENG_MOUNT_001_001",
                "vehicle_model_name": "BMW X5 2023款",
                "component_name": "发动机悬置",
                "frequency": "25.50",
                "damping_ratio": "0.02",
                "mode_shape_description": "第一阶弯曲模态",
                "mode_shape_file": "/media/modal_shapes/modal_001.gif",
                "test_photo_file": "/media/test_photos/test_001.jpg",
                "notes": "TEST_BMW_X5_2023_ENG_MOUNT_001_001 - 第一阶弯曲模态",
                "created_at": "2025-08-27T14:44:35.123456Z",
                "updated_at": "2025-08-27T14:44:35.123456Z",
                "updated_by": "系统初始化"
            }
        ]
    },
    "success": true
}
```

### 4. 获取模态数据统计信息
**接口**: `GET /api/modal/modal-data/statistics/`

**功能**: 获取指定车型和零件的模态数据统计信息

**请求参数**:
- `vehicle_model_id`: 车型ID (必填)
- `component_id`: 零件ID (可选)

**请求示例**:
```
GET /api/modal/modal-data/statistics/?vehicle_model_id=1&component_id=1
```

**响应示例**:
```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        "total_count": 3,
        "frequency_range": {
            "min": 25.5,
            "max": 78.9,
            "avg": 49.87
        }
    },
    "success": true
}
```

## 测试数据说明

系统已初始化以下测试数据：

### 车型数据 (3个)
1. BMW X5 2023款 (ID: 1)
2. Audi Q7 2023款 (ID: 2) 
3. Mercedes-Benz GLE 2023款 (ID: 3)

### 零件数据 (5个)
1. 发动机悬置 (ID: 1)
2. 变速箱悬置 (ID: 2)
3. 前悬架弹簧 (ID: 3)
4. 后悬架减震器 (ID: 4)
5. 车身框架 (ID: 5)

### 级联关系
- 每个车型都有前3个零件的测试项目
- 每个测试项目有3条模态数据
- 总共27条模态数据

## Apifox 测试建议

1. **认证设置**: 在Apifox中配置Bearer Token认证
2. **环境变量**: 设置base_url = http://127.0.0.1:8000
3. **测试流程**:
   - 先调用车型列表接口获取车型ID
   - 使用车型ID调用零件列表接口获取零件ID
   - 使用车型ID和零件ID查询模态数据
   - 调用统计接口获取汇总信息

## 错误处理

所有接口都使用统一的错误响应格式：
```json
{
    "code": 400,
    "message": "错误描述",
    "data": null,
    "success": false
}
```

常见错误码：
- 400: 请求参数错误
- 401: 认证失败
- 404: 资源不存在
- 500: 服务器内部错误
