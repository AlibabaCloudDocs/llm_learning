# 通义千问API入门教程
本教程将带你从零开始，快速了解如何通过 API 使用大模型，并尝试使用大模型 API 开发一些简单的应用应用到工作中，提升效率。

## 学习之前
- 本教程假设你已经初步了解并使用过 python、git，因此不会涉及如何安装 [python](https://www.python.org/downloads/)、pip、[git](https://git-scm.com/) 等基础工具。
- 本教程侧重于如何将大模型 API 应用到工作中，因此并不不会详细介绍大模型以及机器学习的基础概念。

## 教程目录
| 章节                              | Notebook                  | 目标                                                       | 
|:-----------------------------------|:------------------------|:---------------------------------------------------------|
| [第 1 章 用4行代码实现流式输出](chapter1/README.md)              |[Notebook 1](chapter1/demo-chapter1.ipynb)      | 了解如何通过 API 使用通义千问                                        |
| [第 2 章 找出网络上两篇文档之间的差异](chapter2/README.md) |[Notebook 2](chapter2/demo-chapter2.ipynb)  | 以对比阿里云中国站和国际站文档这个场景为例，让大模型对文档做对比和总结 |
| [第 3 章 使用工具扩展问答能力的基本原理](chapter3/README.md) |[Notebook 3](chapter3/demo-chapter3.ipynb) | 了解如何让大模型使用外部工具，以及背后的工作原理。                                 |
| [第 4 章 让通义千问编写并执行代码](chapter4/README.md) |[Notebook 4](chapter4/demo-chapter4.ipynb)  | 了解如何添加更多工具，以及让大模型自己写代码来执行工作。    |

## 代码安装

```bash
# 安装依赖
git clone https://github.com/AlibabaCloudDocs/llm_learning.git
cd llm_learning
pip install -r requirements.txt
```

## License
本项目使用 [Apache License (Version 2.0)](https://github.com/AlibabaCloudDocs/llm_learning/blob/master/LICENSE).