# -*- coding: utf-8 -*-
import os
from alibabacloud_cloudcontrol20220830.client import Client as cloudcontrol20220830Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_cloudcontrol20220830 import models as cloudcontrol_20220830_models
from alibabacloud_tea_util import models as util_models


class AliyunResources:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> cloudcontrol20220830Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 必填，您的 AccessKey ID,
            access_key_id=access_key_id,
            # 必填，您的 AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # Endpoint 请参考 https://api.aliyun.com/product/cloudcontrol
        config.endpoint = f'cloudcontrol.aliyuncs.com'
        return cloudcontrol20220830Client(config)

    @staticmethod
    def list_ecs_instances() -> None:
        # 请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET。
        # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例使用环境变量获取 AccessKey 的方式进行调用，仅供参考，建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html
        client = AliyunResources.create_client(os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID'], os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET'])
        request_path = '/api/v1/providers/Aliyun/products/ECS/resources/Instance'
        get_resources_request = cloudcontrol_20220830_models.GetResourcesRequest(
            region_id='cn-hangzhou',
            max_results=2
        )
        runtime = util_models.RuntimeOptions()
        headers = {}
        try:
            # 复制代码运行请自行打印 API 的返回值
            result = client.get_resources_with_options(request_path, get_resources_request, headers, runtime)
            # print(result.body)
            return result.body
        except Exception as error:
            # 错误 message
            print(error)
            # 诊断地址
            print(error.data.get("Recommend"))


if __name__ == '__main__':
    AliyunResources.list_ecs_instances()
