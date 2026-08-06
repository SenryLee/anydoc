from typing import Any

from dify_plugin import ToolProvider


class TextConvertProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # No credentials required; conversion runs locally inside the plugin.
        return
