# -*- coding: utf-8 -*-
from aliyun_doc_loader import AliyunDocLoader
from langchain_community.llms import Tongyi
from doc_spliter import find_same_headers, split_docs

llm = Tongyi()
llm.model_name = 'qwen-max'


def _load_doc_content(url):
    loader = AliyunDocLoader([url])
    docs = loader.load()
    return docs[0].page_content


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


def diff(url_cn, url_intl):
    doc_content_cn = _load_doc_content(url_cn)
    doc_content_intl = _load_doc_content(url_intl)

    same_headers = find_same_headers(doc_content_cn, doc_content_intl)
    chunks_cn = split_docs(doc_content_cn, same_headers)
    chunks_intl = split_docs(doc_content_intl, same_headers)

    answer = ''

    for index, chunk in enumerate(same_headers):
        print(f'正在对比第{index + 1}个片段...')
        if index == 0:
            prompt = get_question_prompt(chunks_cn[index], chunks_intl[index])
            answer = llm.invoke(prompt)
        else:
            refine_prompt = get_refine_prompt(chunks_cn[index], chunks_intl[index], answer)
            answer = llm.invoke(refine_prompt)

    return answer
