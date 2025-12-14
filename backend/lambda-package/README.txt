Lambda Deployment Package

To complete the package:
1. Install dependencies for Linux x86_64:
   docker run --rm -v $(pwd):/var/task public.ecr.aws/sam/build-python3.13:latest pip install -r requirements.txt -t lambda-package/

2. Or use AWS Lambda Layers for psycopg2-binary

3. Zip the package:
   cd lambda-package && zip -r ../lambda-deployment.zip .
