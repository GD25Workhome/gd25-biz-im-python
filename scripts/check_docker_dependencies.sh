#!/bin/bash

# ============================================================================
# Docker 依赖检查脚本
# ============================================================================
# 功能：检查项目依赖的外部 Docker 容器是否都已启动
# 用法：./scripts/check_docker_dependencies.sh
# ============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 检查结果
ALL_PASSED=true
FAILED_SERVICES=()

# ============================================================================
# 工具函数
# ============================================================================

# 打印信息
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# 打印成功
success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

# 打印警告
warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# 打印错误
error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 检查 Docker 是否运行
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker 未安装或不在 PATH 中"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker 守护进程未运行，请先启动 Docker"
        exit 1
    fi
}

# 从 URL 中提取主机和端口
# 支持格式：
# - postgresql://user:pass@host:port/db
# - mysql+pymysql://user:pass@host:port/db
# - redis://host:port/db
# - amqp://user:pass@host:port/vhost
extract_host_port() {
    local url=$1
    local host=""
    local port=""
    
    # 移除协议前缀
    if [[ $url =~ ^[^:]+:// ]]; then
        url=${url#*://}
    fi
    
    # 移除认证信息（user:pass@）
    if [[ $url =~ @ ]]; then
        url=${url#*@}
    fi
    
    # 提取主机和端口
    if [[ $url =~ ^([^:/]+):([0-9]+) ]]; then
        host=${BASH_REMATCH[1]}
        port=${BASH_REMATCH[2]}
    elif [[ $url =~ ^([^:/]+) ]]; then
        host=${BASH_REMATCH[1]}
        # 根据协议设置默认端口
        if [[ $1 =~ ^postgresql ]]; then
            port="5432"
        elif [[ $1 =~ ^mysql ]]; then
            port="3306"
        elif [[ $1 =~ ^redis ]]; then
            port="6379"
        elif [[ $1 =~ ^amqp ]]; then
            port="5672"
        fi
    fi
    
    echo "$host:$port"
}

# 检查容器是否运行（通过容器名称）
check_container_by_name() {
    local container_name=$1
    local service_name=$2
    
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        success "${service_name} 容器正在运行 (${container_name})"
        return 0
    else
        error "${service_name} 容器未运行 (${container_name})"
        return 1
    fi
}

# 检查端口是否在监听（通过主机和端口）
check_port() {
    local host=$1
    local port=$2
    local service_name=$3
    
    # 如果是 localhost 或 127.0.0.1，使用本地检查
    if [[ "$host" == "localhost" ]] || [[ "$host" == "127.0.0.1" ]] || [[ "$host" == "0.0.0.0" ]]; then
        if command -v nc &> /dev/null; then
            if nc -z localhost "$port" 2>/dev/null; then
                success "${service_name} 服务正在监听端口 ${port}"
                return 0
            else
                error "${service_name} 服务未在端口 ${port} 监听"
                return 1
            fi
        elif command -v timeout &> /dev/null && command -v bash &> /dev/null; then
            # 使用 bash 内置的 TCP 连接检查
            if timeout 1 bash -c "echo > /dev/tcp/localhost/$port" 2>/dev/null; then
                success "${service_name} 服务正在监听端口 ${port}"
                return 0
            else
                error "${service_name} 服务未在端口 ${port} 监听"
                return 1
            fi
        else
            warning "无法检查端口 ${port}（需要 nc 或 timeout 命令）"
            return 2
        fi
    else
        # 远程主机，尝试连接
        if command -v nc &> /dev/null; then
            if nc -z "$host" "$port" 2>/dev/null; then
                success "${service_name} 服务可达 (${host}:${port})"
                return 0
            else
                error "${service_name} 服务不可达 (${host}:${port})"
                return 1
            fi
        else
            warning "无法检查远程服务 ${host}:${port}（需要 nc 命令）"
            return 2
        fi
    fi
}

# 检查 Docker 容器（通过端口映射）
check_container_by_port() {
    local port=$1
    local service_name=$2
    
    # 查找使用该端口的容器
    local container=$(docker ps --format '{{.Names}}\t{{.Ports}}' | grep -E ":$port->|:$port/" | head -1 | awk '{print $1}')
    
    if [[ -n "$container" ]]; then
        success "${service_name} 容器正在运行 (${container}, 端口 ${port})"
        return 0
    else
        # 如果找不到容器，尝试检查端口是否在监听
        return 1
    fi
}

# 检查服务（智能选择检查方式）
check_service() {
    local url=$1
    local service_name=$2
    local container_name=${3:-""}
    
    if [[ -z "$url" ]]; then
        warning "${service_name} 未配置，跳过检查"
        return 0
    fi
    
    info "检查 ${service_name}..."
    
    # 提取主机和端口
    local host_port=$(extract_host_port "$url")
    local host="${host_port%%:*}"
    local port="${host_port##*:}"
    
    if [[ -z "$host" ]] || [[ -z "$port" ]]; then
        error "${service_name} URL 格式错误: $url"
        ALL_PASSED=false
        FAILED_SERVICES+=("${service_name}")
        return 1
    fi
    
    # 优先使用容器名称检查
    if [[ -n "$container_name" ]]; then
        if check_container_by_name "$container_name" "$service_name"; then
            return 0
        fi
    fi
    
    # 尝试通过端口查找容器
    if check_container_by_port "$port" "$service_name"; then
        return 0
    fi
    
    # 最后尝试端口检查
    if check_port "$host" "$port" "$service_name"; then
        return 0
    else
        ALL_PASSED=false
        FAILED_SERVICES+=("${service_name}")
        return 1
    fi
}

# ============================================================================
# 主检查逻辑
# ============================================================================

main() {
    echo "============================================================================"
    echo "Docker 依赖检查脚本"
    echo "============================================================================"
    echo ""
    
    # 检查 Docker
    check_docker
    echo ""
    
    # 加载 .env 文件
    local env_file="${PROJECT_ROOT}/.env"
    if [[ ! -f "$env_file" ]]; then
        warning ".env 文件不存在，尝试使用环境变量"
    else
        info "加载配置文件: $env_file"
        # 使用 source 加载环境变量（注意：只导出需要的变量）
        set -a
        source "$env_file" 2>/dev/null || true
        set +a
    fi
    echo ""
    
    # 检查数据库
    if [[ -n "${DATABASE_URL:-}" ]]; then
        local db_type=""
        if [[ "$DATABASE_URL" =~ ^postgresql ]]; then
            db_type="PostgreSQL"
        elif [[ "$DATABASE_URL" =~ ^mysql ]]; then
            db_type="MySQL"
        fi
        
        # 尝试常见的容器名称
        local db_container=""
        if [[ "$db_type" == "PostgreSQL" ]]; then
            # 常见的 PostgreSQL 容器名称
            for name in postgres postgresql db database; do
                if docker ps --format '{{.Names}}' | grep -qi "$name"; then
                    db_container=$(docker ps --format '{{.Names}}' | grep -i "$name" | head -1)
                    break
                fi
            done
        elif [[ "$db_type" == "MySQL" ]]; then
            # 常见的 MySQL 容器名称
            for name in mysql mariadb db database; do
                if docker ps --format '{{.Names}}' | grep -qi "$name"; then
                    db_container=$(docker ps --format '{{.Names}}' | grep -i "$name" | head -1)
                    break
                fi
            done
        fi
        
        check_service "${DATABASE_URL}" "${db_type} 数据库" "$db_container"
        echo ""
    else
        warning "DATABASE_URL 未配置，跳过数据库检查"
        echo ""
    fi
    
    # 检查 Redis
    if [[ -n "${REDIS_URL:-}" ]]; then
        # 尝试常见的 Redis 容器名称
        local redis_container=""
        for name in redis cache; do
            if docker ps --format '{{.Names}}' | grep -qi "$name"; then
                redis_container=$(docker ps --format '{{.Names}}' | grep -i "$name" | head -1)
                break
            fi
        done
        
        check_service "${REDIS_URL}" "Redis" "$redis_container"
        echo ""
    else
        info "REDIS_URL 未配置（可选服务），跳过检查"
        echo ""
    fi
    
    # 检查 Celery Broker
    if [[ -n "${CELERY_BROKER_URL:-}" ]]; then
        local broker_type=""
        local broker_container=""
        
        if [[ "$CELERY_BROKER_URL" =~ ^redis ]]; then
            broker_type="Celery Broker (Redis)"
            # Redis 容器可能已经被检查过了
            for name in redis cache; do
                if docker ps --format '{{.Names}}' | grep -qi "$name"; then
                    broker_container=$(docker ps --format '{{.Names}}' | grep -i "$name" | head -1)
                    break
                fi
            done
        elif [[ "$CELERY_BROKER_URL" =~ ^amqp ]]; then
            broker_type="Celery Broker (RabbitMQ)"
            # 常见的 RabbitMQ 容器名称
            for name in rabbitmq rabbitmq-server; do
                if docker ps --format '{{.Names}}' | grep -qi "$name"; then
                    broker_container=$(docker ps --format '{{.Names}}' | grep -i "$name" | head -1)
                    break
                fi
            done
        else
            broker_type="Celery Broker"
        fi
        
        check_service "${CELERY_BROKER_URL}" "$broker_type" "$broker_container"
        echo ""
    else
        info "CELERY_BROKER_URL 未配置（可选服务），跳过检查"
        echo ""
    fi
    
    # 检查 Celery Result Backend
    if [[ -n "${CELERY_RESULT_BACKEND:-}" ]]; then
        local backend_type=""
        local backend_container=""
        
        if [[ "$CELERY_RESULT_BACKEND" =~ ^redis ]]; then
            backend_type="Celery Result Backend (Redis)"
            # Redis 容器可能已经被检查过了
            for name in redis cache; do
                if docker ps --format '{{.Names}}' | grep -qi "$name"; then
                    backend_container=$(docker ps --format '{{.Names}}' | grep -i "$name" | head -1)
                    break
                fi
            done
        elif [[ "$CELERY_RESULT_BACKEND" =~ ^rpc ]]; then
            backend_type="Celery Result Backend (RabbitMQ)"
            # 常见的 RabbitMQ 容器名称
            for name in rabbitmq rabbitmq-server; do
                if docker ps --format '{{.Names}}' | grep -qi "$name"; then
                    backend_container=$(docker ps --format '{{.Names}}' | grep -i "$name" | head -1)
                    break
                fi
            done
        else
            backend_type="Celery Result Backend"
        fi
        
        check_service "${CELERY_RESULT_BACKEND}" "$backend_type" "$backend_container"
        echo ""
    else
        info "CELERY_RESULT_BACKEND 未配置（可选服务），跳过检查"
        echo ""
    fi
    
    # 总结
    echo "============================================================================"
    if $ALL_PASSED; then
        success "所有依赖服务检查通过！"
        echo ""
        exit 0
    else
        error "以下服务检查失败："
        for service in "${FAILED_SERVICES[@]}"; do
            echo "  - $service"
        done
        echo ""
        warning "请确保这些服务已启动，或检查 .env 文件中的配置是否正确"
        echo ""
        exit 1
    fi
}

# 执行主函数
main "$@"
