import base64
import json
import re
from collections.abc import Generator
from typing import Any
import requests

# 日志相关
import logging
from dify_plugin.config.logger_format import plugin_logger_handler

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# 使用 Dify 提供的日志处理器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

class NanobananaTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        使用 Gemini 3 Pro Image Preview 生成图片
        """
        logger.info("NanobananaTool 调用开始, tool_parameters_keys=%s", list(tool_parameters.keys()))

        # 获取凭据
        base_url = self.runtime.credentials.get("base_url", "").rstrip("/")
        api_key = self.runtime.credentials.get("api_key", "")
        if not base_url or not api_key:
            logger.error("凭据缺失, base_url 存在=%s, api_key 存在=%s", bool(base_url), bool(api_key))
            yield self.create_text_message("错误：缺少 base_url 或 api_key 凭据")
            return
        
        # 获取参数
        prompt = tool_parameters.get("prompt", "")
        reference_images = tool_parameters.get("reference_images", [])
        resolution_raw = tool_parameters.get("resolution") or "2K"
        resolution = str(resolution_raw).upper()
        if resolution not in {"1K", "2K", "4K"}:
            logger.warning("收到未知分辨率: %s, 使用默认 2K", resolution_raw)
            resolution = "2K"

        # 处理超时时间参数，单位秒
        timeout_default = 300
        timeout_raw = tool_parameters.get("timeout")
        timeout_seconds = timeout_default
        if timeout_raw is not None:
            try:
                timeout_seconds = int(str(timeout_raw).strip())
                if timeout_seconds <= 0:
                    raise ValueError("timeout must be positive")
            except Exception:
                logger.warning("收到非法超时时间: %s, 使用默认 %s 秒", timeout_raw, timeout_default)
                timeout_seconds = timeout_default

        # 处理重试次数参数，默认 0，限制最大重试次数避免滥用
        retry_default = 0
        retry_max = 5
        retry_raw = tool_parameters.get("retry", retry_default)
        try:
            retry_count = int(str(retry_raw).strip())
            if retry_count < 0:
                raise ValueError("retry must be non-negative")
            if retry_count > retry_max:
                logger.warning("重试次数过大: %s, 截断为 %s", retry_count, retry_max)
                retry_count = retry_max
        except Exception:
            logger.warning("收到非法重试次数: %s, 使用默认 %s", retry_raw, retry_default)
            retry_count = retry_default

        logger.info(
            "收到参数: prompt_len=%s, reference_images_count=%s, resolution=%s, timeout=%s, retry=%s",
            len(prompt) if isinstance(prompt, str) else "N/A",
            len(reference_images) if isinstance(reference_images, list) else "N/A",
            resolution,
            timeout_seconds,
            retry_count,
        )
        
        if not prompt:
            yield self.create_text_message("错误：提示词不能为空")
            return
        
        # 验证参考图片数量
        if reference_images and len(reference_images) > 10:
            logger.warning("参考图片数量过多: %s", len(reference_images))
            yield self.create_text_message("错误：参考图片数量不能超过10张")
            return
        
        try:
            # 构建请求体
            parts = [{"text": prompt}]
            
            # 添加参考图片
            if reference_images:
                for image in reference_images:
                    # 获取图片的 base64 数据和 mime type
                    if hasattr(image, 'blob'):
                        # 从文件对象获取数据
                        image_data = base64.b64encode(image.blob).decode('utf-8')
                        mime_type = image.mime_type or "image/jpeg"
                    else:
                        # 如果已经是 base64 字符串
                        image_data = image
                        mime_type = "image/jpeg"
                    
                    parts.append({
                        "inline_data": {
                            "data": image_data,
                            "mime_type": mime_type
                        }
                    })
            
            request_body = {
                "contents": [
                    {
                        "parts": parts
                    }
                ]
            }

            # 根据分辨率构建模型名称
            # 1K: gemini-3-pro-image-preview
            # 2K: gemini-3-pro-image-preview-2k
            # 4K: gemini-3-pro-image-preview-4k
            model_suffix = ""
            if resolution == "2K":
                model_suffix = "-2k"
            elif resolution == "4K":
                model_suffix = "-4k"

            # 构建完整的 URL（base_url 只需要到域名，例如 https://privnode.com）
            full_url = f"{base_url}/v1beta/models/gemini-3-pro-image-preview{model_suffix}:generateContent"

            logger.info(
                "准备调用 Gemini API, url=%s, parts_count=%s, resolution=%s, timeout=%s, retry=%s",
                full_url,
                len(parts),
                resolution,
                timeout_seconds,
                retry_count,
            )
            
            # 设置请求头
            headers = {
                "x-goog-api-key": api_key,
                "Content-Type": "application/json"
            }

            # 带重试的请求逻辑
            attempt = 0
            response = None
            while True:
                try:
                    attempt += 1
                    logger.info("第 %s 次请求 Gemini API", attempt)
                    response = requests.post(
                        full_url,
                        headers=headers,
                        json=request_body,
                        timeout=timeout_seconds,
                    )
                    logger.info(
                        "Gemini API 返回, status_code=%s, headers=%s",
                        response.status_code,
                        dict(response.headers),
                    )

                    if response.status_code != 200:
                        error_msg = f"API 请求失败: {response.status_code}"
                        logger.error("API 请求失败: %s", error_msg)
                        if attempt <= retry_count:
                            logger.warning("准备重试，剩余重试次数: %s", retry_count - attempt + 1)
                            continue
                        # 没有剩余重试次数，直接返回错误
                        yield self.create_text_message(error_msg)
                        return

                    # 状态码 200，跳出重试循环
                    break

                except requests.exceptions.Timeout:
                    logger.warning("请求超时（第 %s 次），timeout=%s", attempt, timeout_seconds, exc_info=True)
                    if attempt <= retry_count:
                        logger.warning("准备重试，剩余重试次数: %s", retry_count - attempt + 1)
                        continue
                    # 将异常抛给外层统一处理
                    raise
                except requests.exceptions.RequestException:
                    logger.warning("网络请求失败（第 %s 次）", attempt, exc_info=True)
                    if attempt <= retry_count:
                        logger.warning("准备重试，剩余重试次数: %s", retry_count - attempt + 1)
                        continue
                    # 将异常抛给外层统一处理
                    raise
            
            # 解析响应
            result = response.json()
            logger.info(
                "API 响应解析成功, keys=%s",
                list(result.keys()) if isinstance(result, dict) else type(result),
            )
            
            # 提取生成的图片
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                logger.info("检测到 candidates, count=%s（响应按 Markdown 文本处理）", len(result["candidates"]))
                if "content" in candidate and "parts" in candidate["content"]:
                    logger.info("candidate.content.parts 数量: %s", len(candidate["content"]["parts"]))
                    for part in candidate["content"]["parts"]:
                        if "text" in part:
                            text = part.get("text") or ""
                            logger.info("检测到文本内容, 直接返回文本")
                            # 直接返回模型返回的 text 字段内容
                            yield self.create_text_message(text)
                            return
                    # 如果没有找到 text 字段，返回完整响应用于调试
                    logger.error("未在响应 parts 中找到 text 字段, 返回完整响应用于调试")
                    yield self.create_json_message({
                        "message": "未在响应 parts 中找到 text 字段",
                        "response": result
                    })
            else:
                logger.error("API 响应格式异常, 不包含有效的 candidates")
                yield self.create_json_message({
                    "message": "API 响应格式异常",
                    "response": result
                })
                
        except requests.exceptions.Timeout:
            logger.error("请求超时", exc_info=True)
            yield self.create_text_message("错误：请求超时，请稍后重试")
        except requests.exceptions.RequestException as e:
            logger.error("网络请求失败: %s", str(e), exc_info=True)
            yield self.create_text_message(f"错误：网络请求失败 - {str(e)}")
        except Exception as e:
            logger.error("调用过程中发生未预期异常: %s", str(e), exc_info=True)
            yield self.create_text_message(f"错误：{str(e)}")
