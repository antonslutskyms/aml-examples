from semantic_kernel.connectors.ai.open_ai import OpenAITextToImage

from collections.abc import Mapping
from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import ValidationError

from semantic_kernel.connectors.ai.open_ai.services.open_ai_config_base import OpenAIConfigBase
from semantic_kernel.connectors.ai.open_ai.services.open_ai_model_types import OpenAIModelTypes
from semantic_kernel.connectors.ai.open_ai.services.open_ai_text_to_image_base import OpenAITextToImageBase
from semantic_kernel.connectors.ai.open_ai.settings.open_ai_settings import OpenAISettings
from semantic_kernel.exceptions.service_exceptions import ServiceInitializationError

from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_text_to_image_execution_settings import (
    ImageSize,
    OpenAITextToImageExecutionSettings,
)
from semantic_kernel.connectors.ai.open_ai.services.open_ai_handler import OpenAIHandler
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.connectors.ai.text_to_image_client_base import TextToImageClientBase
from semantic_kernel.exceptions.service_exceptions import ServiceInvalidRequestError, ServiceResponseException

from typing import Any
from warnings import warn

from openai.types.images_response import ImagesResponse


T_ = TypeVar("T_", bound="OpenAITextToImage")


class ImageGenTextToImage(OpenAITextToImage):
    """OpenAI Text to Image service."""

    def __init__(
        self,
        ai_model_id: str | None = None,
        api_key: str | None = None,
        org_id: str | None = None,
        service_id: str | None = None,
        default_headers: Mapping[str, str] | None = None,
        async_client: AsyncOpenAI | None = None,
        env_file_path: str | None = None,
        env_file_encoding: str | None = None,
    ) -> None:
        
        super().__init__(ai_model_id, api_key, org_id, service_id, default_headers, async_client, env_file_path, env_file_encoding)

    async def _send_edit_request(self, settings: OpenAITextToImageExecutionSettings, image=None) -> ImagesResponse:
        try:
            return await self.client.images.edit(
                image=image,
                **settings.prepare_settings_dict(),
            )
        except Exception as ex:
            raise ServiceResponseException(f"Failed to generate image: {ex}") from ex

    async def edit_image(
        self,
        description: str,
        width: int | None = None,
        height: int | None = None,
        image: bytes | None = None,
        settings: PromptExecutionSettings | None = None,
        **kwargs: Any,
    ) -> bytes | str:
        """Generate image from text.

        Args:
            description: Description of the image.
            width: Deprecated, use settings instead.
            height: Deprecated, use settings instead.
            settings: Execution settings for the prompt.
            kwargs: Additional arguments, check the openai images.generate documentation for the supported arguments.

        Returns:
            bytes | str: Image bytes or image URL.
        """
        if not settings:
            settings = OpenAITextToImageExecutionSettings(**kwargs)
        if not isinstance(settings, OpenAITextToImageExecutionSettings):
            settings = OpenAITextToImageExecutionSettings.from_prompt_execution_settings(settings)
        if width:
            warn("The 'width' argument is deprecated. Use 'settings.size' instead.", DeprecationWarning)
            if settings.size and not settings.size.width:
                settings.size.width = width
        if height:
            warn("The 'height' argument is deprecated. Use 'settings.size' instead.", DeprecationWarning)
            if settings.size and not settings.size.height:
                settings.size.height = height
        if not settings.size and width and height:
            settings.size = ImageSize(width=width, height=height)

        if not settings.prompt:
            settings.prompt = description

        if not settings.prompt:
            raise ServiceInvalidRequestError("Prompt is required.")

        if not settings.ai_model_id:
            settings.ai_model_id = self.ai_model_id

        print("Settings:", settings)

        response = await self._send_edit_request(settings, image=image)

        assert isinstance(response, ImagesResponse)  # nosec
        if not response.data or not response.data[0].b64_json:
            raise ServiceResponseException("Failed to generate image.")

        b64_img = response.data[0].b64_json

        return b64_img


    async def generate_image(
        self,
        description: str,
        width: int | None = None,
        height: int | None = None,
        settings: PromptExecutionSettings | None = None,
        **kwargs: Any,
    ) -> bytes | str:
        """Generate image from text.

        Args:
            description: Description of the image.
            width: Deprecated, use settings instead.
            height: Deprecated, use settings instead.
            settings: Execution settings for the prompt.
            kwargs: Additional arguments, check the openai images.generate documentation for the supported arguments.

        Returns:
            bytes | str: Image bytes or image URL.
        """
        if not settings:
            settings = OpenAITextToImageExecutionSettings(**kwargs)
        if not isinstance(settings, OpenAITextToImageExecutionSettings):
            settings = OpenAITextToImageExecutionSettings.from_prompt_execution_settings(settings)
        if width:
            warn("The 'width' argument is deprecated. Use 'settings.size' instead.", DeprecationWarning)
            if settings.size and not settings.size.width:
                settings.size.width = width
        if height:
            warn("The 'height' argument is deprecated. Use 'settings.size' instead.", DeprecationWarning)
            if settings.size and not settings.size.height:
                settings.size.height = height
        if not settings.size and width and height:
            settings.size = ImageSize(width=width, height=height)

        if not settings.prompt:
            settings.prompt = description

        if not settings.prompt:
            raise ServiceInvalidRequestError("Prompt is required.")

        if not settings.ai_model_id:
            settings.ai_model_id = self.ai_model_id

        print("Settings:", settings)

        response = await self._send_request(settings)

        assert isinstance(response, ImagesResponse)  # nosec
        if not response.data or not response.data[0].b64_json:
            raise ServiceResponseException("Failed to generate image.")

        b64_img = response.data[0].b64_json

        return b64_img