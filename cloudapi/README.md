# 如何利用通义千问查询阿里云资源

作为阿里云开发者，我们常常需要查询阿里云上的资源信息，比如ECS、RDS等资源详情或产品说明。以往我们只能在官网上按步骤一页一页找到控制中心，再查到资源页面，节奏略显拖沓。如今，我们已经进入大模型时代，有什么办法可以更简便快捷的获取这些信息呢？能不能让大模型来做这件事？于是，基于LangChain的Agent架构，我们尝试制作了一个实现上述想法的大模型Agent，让大模型可以协助您查询您在阿里云上开通了哪些资源。您可以进入Jupyter Notebook环境来运行本章的代码，查询您在阿里云的资源使用情况，也可以将代码加入到您的工程项目中，利用[阿里云控制API](https://api.aliyun.com/product/cloudcontrol?tab=apis)实现更多功能，我们欢迎您将实验结果分享出来。

本我呢我们将使用灵积API调用通义千问大模型，并利用[阿里云控制API](https://api.aliyun.com/product/cloudcontrol?tab=apis)来查询您的阿里云资源。

## 学习之前
- 本文假设你已经初步了解并使用过 python、git，因此不会涉及如何安装 [python](https://www.python.org/downloads/)、pip、[git](https://git-scm.com/) 等基础工具。
- 本文侧重于如何将大模型 API 应用到工作中，因此并不不会详细介绍大模型以及机器学习的基础概念。

## 1. 准备工作
### 1.1. 环境配置
在开始本文的学习之前，你可以先安装一下必要的依赖，以便运行相关代码：
```bash
pip install dashscope==1.13.6
pip install langchain==0.1.0
pip install langchainhub==0.1.14
pip install langchain-experimental==0.0.49
pip install beautifulsoup4==4.12.2
pip install html2text==2020.1.16
pip install alibabacloud_cloudcontrol20220830==1.1.0
```

### 1.2. 账号准备

首先，您需要前往 [官网创建 API Key](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key)。接下来，请获取你的 [DASHSCOPE_API_KEY](https://dashscope.console.aliyun.com/apiKey)，您可以使用以下命令行导入系统，请于[RAM访问控制](https://ram.console.aliyun.com/manage/ak)查询和创建您的阿里云AK/SK

您可以使用命令行导入系统
```bash
export DASHSCOPE_API_KEY="sk-****"
export ALIBABA_CLOUD_ACCESS_KEY_ID="<your access key id>"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="<your access key secret>"
```

## 2. 搭建云资源查询AGENT
### 2.1. 创建阿里云资源查询API工具
```python
# 阿里云资源查询工具

# -*- coding: utf-8 -*-
import json
import os
from typing import Any
from langchain_core.tools import BaseTool
from alibabacloud_cloudcontrol20220830.client import Client as cloudcontrol20220830Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cloudcontrol20220830 import models as cloudcontrol_20220830_models
from alibabacloud_tea_util import models as util_models


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
```

### 2.2. 创建通义千问AGENT
```python
# 定义通义千问大模型AGENT

# -*- coding: utf-8 -*-
import sys
from langchain import hub
from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain_community.llms import Tongyi

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

llm = MyAgent()
```

### 2.3. 阿里云资源查询

下面我们尝试利用上述代码工具来查询阿里云资源，API应用[详情点击](https://api.aliyun.com/product/cloudcontrol?tab=apis)

#### 2.3.1. 使用工具查询ECS资源
首先测试Agent初始化是否成功，是否能查询“杭州的ECS实例信息”。本账号并没有关联ECS实例，所以查询结果为空。
```python
llm.ask("杭州的ECS实例什么时候到期")
```
输出内容
```text
> Entering new AgentExecutor chain...
 需要使用阿里云的云资源查询工具来获取ECS实例的信息，包括到期时间
Action: 阿里云的云资源查询工具
Action Input: {"product": "ECS", "resource": "Instance", "region": "cn-hangzhou"}
{'maxResults': 2, 'requestId': '3A02BE18-DA09-576D-BD98-68FDAD75DDDF', 'resources': [], 'totalCount': 0} 根据API返回结果，当前在杭州地域下没有ECS实例。
Final Answer: 目前在杭州地域下没有到期的ECS实例。如果有实例并需要查询其到期时间，请确保输入正确的region信息，并且该账号下在对应地域存在ECS实例。

> Finished chain.
'目前在杭州地域下没有到期的ECS实例。如果有实例并需要查询其到期时间，请确保输入正确的region信息，并且该账号下在对应地域存在ECS实例。'
```

由于本章使用的测试账号没有开通ECS服务，因此反馈没有查询到ECS实例。

>您可以[查看云服务产品信息](https://www.aliyun.com/product/ecs?source=5176.11533457#/)通过阿里云权益中心购买的 99 元/年的经济型 2核2G ECS 实例，新老客户都可以购买，并且后续可以 99 元续费。您可以参考[阿里云便宜服务器优惠合集](https://developer.aliyun.com/article/1445729)参与优惠活动

#### 2.3.2. 查询更多阿里云资源

接下来，我们在不做任何代码改动的情况下查询VPC信息。理论上我们可以查询[API应用范围](https://api.aliyun.com/product/cloudcontrol?tab=apis)的所有资源。
```python
llm.ask("我在上海有没有VPC")
```

输出内容
```text
> Entering new AgentExecutor chain...
 需要查询我在上海地区的VPC资源
Action: 阿里云的云资源查询工具
Action Input: {"product": "VPC", "resource": "VPC", "region": "cn-shanghai"}
{'maxResults': 2, 'requestId': 'BC5C3BBE-762F-5451-830C-40FB15E806EC', 'resources': [], 'totalCount': 0} 查询结果显示在上海地区没有VPC资源
Final Answer: 您在上海地区目前没有VPC资源。

> Finished chain.
'您在上海地区目前没有VPC资源。'
```
#### 2.3.3. 通义千问无需工具就能回答的问题

最后，我们看看大模型是如何回答不在API范围内的问题的，这里我们将询问ECS的定价策略，通义千问能直接给出合理的答案。
```python
ans= llm.ask("ECS服务如何定价")
```
输出内容
```
> Entering new AgentExecutor chain...
 提供的工具对回答该问题帮助较小，我将不使用工具直接作答。
Final Answer: 阿里云函数计算服务（Function Compute）的定价模式基于以下几个方面：

1. **计费单位**：函数计算以 GB-s（GB 内存每秒）为计费单位。即您的函数运行时消耗的内存大小乘以运行时间（以秒计）。

2. **资源使用**：
   - **内存**：您可以根据实际需求配置函数运行所需的最小和最大内存，价格会随着内存规格不同而变化。
   - **执行时间**：函数每次执行的实际耗时，精确到毫秒级计费，但不足 1ms 的部分不收费。
   - **请求次数**：除了按量计费的资源使用外，函数计算还有免费额度的调用次数。

3. **冷启动**：首次创建或长时间未被调用后重新调用时可能会产生额外的冷启动费用，具体取决于函数的运行环境和镜像大小。

4. **免费额度**：阿里云为每个账号提供了一定额度的免费资源包，包括一定的函数调用次数、GB-s 计算资源以及一定数量的免费日志存储空间等。

5. **长期优惠**：对于持续运行的函数实例，可以采用预留实例（RI）的方式获得更优惠的价格。

为了获取最新的、详细的定价信息，请直接访问阿里云函数计算官网的定价页面，那里会有详尽且实时更新的价格列表和计费示例说明。

> Finished chain.
```

#### 2.3.4. 封装成文件来执行

上述代码我们封装在文件 aliyun_resource_agent.py 中，你可以使用如下的指令来执行

```bash
python aliyun_resource_agent.py "我在上海有没有VPC"
```
输出内容
```
问题：我在上海有没有VPC

> Entering new AgentExecutor chain...
 需要查询用户在上海的VPC资源
Action: 阿里云的云资源查询工具
Action Input: {"product": "VPC", "resource": "VPC", "region": "cn-shanghai"}
{'maxResults': 2, 'requestId': '99B869A2-8F8C-53A8-AC0C-F53DD4571BC9', 'resources': [], 'totalCount': 0} 根据查询结果，用户在上海没有VPC资源
Final Answer: 您在上海没有VPC资源。

> Finished chain.
您在上海没有VPC资源。
```


## 3. 参考资料
- [阿里云控制API](https://api.aliyun.com/product/cloudcontrol?tab=apis)
- [DashScope](https://dashscope.aliyun.com/)
- [通义灵码](https://help.aliyun.com/document_detail/2590613.html)
- [LangChain- 基于语义相似度的路由](https://python.langchain.com/docs/expression_language/cookbook/embedding_router)


*****
## 继续学习
- [【通义千问API入门教程】章节目录](../README.md)