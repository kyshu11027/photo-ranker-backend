# AWS Lambda Project

This repository contains multiple AWS Lambda functions written in Python. Each Lambda function serves a specific purpose, and this guide will help you set up, test, and deploy them efficiently.

---

## Prerequisites

Before you begin, ensure you have the following installed on your local machine:

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **AWS CLI** (Configured with the necessary permissions to manage AWS Lambda)
- **virtualenv** (optional but recommended)

---

## Project Setup

Follow these steps to set up the project locally:

### 1. Clone the Repository

```bash
git clone <repository_url>
cd <project_directory>
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
```

On Linux/Mac:

```bash
source venv/bin/activate
```

On Windows:

```powershell
venv\Scripts\activate
```

### 3. Install Dependencies

```
pip install -r requirements.txt
```

### 4. Add a .env to the Project Root Directory

Below are the environment variables needed to test locally:

1. DB_HOST
2. DB_NAME
3. DB_USER
4. DB_PASSWORD
5. AUTH0_DOMAIN
6. API_AUDIENCE
7. CLIENT_ID
8. CLIENT_SECRET

## Development Guide

There are three subdirectories in this project: src, terraform, test

1. src contains all business logic for the application
2. terraform contains all of the configurations for deploying code to AWS reliably
3. test contains integration tests for us to test business logic locally before deployment

### 1. Develop Your Changes

Implement your API in the src directory. If a file for your route is not yet defined,
you will have to define a new API Gateway route in terraform/apigateway.tf and create a new
lambda definition in terraform/lambda

### 2. Implement a Test

To verify your business logic works without having to deploy code to AWS, you must run tests locally.
Testing uses moto, a python package that mocks AWS services.

To run your tests, use the command below:

```bash
pytest
```

### 3. Push Your Code/Deploy

Before pushing your code, cd into the terraform directory and run the command below to make sure the
deployment does not fail due to configuration formatting:

```bash
terraform fmt
```

When your tests are passing, push your code. You can deploy the changes by running the GitHub Action.
