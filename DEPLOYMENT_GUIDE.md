# NVH系统云服务器部署指南

## 📋 部署概述

本指南将帮助你在Ubuntu 22.04服务器上部署NVH系统，采用Docker Compose一键部署方案。

**服务器信息：**
- 公网IP: 117.72.42.68
- 操作系统: Ubuntu 22.04
- 架构: Django + Vue + MySQL + Nginx

## 🚀 快速部署（推荐方式）

### 第一步：连接服务器并准备环境

```bash
# 连接到服务器
ssh root@117.72.42.68

# 创建项目目录
mkdir -p /opt/nvh-system
cd /opt/nvh-system
```

### 第二步：上传项目文件

将本地项目文件上传到服务器的 `/opt/nvh-system` 目录：

```bash
# 方法1: 使用scp命令（在本地执行）
scp -r ./nvh_django/* root@117.72.42.68:/opt/nvh-system/

# 方法2: 使用rsync命令（在本地执行）
rsync -avz --progress ./nvh_django/ root@117.72.42.68:/opt/nvh-system/

# 方法3: 使用Git（在服务器上执行）
git clone <你的项目仓库地址> /opt/nvh-system
```

### 第三步：配置服务器环境

```bash
# 进入项目目录
cd /opt/nvh-system

# 设置脚本执行权限
chmod +x server-setup.sh deploy.sh

# 运行环境配置脚本
./server-setup.sh
```

这个脚本会自动：
- 更新系统包
- 安装Docker和Docker Compose
- 配置国内镜像源
- 设置防火墙规则
- 安装必要工具

### 第四步：重新登录服务器

```bash
# 退出当前连接
exit

# 重新连接服务器（应用Docker组权限）
ssh root@117.72.42.68

# 进入项目目录
cd /opt/nvh-system
```

### 第五步：配置环境变量

```bash
# 编辑生产环境配置文件
vim .env.production
```

**重要配置项：**
```env
# 数据库配置 - 请修改默认密码
DB_PASSWORD=YourStrongPassword123!

# Django安全密钥 - 请生成新的密钥
SECRET_KEY=your-super-secret-key-change-this-in-production-123456789

# 其他配置已预设好，通常不需要修改
DB_NAME=nvh_database
DB_USER=nvh_user
ALLOWED_HOSTS=117.72.42.68,localhost,127.0.0.1
```

### 第六步：一键部署

```bash
# 运行部署脚本
./deploy.sh
```

部署脚本会自动：
1. 检查环境依赖
2. 停止现有服务
3. 构建Docker镜像
4. 启动所有服务
5. 初始化数据库
6. 执行健康检查

### 第七步：验证部署

部署完成后，访问以下地址验证：

- **前端应用**: http://117.72.42.68
- **后端API**: http://117.72.42.68/api
- **管理后台**: http://117.72.42.68/admin
- **健康检查**: http://117.72.42.68/health

## 🔧 手动部署（如果自动部署失败）

### 1. 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 配置Docker镜像加速
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.ccs.tencentyun.com"
  ]
}
EOF

sudo systemctl restart docker
```

### 2. 手动部署服务

```bash
# 复制环境配置
cp .env.production .env

# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 等待MySQL启动并初始化数据库
sleep 30
docker exec nvh_backend python manage.py migrate
docker exec nvh_backend python manage.py collectstatic --noinput
```

## 📱 常用管理命令

### 服务管理

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 停止服务
docker-compose -f docker-compose.prod.yml down

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build
```

### 数据库管理

```bash
# 连接数据库
docker exec -it nvh_mysql mysql -u nvh_user -p nvh_database

# 备份数据库
docker exec nvh_mysql mysqldump -u nvh_user -p nvh_database > backup.sql

# 恢复数据库
docker exec -i nvh_mysql mysql -u nvh_user -p nvh_database < backup.sql
```

### Django管理

```bash
# 进入Django容器
docker exec -it nvh_backend bash

# 创建超级用户
docker exec -it nvh_backend python manage.py createsuperuser

# 运行Django命令
docker exec nvh_backend python manage.py <command>
```

## 🔍 故障排除

### 1. 端口占用问题

```bash
# 检查端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :3306

# 停止占用端口的服务
sudo systemctl stop apache2  # 如果安装了Apache
sudo systemctl stop mysql    # 如果安装了MySQL
```

### 2. 内存不足

```bash
# 检查内存使用
free -h
docker stats

# 清理Docker缓存
docker system prune -a
docker volume prune
```

### 3. 网络问题

```bash
# 检查防火墙状态
sudo ufw status

# 允许端口（如果需要）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 4. 查看详细日志

```bash
# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs mysql

# 实时查看日志
docker-compose -f docker-compose.prod.yml logs -f --tail=100
```

## 🔒 安全建议

### 1. 修改默认密码

- 数据库密码：修改 `.env.production` 中的 `DB_PASSWORD`
- Django SECRET_KEY：生成新的安全密钥

### 2. 启用HTTPS（可选）

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d 117.72.42.68

# 自动续期
sudo crontab -e
# 添加以下行：
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. 定期备份

```bash
# 创建备份脚本
cat > /opt/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec nvh_mysql mysqldump -u nvh_user -p"YourStrongPassword123!" nvh_database > /opt/backup_${DATE}.sql
find /opt -name "backup_*.sql" -mtime +7 -delete
EOF

chmod +x /opt/backup.sh

# 设置定时备份
sudo crontab -e
# 添加：0 2 * * * /opt/backup.sh
```

## 📞 技术支持

如果遇到问题，请按以下步骤操作：

1. 查看服务状态：`docker-compose -f docker-compose.prod.yml ps`
2. 查看日志：`docker-compose -f docker-compose.prod.yml logs -f`
3. 检查网络连接：`curl http://117.72.42.68/health`
4. 重启服务：`./deploy.sh`

**部署成功标志：**
- 所有容器状态为 "Up"
- 访问 http://117.72.42.68 能看到前端页面
- 访问 http://117.72.42.68/health 返回 "healthy"

---

## 📝 部署清单

- [ ] 服务器环境配置完成
- [ ] 项目文件上传完成
- [ ] 环境变量配置完成
- [ ] Docker服务运行正常
- [ ] 数据库初始化完成
- [ ] 前端页面访问正常
- [ ] API接口测试正常
- [ ] 管理后台访问正常

**恭喜！你的NVH系统已成功部署到云服务器！** 🎉