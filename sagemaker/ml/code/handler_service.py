from __future__ import absolute_import

from sagemaker_inference.default_handler_service import DefaultHandlerService
from sagemaker_inference.transformer import Transformer
from inference_handler import DefaultLightgbmInferenceHandler

import os
import sys

ENABLE_MULTI_MODEL = os.getenv("SAGEMAKER_MULTI_MODEL", "false") == "true"


class HandlerService(DefaultHandlerService):

    """Handler service that is executed by the model server.

    Determines specific default inference handlers to use based on the type MXNet model being used.

    This class extends ``DefaultHandlerService``, which define the following:
        - The ``handle`` method is invoked for all incoming inference requests to the model server.
        - The ``initialize`` method is invoked at model server start up.

    Based on: https://github.com/awslabs/mxnet-model-server/blob/master/docs/custom_service.md

    """
    def __init__(self):
        self._initialized = False

        transformer = Transformer(default_inference_handler=DefaultLightgbmInferenceHandler())
        super(HandlerService, self).__init__(transformer=transformer)

    def initialize(self, context):
        # Adding the 'code' directory path to sys.path to allow importing user modules when multi-model mode is enabled.
        if (not self._initialized) and ENABLE_MULTI_MODEL:
            code_dir = os.path.join(context.system_properties.get("model_dir"), 'code')
            sys.path.append(code_dir)
            self._initialized = True

        super().initialize(context)