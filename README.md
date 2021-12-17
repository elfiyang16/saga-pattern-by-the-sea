### SAGA BY THE SEA -- A SERVERLESS SAGA PATTERN WITH STEP FUNCTION

![](2021-12-08-19-38-54.png)

![diagram](https://user-images.githubusercontent.com/29664811/146546749-ba9d66bc-204d-4ba0-9198-3a9ab45e412c.png)
![statemachine](https://user-images.githubusercontent.com/29664811/146546831-34e2ab0d-574a-41f2-991d-8148710d09ee.png)

#### AWS Services

- Lambda
- API Gateway
- Stepfunctions
- DynamoDB
- SNS
- SQS

Architecture is provisioned with CloudFormation

#### Deployment and Test

- Set env var:

```
PROJECTNAME=SAGA_ORDER_PROCESS
YOURNAME=XXX
YOUREMAIL=XXX@gmail.com
```

- Create the S3 bucket for the lambda functions:`aws s3 mb s3://$PROJECT`

- Install python package

```shell

cd lambda/layer/python
pip install -r requirements.txt -t .
```

- Upload local artifacts

```shell
aws cloudformation package \
    --template-file stepfunction.yml \
    --s3-bucket $PROJECT \
    --output-template-file packaged.yml

aws cloudformation deploy \
    --stack-name $PROJECT \
    --region eu-west-1 \
    --template-file packaged.yml \
    --capabilities CAPABILITY_NAMED_IAM \
    --output text \
    --parameter-overrides \
        NotifyEmail=$YOUREMAIL
```

- To trigger a run

```shell
aws lambda invoke \
    --function-name TestSfnFunction \
    --region eu-west-1 \
    --payload '{}' \
    response.json
```

You can have your own data sample or use the example provided:

```json
{
  "order_id": "40063fe3-56d9-4c51-b91f-71929834ce03",
  "order_date": "2019-12-01 12:32:24.927479",
  "customer_id": "2d14eb6c-a3c2-3412-8450-239a16f01fea",
  "items": [
    {
      "item_id": "0123",
      "qty": 1.0,
      "description": "item 1",
      "unit_price": 12.99
    },
    {
      "item_id": "0234",
      "qty": 2.0,
      "description": "item 2",
      "unit_price": 41.98
    },
    {
      "item_id": "0345",
      "qty": 3.0,
      "description": "item 3",
      "unit_price": 3.5
    }
  ]
}
```
