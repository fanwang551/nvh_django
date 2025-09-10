@echo off
echo 开始部署 NVH 项目...
echo 项目仓库: https://github.com/fanwang551/nvh_django
echo 数据库方案: 方案1 (MySQL 8.0 容器化)

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

REM 停止并删除现有容器
echo 停止现有服务...
docker-compose -f docker-compose.prod.yml down

REM 清理悬挂的镜像
echo 清理悬挂的镜像...
docker image prune -f

REM 构建并启动服务
echo 构建并启动服务...
docker-compose -f docker-compose.prod.yml up --build -d

REM 等待服务启动
echo 等待服务启动...
timeout /t 30 /nobreak

REM 检查服务状态
echo 检查服务状态...
docker-compose -f docker-compose.prod.yml ps

REM 显示日志
echo 显示最近的日志...
docker-compose -f docker-compose.prod.yml logs --tail=50

echo 部署完成！
echo 前端访问地址: http://117.72.42.68
echo 后端 API 地址: http://117.72.42.68/api/
echo Django 管理界面: http://117.72.42.68/admin/
pause