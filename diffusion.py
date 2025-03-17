import json
import time
import requests
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

class ImageGenerator:
    def __init__(self, secret_id, secret_key):
        """初始化图像生成器"""
        try:
            self.cred = credential.Credential(secret_id, secret_key)
            
            http_profile = HttpProfile()
            http_profile.endpoint = "hunyuan.tencentcloudapi.com"
            
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            
            self.client = hunyuan_client.HunyuanClient(
                self.cred, 
                "ap-guangzhou",
                client_profile
            )
            
        except Exception as e:
            print(f"初始化图像生成器失败: {e}")
            raise e

    def submit_image_job(self, prompt, style=None):
        """提交图像生成任务"""
        try:
            req = models.SubmitHunyuanImageJobRequest()
            
            params = {
                "Prompt": prompt,
                "Resolution": "1024:1024",  # 使用 1:1 的分辨率
                "Num": 1,                   # 生成1张图片
                "Revise": 1,               # 开启 prompt 扩写
                "LogoAdd": 0,              # 添加水印
            }
            
            # 如果指定了风格，添加到参数中
            if style:
                params["Style"] = style
            
            req.from_json_string(json.dumps(params))
            print(f"提交任务参数: {params}")
            
            response = self.client.SubmitHunyuanImageJob(req)
            return response.JobId
            
        except TencentCloudSDKException as e:
            print(f"提交图像生成任务失败: {e}")
            return None

    def query_image_job(self, job_id, max_retries=30, interval=2):
        """查询图像生成任务状态"""
        try:
            req = models.QueryHunyuanImageJobRequest()
            params = {
                "JobId": job_id
            }
            req.from_json_string(json.dumps(params))
            
            retries = 0
            while retries < max_retries:
                response = self.client.QueryHunyuanImageJob(req)
                
                # 根据状态码判断任务状态
                if response.JobStatusCode == "5":  # 处理完成
                    if response.ResultImage and len(response.ResultImage) > 0:
                        # 打印扩写后的 prompt（如果有）
                        if hasattr(response, 'RevisedPrompt') and response.RevisedPrompt:
                            print(f"扩写后的 prompt: {response.RevisedPrompt[0]}")
                        
                        # 检查结果详情
                        if response.ResultDetails and response.ResultDetails[0] == "Success":
                            return response.ResultImage[0]  # 返回第一张图片的URL
                        else:
                            print(f"生成结果异常: {response.ResultDetails}")
                            return None
                    else:
                        print("任务完成但未返回图片URL")
                        return None
                elif response.JobStatusCode == "4":  # 处理失败
                    print(f"任务失败: {response.JobErrorCode} - {response.JobErrorMsg}")
                    return None
                elif response.JobStatusCode in ["1", "2"]:  # 等待中或运行中
                    print(f"任务进行中... (状态: {response.JobStatusMsg})")
                    time.sleep(interval)
                    retries += 1
                else:
                    print(f"未知状态码: {response.JobStatusCode}")
                    return None
            
            print("任务超时")
            return None
            
        except TencentCloudSDKException as e:
            print(f"查询任务状态失败: {e}")
            return None

    def generate_image(self, prompt, output_path=None, style=None):
        """生成图像"""
        try:
            # 提交任务
            job_id = self.submit_image_job(prompt, style)
            if not job_id:
                return None
                
            print(f"任务提交成功，JobId: {job_id}")
            
            # 轮询任务状态
            image_url = self.query_image_job(job_id)
            if not image_url:
                return None
            
            # 如果需要保存图片，下载并保存
            if output_path:
                try:
                    response = requests.get(image_url)
                    if response.status_code == 200:
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        print(f"图片已保存至: {output_path}")
                        return True
                    else:
                        print(f"下载图片失败: {response.status_code}")
                        return None
                except Exception as e:
                    print(f"保存图片失败: {e}")
                    return None
            else:
                return image_url
            
        except Exception as e:
            print(f"生成图像失败: {e}")
            return None

