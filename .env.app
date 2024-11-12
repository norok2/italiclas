API_PREFIX=
API_VERSION=

ALLOWED_HOSTS=["localhost","10.0.0.1","127.0.0.1","0.0.0.0"]

LOG_LEVEL="INFO"
MAX_LOG_FILE_SIZE=16777216
MAX_LOG_FILE_COUNT=8

DATA_DIR="artifacts/data"
ML_DIR="artifacts/ml"

RAW_DATA_SOURCE="https://www.kaggle.com/api/v1/datasets/download/basilb2s/language-detection"
RAW_DATA_SOURCE_FILENAME="Language Detection.csv"

RAW_FILENAME="raw_data.csv"
CLEAN_FILENAME="clean_data.csv"
ML_MODEL_PIPELINE_FILENAME="model_pipeline.pkl.lzma"
OPTIM_PARAMS_FILENAME="optim_params.pkl.lzma"
