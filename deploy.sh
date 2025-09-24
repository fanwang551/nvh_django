#!/bin/bash

# 部署脚本 - deploy.sh
# 使用方法: ./deploy.sh

set -e

echo "🚀 开始部署 NVH 系统..."

# 检查Docker和Docker Compose是否安装
check_requirements() {
    echo "📋 检查部署环境..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    echo "✅ 环境检查通过"
}

# 停止现有服务
stop_services() {
    echo "🛑 停止现有服务..."
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true
}

# 清理旧镜像（可选）
cleanup_images() {
    echo "🧹 清理旧镜像..."
    docker system prune -f
}

# 构建和启动服务
deploy_services() {
    echo "🔧 构建和启动服务..."
    
    # 复制环境变量文件
    cp .env.production .env
    
    # 构建并启动服务
    docker-compose -f docker-compose.prod.yml build --no-cache
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "⏰ 等待服务启动..."
    sleep 30
}

# 初始化数据库
init_database() {
    echo "🗄️ 初始化数据库..."
    
    # 等待MySQL启动
    echo "等待MySQL启动..."
    until docker exec nvh_mysql mysqladmin ping -h localhost --silent; do
        echo "MySQL还未就绪，等待5秒..."
        sleep 5
    done
    
    # 运行数据库迁移
    echo "执行数据库迁移..."
    docker exec nvh_backend python manage.py migrate
    
    # 创建超级用户（可选）
    echo "创建超级用户（可选，按Ctrl+C跳过）..."
    docker exec -it nvh_backend python manage.py createsuperuser || true
    
    # 收集静态文件
    echo "收集静态文件..."
    docker exec nvh_backend python manage.py collectstatic --noinput
}

# 检查服务状态
check_services() {
    echo "🔍 检查服务状态..."
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    echo "🌐 服务访问地址："
    echo "前端应用: http://117.72.42.68"
    echo "后端API: http://117.72.42.68/api"
    echo "管理后台: http://117.72.42.68/admin"
    echo ""
    
    # 健康检查
    echo "🏥 执行健康检查..."
    sleep 5
    
    if curl -f http://117.72.42.68/health &> /dev/null; then
        echo "✅ 服务部署成功！"
    else
        echo "⚠️  健康检查失败，请检查服务状态"
        echo "查看日志: docker-compose -f docker-compose.prod.yml logs"
    fi
}

# 主函数
main() {
    check_requirements
    stop_services
    cleanup_images
    deploy_services
    init_database
    check_services
    
    echo ""
    echo "🎉 部署完成！"
    echo ""
    echo "📝 常用命令："
    echo "查看日志: docker-compose -f docker-compose.prod.yml logs -f"
    echo "重启服务: docker-compose -f docker-compose.prod.yml restart"
    echo "停止服务: docker-compose -f docker-compose.prod.yml down"
    echo "更新服务: ./deploy.sh"
}

# 执行主函数
main "$@"
