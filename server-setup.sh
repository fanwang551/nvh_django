#!/bin/bash

# 服务器环境初始化脚本
# 在Ubuntu 22.04上运行

set -e

echo "🔧 开始配置服务器环境..."

# 更新系统包
update_system() {
    echo "📦 更新系统包..."
    sudo apt update && sudo apt upgrade -y
}

# 安装Docker
install_docker() {
    echo "🐳 安装Docker..."
    
    # 卸载旧版本
    sudo apt remove -y docker docker-engine docker.io containerd runc || true
    
    # 安装依赖
    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # 添加Docker官方GPG密钥
    curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # 添加Docker仓库
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装Docker Engine
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    
    # 启动Docker服务
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 将当前用户添加到docker组
    sudo usermod -aG docker $USER
    
    echo "✅ Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    echo "🔧 安装Docker Compose..."
    
    # 下载Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    echo "✅ Docker Compose安装完成"
}

# 配置Docker镜像加速
configure_docker_mirror() {
    echo "🚀 配置Docker镜像加速..."
    
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://mirror.ccs.tencentyun.com",
    "https://reg-mirror.qiniu.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    
    echo "✅ Docker镜像加速配置完成"
}

# 安装其他必要工具
install_tools() {
    echo "🛠️ 安装其他必要工具..."
    sudo apt install -y curl wget git vim htop unzip
    echo "✅ 工具安装完成"
}

# 配置防火墙
configure_firewall() {
    echo "🔥 配置防火墙..."
    
    # 安装ufw
    sudo apt install -y ufw
    
    # 重置防火墙规则
    sudo ufw --force reset
    
    # 设置默认规则
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # 允许SSH
    sudo ufw allow ssh
    sudo ufw allow 22/tcp
    
    # 允许HTTP和HTTPS
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    # 启用防火墙
    sudo ufw --force enable
    
    echo "✅ 防火墙配置完成"
}

# 创建项目目录
create_project_dir() {
    echo "📁 创建项目目录..."
    
    PROJECT_DIR="/opt/nvh-system"
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    
    echo "✅ 项目目录创建完成: $PROJECT_DIR"
}

# 检查安装结果
check_installation() {
    echo "🔍 检查安装结果..."
    
    echo "Docker版本:"
    docker --version
    
    echo "Docker Compose版本:"
    docker-compose --version
    
    echo "Docker服务状态:"
    sudo systemctl status docker --no-pager -l
    
    echo "✅ 环境配置完成！"
}

# 主函数
main() {
    echo "开始配置Ubuntu 22.04服务器环境..."
    echo "这将安装Docker、Docker Compose和其他必要工具"
    echo ""
    
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消安装"
        exit 1
    fi
    
    update_system
    install_docker
    install_docker_compose
    configure_docker_mirror
    install_tools
    configure_firewall
    create_project_dir
    check_installation
    
    echo ""
    echo "🎉 服务器环境配置完成！"
    echo ""
    echo "📝 接下来的步骤："
    echo "1. 重新登录服务器以应用Docker组权限"
    echo "2. 上传项目文件到 /opt/nvh-system"
    echo "3. 运行 ./deploy.sh 开始部署"
    echo ""
    echo "⚠️  请注意：需要重新登录服务器才能使用Docker命令"
}

# 执行主函数
main "$@"