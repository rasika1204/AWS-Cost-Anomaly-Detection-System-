# AWS Cost Anomaly Detection System
A fully serverless cloud cost monitoring system using **AWS Lambda**, **Cost Explorer**, **EventBridge**, **SNS**, **Slack**, and **S3**.

This project analyzes daily AWS cost, detects unusual spikes using anomaly detection, and sends automatic alerts.

---

## 📌 Features

- 🔁 Daily automated execution (EventBridge)  
- 💸 Fetch AWS daily spending from Cost Explorer  
- 📈 Anomaly detection using:
  - Rolling mean & standard deviation (z-score)
  - Percentage increase thresholds
- 📤 Alerts via Slack Webhook + SNS Email  
- 📦 Daily JSON report stored in S3  
- 🛡 IAM least-privilege execution role  
- 🆓 Serverless and works within Free Tier

---

## 🏗 Architecture Diagram

```mermaid
flowchart TD

A[EventBridge Daily Trigger] --> B[Lambda Function]

B --> C[Fetch Daily Cost via Cost Explorer API]

C --> D[Calculate Baseline Mean & Standard Deviation]

D --> E{Anomaly Detected?}

E -- Yes --> F[Generate JSON Report]
E -- Yes --> G[Send Slack/SNS Alert]

F --> H[Upload Report to S3 Bucket]

E -- No --> I[Log 'No anomaly' to CloudWatch]

G --> I
H --> I

I --> J[End]

---

## 🛠 Setup Instructions
1) Enable AWS Cost Explorer

AWS Console → Billing → Cost Explorer → Enable
(It may take some hours for data to appear.)

2) Create an S3 Bucket

Example name (must be globally unique):

rasika-cost-reports-12345


Folder structure:

cost-reports/YYYY-MM-DD.json

3) Create SNS Topic (Email Alerts)

AWS Console → SNS → Topics → Create
Name example:

cost-alerts-topic


Subscribe your email and confirm the subscription from your inbox.

4) Create IAM Role for Lambda

Attach managed policy:

AWSLambdaBasicExecutionRole

Add inline policy (update with YOUR values):

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCostExplorerRead",
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowS3Put",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR_S3_BUCKET",
        "arn:aws:s3:::YOUR_S3_BUCKET/*"
      ]
    },
    {
      "Sid": "AllowSNSPublish",
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": [
        "arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT_ID:YOUR_SNS_TOPIC_NAME"
      ]
    }
  ]
}

5) Create Lambda Function

AWS Console → Lambda → Create Function

Name: cost-anomaly-detector

Runtime: Python 3.10+

Execution role: the IAM role created above

Paste your lambda_function.py code into the function editor and Deploy.

6) Add Environment Variables

Set these in Lambda → Configuration → Environment variables:

S3_BUCKET = your bucket name

SNS_TOPIC_ARN = arn:aws:sns:REGION:ACCOUNT:cost-alerts-topic

SLACK_WEBHOOK = your Slack webhook URL (optional)

LOOKBACK_DAYS = 30

WINDOW_DAYS = 7

Z_THRESHOLD = 2.0

PCT_THRESHOLD = 0.5

7) Create EventBridge Rule (Scheduler)

AWS Console → EventBridge → Rules → Create rule
Schedule example (daily at 06:00 UTC):

cron(0 6 * * ? *)


Target: your Lambda function cost-anomaly-detector.

🧪 Testing
Manual test

Lambda console → Test → Run → Check CloudWatch Logs, S3 for JSON, and Slack/SNS notifications.

Force-alert test (for verification)

Temporarily set:

Z_THRESHOLD = 0.1

PCT_THRESHOLD = 0.0001

Run the function to force alert delivery, then revert to production thresholds.

📤 Output Examples

Example Slack message:

[COST ALERT] Anomaly detected for 2025-11-13: $4.23
Reasons: pct_increase >= 50%
Report saved to S3.


Example S3 JSON report:

{
  "generated_at": "2025-11-14T05:23:33Z",
  "yesterday": {
    "date": "2025-11-13",
    "cost": 4.23
  },
  "baseline": {
    "mean": 1.23,
    "stdev": 0.52
  },
  "z_score": 3.12,
  "pct_increase": 2.34
}

🎥 Demo Script

See demo.md for a step-by-step demo script to record a short walkthrough.

🧠 Skills Demonstrated

AWS Lambda

AWS S3

AWS SNS

AWS EventBridge

AWS Cost Explorer

IAM (least privilege)

Python (boto3)

Serverless automation & monitoring

📄 License

MIT

⭐ Author

Rasika
