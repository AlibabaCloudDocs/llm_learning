# -*- coding: utf-8 -*-
from aliyun_doc_loader import AliyunDocLoader
from langchain_community.llms import Tongyi

llm = Tongyi()
llm.model_name = 'qwen-max'


def _load_doc_content(url):
    loader = AliyunDocLoader([url])
    docs = loader.load()
    return docs[0].page_content


def diff(url_cn, url_intl):
    doc_content_cn = _load_doc_content(url_cn)
    doc_content_intl = _load_doc_content(url_intl)

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

    diff_result = llm.invoke(prompt)
    return diff_result
