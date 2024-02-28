# For prerequisites running the following sample, visit https://help.aliyun.com/document_detail/611472.html
# -*- coding: utf-8 -*-
import sys
from langchain_community.llms import Tongyi

if __name__ == '__main__':
    question = sys.argv[1]    
    
    llm = Tongyi(streaming=True)
    for chunk in llm.stream(question):
        print(chunk, end="", flush=True)
