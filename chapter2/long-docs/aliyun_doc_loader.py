# -*- coding: utf-8 -*-
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
