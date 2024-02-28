# -*- coding: utf-8 -*-
import re

pattern = r"(##\s*.*?)\n"


def find_same_headers(content1, content2):
    """
    找出两个文档中相同的标题
    @param content1: 文档 1
    @param content2: 文档 2
    @return: 相同的标题数组
    """
    headers1 = re.findall(pattern, content1)
    headers2 = re.findall(pattern, content2)
    return _find_common_elements(headers1, headers2)


def split_docs(content, same_headers):
    """
    根据相同的标题，将文档切片成更小的文档单元
    @param content: 文档内容
    @param same_headers: 相同的标题
    @return: chunks, 文档分片
    """
    chunks = []
    start_index = 0
    for same_header in same_headers:
        index = content.find(same_header)
        chunks.append(content[start_index:index])
        start_index = index
    chunks.append(content[start_index:])
    return chunks


def _find_common_elements(array1, array2):
    """
    按顺序找出两个数组中的相同元素
    @param array1: 数组 1
    @param array2: 数组 2
    @return: 相同的元素数组
    """
    common_elements = []
    for elem1 in array1:
        if elem1 in array2 and elem1 not in common_elements:
            common_elements.append(elem1)
    return common_elements


if __name__ == '__main__':
    content_1 = '''# 快速购买包年包月实例
    ...
    ##  **前提条件**
    ...
    ##  **默认配置**
    ...
    ## 操作步骤
    ...

    '''

    content_2 = '''# 快速购买包年包月实例
    ...
    ##  **必要条件**
    ...
    ##  **默认配置**
    ...
    ## 操作步骤
    ...
    ...

    '''
    common_headers = find_same_headers(content_1, content_2)
    print(common_headers)
    print(split_docs(content_1, common_headers))
    print(split_docs(content_2, common_headers))
