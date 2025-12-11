#!/usr/bin/env python3
"""
自动生成 FastAPI 路由索引脚本

扫描项目中的所有 FastAPI 路由，生成路由索引文档，方便快速查找 URL 对应的实现。

使用方法:
    python scripts/generate_route_index.py
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict


class RouteVisitor(ast.NodeVisitor):
    """AST 访问器，用于提取 FastAPI 路由信息"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.routes: List[Dict] = []
        self.current_decorator = None
        self.current_function = None
        self.router_prefix = ""
        
    def visit_FunctionDef(self, node):
        """访问函数定义节点"""
        # 保存当前函数信息
        old_function = self.current_function
        
        # 检查是否有路由装饰器
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    # 处理 @router.get, @router.post 等
                    if isinstance(decorator.func.value, ast.Name):
                        if decorator.func.value.id in ['router', 'app']:
                            method = decorator.func.attr.upper()
                            if method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                                self.current_decorator = decorator
                                self.current_function = node.name
                                
                                # 提取路径
                                path = self._extract_path(decorator)
                                
                                # 提取行号
                                line_no = node.lineno
                                
                                self.routes.append({
                                    'method': method,
                                    'path': path,
                                    'function': node.name,
                                    'line': line_no,
                                    'file': self.file_path
                                })
        
        # 继续访问子节点
        self.generic_visit(node)
        
        # 恢复
        self.current_function = old_function
    
    def _extract_path(self, decorator: ast.Call) -> str:
        """从装饰器中提取路径"""
        # 第一个位置参数通常是路径
        if decorator.args and len(decorator.args) > 0:
            if isinstance(decorator.args[0], ast.Constant):
                return decorator.args[0].value
            elif isinstance(decorator.args[0], ast.Str):  # Python < 3.8
                return decorator.args[0].s
        
        return ""


def scan_routes_in_file(file_path: Path) -> List[Dict]:
    """扫描单个文件中的路由（使用正则表达式）"""
    routes = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            content = ''.join(lines)
        
        # 使用正则表达式匹配路由装饰器
        # 匹配 @router.get("/path") 或 @app.get("/path") 等格式
        pattern = r'@(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            method = match.group(1).upper()
            path = match.group(2)
            
            # 找到匹配行的行号
            line_no = content[:match.start()].count('\n') + 1
            
            # 查找对应的函数定义（在装饰器后面的函数）
            # 从当前行开始向后查找函数定义
            func_name = None
            for i in range(line_no - 1, min(line_no + 10, len(lines))):
                if i < len(lines):
                    func_match = re.search(r'^(?:async\s+)?def\s+(\w+)', lines[i])
                    if func_match:
                        func_name = func_match.group(1)
                        break
            
            if func_name:
                routes.append({
                    'method': method,
                    'path': path,
                    'function': func_name,
                    'line': line_no,
                    'file': str(file_path)
                })
        
        return routes
    except Exception as e:
        print(f"警告: 无法解析文件 {file_path}: {e}")
        return []


