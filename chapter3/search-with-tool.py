from langchain_community.llms import Tongyi
from langchain.output_parsers import XMLOutputParser
import argparse

# 定义模型
llm = Tongyi()
llm.model_name = 'qwen-max'

# 定义搜索工具
class SearchTool():
    """服务查询工具"""

    name: str = "阿里云服务查询工具"
    description: str = (
        "当你不确定一个阿里云服务是什么，才使用此工具。"
    )

    def run(self, name: str) -> str:
        if(name=="灵积") or (name=="灵积 阿里云服务"):
            return '''DashScope灵积模型服务建立在“模型即服务”（Model-as-a-Service，MaaS）的理念基础之上，围绕AI各领域模型，通过标准化的API提供包括模型推理、模型微调训练在内的多种模型服务。DashScope灵积模型服务依托于业界各领域的优质模型，基于阿里云强大的基础设施搭建。欢迎AI应用开发者由此开启模型探索之旅！'''
        elif name=="百炼":
            return "百炼，即大模型服务平台，是面向企业客户及合作伙伴的，基于通义大模型、行业大模型以及三方大模型，结合企业专属数据，包含全链路大模型开发工具的一站式大模型商业化平台。提供完整的模型训练、微调、评估等产品工具，预置丰富的应用插件，提供便捷的集成方式，更快更高效地完成大模型应用的构建。"
        elif (name=="PAI") or (name=="阿里云 PAI")or (name=="PAI 阿里云服务"):
            return "人工智能平台 PAI（Platform of Artificial Intelligence）面向企业客户及开发者，提供轻量化、高性价比的云原生人工智能，涵盖DSW交互式建模、Designer拖拽式可视化建模、DLC分布式训练到EAS模型在线部署的全流程。"
        elif name=="OSS":
            return "阿里云对象存储OSS（Object Storage Service）是一款海量、安全、低成本、高可靠的云存储服务，可提供99.9999999999%（12个9）的数据持久性，99.995%的数据可用性。多种存储类型供选择，全面优化存储成本。"
        return name + '抱歉，没有查到相关信息。'
    

# 定义查询模版
prompt_template = '''你是一个可以回答任何问题的助手。
你可以使用下列工具: 

{tools}

为了使用这个工具，你必须用<tool></tool>和<tool_input></tool_input>标签。
例如，如果您有一个名为“{tool1}”的工具，可以查询企业内部服务信息，为了搜索阿里云是什么服务，你会返回：
<tool>{tool1}</tool><tool_input>阿里云</tool_input>

使用工具后你会得到一个形式为<observation></observation>的响应，因此在第二轮你会得到输入为
<tool>{tool1}</tool><tool_input>阿里云</tool_input><observation>阿里云服务简介等等</observation>

你需要判断<observation></observation>标签中的内容是不是你需要的答案。如果是final_answer，你需要返回答案：
<final_answer>阿里云服务简介等等</final_answer>

不管你是否选用工具你都必须要用<final_answer></final_answer>标签来包裹最终返回答案。比如
<final_answer>阿里云服务详细介绍等等</final_answer>

如果是final_answer，请检查返回答案的结尾，该结尾必须有</final_answer>标签结束

开始任务：

问题：
'''


# 定义一个简单的工具调用Agent
class DIYAgent():
    def __init__(self,tools,model=None,prompt=None):
        self.tools = tools
        self.model = model
        self.verbose = False
        self.tool_name = [self.get_class_name(t) for t in self.tools]
        self.tool_prompt_desc = [self.get_class_name(t)+": "+t.name for t in self.tools]
        self.prompt = prompt.format(tools=self.tool_prompt_desc, tool1 = self.tool_name[0])

    def get_class_name(self,tool):
        return tool.__class__.__name__
    
    # 从xml中获取tool和tool_input
    def _parse_tool_args(self, response):
        xml_response = f"<xml>{response}</xml>"
        parsed_xml_response = XMLOutputParser().invoke(xml_response)
        response_dict = {}
        for item in parsed_xml_response['xml']:
            for key in item:
                response_dict[key] = item[key]
        return response_dict

    # 由于大模型可能不能正确返回<final_answer></final_answer>，所以需要增加大量异常处理和判断逻辑
    def parsed_xml_response(self, response):
        response_dict={}
        try:
            response_dict = self._parse_tool_args(response)
        except Exception as e:
            if (response.startswith('<final_answer>')):
                response += '</final_answer>'
                try:
                    response_dict = self._parse_tool_args(response)
                except Exception as e:
                    return False, response
            else:
                return False, response
        # 正常返回结束
        if response_dict.get('final_answer') is not None:
            return False, response_dict['final_answer']
        elif response_dict.get('tool') is None:
            return False, response
        # 正常返回工具信息
        return True, response_dict
    
    # 找到合适的工具并执行
    def run_tool(self, response_dict):
        search_input =''
        search_result = ''
        for t in self.tools:
            tool_name = self.get_class_name(t)
            if response_dict['tool'] == tool_name:
                search_input = response_dict['tool_input']
                search_result = t.run(search_input)
                return tool_name, search_input, search_result

    # run agent
    def run(self, request):
        prompt= self.prompt + request
        while True:
            print(f"\033[32m正在分析内容...\033[0m")
            raw_response = self.model.invoke(prompt)
            is_dict, response_dict=self.parsed_xml_response(raw_response)
            if(is_dict==False):
                return response_dict
            
            print(f"\033[32m使用工具：{response_dict['tool']}...\033[0m")   
            print(f"\033[32m查询内容：{response_dict['tool_input']}...\033[0m")

            tool_name, search_input, search_result = self.run_tool(response_dict)
            
            prompt = self.prompt + f"<tool>{tool_name}</tool><tool_input>{search_input}</tool_input><observation>{search_result}</observation>"
            print(f"\033[32m查询到参考信息：{search_result[0:30]}...\033[0m")


if __name__ == '__main__':
    # define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--question', type=str, default='灵积是什么服务', help='question to be answered')

    # extract arguments
    args = parser.parse_args()

    # # define environment
    # import os
    # from modelscope.utils.config import Config
    # key_cfg = Config.from_file("../config/key-configs.json")
    # os.environ['DASHSCOPE_API_KEY']=key_cfg["DASHSCOPE_API_KEY"]

    # define tools
    tool = [SearchTool()]

    # run agent
    diyAgent = DIYAgent(tool ,llm, prompt_template)
    result = diyAgent.run(args.question)
    print(f"\033[32m最终答案：{result}\033[0m")
