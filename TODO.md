# TODO

Format: **[estimated effort in man hours]** - [description]

 - Complete unit tests
    - **2..4** add unit tests in `test_ml_optim.py`
    - **2..4** add unit tests in `test_ml_training.py`
    - **1..3** add unit tests in `test_ml_model.py`
    - **1..3** add unit tests in `test_ml_prediction.py` 
    - **4..8** create and add unit tests in `test_utils_misc.py`
    - **4..8** create and add unit tests in `test_utils_core.py`
 - Complete functional tests
    - **1..3** add functional tests in `test_cli_main.py`
 - Add Security Layer
    - **4..16** Add support for JSON Web Token (JWT) authentication (incl. tests)
 - Harden the Docker image
 - Investigate more performat ML models
    - The model seems to not perform well on short text inputs
    - Undefined and unclear behavior on longer text with mixed languages
 - Complete Makefile rules
 - Complete documentation
