# -*- coding: utf-8 -*-
import sys
from langchain_community.llms import Tongyi


if __name__ == '__main__':
    question = sys.argv[1]
    llm = Tongyi()
    print(llm.invoke(question))
