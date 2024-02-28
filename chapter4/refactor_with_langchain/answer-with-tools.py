# -*- coding: utf-8 -*-
import sys
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain_community.llms import Tongyi
from tools.aliyun_resource_tool import AliyunResourceTool
from tools.auto_coding_tool import AutoCodingTool
from tools.service_search_tool import SearchTool

model = Tongyi()
model.model_name = 'qwen-max'
model.model_kwargs = {'temperature': 0.5}

tools = [
    AliyunResourceTool(),
    AutoCodingTool(),
    SearchTool()
]

prompt = hub.pull("hwchase17/react")

agent = create_react_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if len(sys.argv) < 2:
    print('请输入问题')
    sys.exit(1)
question = sys.argv[1]

print('问题：' + question)
result = agent_executor.invoke({'input': question})
print(result['output'])
