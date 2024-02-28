# -*- coding: utf-8 -*-
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.llms import Tongyi
from chapter2.utils.ds_util import sample_call_streaming

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

