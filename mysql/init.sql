-- 创建数据库和用户
CREATE DATABASE IF NOT EXISTS nvh_database CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（如果不存在）
CREATE USER IF NOT EXISTS 'nvh_user'@'%' IDENTIFIED BY 'YourStrongPassword123!';

-- 授权
GRANT ALL PRIVILEGES ON nvh_database.* TO 'nvh_user'@'%';

-- 刷新权限
FLUSH PRIVILEGES;