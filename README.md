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
