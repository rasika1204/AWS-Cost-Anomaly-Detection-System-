# AWS-Cost-Anomaly-Detection-System-
A serverless cost-monitoring and alerting system using AWS Lambda, Cost Explorer, S3, SNS, and Slack.
# AWS Cost Anomaly Detection System  
A fully serverless cloud cost monitoring system using **AWS Lambda**, **Cost Explorer**, **EventBridge**, **SNS**, **Slack**, and **S3**.

This project analyzes daily AWS cost, detects unusual spikes using anomaly detection, and sends automatic alerts.

---

# 📌 Features

- 🔁 **Daily automated execution** (EventBridge)
- 💸 **Fetch AWS daily spending** from Cost Explorer
- 📈 **Anomaly detection** using:
  - Rolling mean & standard deviation (z-score)
  - Percentage increase thresholds
- 📤 **Alerts** via Slack Webhook + SNS Email
- 📦 **Daily JSON report** stored in S3
- 🛡 **IAM least-privilege** execution role
- 🆓 100% **serverless** & stays under Free Tier

---

# 🏗 Architecture Diagram

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
🗂 Project Structure
.
├── lambda_function.py      # Main Lambda function
├── README.md               # Documentation
└── demo.md                 # Demo script for GitHub video

🛠 Setup Instructions
1️⃣ Enable AWS Cost Explorer

AWS Console → Billing → Cost Explorer → Enable
(It may take a few hours for cost data to appear.)

2️⃣ Create an S3 Bucket

Example name (must be globally unique):

rasika-cost-reports-12345


Folder structure:

cost-reports/YYYY-MM-DD.json

3️⃣ Create SNS Topic (Email Alerts)

AWS Console → SNS → Topics → Create

Name:

cost-alerts-topic


Subscribe your email and confirm the email link.

4️⃣ Create IAM Role for Lambda
Attach managed policy:

AWSLambdaBasicExecutionRole

Add inline policy (update with YOUR S3 bucket & SNS ARN):
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

5️⃣ Create Lambda Function

AWS Console → Lambda → Create Function

Name: cost-anomaly-detector

Runtime: Python 3.10

Role: Choose the IAM role created above

Paste the code from lambda_function.py.

6️⃣ Add Environment Variables
Key	Value
S3_BUCKET	your bucket name
SNS_TOPIC_ARN	your SNS ARN
SLACK_WEBHOOK	your Slack webhook URL (optional)
LOOKBACK_DAYS	30
WINDOW_DAYS	7
Z_THRESHOLD	2.0
PCT_THRESHOLD	0.5
7️⃣ Create EventBridge Rule (Scheduler)

AWS Console → EventBridge → Rules → Create Rule

Choose schedule:

cron(0 6 * * ? *)


This runs the Lambda every day at 06:00 UTC.

🧪 Testing
✔ Manual Test (Recommended)

Lambda Console → Test → Create test event → Run
Check:

CloudWatch Logs

S3 bucket for JSON report

Slack message

SNS email

✔ Force Alert Test

Set thresholds:

Z_THRESHOLD = 0.1
PCT_THRESHOLD = 0.0001


This ensures an alert fires instantly.

📤 Output Examples
Example Slack Message:
[COST ALERT] Anomaly detected for 2025-11-13: $4.23
Reasons: pct increase >= 50%
Report saved to S3.

Example S3 Report:
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

See demo.md for a video walkthrough script.

🧠 Skills Demonstrated

AWS Lambda

AWS S3

AWS SNS

AWS EventBridge

AWS Cost Explorer

IAM (least privilege)

Python (boto3)

Serverless automation

Cloud monitoring & alerting

📄 License

MIT License

⭐ Author

Rasika
