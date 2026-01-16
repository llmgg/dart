#!/usr/bin/env python3
"""
多Agent系统使用示例

此示例展示了如何使用MultiAgentART来创建和运行多Agent系统，
支持DAG调度和并行执行。
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 禁用日志文件创建（可选）
os.environ['DART_LOG_FILE'] = 'false'

from DART.core.base.agent import Agent
from DART.core.multi_agent_art import MultiAgentART
from DART.core.types.runtime_config import RuntimeConfig
from DART.core.types.message import UserMessage


def create_agents():
    """创建示例Agent"""

    # 数据收集Agent
    data_collector = Agent(
        name="data_collector",
        persona="数据收集专家",
        description="负责从各种来源收集数据并整理",
        tools=[]
    )

    # 数据分析Agent
    data_analyzer = Agent(
        name="data_analyzer",
        persona="数据分析专家",
        description="负责分析数据并生成洞察",
        tools=[]
    )

    # 报告生成Agent
    report_generator = Agent(
        name="report_generator",
        persona="报告生成专家",
        description="基于分析结果生成最终报告",
        tools=[]
    )

    return data_collector, data_analyzer, report_generator


def main():
    """主函数：演示多Agent系统"""

    # 1. 创建运行时配置
    runtime_config = RuntimeConfig(
        api_key="your_api_key_here",  # 替换为你的API密钥
        base_url="https://api.openai.com/v1",
        models=["gpt-3.5-turbo"],
        default_model="gpt-3.5-turbo"
    )

    # 2. 创建多Agent运行环境
    multi_art = MultiAgentART(runtime_config, max_workers=3)  # 最多3个并行任务

    # 3. 创建Agent实例
    data_collector, data_analyzer, report_generator = create_agents()

    # 4. 添加任务（定义DAG依赖关系）
    multi_art.add_task(
        task_id="collect_data",
        agent=data_collector,
        inputs={"messages": [UserMessage(content="收集最新的AI技术发展趋势数据")]}
    )

    multi_art.add_task(
        task_id="analyze_data",
        agent=data_analyzer,
        dependencies=["collect_data"],  # 依赖数据收集任务
        inputs={"messages": [UserMessage(content="分析收集的数据，找出关键趋势")]}
    )

    multi_art.add_task(
        task_id="generate_report",
        agent=report_generator,
        dependencies=["analyze_data"],  # 依赖数据分析任务
        inputs={"messages": [UserMessage(content="基于分析结果生成完整的趋势报告")]}
    )

    # 5. 运行多Agent系统
    print("🚀 开始执行多Agent系统...")
    print(f"📊 总任务数: {len(multi_art.scheduler.tasks)}")

    for event in multi_art.run():
        if event.get('task_started'):
            print(f"▶️  任务开始: {event['task_started']}")
        elif event.get('task_completed'):
            task_id = event['task_completed']
            print(f"✅ 任务完成: {task_id}")
        elif event.get('task_failed'):
            task_id = event['task_failed']
            print(f"❌ 任务失败: {task_id} - {event.get('error', '')}")
        elif event.get('multi_agent_status') == 'completed':
            print("🎉 多Agent系统执行完成！")
            break
        elif event.get('error'):
            print(f"💥 执行错误: {event['error']}")
            break

    # 6. 查看结果
    print("\n📈 最终结果:")
    status = multi_art.get_status()
    summary = status['multi_agent_status']['task_summary']
    print(f"总任务: {summary['total']}")
    print(f"完成: {summary['completed']}")
    print(f"失败: {summary['failed']}")
    print(f"完成率: {summary['completion_rate']*100:.1f}%")

    # 7. 获取详细任务结果
    task_results = multi_art.get_task_results()
    print("\n📋 任务详情:")
    for task_id, result in task_results.items():
        status = result['status']
        exec_time = result['execution_time']
        print(f"  {task_id}: {status} ({exec_time:.3f}s)")


if __name__ == "__main__":
    main()