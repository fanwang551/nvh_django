#!/bin/bash

# NVH 项目快速故障恢复脚本
# 项目地址: https://github.com/fanwang551/nvh_django
# 数据库方案: 方案1 (MySQL 容器化)

cd /opt/nvh_django

echo "开始快速恢复服务..."
echo "项目仓库: https://github.com/fanwang551/nvh_django"

# 检查当前目录
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "错误: 未找到 docker-compose.prod.yml 文件"
    echo "请确保在正确的项目目录中执行此脚本"
    exit 1
fi

# 停止所有服务
echo "停止所有服务..."
docker-compose -f docker-compose.prod.yml down

# 等待清理完成
echo "等待容器清理完成..."
sleep 10

# 按顺序启动核心服务
echo "启动 MySQL 数据库..."
docker-compose -f docker-compose.prod.yml up -d mysql
sleep 30

echo "启动 Django 后端..."
docker-compose -f docker-compose.prod.yml up -d backend
sleep 20

echo "启动前端构建..."
docker-compose -f docker-compose.prod.yml up -d frontend
sleep 10

echo "启动 NGINX..."
docker-compose -f docker-compose.prod.yml up -d nginx
sleep 10

# 检查服务状态
echo "检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

# 测试连通性
echo "测试服务连通性..."
sleep 5
curl -f http://127.0.0.1/health/ && echo "✅ 健康检查通过" || echo "❌ 健康检查失败"

echo "服务恢复完成，请验证功能正常性"
echo "前端访问: http://117.72.42.68"
echo "API 接口: http://117.72.42.68/api/"
echo "管理后台: http://117.72.42.68/admin/"