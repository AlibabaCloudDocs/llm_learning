# 第 2 章 找出网络上两篇文档之间的差异
开发一个大模型工具，实现文档内容比对。阿里云的文档工程师们遇到过这样的问题：同一篇文档在中国站和国际站有一些不同，能快速的指出一批文档的这种差异吗？收到这个问题的你起初感到有些犯难，但想到或许可以借助大模型来快速完成这个任务，你又觉得似乎可以很快做到。

本章我们将开发一个程序，该程序可以完成：
- 可以指定文档 URL，程序根据 URL 自动爬取中国站、国际站的文档内容作比对
- 因为要比对的文档很多，你希望是可以从一个 excel 文件中读取 URL 列表，并对其进行比对


## 1. 准备工作

### 1.1. 安装

下载文档代码及安装依赖项
```bash
git clone https://github.com/AlibabaCloudDocs/llm_learning.git
cd llm_learning
pip install -r requirements.txt
```

### 1.2. 账号准备

首先，您需要前往 [官网创建 API Key](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key)。接下来，请获取你的 [DASHSCOPE_API_KEY](https://dashscope.console.aliyun.com/apiKey)，您可以使用以下命令行导入系统
```bash
export DASHSCOPE_API_KEY="sk-****"
```

## 2. MVP 开发
在正式开发一个完整的程序之前，我们可以先开发一个最小可运行的程序，来验证一下效果。

### 2.1 根据 URL 加载文档
为了实现根据 URL 读取文档内容，你参考了 LangChain 的[这篇 WebBaseLoader 文档](https://python.langchain.com/docs/integrations/document_loaders/web_base)，并尝试在代码中使用 WebBaseLoader 来加载一篇文档：
```python
from langchain_community.document_loaders import WebBaseLoader

loader = WebBaseLoader("https://help.aliyun.com/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab")

doc = loader.load()
print(doc[0].page_content)
```
### 2.2 比较文档内容
接下来你可以再加载一下国际站的文档，并将其交给通义千问帮你比对差别了：
```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.llms import Tongyi
from utils.ds_util import sample_call_streaming

llm = Tongyi()
llm.model_name = 'qwen-max'


def load_doc_content(url):
    loader = WebBaseLoader(url)
    doc = loader.load()
    return doc[0].page_content


doc_content_cn = load_doc_content("https://help.aliyun.com/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab")
doc_content_intl = load_doc_content("https://www.alibabacloud.com/help/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab")

prompt = f"""你现在的任务是找出下面两篇文档的不同之处，请不要放过任何细节。
--------
【中国站的文档】：
{doc_content_cn}
--------
【国际站的文档】:
{doc_content_intl}
--------
请给出结论，并用列表形式指出不同之处的具体位置：
"""

sample_call_streaming(prompt)
```
输出如下：
```text
以下是两篇文档的不同之处列表：

1. 文档标题：
   - 中国站文档：快速购买ECS实例_云服务器 ECS(ECS)-阿里云帮助中心
   - 国际站文档：快速购买ECS实例 - 云服务器 ECS - 阿里云

2. 页面布局与导航链接：
   - 中国站文档：文档结尾包含了联系信息、备案控制台登录/注册、产品文档、输入文档关键字查找等；还有“首页”、“云服务器 ECS”的子菜单，以及“操作指南”下的多个小节链接。
   - 国际站文档：文档结构更为简洁，只有“文档中心”、“全部产品”两个大类导航，且没有提及具体的子菜单或操作指南链接。

3. 内容差异：
   - 可用地区域范围：中国站文档提到“华东1（杭州）”，而国际站文档只提到了“华北2（北京）”作为实例创建时可以选择的地域，且未明确提到“华东1（杭州）”。
   - 实例规格：中国站文档列出“ecs.s6-c1m1.small”实例规格，而国际站文档只提及“突发性能实例t5”，并且只支持CentOS、Windows Server、Ubuntu三种操作系统，与中国站文档的四种操作系统有所不同。
   - 网络类型选项：中国站文档提及了“专有网络”和“公网IP”选项以及两种计费模式（固定带宽和按使用流量），而国际站文档只提到了“专有网络”和“公网带宽”选项，且只提供了固定带宽计费模式。
   - 自动续费选项：中国站文档明确提到了“自动续费”且允许用户选择是否开启，而国际站文档虽然提供了选择购买时长的选项，但没有直接提及自动续费功能。

4. 文档更新时间和语言版本：
   - 中国站文档提到“更新时间：一键部署”，没有具体日期；国际站文档的更新时间为“Nov 30, 2023”。
   - 中国站文档在某些语句后面注明了简体中文，如“操作步骤”、“重置实例登录密码”等；国际站文档则未明确标注语言，但整体内容倾向于英文描述。
```
以上就是一个 MVP 版本的程序了。它可以根据 URL 加载文档并进行比较，一定程度上，它已经能帮你减轻很多工作量了。

## 3. 完善程序
接下来我们可以完善一下程序，以达成我们最初设想的实现目标。

### 3.1 遍历 Excel 中的文档 URL
因为要比对的文档比较多，而且也经常会变，所以在代码中写死这些链接并不是一个好的做法。 我们可以在 excel 文件中管理 url，然后在程序中读取出来。

参考代码如下：
```python
import os
from openpyxl import load_workbook

file_path = 'data/doc_urls.xlsx'

wb = load_workbook(file_path)
sheet = wb.active
for row in sheet.iter_rows(values_only=True, min_row=2):
    url_cn = row[0]
    url_intl = row[0].replace('help.aliyun.com', 'www.alibabacloud.com/help')
    print(url_cn)
    print(url_intl)
```
输出如下：
```text
https://help.aliyun.com/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab
https://www.alibabacloud.com/help/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab
https://help.aliyun.com/zh/ecs/user-guide/overview-52
https://www.alibabacloud.com/help/zh/ecs/user-guide/overview-52
```
你已经可以从 excel 中读取链接，并自动替换获取国际站的文档链接了。 我们可以对 MVP 程序进行一点封装，以便在遍历 excel 里的 url 时调用通义千问进行文档对比。 详细的代码可以查看：

详细的代码可以查看：
- [chapter2/load-from-excel/diff_docs.py](load-from-excel/diff_docs.py)
- [chapter2/load-from-excel/main.py](load-from-excel/main.py)

现在，你就可以运行程序，来实现批量自动文档对比了：
```bash
python load-from-excel/main.py
```
输出如下：
```text
------
中国站文档：https://help.aliyun.com/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab
国际站文档：https://www.alibabacloud.com/help/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab
结论：两篇文档分别是中国站和国际站关于快速购买阿里云ECS实例的指南，它们在内容上大部分一致，但在细节、语言表述以及部分功能选项上存在差异。以下是具体的不同之处列表：

1. 文档标题与更新时间：
   - 中国站文档：快速购买包年包月实例_更新时间未明确
   - 国际站文档：一键购买包年包月实例 - 更新时间：Nov 30, 2023

2. 注册与实名认证指引：
   - 中国站文档：提及“已注册账号并完成实名认证”，并提供“阿里云账号注册流程”链接。
   - 国际站文档：提及“已注册账号并完成实名认证”，并指向“注册阿里云账号”。

3. 实例规格选择：
   - 中国站文档：默认配置中产品规格可选ecs.s6-c1m1.small，并提示如需更多实例规格可前往自定义购买。
   - 国际站文档：一键购买仅支持突发性能实例t5，如果需要更多实例规格，也建议前往自定义购买。

4. 操作系统选择：
   - 中国站文档：支持Alibaba Cloud Linux、Windows Server、Ubuntu、CentOS四种操作系统。
   - 国际站文档：一键购买支持CentOS、Windows Server、Ubuntu三种操作系统。

5. 确认订单页面的服务条款说明：
   - 中国站文档：阅读《云服务器 ECS 服务条款》|《云服务器ECS退订说明》，选中《云服务器ECS服务条款》后点击确认订单。
   - 国际站文档：阅读《云服务器 ECS 服务条款》|《通用服务条款》，选中《云服务器ECS服务条款》后点击确认下单。

除此之外，文档中的一些语言表述、按钮名称（如“快速购买”与中国站对应的是“一键购买”）以及部分内容布局有所调整，但不影响整体操作流程的理解和执行。
------
中国站文档：https://help.aliyun.com/zh/ecs/user-guide/overview-52
国际站文档：https://www.alibabacloud.com/help/zh/ecs/user-guide/overview-52
结论：这两篇文档内容实质上是相同的，主要描述了阿里云ECS实例的概述、基础配置、镜像、存储、购买方式和使用指导等信息。但是，两篇文档在排版布局、更新时间和联系方式等方面存在细微差异。

不同之处具体位置：
1. 文档标题及更新时间：
   - 中国站文档：【实例概述_云服务器 ECS】，更新时间：一键部署产品详情
   - 国际站文档：【实例概述 - 云服务器 ECS】，更新时间：Jul 18, 2023

2. 导航栏与底部联系信息：
   - 中国站文档提供了详细的导航栏，包括产品解决方案、社区权益中心、定价、云市场、合作伙伴支持与服务等，并且列出了售前咨询、售后咨询以及多种联系方式。
   - 国际站文档的导航栏和底部联系信息相对简洁，未列出详细联系方式，只在文档末尾有简单的反馈功能。

3. 排版细节：
   - 中国站文档包含较多的中文引导链接和分区标签，如“操作指南”、“实践教程”等；
   - 国际站文档整体排版更符合英文用户的阅读习惯，没有明显的分区标签和过多的内部链接。
```

### 3.2 排除网页中的页头页尾等非关键内容
细心的你可能会发现运行前面的代码时，通义千问给出的文档差异，可能还会包含一些页面尾部的差异，比如：
```text
...
2. 联系方式和链接格式：
   - 中国站文档中提供了详细的联系方式，如“95187-1 在线服务”、“4008013260 在线服务”，并且附带了“我要建议”、“我要投诉”、“体验反馈”等功能入口，同时链接地址采用了中文描述且未直接展示超链接形式。
   - 国际站文档没有在该处明确提供电话联系方式，而是集中在文档底部显示版权信息时提及，并且所有链接均采用英文描述及超链接形式展现。

3. 页面底部信息：
   - 中国站文档在底部包含了更多的附加信息，如“阿里云首页”、“相关技术圈”、“为什么选择阿里云”等，并列出了各类服务热线、法律声明、隐私权政策、廉正举报等链接。
   - 国际站文档在底部只包含了版权信息、许可证编号以及指向其他阿里云产品的链接，联系方式较为简洁。
...
```
出现这个情况的原因是，我们给到大模型的文档内容，其实是整个页面的内容。为了解决这一问题，我们需要想办法提取到文档正文本身，排除页头页尾等非文档正文内容。

这里我们可以选择针对阿里云文档页面的结构，编写一个自定义的 loader：
```python
from typing import List
from bs4 import BeautifulSoup
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
import requests


class AliyunDocLoader(BaseLoader):
    """
    阿里云文档加载器
    """

    def __init__(self, urls: List[str]):
        self.urls = urls

    def load(self) -> List[Document]:
        results = []
        for url in self.urls:
            content, metadata = self._get_aliyun_help_doc(url)
            doc = Document(page_content=content, metadata=metadata)
            results.append(doc)
        html2text = Html2TextTransformer()
        return html2text.transform_documents(results)

    @staticmethod
    def _get_aliyun_help_doc(url: str):
        """
        @param url: 文档 URL
        @return: content, metadata. content 为 html，metadata 里包含 TDK
        """
        html = requests.get(url).text
        soup = BeautifulSoup(html, features='html.parser')
        markdown_body = soup.find('article', class_='markdown-body') or soup.find('div', class_='markdown-body')
        contents = markdown_body.contents
        content_html = ''.join([str(item) for item in contents])
        content_html = f'<h1>{soup.find("h1").text}</h1>' + content_html

        metadata = {
            "title": soup.find('title').text,
            "keywords": soup.find('meta', attrs={'name': 'keywords'}).attrs['content'],
            "description": soup.find('meta', attrs={'name': 'description'}).attrs['content']
        }
        return content_html, metadata
```
完整的代码在 [`chapter2/custom-loader/`](custom-loader/) 中。
现在你可以尝试运行一下使用自定义阿里云文档 loader 的对比程序了：
```bash
python custom-loader/main.py
```
输出如下：
```text
------
中国站文档：https://help.aliyun.com/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab
国际站文档：https://www.alibabacloud.com/help/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab
结论：两篇文档的主要内容和结构相似，但存在一些细节上的差异。以下是不同之处的具体位置列表：

1. 文档标题：
   - 中国站文档标题：快速购买包年包月实例
   - 国际站文档标题：云服务器 ECS：一键购买包年包月实例

2. 快速购买/一键购买页签的表述：
   - 中国站文档中使用“快速购买”页签
   - 国际站文档中使用“**** **** **一键购买** ”页签

3. 实例规格配置部分：
   - 中国站文档提供的是ecs.s6-c1m1.small产品规格示例
   - 国际站文档提供的是一键购买仅支持突发性能实例t5（2 vCPU 4 GiB）

4. 操作系统镜像选择：
   - 中国站文档提到支持Alibaba Cloud Linux、Windows Server、Ubuntu、CentOS四种操作系统，并强调操作系统和预装应用仅支持选择其中一个。
   - 国际站文档提到一键购买支持CentOS、Windows Server、Ubuntu三种操作系统，没有提及预装应用选项。

5. 公网带宽计费模式下的配置项展示：
   - 中国站文档将“带宽计费模式”与“带宽值”分开描述。
   - 国际站文档在公网带宽部分直接列出“分配公网IPv4地址”、“按固定带宽”及“带宽值”。

6. 确认订单页面的描述：
   - 中国站文档提及阅读《云服务器 ECS 服务条款》|《云服务器ECS退订说明》并单击“确认订单”。
   - 国际站文档提及阅读《云服务器 ECS 服务条款》|《通用服务条款》并单击“确认下单”。
------
中国站文档：https://help.aliyun.com/zh/ecs/user-guide/overview-52
国际站文档：https://www.alibabacloud.com/help/zh/ecs/user-guide/overview-52
经过比对，两篇文档内容完全一致，没有发现任何不同之处。
```
### 3.3 应对超大文档
以上的程序似乎已经比较完善了。但很快你就会发现，有一些文档非常大，超出通义千问 API 的最大 token 数限制了。

### 3.3.1 更换模型
经过查阅阿里云的 [DashScope - 通义千问模型](https://help.aliyun.com/zh/dashscope/developer-reference/api-details)说明文档，你会发现正在使用的`qwen-max`最大 token 数是 6k。
另外，你还发现`qwen-plus`和`qwen-max-longcontext`支持的 token 数分别是 30k 和 28k。
所以最简单的办法就是修改现有的代码，使用`qwen-plus`和`qwen-max-longcontext`即可。
```python
llm = Tongyi()
llm.model_name = 'qwen-max-longcontext'
```
尽管上面的代码改动已经解决了你遇到的问题，但严谨的你一定会想到，如果遇到了更大的文档，还是超过了 token 数量限制该怎么办。

### 3.3.2 分而治之
我们可以借鉴 MapReduce 的思想，将文档分成多个小文档分片，然后对每个分片做对比，最后汇总结果。

具体实现思路是：
1. 我们可以先找出两篇文档中相同的二级标题；
2. 然后以这些相同的二级标题对文档进行切片；
3. 对每个切片进行对比，并将结果汇总，得到最终结果。

我们在[`chapter2/long-docs/doc_spliter.py`](long-docs/doc_spliter.py)中提供了两个方法，用于找到相同的二级标题，和对文档进行切片。
另外在[`chapter2/long-docs/diff_docs.py`](long-docs/diff_docs.py)中调整了对比程序的实现，程序会先对第一个文档切片进行对比，然后带着对比结论，对剩余文档切片进行对比，最终遍历完所有的切片时，就得到了最终答案。

这是切片提问模式下的两段提示词：
```python
def get_question_prompt(doc_content_cn, doc_content_intl):
    return f"""你现在的任务是找出下面两段文档的不同之处，请不要放过任何细节。
--------
【中国站的文档】：
{doc_content_cn}
--------
【国际站的文档】:
{doc_content_intl}
--------
请给出结论，并用列表形式指出不同之处的具体位置：
"""


def get_refine_prompt(doc_content_cn, doc_content_intl, existing_answer):
    return f"""这是你在前面的文档片段中找出的不同：
{existing_answer}
--------
请找出下面两个文档片段不同之处的具体位置，并补充到之前的结果中：
--------
【中国站的文档】：
{doc_content_cn}
--------
【国际站的文档】:
{doc_content_intl}
"""
```

你可以运行一下试试看：
```bash
python long-docs/main.py
```
输出如下：
```text
------
中国站文档：https://help.aliyun.com/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab
国际站文档：https://www.alibabacloud.com/help/zh/ecs/user-guide/create-a-subscription-instance-on-the-quick-launch-tab
正在对比第1个片段...
正在对比第2个片段...
正在对比第3个片段...
正在对比第4个片段...
在对比两个文档片段后，可以发现以下不同之处：

1. **页签名称**：
   - 中国站的文档中，用户需要单击左上角的“**快速购买**”页签。
   - 国际站的文档中，用户需要单击左上角的“**** **** **一键购买**”页签。

2. **产品规格说明和示例**：
   - 中国站的文档提供了实例规格ecs.s6-c1m1.small的示例，并指出可选规格与地域相关，用户可以在“使用说明”列查看适用场景。
   - 国际站的文档中，仅支持突发性能实例t5规格，示例为“2 vCPU 4 GiB（突发性能实例t5）”。

3. **操作系统及预装应用**：
   - 中国站的文档详细列举了四种操作系统供选择（Alibaba Cloud Linux、Windows Server、Ubuntu、CentOS），并特别说明操作系统和预装应用只能选择其中一个。
   - 国际站的文档只提到一键购买支持CentOS、Windows Server、Ubuntu三种操作系统，未提及预装应用的选择。

4. **公网带宽配置**：
   - 中国站的文档将公网IP和带宽计费模式分为两个独立参数，其中带宽计费模式下有“按固定带宽”和“按使用流量”的选项，并提供了带宽值的例子。
   - 国际站的文档中公网带宽部分整合了公网IP分配和带宽计费模式的选择，在一个表格内展示了“分配公网IPv4地址”、“按固定带宽”以及“带宽值”的例子。

5. **购买时长和自动续费**：
   - 中国站的文档中，购买时长和自动续费是分开描述的参数。
   - 国际站的文档中，购买时长和是否启用自动续费是在同一个描述里，用户同时选择购买时长（例如：1个月）和是否启用自动续费。

6. **确认订单按钮后的操作**：
   - 中国站的文档在右侧“确认订单”面板阅读《云服务器 ECS 服务条款》和《云服务器ECS退订说明》，然后选中《云服务器ECS服务条款》后点击“确认订单”。
   - 国际站的文档在“确认订单”页面阅读《云服务器 ECS 服务条款》和《通用服务条款》，选中《云服务器ECS服务条款》后点击的是“确认下单”。
------
中国站文档：https://help.aliyun.com/zh/ecs/user-guide/overview-52
国际站文档：https://www.alibabacloud.com/help/zh/ecs/user-guide/overview-52
正在对比第1个片段...
正在对比第2个片段...
正在对比第3个片段...
正在对比第4个片段...
正在对比第5个片段...
正在对比第6个片段...
正在对比第7个片段...
经过对比分析，两个文档片段的内容完全相同，没有找到任何具体的不同之处。
```
## 4. 总结
通过本章的学习，你已经能借助通义千问的 API 来帮助自己完成一些原来要人工完成的工作了，也学会了通过分而治之的思路来解决提示词过长的问题。分而治之的思想在很多场景下都有应用，除了用于做两篇长文档的对比，也可以用于超长文档的总结。

需要注意的时，这里出于学习的目的，文档的切片方法并不是最优的：

提示词长度没有超限时，是可以不用切片的；
一些特殊的文档也可能存在一个二级标题下内容也超过 token 限制，实际用于生产时，需要结合具体业务来定制切片方法。
另外，在实际使用中，你也可以使用 LangChain 提供的 refine 类型的 load_summarize_chain 来完成这个切片后调用大模型的任务。详情可以参考：[LangChain Use cases：Summarization - Refine](https://python.langchain.com/docs/use_cases/summarization#option-3.-refine)。


## 5. 参考资料
- [DashScope](https://dashscope.aliyun.com/)
- [通义千问 - 模型概览](https://help.aliyun.com/zh/dashscope/developer-reference/api-details)
- [LangChain](https://python.langchain.com/docs)
- [LangChain Use cases：Summarization - Refine](https://python.langchain.com/docs/use_cases/summarization#option-3.-refine)


*****
## 本章代码
- 请点击[本章实验代码](https://github.com/AlibabaCloudDocs/llm_learning/blob/main/chapter2/)查阅相关内容。

## 继续学习
- [上一篇：第 1 章 用4行代码实现流式输出](../chapter1/README.md)
- [下一篇：第 3 章 使用工具扩展问答能力的基本原理](../chapter3/README.md)
- [【通义千问API入门教程】章节目录](../README.md)