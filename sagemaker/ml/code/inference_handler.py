import os
import logging

import lightgbm
import pandas as pd
import numpy as np
import pickle
import json

from sagemaker_inference import (
    content_types,
    decoder,
    default_inference_handler,
    encoder,
    errors,
    utils,
)

INFERENCE_ACCELERATOR_PRESENT_ENV = "SAGEMAKER_INFERENCE_ACCELERATOR_PRESENT"
DEFAULT_MODEL_FILENAME = "model.pkl"


class ModelLoadError(Exception):
    pass


class DefaultLightgbmInferenceHandler(default_inference_handler.DefaultInferenceHandler):
    VALID_CONTENT_TYPES = (content_types.JSON)

    @staticmethod
    def _is_model_file(filename):
        is_model_file = False
        if os.path.isfile(filename):
            _, ext = os.path.splitext(filename)
            is_model_file = ext in [".pkl"]
        return is_model_file

    def default_model_fn(self, model_dir):
        """Loads a model.
        In other cases, users should provide customized model_fn() in script.

        Args:
            model_dir: a directory where model is saved.

        Returns: A LightGBM model.
        """
        model_path = os.path.join(model_dir, DEFAULT_MODEL_FILENAME)
        if not os.path.exists(model_path):
            raise FileNotFoundError("Failed to load model with default model_fn: missing file {}."
                                    .format(DEFAULT_MODEL_FILENAME))
        # Client-framework is CPU only. But model will run in Elastic Inference server with CUDA.
        try:
            with open(model_path, 'rb') as f:
                _model = pickle.load(f)
            return _model
        except RuntimeError as e:
            raise ModelLoadError(
                "Failed to load {}. Please ensure model is saved using torchscript.".format(model_path)
            ) from e

    def default_input_fn(self, input_data, content_type):
        """A default input_fn that can handle JSON formats.

        Args:
            input_data: the request payload serialized in the content_type format
            content_type: the request content_type

        Returns: input_data deserialized into pandas and preprocessed.
        """
        # Parse Json(Dict) to pandas df
        logging.info("start preprocessing")

        input_json = json.loads(input_data)

        logging.info("parsed input data to dict")

        data = pd.DataFrame(input_json["data"])

        logging.info("parsed input data to dataframe")


        # Preprocessing
        data['Sex'].replace(['male', 'female'], [0, 1], inplace=True)
        data['Embarked'].fillna(('S'), inplace=True)
        data['Embarked'] = data['Embarked'].map({'S': 0, 'C': 1, 'Q': 2}).astype(int)
        data['Fare'].fillna(np.mean(data['Fare']), inplace=True)
        data['Age'].fillna(data['Age'].median(), inplace=True)
        data['FamilySize'] = data['Parch'] + data['SibSp'] + 1
        data['IsAlone'] = 0
        data.loc[data['FamilySize'] == 1, 'IsAlone'] = 1

        delete_columns = ['Name', 'PassengerId', 'Ticket', 'Cabin']
        data.drop(delete_columns, axis=1, inplace=True)

        logging.info("preprocessing finish")

        return data

    def default_predict_fn(self, data, model):
        """A default predict_fn for LightGBM. Calls a model on data deserialized in input_fn.

        Args:
            data: input data (Pandas DataFrame) for prediction deserialized by input_fn
            model: LightGBM model loaded in memory by model_fn

        Returns: a prediction
        """
        logging.info("start_prediction")

        output = model.predict(data)

        return output

    def default_output_fn(self, prediction, accept):
        """A default output_fn for LightGBM. Serializes predictions from predict_fn to JSON format.

        Args:
            prediction: a prediction result from predict_fn
            accept: type which the output data needs to be serialized

        Returns: output data serialized
        """
        logging.info("start post processing")

        for content_type in utils.parse_accept(accept):
            if content_type in encoder.SUPPORTED_CONTENT_TYPES:
                encoded_prediction = encoder.encode(prediction, content_type)
                if content_type == content_types.CSV:
                    encoded_prediction = encoded_prediction.encode("utf-8")
                return encoded_prediction

        raise errors.UnsupportedFormatError(accept)