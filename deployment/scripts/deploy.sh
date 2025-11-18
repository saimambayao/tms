#!/bin/bash

# Deployment script for #FahanieCares

# Exit on error
set -e

# Configuration
APP_NAME="fahaniecares"
REGION="ap-southeast-1"
ECR_REPOSITORY="${APP_NAME}"
ECS_CLUSTER="${APP_NAME}-cluster"
ECS_SERVICE="${APP_NAME}-service"

# Check environment variables
if [ -z "$AWS_ACCOUNT_ID" ]; then
    echo "ERROR: AWS_ACCOUNT_ID is not set"
    exit 1
fi

if [ -z "$SUBNET_IDS" ]; then
    echo "ERROR: SUBNET_IDS is not set"
    exit 1
fi

if [ -z "$SECURITY_GROUP_IDS" ]; then
    echo "ERROR: SECURITY_GROUP_IDS is not set"
    exit 1
fi

echo "Starting deployment for ${APP_NAME}..."

# Build and tag Docker image
echo "Building Docker image..."
docker build -t ${APP_NAME}:latest -f deployment/docker/Dockerfile .

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Create ECR repository if it doesn't exist
echo "Creating ECR repository if needed..."
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${REGION} || \
aws ecr create-repository --repository-name ${ECR_REPOSITORY} --region ${REGION}

# Tag and push image to ECR
echo "Tagging and pushing image to ECR..."
docker tag ${APP_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPOSITORY}:latest

# Update ECS service
echo "Updating ECS service..."
aws ecs update-service --cluster ${ECS_CLUSTER} --service ${ECS_SERVICE} --force-new-deployment --region ${REGION}

# Run database migrations
echo "Running database migrations..."
MIGRATION_TASK_ARN=$(aws ecs run-task \
    --cluster ${ECS_CLUSTER} \
    --task-definition ${APP_NAME}-migration \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[${SUBNET_IDS}],securityGroups=[${SECURITY_GROUP_IDS}],assignPublicIp=ENABLED}" \
    --region ${REGION} \
    --query 'tasks[0].taskArn' \
    --output text)

# Wait for migration to complete
echo "Waiting for migrations to complete..."
aws ecs wait tasks-stopped --cluster ${ECS_CLUSTER} --tasks ${MIGRATION_TASK_ARN} --region ${REGION}

# Check migration task exit code
MIGRATION_EXIT_CODE=$(aws ecs describe-tasks \
    --cluster ${ECS_CLUSTER} \
    --tasks ${MIGRATION_TASK_ARN} \
    --region ${REGION} \
    --query 'tasks[0].containers[0].exitCode' \
    --output text)

if [ "${MIGRATION_EXIT_CODE}" != "0" ]; then
    echo "ERROR: Migration task failed with exit code ${MIGRATION_EXIT_CODE}"
    exit 1
fi

# Wait for deployment to complete
echo "Waiting for deployment to complete..."
aws ecs wait services-stable --cluster ${ECS_CLUSTER} --services ${ECS_SERVICE} --region ${REGION}

# Run health check
echo "Running health check..."
LOAD_BALANCER_DNS=$(aws elbv2 describe-load-balancers \
    --names ${APP_NAME}-alb \
    --region ${REGION} \
    --query 'LoadBalancers[0].DNSName' \
    --output text)

sleep 30  # Wait for service to stabilize

HEALTH_CHECK_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://${LOAD_BALANCER_DNS}/health/)

if [ "${HEALTH_CHECK_RESPONSE}" == "200" ]; then
    echo "Health check passed!"
else
    echo "WARNING: Health check returned ${HEALTH_CHECK_RESPONSE}"
fi

echo "Deployment completed successfully!"
echo "Application is available at: https://${LOAD_BALANCER_DNS}"