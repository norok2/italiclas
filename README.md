## Italiclas: Italian Language Classifier

### Overview

**Italiclas** is a simple machine learning model designed to classify text as being Italian or not.

### Implementation

The model is implemented using a [scikit-learn](https://scikit-learn.org/stable/).
It is not meant to be particularly performant.
The main objective of this project is to apply state-of-the-art software engineering practices.

### Architecture
[Insert a diagram or textual description of your model's architecture, including data preprocessing, feature extraction, model training, and prediction stages.]

### Endpoints

The API exposes mainly these endpoints:

* **POST `/predict`**: Takes a text input and returns a boolean indicating whether the text is Italian.
* **GET `/ping`**: Check service availability and display the version.
* **GET `/docs`**: Display Swagger Web UI documentation.

For detailed specifications, see [`openapi.yaml`](https://github.com/norok2/italiclas/blob/main/openapi.yaml).

### Setup

#### Prerequisites
- [GNU Make](https://www.gnu.org/software/make/) (version 4.3)
- [pipx](https://pipx.pypa.io/) (version 1.7.1)


#### Installation
1. Clone the repository:
   ```shell
   git clone https://github.com/norok2/italiclas.git
   ```
2. Move to the project dir:
   ```shell
   cd italiclas
   ```
3. Install [Poetry](https://python-poetry.org/) using `pipx`
   ```shell
   make poetry_setup
   ```
4. Install dependencies using Poetry:
   ```shell
   make install
   ```

### Run

#### Training Pipeline
1. **Data Preparation:** Collect and preprocess the training data, including tokenization, normalization, and feature extraction.
2. **Model Training:** Train the chosen machine learning model on the prepared dataset.
3. **Model Evaluation:** Evaluate the model's performance using appropriate metrics (e.g., accuracy, precision, recall, F1-score).
4. **Model Saving:** Save the trained model for future use.

#### Prediction API
1. **Start the API:** Run the API server using a framework like FastAPI or Flask.
2. **Make Predictions:** Send HTTP POST requests to the `/predict` endpoint with the text to be classified.

### Testing

#### Unit Tests
- Test individual functions and components of the codebase.
- Cover edge cases and error handling scenarios.

#### Integration Tests
- Test the integration of different components (e.g., data preprocessing, model training, API endpoints).

#### Functional Tests
- Test the API endpoints to ensure they return correct responses for various input scenarios.

#### Performance Tests
- Measure the performance of the model and API endpoints under different load conditions.
- Optimize performance by profiling and identifying bottlenecks.

#### Security Tests
- Conduct security audits to identify and address potential vulnerabilities.
- Implement security best practices, such as input validation, output sanitization, and secure coding practices.

### Monitoring
- Set up monitoring tools to track API performance, error rates, and latency.
- Implement logging to record important events and errors.
- Consider using a monitoring tool like Prometheus and Grafana to visualize metrics and alerts.

### Development
- **Best Practices:** Adhere to best practices for code readability, maintainability, and testability.
- **Version Control:** Use Git to manage code versions and collaborate with others.
- **Continuous Integration/Continuous Delivery (CI/CD):** Set up a CI/CD pipeline to automate testing, building, and deployment.
- **Documentation:** Write clear and concise documentation for the project.

By following these guidelines, you can build a robust and efficient Italian language classifier.
