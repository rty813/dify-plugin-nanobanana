from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class NanobananaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证凭据
        """
        try:
            base_url = credentials.get("base_url", "")
            api_key = credentials.get("api_key", "")
            
            if not base_url:
                raise ToolProviderCredentialValidationError("Base URL 不能为空")
            
            if not api_key:
                raise ToolProviderCredentialValidationError("API Key 不能为空")
            
            # 凭据验证通过
            pass
            
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