def get_router_prefix(file_path: Path) -> str:
    """从 main.py 中提取路由前缀"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找 include_router 调用
        pattern = r'app\.include_router\((\w+)\.router,\s*prefix=["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)
        
        prefixes = {}
        for module_name, prefix in matches:
            prefixes[module_name] = prefix
        
        return prefixes
    except Exception as e:
        print(f"警告: 无法读取 main.py: {e}")
        return {}


def generate_route_index(project_root: Path) -> str:
    """生成路由索引文档"""
    
    # 扫描 API 目录
    api_dir = project_root / "app" / "api"
    all_routes = []
    
    if api_dir.exists():
        for py_file in api_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            routes = scan_routes_in_file(py_file)
            all_routes.extend(routes)
    
    # 扫描 main.py 中的路由
    main_file = project_root / "app" / "main.py"
    if main_file.exists():
        routes = scan_routes_in_file(main_file)
        all_routes.extend(routes)
    
    # 获取路由前缀
    router_prefixes = get_router_prefix(main_file) if main_file.exists() else {}
    
    # 按文件分组
    routes_by_file = defaultdict(list)
    for route in all_routes:
        file_name = Path(route['file']).name
        routes_by_file[file_name].append(route)
    
    # 生成 Markdown 文档
    md_lines = [
        "# FastAPI 路由索引",
        "",
        "> 本文档由 `scripts/generate_route_index.py` 自动生成",
        "",
        "## 路由映射表",
        ""
    ]
    
    # 输出文件路径（用于计算相对路径）
    output_file = project_root / "cursor_docs" / "route_index.md"
    
    # 按文件分组显示
    for file_name in sorted(routes_by_file.keys()):
        routes = sorted(routes_by_file[file_name], key=lambda x: x['line'])
        route_file_path = Path(routes[0]['file'])
        
        # 计算相对于输出文件的相对路径
        try:
            relative_path = route_file_path.relative_to(project_root)
            # 从 cursor_docs/route_index.md 到 app/api/xxx.py 的相对路径
            relative_link = os.path.relpath(route_file_path, output_file.parent)
        except Exception:
            # 如果计算失败，使用绝对路径（不应该发生）
            relative_link = str(route_file_path)
        
        # 确定 API 前缀
        api_prefix = "/api"
        if "main.py" in str(route_file_path):
            api_prefix = ""
        elif "user" in file_name:
            api_prefix = "/api"
        elif "group" in file_name:
            api_prefix = "/api"
        
        md_lines.append(f"### {file_name} ({api_prefix})")
        md_lines.append("")
        md_lines.append("| HTTP 方法 | URL 路径 | 完整路径 | 函数名 | 行号 |")
        md_lines.append("|----------|---------|---------|--------|------|")
        
        for route in routes:
            full_path = f"{api_prefix}{route['path']}"
            # 使用相对路径生成链接，确保在 Markdown 中可以点击跳转
            md_lines.append(
                f"| {route['method']} | `{route['path']}` | "
                f"`{full_path}` | `{route['function']}` | "
                f"[{route['line']}]({relative_link}#L{route['line']}) |"
            )
        
        md_lines.append("")
    
    md_lines.extend([
        "## 快速查找技巧",
        "",
        "### 在 Cursor/VSCode 中：",
        "",
        "1. **全局搜索**：`Cmd + Shift + F`（Mac）或 `Ctrl + Shift + F`（Windows/Linux）",
        "   - 搜索 URL 路径（如 `/user/create`）",
        "",
        "2. **符号搜索**：`Cmd + Shift + O`（Mac）或 `Ctrl + Shift + O`（Windows/Linux）",
        "   - 搜索函数名（如 `create_user`）",
        "",
        "3. **文件内搜索**：`Cmd + F`（Mac）或 `Ctrl + F`（Windows/Linux）",
        "   - 在当前文件中搜索路径字符串",
        "",
        "4. **Go to Definition**：`Cmd + Click`（Mac）或 `Ctrl + Click`（Windows/Linux）",
        "   - 点击路由路径字符串，可以跳转到定义",
        "",
        "### 路由注册位置",
        "",
        f"所有业务路由在 `app/main.py` 中注册。",
        "",
        "## 更新说明",
        "",
        "运行以下命令更新此索引：",
        "```bash",
        "python scripts/generate_route_index.py",
        "```",
        ""
    ])
    
    return "\n".join(md_lines)


def main():
    """主函数"""
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"正在扫描项目: {project_root}")
    
    # 生成索引
    index_content = generate_route_index(project_root)
    
    # 写入文件
    output_file = project_root / "cursor_docs" / "route_index.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"✓ 路由索引已生成: {output_file}")
    route_count = len(re.findall(r'\| (GET|POST|PUT|DELETE|PATCH)', index_content))
    print(f"  共找到 {route_count} 个路由")


if __name__ == "__main__":
    main()
