# -*- coding: utf-8 -*-
from langchain_core.tools import BaseTool
from langchain import hub
from langchain.agents import AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from langchain.agents import create_react_agent
from langchain_community.llms import Tongyi

tools = [PythonREPLTool()]
model = Tongyi()
model.model_name = 'qwen-max'
model.model_kwargs = {'temperature': 0}


instructions = """You are an agent designed to write and execute python code to answer questions.
You have access to a python REPL, which you can use to execute python code.
If you get an error, debug your code and try again.
Only use the output of your code to answer the question. 
You might know the answer without running any code, but you should still run the code to get the answer.
If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.
"""
base_prompt = hub.pull("langchain-ai/react-agent-template")
prompt = base_prompt.partial(instructions=instructions)
agent = create_react_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


class AutoCodingTool(BaseTool):
    """自动编写代码并执行的工具"""

    name: str = "自动编写并运行代码的工具"
    description: str = (
        "此工具适用于天气查询、加载页面、数学运算，需要将结果通过 print 函数打印出来：print(result)。"
        "查询天气时，可以请求 http://wttr.in 获取对应城市天气。"
        "根据URL链接加载页面内容任务时，可以使用 requests 库。"
    )

    def _run(self, task: str) -> str:
        result = agent_executor.invoke({'input': '请编写并运行 python 代码来解决这个问题：' + task + '。记得使用 print() 函数将结果打印出来'})
        return result['output']
