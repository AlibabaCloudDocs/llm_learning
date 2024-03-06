# 第 3 章 使用工具扩展问答能力的基本原理

经常使用大模型的你，一定会发现大模型并不能回答所有的问题。比如大模型大概率无法回答：你的同事小明是谁，如果小明不是特别出名的话。

本章将通过一个简单的例子，让你快速了解如何让大模型利用外部工具，来回答一些原本无法回答的问题。


## 1. 准备工作

### 1.1. 安装

下载文档代码及安装依赖项
```bash
git clone https://github.com/AlibabaCloudDocs/llm_learning.git
cd llm_learning
pip install -r requirements.txt
```

### 1.2. 账号准备

首先，您需要前往 [官网创建 API Key](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key)。接下来，请获取你的 [DASHSCOPE_API_KEY](https://dashscope.console.aliyun.com/apiKey)

####  MacOS or Linux
您可以使用以下命令行导入环境变量
```bash
export DASHSCOPE_API_KEY="sk-****"
```

#### Windows
可以在终端使用[`SET`](https://learn.microsoft.com/zh-cn/windows-server/administration/windows-commands/set_1)命令设置环境变量
```bat
set DASHSCOPE_API_KEY=sk-****
```
或者在[`PowerShell`](https://learn.microsoft.com/zh-cn/powershell/module/microsoft.powershell.core/about/about_environment_variables?view=powershell-7.4)中使用以下命令行配置环境变量 
```powershell
$Env:DASHSCOPE_API_KEY = "sk-****"
```

#### Jupyter Notebook
您可以使用[`os.environ`](https://docs.python.org/3/library/os.html)方法，在代码开头设置临时环境变量。

## 2. 快速开始
### 2.1. 与Qwen-MAX直接对话
首先我们尝试直接询问大模型关于“阿里云灵积服务”是什么的问题，方式如下：
```python
from langchain_community.llms import Tongyi

llm = Tongyi()
# 使用更强大的通义千问 max
llm.model_name = 'qwen-max'

print(llm.invoke('灵积是什么服务'))
```
输出如下：
```text
灵积（或“灵聚”）是一家提供人工智能技术服务的公司，主要服务包括智能语音交互技术、自然语言处理技术及AI解决方案等。其核心技术应用于智能家居、智能车载、机器人等领域，为各类智能终端产品赋予能听、会说、懂思考、有情感的智慧能力。但请注意，由于信息可能具有时效性，建议直接查询最新的官方资料以获取准确信息。
```
我们可以看到由于大模型不了解这个服务，所以在创造一个它认为合理的答案。

下面我们来为大模型添加一些知识，让他能正确回答这个问题。

### 2.2.基于Langchain调用自定义工具

我们首先通过调用langchain来实现自定义工具的调用，然后我们将手动实现langchain的能力，从而让大家很好的理解其中的奥妙。

这里我们将使用langchain中的AgentExecutor来实现这个能力：

（注意：如果你遇到了 TypeError: Additional kwargs key output_tokens already exists in left dict and value has unsupported type <class 'int'> 这个错误，请参考[github](https://github.com/langchain-ai/langchain/pull/16580)中的说明）

```python
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain_community.llms import Tongyi
from langchain_core.tools import BaseTool

model = Tongyi()
model.model_name = 'qwen-max'


class SearchTool(BaseTool):
    """服务查询工具"""

    name: str = "服务查询工具"
    description: str = (
        "当你不确定一个服务是什么，才使用此工具。"
    )

    def _run(self, name: str) -> str:
        if name == '灵积':
            return '''DashScope灵积模型服务建立在“模型即服务”（Model-as-a-Service，MaaS）的理念基础之上，围绕AI各领域模型，通过标准化的API提供包括模型推理、模型微调训练在内的多种模型服务。DashScope灵积模型服务依托于业界各领域的优质模型，基于阿里云强大的基础设施搭建。欢迎AI应用开发者由此开启模型探索之旅！'''
        return name + '抱歉，没有查到相关信息。'


tools = [SearchTool()]

prompt = hub.pull("hwchase17/react")

agent = create_react_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = agent_executor.invoke({'input': '灵积是什么服务'})
print(result['output'])
```
输出如下：
```text
> Entering new AgentExecutor chain...
 需要查询服务查询工具来了解“灵积”是什么服务。
Action: 服务查询工具
Action Input: 灵积DashScope灵积模型服务建立在“模型即服务”（Model-as-a-Service，MaaS）的理念基础之上，围绕AI各领域模型，通过标准化的API提供包括模型推理、模型微调训练在内的多种模型服务。
DashScope灵积模型服务依托于业界各领域的优质模型，基于阿里云强大的基础设施搭建。欢迎AI应用开发者由此开启模型探索之旅！ 根据查询结果，“灵积”是阿里云提供的一种模型服务，它基于“模型即服务”（MaaS）的理念，通过标准化API为用户提供多种AI模型服务，包括模型推理、模型微调训练等。
Final Answer: “灵积”是阿里云推出的一款围绕AI各领域模型的模型服务产品，基于“模型即服务”理念，通过标准化API接口为用户提供模型推理、模型微调训练等多种功能。

> Finished chain.
“灵积”是阿里云推出的一款围绕AI各领域模型的模型服务产品，基于“模型即服务”理念，通过标准化API接口为用户提供模型推理、模型微调训练等多种功能。
```
## 3. 原理说明
第一次执行时，我们直接向大模型提问：灵积是什么服务。 这时大模型并没有在预训练中学习过关于“灵积”服务的知识，因此无法回答。

为了解决这个问题，我们可以借助外部工具，比如搜索引擎工具如Elastic Search等，先查询一下灵积是什么服务，然后再向大模型提问。有了准确的信息补充，大模型就能回答的更准确了。

上述代码采用了"hwchase17/react"风格，这种prompt风格定义为：
```bash
input_variables=['agent_scratchpad', 'input', 'tool_names', 'tools'] 
template='Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'
```
在上述prompt中，大模型根据输入的问题{question}，来构造了一个思维链。在这个思维链中：问题、思考、行为、行动的输入、行动的结果，这五点是Agent工作的核心。在思考中，我们定义了Agent的scratchpad，这个scratchpad可以用于记录Agent的思考过程。在行动中，我们定义了Agent的工具{tools}，这个工具可以用于帮助Agent解决问题。这个思考过程可以进行N次直到Agent认为自己已经解决了问题。这时通过Thought: I now know the final answer来结束这个思考过程，然后通过Final Answer来输出最终的答案。

理解了上述过程，我们就可以考虑如何实现Agent的工具。

## 4. 自定义大模型XML交互工具
### 4.1. 定义XML交互格式
基于上述Langchain的思路我们来研究如何自定义一个工具。为了便于和大模型交互，我们定义一个XML交互工具。当用户向大模型提问时，大模型必须返回XML格式的回复，便于我们后续解析和调用工具。
```python
from langchain_community.llms import Tongyi

llm = Tongyi()
# 使用更强大的通义千问 max
llm.model_name = 'qwen-max'

prompt = '''你是一个可以回答任何问题的助手。
你可以使用下列工具: 

find_service: 当你不确定答案时，你可以使用此工具。

为了使用这个工具，你必须用<tool></tool>和<tool_input></tool_input>标签。
例如，如果您有一个名为“find_service”的工具，可以查询企业内部服务信息，为了搜索阿里云是什么服务，你会返回：
<tool>find_service</tool><tool_input>阿里云</tool_input>

使用工具后你会得到一个形式为<observation></observation>的响应，因此在第二轮你会得到输入为
<tool>find_service</tool><tool_input>阿里云</tool_input><observation>阿里云服务简介...</observation>

你需要判断<observation></observation>标签中的内容是不是你需要的答案。如果是最终答案final_answer，你需要返回答案：
<final_answer>阿里云服务简介...</final_answer>

如果你不需要使用工具也能回答问题，你也必须要用<final_answer></final_answer>标签来包裹答案。比如
<final_answer>阿里云服务详细介绍...</final_answer>

开始任务：

问题：
'''

print(llm.invoke(prompt + '灵积是什么服务'))
```
输出内容
```bash
<tool>find_service</tool><tool_input>灵积</tool_input>
```

### 4.2. 定义XML解析函数和搜索工具
```python
from langchain.output_parsers import XMLOutputParser

# 从xml中获取tool和tool_input
def get_tool_and_input(response):
    xml_response = f"<xml>{response}</xml>"
    parsed_xml_response = XMLOutputParser().invoke(xml_response)
    response_dict = {}
    for item in parsed_xml_response['xml']:
        for key in item:
            response_dict[key] = item[key]
    return response_dict

# 运行tool
def run_tool(response_dict):
    search_input =''
    search_result = ''
    if response_dict.get('tool') is None:
        search_result = response
    elif response_dict['tool'] == 'find_service':
        search_input = response_dict['tool_input']
        search_result = SearchTool().run(search_input)
    return search_input, search_result

response="""<tool>find_service</tool><tool_input>灵积</tool_input>"""
response_dict = get_tool_and_input(response)
search_input, search_result = run_tool(response_dict)
search_result
```
输出如下：
```text
'DashScope灵积模型服务建立在“模型即服务”（Model-as-a-Service，MaaS）的理念基础之上，围绕AI各领域模型，通过标准化的API提供包括模型推理、模型微调训练在内的多种模型服务。DashScope灵积模型服务依托于业界各领域的优质模型，基于阿里云强大的基础设施搭建。欢迎AI应用开发者由此开启模型探索之旅！'
```

### 4.3.一个完整的工具定义

为了更好帮助读者理解大模型Agent调用的原理，下面的代码是我们自己定义了一个简单的工具类 SearchTool 类，而不是继承自langchain的 BaseTool。并且我们实现了一个简单的 DIYAgent 类，这个类参考了langchain的接口，实现基本的调用工具的能力。这样读者可以看到大模型是如何理解用户问题并返回调用工具的指令，而Agent又是如何理解这个指令，并启动对应工具的。

```python
from langchain_community.llms import Tongyi
import json

# 定义模型
llm = Tongyi()
llm.model_name = 'qwen-max'

# 定义搜索工具
class SearchTool():
    """服务查询工具"""

    name: str = "服务查询工具"
    description: str = (
        "当你不确定一个服务是什么，才使用此工具。"
    )

    def run(self, name: str) -> str:
        if name == '灵积':
            return '''DashScope灵积模型服务建立在“模型即服务”（Model-as-a-Service，MaaS）的理念基础之上，围绕AI各领域模型，通过标准化的API提供包括模型推理、模型微调训练在内的多种模型服务。DashScope灵积模型服务依托于业界各领域的优质模型，基于阿里云强大的基础设施搭建。欢迎AI应用开发者由此开启模型探索之旅！'''
        return name + '抱歉，没有查到相关信息。'
    

# 定义查询模版
prompt_template = '''你是一个可以回答任何问题的助手。
你可以使用下列工具: 

{tools}: 当你不确定答案时，你可以使用此工具。

为了使用这个工具，你必须用<tool></tool>和<tool_input></tool_input>标签。
例如，如果您有一个名为“{tool1}”的工具，可以查询企业内部服务信息，为了搜索阿里云是什么服务，你会返回：
<tool>{tool1}</tool><tool_input>阿里云</tool_input>

使用工具后你会得到一个形式为<observation></observation>的响应，因此在第二轮你会得到输入为
<tool>{tool1}</tool><tool_input>阿里云</tool_input><observation>阿里云服务简介XXX</observation>

你需要判断<observation></observation>标签中的内容是不是你需要的答案。如果是最终答案final_answer，你需要返回答案：
<final_answer>阿里云服务简介XXX</final_answer>

如果你不需要使用工具也能回答问题，你也必须要用<final_answer></final_answer>标签来包裹答案。比如
<final_answer>阿里云服务详细介绍XXX</final_answer>

开始任务：

问题：
'''


# 定义一个简单的工具调用Agent
class DIYAgent():
    def __init__(self,tool,model=None,prompt=None):
        self.tool = tool
        self.model = model
        self.verbose = False
        self.tool_name = self.get_class_name(self.tool) 
        self.prompt = prompt.format(tools=self.tool_name,tool1 = self.tool_name)

    def get_class_name(self,tool):
        return tool.__class__.__name__
    
    # 从xml中获取tool和tool_input
    def get_tool_and_input(self, response):
        xml_response = f"<xml>{response}</xml>"
        parsed_xml_response = XMLOutputParser().invoke(xml_response)
        response_dict = {}
        for item in parsed_xml_response['xml']:
            for key in item:
                response_dict[key] = item[key]
        return response_dict

    # 运行tool
    def run_tool(self, response_dict):
        search_input =''
        search_result = ''

        if response_dict.get('tool') is None:
            if response_dict.get('final_answer') is not None:
                return search_input, response_dict['final_answer']
            else:
                return search_input, "Error in tool"+json.dumps(response_dict)

        if response_dict['tool'] ==  self.tool_name:
            search_input = response_dict['tool_input']
            search_result = self.tool.run(search_input)
            return search_input, search_result

    # run agent
    def run(self, request):
        raw_response = self.model.invoke(self.prompt + request)
        response_dict = self.get_tool_and_input(raw_response)
        print("使用工具：", response_dict['tool'])
        print("查询内容：", response_dict['tool_input'])
        search_input, search_result = self.run_tool(response_dict)
        print("搜索结果：", search_result)

        new_prompt = self.prompt + f"<tool>{self.tool_name}</tool><tool_input>{search_input}</tool_input><observation>{search_result}</observation>"
        final_response = self.model.invoke(new_prompt)
        final_response_dict = self.get_tool_and_input(final_response)
        search_input, final_answer = self.run_tool(final_response_dict)
        return final_answer



# MIAN Function
tool = SearchTool()

diyAgent = DIYAgent(tool ,llm, prompt_template)

result = diyAgent.run("灵积是什么服务")
print("最终输出：",result)
```
输出如下：
```text
使用工具： SearchTool
查询内容： 灵积
搜索结果： DashScope灵积模型服务建立在“模型即服务”（Model-as-a-Service，MaaS）的理念基础之上，围绕AI各领域模型，通过标准化的API提供包括模型推理、模型微调训练在内的多种模型服务。DashScope灵积模型服务依托于业界各领域的优质模型，基于阿里云强大的基础设施搭建。欢迎AI应用开发者由此开启模型探索之旅！
最终输出： DashScope灵积模型服务是一个基于“模型即服务”（Model-as-a-Service，MaaS）理念的平台，它提供了AI各领域模型的标准化API服务，包括模型推理、模型微调训练等。该服务依托于业界各领域的优质模型资源，并借助阿里云强大的基础设施构建而成。其目的是为了方便AI应用开发者能够便捷地使用和探索各类模型。
```

### 4.4. 添加更多的搜索词条
扩展搜索范围时，我们只需要扩展SearchTool函数的能力即可，比如从搜索引擎上下载信息。为了进行对比，我们直接填入一些已知信息。
```python
# 扩展支持的服务查询
class SearchTool2():
    """服务查询工具"""

    name: str = "服务查询工具"
    description: str = (
        "当你不确定一个服务是什么，才使用此工具。"
    )

    def run(self, name: str) -> str:
        if name == '灵积':
            return '''DashScope灵积模型服务建立在“模型即服务”（Model-as-a-Service，MaaS）的理念基础之上，围绕AI各领域模型，通过标准化的API提供包括模型推理、模型微调训练在内的多种模型服务。DashScope灵积模型服务依托于业界各领域的优质模型，基于阿里云强大的基础设施搭建。欢迎AI应用开发者由此开启模型探索之旅！'''
        elif name=="百炼":
            return "百炼，即大模型服务平台，是面向企业客户及合作伙伴的，基于通义大模型、行业大模型以及三方大模型，结合企业专属数据，包含全链路大模型开发工具的一站式大模型商业化平台。提供完整的模型训练、微调、评估等产品工具，预置丰富的应用插件，提供便捷的集成方式，更快更高效地完成大模型应用的构建。"
        elif (name=="PAI") or (name=="阿里云 PAI"):
            return "人工智能平台 PAI（Platform of Artificial Intelligence）面向企业客户及开发者，提供轻量化、高性价比的云原生人工智能，涵盖DSW交互式建模、Designer拖拽式可视化建模、DLC分布式训练到EAS模型在线部署的全流程。"
        elif name=="OSS":
            return "阿里云对象存储OSS（Object Storage Service）是一款海量、安全、低成本、高可靠的云存储服务，可提供99.9999999999%（12个9）的数据持久性，99.995%的数据可用性。多种存储类型供选择，全面优化存储成本。"
        return name + '抱歉，没有查到相关信息。'
    

# MIAN Function
tool = SearchTool2()

diyAgent = DIYAgent(tool ,llm, prompt_template)

result = diyAgent.run("百炼是什么服务")
print("最终输出：",result)
```
输出如下：
```text
使用工具： SearchTool2
查询内容： 百炼
搜索结果： 百炼，即大模型服务平台，是面向企业客户及合作伙伴的，基于通义大模型、行业大模型以及三方大模型，结合企业专属数据，包含全链路大模型开发工具的一站式大模型商业化平台。提供完整的模型训练、微调、评估等产品工具，预置丰富的应用插件，提供便捷的集成方式，更快更高效地完成大模型应用的构建。
最终输出： 百炼是阿里云推出的大模型服务平台，旨在为企业客户及合作伙伴提供一站式大模型商业化解决方案。该平台基于通义大模型、行业大模型以及三方大模型，并结合企业专属数据，提供了全链路的大模型开发工具。通过百炼，用户可以进行模型训练、微调、评估等操作，并且拥有预置的丰富应用插件和便捷的集成方式，从而高效快速地构建大模型应用。
```

### 4.5.使用封装好的代码来实现服务查询

我们将上述代码重构后封装在文件[`search-with-tool.py`](search-with-tool.py)中。为了便于后续章节扩展，我们实现了列表式工具加载，与langchain的接口保持一致。
  
列表式工具加载：```tool = [SearchTool()]```

你可以尝试用自己的方式来修改代码。这段代码可以用以下方式来运行：

```python3 search-with-tool.py -question="the question"```

尝试执行代码
```bash
python search-with-tool.py --question="百炼是什么服务"
```
输出内容
```text
正在分析内容...
使用工具：SearchTool...
查询内容：百炼...
查询到参考信息：百炼，即大模型服务平台，是面向企业客户及合作伙伴的，基于通义...
正在分析内容...
最终答案：百炼是阿里云推出的大模型服务平台，旨在为客户提供一站式大模型商业化解决方案。该平台基于通义大模型、行业大模型及第三方大模型，并结合企业专属数据，提供全链路大模型开发工具，包括模型训练、微调和评估等功能。此外，百炼还预置了丰富的应用插件，方便用户快速集成构建大模型应用，以实现更高效便捷的应用落地。
```
尝试执行代码
```bash
python search-with-tool.py --question="PAI是什么服务"
```
输出内容
```text
正在分析内容...
使用工具：SearchTool...
查询内容：PAI 阿里云服务...
查询到参考信息：人工智能平台 PAI（Platform of Artific...
正在分析内容...
最终答案：阿里云PAI服务是面向企业客户及开发者的人工智能平台，提供轻量化、高性价比的云原生人工智能解决方案，覆盖从DSW交互式建模、Designer拖拽式可视化建模、DLC分布式训练到EAS模型在线部署的全流程。
```

## 5. 参考资料
- [DashScope](https://dashscope.aliyun.com/)
- [LangChain](https://python.langchain.com/docs)

*****
## 本章代码
- 请点击[本章实验代码](demo-chapter3.ipynb)查阅相关内容。

## 继续学习
- [上一篇：第 2 章 找出网络上两篇文档之间的差异](../chapter2/README.md)
- [下一篇：第 4 章 让通义千问编写并执行代码](../chapter4/README.md)
- [【通义千问API入门教程】章节目录](../README.md)



