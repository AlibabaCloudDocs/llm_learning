# 第 1 章 用4行代码与大模型对话
以前经常使用搜索引擎来解决问题的你，现在大概率已经在工作中频繁使用大模型了。 但是只在网页聊天框中和大模型对话，终究有一些局限性：比如你在本地有一个超大的用户反馈表格、或者是有一些仅内部可访问的网页，想要借助大模型做一系列处理，就不太好做到了。 幸运的是，现在很多大模型服务提供商，都提供了 API 接口，可以让你方便地实现各种原本在网页聊天框中不方便、或无法实现的功能。

本章将通过一个简单的例子，让你快速进入到大模型应用开发的世界。

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


## 2. 文本生成实验

通过 langchain_community 库中封装的 Tongyi 工具，我们可以通过[灵积API](https://dashscope.console.aliyun.com/apiKey)访问通义千问，让通义千问回答问题。

### 2.1. 简单文本生成

首先，Tongyi 工具的接口默认是一次性输出全部生成的答案，用户需要等待数秒才能看到完整答案。下面，我们先来看看一次性生成全部答案的代码和执行效果。代码只有三行，如下：

```python
from langchain_community.llms import Tongyi

llm = Tongyi()
print(llm.invoke('阿里云成立于什么时间'))
```
输出内容
```bash
阿里云成立于2009年9月10日，是阿里巴巴集团旗下的云计算服务品牌，提供包括计算、存储、网络、安全、数据库、大数据、人工智能等全面的云计算服务。
```
### 2.2. 流式文本生成

采用LangChain封装的接口来实现流式文本生成，我们需要在创建Tongyi对象时声明采用流式输出（streaming=True），然后用一个循环来接收生成的文本，直到生成的文本为空。
>（注意：如果你遇到了 TypeError: Additional kwargs key output_tokens already exists in left dict and value has unsupported type <class 'int'> 这个错误，请参考[github](https://github.com/langchain-ai/langchain/pull/16580)中的说明）
```python
from langchain_community.llms import Tongyi
llm = Tongyi(streaming=True)
for chunk in llm.stream('为什么要使用阿里云'):
    print(chunk, end="", flush=True)
```
输出内容
```bash
阿里云作为全球领先的云计算及人工智能科技公司，提供了丰富且强大的云计算、大数据、人工智能等服务，以下是一些选择阿里云的主要原因：

1. 技术实力：阿里云拥有强大的技术研发能力，不断推出创新产品和服务，满足不同行业的数字化转型需求。在数据库、安全、物联网、人工智能等领域都有深厚的技术积累。

2. 稳定性：阿里云以其高可用性和稳定性著称，通过多地域、多可用区的架构设计，能够提供99.99%的服务可用性，保障业务连续性。

3. 安全性：阿里云提供全面的安全防护措施，包括防火墙、DDoS防护、数据加密、身份认证等，保护用户的数据和应用安全。

4. 丰富的服务：从基础设施即服务（IaaS）到平台即服务（PaaS），再到软件即服务（SaaS），阿里云提供一整套完整的云解决方案，覆盖了企业从开发、测试、部署到运营的全过程。

5. 全球化布局：阿里云在全球多个地区设有数据中心，可以为跨国企业提供本地化的云计算服务，帮助企业快速拓展海外市场。

6. 行业解决方案：针对电商、金融、教育、医疗等多个行业，阿里云提供了针对性的解决方案，帮助企业在特定领域实现高效运营。

7. 优质支持：阿里云提供24小时的技术支持和服务，有专业的团队解答用户问题，确保用户在使用过程中得到及时的帮助。

综上所述，无论你是初创公司还是大型企业，无论是国内业务还是全球化布局，阿里云都能提供合适的产品和服务，助力你的业务发展。
```

## 3. 封装成文件来访问通义千问

我们将上述两端代码功能封装进文件，读者可以直接调用文件来实现与大模型的对话。

### 3.1. 批量输出
```bash
python main_simple.py "阿里云是什么时候成立的"
```
输出内容
```
阿里云成立于2009年9月10日，是阿里巴巴集团旗下的云计算服务品牌，提供包括计算、存储、网络、安全、数据库、大数据、人工智能等全面的云计算服务。阿里云致力于为企业数字化转型提供技术支撑，帮助全球企业实现更高效、更绿色的运营。
```

### 3.2. 流式输出
```bash
python main_stream.py "为什么要使用阿里云"
```
输出内容
```text
使用阿里云有以下几个主要原因：

1. 技术实力：阿里云是全球领先的云计算服务提供商，拥有强大的技术研发能力和丰富的实践经验。它提供了包括计算、存储、数据库、网络、安全、大数据、人工智能等全方位的云产品和服务。

2. 稳定性与安全性：阿里云在全球范围内拥有多个数据中心和边缘节点，通过负载均衡和容灾备份技术，保证了服务的高可用性和数据的安全性。

3. 弹性扩展：根据业务需求，用户可以轻松地在云端进行资源的按需分配和弹性伸缩，无需预先投入大量硬件成本，有效降低了运营成本。

4. 一站式解决方案：阿里云提供了一站式的企业级服务，包括云计算、域名注册、企业邮箱、网站托管、物联网、区块链等，满足不同企业的多元化需求。

5. 全球化服务：阿里云在全球多地设有数据中心，能够为跨国企业提供便捷的数据合规和本地化服务。

6. 售后支持：阿里云有专业的技术支持团队，提供7x24小时的技术咨询和问题解决服务，确保用户在遇到问题时能得到及时的帮助。

总的来说，选择阿里云可以帮助企业和个人开发者更高效、稳定、经济地运行其应用程序和业务，同时享受到前沿的云计算技术和优质的服务。
```

## 4. 总结

通过本章的学习，你已经获得了两个与大模型对话聊天的命令行工具！你不仅已经了解了如何使用通义千问的 API，如何流式输出大模型返回的结果，并在本地运行了示例代码。 在开始下一章的学习之前，你也可以尝试调整 prompt 语句，让通义千问回答不同的问题。或者将这段代码集成到其他更复杂的场景中，来帮助你完成任务，比如从一个本地 excel 文件中逐行读取问题，并对其做出回答。

## 5. 参考资料
- [DashScope](https://dashscope.aliyun.com/)
- [LangChain](https://python.langchain.com/docs)


*****
## 本章代码
- 请点击[本章实验代码](demo-chapter1.ipynb)查阅相关内容。

## 继续学习
- [下一篇：第 2 章 找出网络上两篇文档之间的差异](../chapter2/README.md) 
- [【通义千问API入门教程】章节目录](../README.md)