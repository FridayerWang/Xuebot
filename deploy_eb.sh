#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# === Configuration ===
# !! EDIT THESE VARIABLES !!
APP_NAME="xuebot-app" 
ENV_NAME="xuebot-env" 
AWS_REGION="us-east-1" # The AWS region to deploy to
PYTHON_PLATFORM="64bit Amazon Linux 2023 v4.5.0 running Python 3.11" # Using the latest available Python platform
INSTANCE_TYPE="t3.large" # Upgraded instance type for more resources

# Environment variables to set in Elastic Beanstalk
# !! REPLACE PLACEHOLDER FOR OPENAI_API_KEY !!
EB_ENV_VARS="OPENAI_API_KEY='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',USE_VECTOR_STORE='true',VECTOR_STORE_DIR='./chroma_db',EMBEDDING_MODEL='BAAI/bge-large-en-v1.5',LOG_LEVEL='INFO',CONSOLE_LOG_LEVEL='INFO',FILE_LOG_LEVEL='INFO'"

# === Script ===

echo "Starting Elastic Beanstalk deployment..."

# Check if EB CLI is installed
if ! command -v eb &> /dev/null
then
    echo "Error: EB CLI ('eb') could not be found."
    echo "Please install it: pip install awsebcli --upgrade"
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
  echo "AWS credentials not configured or invalid. Please run 'aws configure'."
  exit 1
fi

# Initialize Elastic Beanstalk application if not already initialized
if [ ! -d ".elasticbeanstalk" ]; then
  echo "Initializing Elastic Beanstalk application..."
  eb init "$APP_NAME" --platform "$PYTHON_PLATFORM" --region "$AWS_REGION"
else
  echo "Elastic Beanstalk application already initialized."
fi

# Check if the environment already exists
echo "Checking for existing environment '$ENV_NAME'..."
if eb status "$ENV_NAME" --region "$AWS_REGION" &> /dev/null; then
  echo "Environment '$ENV_NAME' already exists. Terminating and recreating..."
  
  # Terminate the existing environment
  echo "Terminating environment..."
  eb terminate "$ENV_NAME" --force
  
  # Wait for termination to complete
  echo "Waiting for environment termination..."
  sleep 60
fi

# Create a new environment
echo "Creating new environment with $INSTANCE_TYPE instance type..."
eb create "$ENV_NAME" -p "$PYTHON_PLATFORM" --region "$AWS_REGION" --envvars "$EB_ENV_VARS" --instance_type "$INSTANCE_TYPE"

echo "Deployment process initiated for environment '$ENV_NAME'."
echo "You can monitor the progress in the AWS Elastic Beanstalk console or by using 'eb status $ENV_NAME'."
echo "To open the application URL, use: eb open $ENV_NAME"

exit 0 