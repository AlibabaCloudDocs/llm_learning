# -*- coding: utf-8 -*-
import json
import os
import sys
from typing import Any
from langchain_core.tools import BaseTool
from alibabacloud_cloudcontrol20220830.client import Client as cloudcontrol20220830Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cloudcontrol20220830 import models as cloudcontrol_20220830_models
from alibabacloud_tea_util import models as util_models
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain_community.llms import Tongyi

# 阿里云资源查询工具
class AliyunResourceTool(BaseTool):
    """查询阿里云资源的工具"""

    name: str = "阿里云的云资源查询工具"
    description: str = (
        "用于查询账号下的阿里云的源信息，需要指通过 json 指定产品名 product、资源类型 resource、地域 region。"
        "ECS 的默认资源为 Instance，VPC 的默认资源为 VPC。"
        "region 只能是某一个指定的地域，参考格式：cn-hangzhou、cn-beijing、us-east-1"
    )

    def _run(self, params) -> Any:
        params_dict = json.loads(params)
        request_path = f'/api/v1/providers/Aliyun/products/{params_dict["product"]}/resources/{params_dict["resource"]}'
        get_resources_request = cloudcontrol_20220830_models.GetResourcesRequest(
            region_id=params_dict.get("region") or 'cn-hangzhou',
            max_results=2
        )
        runtime = util_models.RuntimeOptions()
        headers = {}
        try:
            config = open_api_models.Config(
                access_key_id=os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'],
                access_key_secret=os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
            )
            # Endpoint 请参考 https://api.aliyun.com/product/cloudcontrol
            config.endpoint = f'cloudcontrol.aliyuncs.com'
            client = cloudcontrol20220830Client(config)
            # 复制代码运行请自行打印 API 的返回值
            result = client.get_resources_with_options(request_path, get_resources_request, headers, runtime)
            return result.body
        except Exception as error:
            # 错误 message
            print(error)
            return '查询失败'


# 定义通义千问大模型AGENT

class MyAgent():
    def __init__(self):
        self.agent_executor=self.assemble_agent_executor()

    def assemble_agent_executor(self):
        model = Tongyi()
        model.model_name = 'qwen-max'
        model.model_kwargs = {'temperature': 0.5}

        tools = [
            AliyunResourceTool(),
        ]

        prompt = hub.pull("hwchase17/react")

        agent = create_react_agent(model, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        return agent_executor

    def ask(self, question):
        result = self.agent_executor.invoke({'input': question})
        return result['output']
    



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('请输入问题')
        sys.exit(1)
    question = sys.argv[1]

    print('问题：' + question)
    llm = MyAgent()
    result = llm.ask(question)
    print(result)