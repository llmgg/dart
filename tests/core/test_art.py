import unittest

from DART.core.art import ART
from DART.core.base.agent import Agent
from DART.core.types.chat_config import ChatConfig
from DART.core.types.runtime_config import RuntimeConfig
from DART.core.types.message import UserMessage
from DART.utils.logger import logger
from DART.core.models.remote_models import jd_runtime, RemoteModels
from DART.core.models.local_models import local_models


class TestARTRunStream(unittest.TestCase):
    def setUp(self):
        # 初始化一个 ART 实例
        ollama_config = RuntimeConfig(
            api_key='ollama',
            base_url='http://localhost:11434/v1',
            default_model=local_models[0],
            models=local_models,
        )
        self.remote_runtime_config = jd_runtime
        self.art_7B = ART(runtime_config=ollama_config, chat_config=ChatConfig(model=local_models[0]))
        self.art_remote = ART(runtime_config=self.remote_runtime_config)
        self.art_remote.client = RemoteModels()

        def get_whether(city: str, date: str):
            '''
            获取指定城市指定日期的天气情况。
            @param city:
            @param date:
            @return:
            '''
            if not isinstance(date, str) or len(date.split('*')) < 3:
                raise ValueError(f'the format of "date" should be "yyyy*mm*dd"')
            return f'日期：{date}，城市：{city}，气温：25度，天气情况：晴天。'

        def get_hotel(city: str, price: float = 300):
            '''
            获取城市下不超过指定价格的酒店列表。
            @param city:
            @param price:
            @return:
            '''
            return f'{city}价格不超过{price}的酒店列表：\nHotel A\nHotel B\nHotel C'

        def get_diet(city: str, style: str):
            '''
            获取城市下不同风格的美食列表。
            @param city:
            @param style:
            @return:
            '''
            return f'{city}时风格为{style}的美食列表：\nDiet A\nDiet B\nDiet C'

        def get_scenic(city: str):
            '''
            获取城市下景点列表。
            @param city:
            @return:
            '''
            return f'{city}的景点列表：\nScenic A\nScenic B\nScenic C'

        def get_transport(city: str):
            '''
            获取城市下交通方式列表。
            @param city:
            @return:
            '''
            return f'去城市{city}的交通方式列表：\nTransport A\nTransport B\nTransport C'

        def get_date():
            """
            返回当前日期
            @return:
            """
            return '2023-08-01'

        # test handoffs
        self.agent_A = Agent(
            name='agent_A',
            persona='旅游向导。',
            description='根据用户的问题给出对应城市相应的出行建议和旅游向导，包括出行方式、住宿、饮食、景点、天气等相关信息。',
            art=self.art_7B,
        )
        tools = [
            get_whether, get_scenic, get_transport, get_hotel, get_diet
        ]
        self.agent_A.set_tools(tools)

        self.agent_B = Agent(
            name='agent_B',
            persona='翻译专家。',
            description='根据用户的问题，处理与翻译相关的问题。',
            art=self.art_7B,
        )
        self.agent_C = Agent(
            name='agent_C',
            persona='An agent to get the current date.',
            description='根据用户的问题，处理与日期相关的问题。',
            tools=[get_date],
            art=self.art_7B,
        )
        self.agent_D = Agent(
            name='agent_D',
            persona='天气预报专家',
            description='根据用户的问题，对工具进行调用，处理与天气相关的问题。',
            tools=[get_whether],
            art=self.art_7B,
        )
        self.agent_PM = Agent(
            name='agent_PM',
            persona='项目经理。',
            description='根据用户的需求选择合适的智能体和工具进行处理，结合返回的消息回答用户的问题。',
            tools=[get_whether],
        )
        self.agent_PM.set_handoffs([self.agent_A, self.agent_B, self.agent_C])

    def test_run_stream_without_tool_calls(self):
        # 模拟 Agent 对象
        agent = Agent(
            name='stream_agent',
            persona='你是个Agent运行环境测试机。',
            description='请从1数到10',
        )
        messages = [UserMessage(content="开始测试").to_dict()]
        for output in self.art_7B.run(agent, messages=messages, debug=True, stream=True):
            print(output)

    def test_tool_calls(self):
        messages = [
            UserMessage(content="我明天要去北京旅游2天，帮我看一下北京的天气和交通情况，给我一个旅游攻略。").to_dict()]
        for output in self.art_7B.run(self.agent_A, messages=messages, max_chat_times=5, debug=True, stream=True):
            print(output, flush=True)

    def test_handoffs(self):
        # messages = [UserMessage(content="帮我将下面的句子翻译成英文：你好，这是一个测试。直接输出翻译后的结果，不要其它信息。").to_dict()]
        messages = [UserMessage(content="今天是几号？北京的天气怎么样？").to_dict()]
        # messages = [UserMessage(content="明天是几号？我要去北京旅游2天，帮我看一下北京的天气和交通情况，给我一个旅游攻略。").to_dict()]
        result = ''
        for output in self.art_7B.run(
                self.agent_PM, messages=messages, max_chat_times=10, debug=True, stream=True,
                # stop_if_no_tools=False, include_think=False,
        ):
            if 'content' in output and output['content']:
                result += output['content']
        logger.info('The final result is: \n' + result)

    def test_async(self):
        messages = [UserMessage(content="今天是几号？北京的天气怎么样？").to_dict()]
        self.agent_PM.parallel_execute = True
        result = ''
        for output in self.art_7B.run(
                self.agent_PM, messages=messages, max_chat_times=10, debug=True, stream=True,
                # stop_if_no_tools=False,
        ):
            if 'content' in output and output['content']:
                result += output['content']
        logger.info('The final result is: \n' + result)


if __name__ == '__main__':
    unittest.main()
