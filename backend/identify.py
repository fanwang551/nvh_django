import json
import re
from pathlib import Path


def validate_json_in_sql(sql_file_path):
    """验证SQL文件中的JSON格式"""

    print(f"\n{'=' * 80}")
    print(f"验证文件: {sql_file_path}")
    print(f"{'=' * 80}\n")

    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取所有UPDATE语句
    pattern = r"UPDATE `ntf_test_result` SET `ntf_curve` = '(.+?)' WHERE `id` = (\d+);"
    matches = re.findall(pattern, content, re.DOTALL)

    print(f"找到 {len(matches)} 条UPDATE语句\n")

    errors = []

    for idx, (json_str, record_id) in enumerate(matches, 1):
        try:
            # 尝试解析JSON
            json_obj = json.loads(json_str)

            # 验证JSON结构
            issues = validate_json_structure(json_obj, record_id)

            if issues:
                errors.append({
                    'record_id': record_id,
                    'statement_num': idx,
                    'type': 'structure',
                    'issues': issues
                })
                print(f"❌ 记录 {record_id} (第{idx}条语句) - 结构问题:")
                for issue in issues:
                    print(f"   - {issue}")
            else:
                print(f"✅ 记录 {record_id} (第{idx}条语句) - JSON有效")

        except json.JSONDecodeError as e:
            errors.append({
                'record_id': record_id,
                'statement_num': idx,
                'type': 'json_decode',
                'error': str(e),
                'position': e.pos
            })
            print(f"❌ 记录 {record_id} (第{idx}条语句) - JSON解析错误:")
            print(f"   错误: {e}")
            print(f"   位置: {e.pos}")

            # 显示错误位置附近的内容
            start = max(0, e.pos - 50)
            end = min(len(json_str), e.pos + 50)
            print(f"   上下文: ...{json_str[start:end]}...")

        except Exception as e:
            errors.append({
                'record_id': record_id,
                'statement_num': idx,
                'type': 'other',
                'error': str(e)
            })
            print(f"❌ 记录 {record_id} (第{idx}条语句) - 其他错误: {e}")

    # 总结
    print(f"\n{'=' * 80}")
    print(f"验证完成")
    print(f"{'=' * 80}")
    print(f"总语句数: {len(matches)}")
    print(f"错误数: {len(errors)}")
    print(f"成功率: {((len(matches) - len(errors)) / len(matches) * 100):.2f}%")

    return errors


def validate_json_structure(json_obj, record_id):
    """验证JSON数据结构"""
    issues = []

    if not isinstance(json_obj, dict):
        issues.append("根对象不是字典类型")
        return issues

    # 检查位置键
    valid_positions = ['front', 'middle', 'rear']

    for position in valid_positions:
        if position in json_obj:
            pos_data = json_obj[position]

            if pos_data is None:
                continue

            if not isinstance(pos_data, dict):
                issues.append(f"{position}: 不是字典类型")
                continue

            # 检查必需字段
            required_fields = ['frequency', 'x_values', 'y_values', 'z_values', 'stats']
            for field in required_fields:
                if field not in pos_data:
                    issues.append(f"{position}: 缺少字段 '{field}'")

            # 检查数组字段
            array_fields = ['frequency', 'x_values', 'y_values', 'z_values']
            for field in array_fields:
                if field in pos_data:
                    if not isinstance(pos_data[field], list):
                        issues.append(f"{position}.{field}: 不是数组类型")
                    else:
                        # 检查是否包含NaN或Infinity
                        for i, val in enumerate(pos_data[field]):
                            if isinstance(val, float):
                                if val != val:  # NaN检查
                                    issues.append(f"{position}.{field}[{i}]: 包含NaN值")
                                elif val == float('inf') or val == float('-inf'):
                                    issues.append(f"{position}.{field}[{i}]: 包含Infinity值")

            # 检查stats结构
            if 'stats' in pos_data:
                stats = pos_data['stats']
                if not isinstance(stats, dict):
                    issues.append(f"{position}.stats: 不是字典类型")
                else:
                    for direction in ['x', 'y', 'z']:
                        if direction in stats:
                            dir_stats = stats[direction]
                            if not isinstance(dir_stats, dict):
                                issues.append(f"{position}.stats.{direction}: 不是字典类型")
                            else:
                                for key in ['max_20_200', 'max_200_500']:
                                    if key in dir_stats:
                                        val = dir_stats[key]
                                        if val is not None and isinstance(val, float):
                                            if val != val:
                                                issues.append(f"{position}.stats.{direction}.{key}: 值为NaN")

    return issues


