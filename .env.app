API_PREFIX=
API_VERSION=

ALLOWED_HOSTS=["localhost","10.0.0.1","127.0.0.1","0.0.0.0"]

LOG_LEVEL="INFO"
MAX_LOG_FILE_SIZE=16777216
MAX_LOG_FILE_COUNT=8

DATA_DIR="artifacts/data"
PIPELINE_DIR="artifacts/pipelines"

RAW_DATA_SOURCE="https://www.kaggle.com/api/v1/datasets/download/basilb2s/language-detection"
RAW_DATA_SOURCE_FILENAME="Language Detection.csv"

RAW_FILENAME="raw_data.csv"
CLEAN_FILENAME="clean_data.csv"
ML_PIPELINE_FILENAME="ml_pipeline.pkl.lzma"
ML_PARAMS_FILENAME="ml_params.pkl.lzma"
