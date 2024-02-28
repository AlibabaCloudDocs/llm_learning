from langchain_core.tools import BaseTool
# 定义搜索工具
class SearchTool(BaseTool):
    """服务查询工具"""

    name: str = "阿里云服务查询工具"
    description: str = (
        "当你不确定一个阿里云服务是什么，才使用此工具。"
    )

    def _run(self, name: str) -> str:
        if(name=="灵积") or (name=="灵积 阿里云服务"):
            return '''DashScope灵积模型服务建立在“模型即服务”（Model-as-a-Service，MaaS）的理念基础之上，围绕AI各领域模型，通过标准化的API提供包括模型推理、模型微调训练在内的多种模型服务。DashScope灵积模型服务依托于业界各领域的优质模型，基于阿里云强大的基础设施搭建。欢迎AI应用开发者由此开启模型探索之旅！'''
        elif name=="百炼":
            return "百炼，即大模型服务平台，是面向企业客户及合作伙伴的，基于通义大模型、行业大模型以及三方大模型，结合企业专属数据，包含全链路大模型开发工具的一站式大模型商业化平台。提供完整的模型训练、微调、评估等产品工具，预置丰富的应用插件，提供便捷的集成方式，更快更高效地完成大模型应用的构建。"
        elif (name=="PAI") or (name=="阿里云 PAI"):
            return "人工智能平台 PAI（Platform of Artificial Intelligence）面向企业客户及开发者，提供轻量化、高性价比的云原生人工智能，涵盖DSW交互式建模、Designer拖拽式可视化建模、DLC分布式训练到EAS模型在线部署的全流程。"
        elif name=="OSS":
            return "阿里云对象存储OSS（Object Storage Service）是一款海量、安全、低成本、高可靠的云存储服务，可提供99.9999999999%（12个9）的数据持久性，99.995%的数据可用性。多种存储类型供选择，全面优化存储成本。"
        return name + '抱歉，没有查到相关信息。'