def find_problematic_records(sql_file_path):
    """找出有问题的记录并生成修复建议"""

    errors = validate_json_in_sql(sql_file_path)

    if errors:
        print(f"\n{'=' * 80}")
        print("问题记录详情")
        print(f"{'=' * 80}\n")

        for error in errors:
            print(f"记录ID: {error['record_id']}")
            print(f"语句编号: {error['statement_num']}")
            print(f"错误类型: {error['type']}")

            if error['type'] == 'json_decode':
                print(f"错误位置: {error.get('position', 'N/A')}")
                print(f"错误信息: {error.get('error', 'N/A')}")
            elif error['type'] == 'structure':
                print("结构问题:")
                for issue in error['issues']:
                    print(f"  - {issue}")
            else:
                print(f"错误信息: {error.get('error', 'N/A')}")

            print("-" * 80)

    return errors


def extract_and_test_single_record(sql_file_path, record_id):
    """提取并测试单条记录"""

    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = rf"UPDATE `ntf_test_result` SET `ntf_curve` = '(.+?)' WHERE `id` = {record_id};"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print(f"未找到记录ID: {record_id}")
        return

    json_str = match.group(1)

    print(f"\n记录ID: {record_id}")
    print(f"JSON长度: {len(json_str)} 字符")
    print(f"\n{'=' * 80}")

    try:
        json_obj = json.loads(json_str)
        print("✅ JSON解析成功")
        print(f"\n格式化的JSON (前500字符):")
        formatted = json.dumps(json_obj, indent=2, ensure_ascii=False)
        print(formatted[:500])

        # 验证结构
        issues = validate_json_structure(json_obj, record_id)
        if issues:
            print(f"\n⚠️ 发现 {len(issues)} 个结构问题:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ 结构验证通过")

    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败")
        print(f"错误: {e}")
        print(f"位置: {e.pos}")

        # 显示错误位置
        start = max(0, e.pos - 100)
        end = min(len(json_str), e.pos + 100)

        print(f"\n错误位置上下文:")
        print(json_str[start:e.pos] + " >>> [ERROR HERE] <<< " + json_str[e.pos:end])


def main():
    """主函数"""

    # 设置SQL文件路径
    sql_dir = Path(r"C:\Users\wangfan\Desktop\sql_output")

    sql_files = [
        sql_dir / "update_ntf_curve_part_3.sql"
    ]

    all_errors = {}

    # 验证所有文件
    for sql_file in sql_files:
        if sql_file.exists():
            errors = find_problematic_records(sql_file)
            if errors:
                all_errors[sql_file.name] = errors
        else:
            print(f"⚠️ 文件不存在: {sql_file}")

    # 生成错误报告
    if all_errors:
        print(f"\n\n{'=' * 80}")
        print("错误汇总报告")
        print(f"{'=' * 80}\n")

        for filename, errors in all_errors.items():
            print(f"\n文件: {filename}")
            print(f"错误数: {len(errors)}")
            print("问题记录ID:", [e['record_id'] for e in errors])
    else:
        print("\n\n✅ 所有SQL文件验证通过！")

    # 可选：详细检查特定记录
    # extract_and_test_single_record(sql_files[0], "24")


if __name__ == '__main__':
    main()
