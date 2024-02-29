# 第 4 章 让通义千问编写并执行代码
基于前面三章的铺垫，本章我们将展示大模型Agent的强大能力。我们不仅要实现让大模型同时使用多种查询工具，还要实现让大模型能查询天气情况，最后让大模型自己写代码来查询天气情况。

在前面的学习中，你已经尝试让大模型学会了使用一个工具，来回答原本不能回答的问题。但是你可能会发现，实际问题中你需要更多的工具：
- Q：能不能问天气情况？
- Q：能不能写代码？
- Q：能不能代码开发再精简一点，好维护一点？

可以，本章不仅一股脑全部教给你，还要让大模型自己写代码自己查天气！


## 1. 准备工作

### 1.1. 安装

下载文档代码及安装依赖项
```bash
git clone https://github.com/AlibabaCloudDocs/llm_learning.git
cd llm_learning
pip install -r requirements.txt
```

### 1.2. 账号准备

首先，您需要前往 [官网创建 API Key](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key)。接下来，请获取你的 [DASHSCOPE_API_KEY](https://dashscope.console.aliyun.com/apiKey)，请于[RAM访问控制](https://ram.console.aliyun.com/manage/ak)创建和查询您的阿里云AK/SK。

您可以使用以下命令行导入系统
```bash
export DASHSCOPE_API_KEY="sk-****"
export ALIBABA_CLOUD_ACCESS_KEY_ID="<your access key id>"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="<your access key secret>"
```


## 2. 搭建能同时使用更多工具的Agent
第二章的例子，通义千问能够回答"灵积服务是什么"这个原本它无法回答的问题了。如果我们想让通义千问回答更多问题，比如：杭州的天气怎么样？我的ECS实例什么时候到期？很明显，目前通义千问是无法回答这些问题的。但是你现在已经知道，给它加两个工具就行了。

首先，我们可以尝试自定的方法。我们用第三章自定义的类`DIYAgent`同时加载了三个Agent查询工具，代码在文件[`search-with-tools.py`](more_tools/search-with-tools.py)中，接下来我们演看一下大模型能否自动使用不同工具完成任务。

### 2.1. 搭建天气查询工具
天气查询工具的代码如下
```python
# 定义天气查询工具
class WeatherSearch(BaseTool):
    """天气查询工具"""

    name: str = "天气查询工具"
    description: str = (
        "用于查询近期的天气，使用此工具。"
    )

    def _run(self, city: str) -> str:
        result = requests.get('http://wttr.in/' + city)
        return result.text
```
你可以尝试运行一下这段代码，它会回答"杭州的天气怎么样"这个问题：
```bash
python more_tools/search-with-tools.py --question="杭州的天气怎么样"
```
输出内容
```text
正在分析内容...
使用工具：WeatherSearch...
查询内容：杭州...
查询到参考信息：Weather report: 杭州

正在分析内容...
最终答案：杭州的当前天气情况如下：

  - 实时天气：晴朗
  - 温度：23°C（体感温度25°C）
  - 风速：22 km/h，方向为下降风
  - 能见度：8公里
  - 湿度：0.0 mm

未来几天预报：
- 2月19日（周一）：早晨部分多云，午后部分多云，傍晚有小雨，夜间有零星小雨。气温在18°C至21°C之间变化，风速从2-3 km/h到8-9 km/h不等。
- 2月20日（周二）：全天均有零星小雨，气温维持在+10°C左右，风向偏南风，风速约在11-16 km/h范围内。
- 2月21日（周三）：早晨有小雨，午后短暂阵雨，傍晚局部地区有小雨，夜间中雨。气温逐渐降低，从+9°C降至+4°C，风速在9-18 km/h到11-15 km/h之间。

地点：杭州市, 江干区 (Jianggan), 杭州市 Hangzhou, 浙江省, 中国 [30.2489468,120.2052547]
```

### 2.2. 自定义查询工具
我们仍然可以为大模型加载在第三章定义过的自定义查询工具，

自定义查询工具的代码如下
```python
# 定义搜索工具
class SearchTool(BaseTool):
    """服务查询工具"""

    name: str = "阿里云服务查询工具"
    description: str = (
        "当你不确定一个阿里云服务是什么，才使用此工具。"
    )

    def _run(self, name: str) -> str:
        if(name=="灵积") or (name=="灵积 阿里云服务"):
            return '''DashScope灵积模型服...（此处省略）'''
        elif name=="百炼":
            return "百炼，即大模型服务平台...（此处省略）"
        elif (name=="PAI") or (name=="阿里云 PAI"):
            return "人工智能平台 PAI...（此处省略）"
        elif name=="OSS":
            return "阿里云对象存储OSS（...（此处省略）"
        return name + '抱歉，没有查到相关信息。'
```

我们看一下其输出：

```bash
python more_tools/search-with-tools.py --question="灵积是什么服务"
```
输出内容
```
正在分析内容...
使用工具：SearchTool...
查询内容：灵积...
查询到参考信息：DashScope灵积模型服务建立在“模型即服务”（Mode...
正在分析内容...
最终答案：DashScope灵积模型服务是一个基于“模型即服务”（MaaS）理念，提供模型推理、模型微调训练等多元服务的平台。该服务整合了业界各领域的高质量模型，并依托阿里云强大的基础设施搭建而成，旨在为AI应用开发者提供便捷高效的模型探索和使用环境。
```

### 2.3. 阿里云资源查询
你也可以运行另一段代码，它会告诉你你在杭州地域的ECS实例什么时候到期：

>ALIBABA_CLOUD_ACCESS_KEY_ID 与 ALIBABA_CLOUD_ACCESS_KEY_SECRET 的导入方法请参考本章前文 [1.2.账号准备]

参考阿里云API，我们实现了阿里云资源查询类[`aliyun_resources.py`](more_tools/aliyun_resources.py)，并用下面定义的`ECSSearch`工具来调用这个类。

出于学习的目的，我们也用langchain接口实现了一个阿里云资源查询工具[`aliyun_resource_tool.py`](refactor_with_langchain/tools/aliyun_resource_tool.py)，并应用于3.1节的场景中，您可以对比这两种实现的异同。

```python
# 定义ECS查询工具
class ECSSearch(BaseTool):
    """ECS查询工具"""

    name: str = "ECS查询工具"
    description: str = (
        "用于查询ECS资源使用情况。返回json格式ECS列表。"
    )

    def _run(self, city: str) -> str:
        return '这是 json 格式的 ECS 列表信息：' + str(AliyunResources.get_resource_details())
```

这里我们需要额外定义一个类AliyunResources，封装查询阿里云资源的具体方法（暂时不讨论 AliyunResources 类，本段主要目的是展示工具接口定义的基本思路和接口一致性）

下面我们让大模型使用这个工具：

```bash
python more_tools/search-with-tools.py --question="我的ECS实例什么时候到期"
```

输出内容
```
正在分析内容...
使用工具：ECSSearch...
查询内容：查询ECS实例到期时间...
查询到参考信息：这是 json 格式的 ECS 列表信息：{'maxResu...
正在分析内容...
最终答案：根据查询结果，当前没有ECS实例信息或者没有实例即将到期。观测到的JSON数据显示'totalCount': 0，意味着没有找到任何ECS实例。
```
### 2.4. 更多阿里云资源查询方法

使用阿里云的[云控制 API](https://help.aliyun.com/zh/cloud-control-api/)，它可以让你使用风格一致的 API 管理绝大多数阿里云资源。

你可以尝试运行以下查询：

```bash
python more_tools/search-with-tools.py --question="我在上海有没有VPC"
```
输出内容
```
正在分析内容...
最终答案：您在上海拥有名为“vpc-123456”的VPC资源。详细信息包括：[此处列出VPC详细信息]。
```
你可以尝试查询ECS安全组：
```bash
python more_tools/search-with-tools.py --question="列出我在杭州的ECS安全组"
```
输出内容
```
正在分析内容...
使用工具：ECSSearch...
查询内容：杭州 ECS 安全组 列出...
查询到参考信息：这是 json 格式的 ECS 列表信息：{'maxResu...
正在分析内容...
最终答案：当前在杭州地域没有查到任何ECS安全组。列表信息如下：{'maxResults': 2, 'requestId': '0F3B5EAD-C386-5116-9748-10336CD31D93', 'resources': [], 'totalCount': 0}
```
由于本章使用的测试账号没有开通ECS服务，因此反馈没有查询到ECS实例。

>您可以[查看云服务产品信息](https://www.aliyun.com/product/ecs?source=5176.11533457#/)通过阿里云权益中心购买的 99 元/年的经济型 2核2G ECS 实例，新老客户都可以购买，并且后续可以 99 元续费。您可以参考[阿里云便宜服务器优惠合集](https://developer.aliyun.com/article/1445729)参与优惠活动


### 2.5. 让代码更好维护

以上我们仿照langchain的代码风格构造了Agent工具调用方法，读者可以根据自己的喜好来定义类似的Agent类。但是工具越多，代码管理起来越难。特别是不同工具导致大模型输出性能没有对齐的情况下，工具之间也有可能出现性能差异，代码维护难度较大。因此，我们可以看一下langchain的实现方法是什么样。

有人说 「LangChain 是大模型时代的 Spring」。LangChain 确实就像 Spring 一样，是一个框架，合理的使用它，可以使得代码更清晰，更易维护。

我们直接来看一下，通过 LangChain 重构后的代码吧：

```python
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

```


## 3. 让通义千问自己写代码解决问题

如果我们想让通义千问可以帮我们查询天气、根据 URL 读取文档里的一些信息，我们就要不断的添加工具，我并不擅长写代码，该怎么办？

针对这个问题，有好几个解决办法：

耐着性子学习一下写代码。遇到问题时你可以使用通义千问等大模型来教你如何写代码。
在你的 IDE 上安装通义灵码，它会根据你的注释自动编写代码，让写代码变得更加简单。
看到这里，机智的你可能会想到，既然通义千问都能自己根据需求写代码了，那是不是可以自动生成并运行代码来解决问题？

这里我们基于 langchain_experimental.tools.PythonREPLTool 封装一个自动代码生成工具，生成一个react_agent。

对象初始化部分如：
```python
tools = [PythonREPLTool()]

model = Tongyi()
model.model_name = 'qwen-max'
...
...
agent = create_react_agent(model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

```

自动代码生成工具的类定义如下

```python
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
```

下面我们来看看大模型遇到不懂的问题就写代码来查询答案的整体效果。


### 3.1. 让通义千问自己写代码来实现功能
我们基于langchain的接口重新定义了一个可以自动写代码完成任务的Agent，代码在文件[`refactor_with_langchain/answer-with-tools.py`](refactor_with_langchain/answer-with-tools.py)中。
```bash
! python refactor_with_langchain/answer-with-tools.py '加载并列出这个页面的二级标题https://help.aliyun.com/zh/oss/product-overview/what-is-oss'
```
输出内容
```
问题：加载并列出这个页面的二级标题https://help.aliyun.com/zh/oss/product-overview/what-is-oss


> Entering new AgentExecutor chain...
 我需要使用自动编写并运行代码的工具来加载页面内容，并从中提取二级标题。
Action: 自动编写并运行代码的工具
Action Input: 
···
import requests
from bs4 import BeautifulSoup

# 加载页面内容
response = requests.get('https://help.aliyun.com/zh/oss/product-overview/what-is-oss')
soup = BeautifulSoup(response.text, 'html.parser')

# 提取二级标题（h2标签）
second_level_headers = soup.find_all('h2')

# 打印二级标题
for header in second_level_headers:
    print(header.text)
···

··· (代码省略，如果有兴趣可以查看demo并执行)

···

> Finished chain.
页面https://help.aliyun.com/zh/oss/product-overview/what-is-oss的二级标题包括：

1. 快速了解OSS
2. OSS工作原理
3. OSS重要特性
4. OSS使用方式
5. OSS计费
6. 其他相关服务
7. 其他阿里云存储服务
```

### 3.2. 让通义千问自己实现天气查询
我们在注释中告诉了大模型查询天气的地址，现在我们来看看他如何自己写代码来查询天气

> "查询天气时，可以请求 http://wttr.in 获取对应城市天气。"

执行如下代码
 ```bash
! python refactor_with_langchain/answer-with-tools.py '杭州气温如何'
```
输出内容
```
问题：杭州气温如何


> Entering new AgentExecutor chain...
 我需要通过自动编写并运行代码的工具来查询杭州的天气
Action: 自动编写并运行代码的工具
Action Input:
···
import requests
response = requests.get('http://wttr.in/杭州')
weather_info = response.text
print(weather_info)
···

··· (代码省略，如果有兴趣可以查看demo并执行)

···
> Finished chain.
杭州目前天气晴朗，气温为23°C（体感温度25°C），风速22公里/小时，能见度8公里，当前无降水。未来几天预报显示有局部多云到小雨的天气变化，气温和风速也有所波动。
```


## 4. 总结
通过本章的学习，你学会了如何通过 LangChain 来大幅简化你的代码。

接下来你可能已经迫不及待地想要添加更多工具了。但是在一个 agent 里不断叠加 tool 会让提示词越来越长，最后可能会超过 token 限制。
为了解决这一问题，你还可以配置一个[基于语义相似度的路由](https://python.langchain.com/docs/expression_language/cookbook/embedding_router)，让最前端的 agent 判断该让背后哪个领域的 agent 回答问题，背后的 agent 再去选取该领域合适的 tool 解答问题，最终由最前端的 agent 总结答案给用户。

更令人兴奋的是，你的程序可以自己根据需求编写并运行代码来解决问题了。

目前大模型生成的代码可能会曲解你的需求，导致答案不那么符合预期，你可以进一步完善提示词，甚至是使用搜索工具，来给通义千问一些代码参考，来让它更准确。与此同时，随着通义千问等大模型的不断演进，未来终有一天，它会在绝大多数场景下都能高效且正确的写出代码，解答你的问题。

## 5. 参考资料
- [DashScope](https://dashscope.aliyun.com/)
- [通义灵码](https://help.aliyun.com/document_detail/2590613.html)
- [LangChain- 基于语义相似度的路由](https://python.langchain.com/docs/expression_language/cookbook/embedding_router)

*****
## 本章代码
- 请点击[本章实验代码](demo-chapter4.ipynb)查阅相关内容。

## 继续学习
- [上一篇：第 3 章 使用工具扩展问答能力的基本原理](../chapter3/README.md)
- [【通义千问API入门教程】章节目录](../README.md)