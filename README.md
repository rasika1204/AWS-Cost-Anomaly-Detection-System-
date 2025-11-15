# AWS Cost Anomaly Detection System

A fully serverless cloud cost monitoring and anomaly detection system built using **AWS Lambda**, **AWS Cost Explorer**, **AWS EventBridge**, **AWS S3**, **AWS SNS**, and **Slack Webhooks**.

This project analyzes daily AWS costs, detects abnormal spikes using statistical analysis, and sends automated alerts.

---

## 📌 Features

- Daily automated execution (EventBridge)
- Fetches daily AWS spending using Cost Explorer API
- Detects anomalies using:
  - Rolling mean & standard deviation (z-score)
  - Percentage increase threshold
- Sends alerts through Slack Webhook and/or SNS Email
- Stores daily JSON reports in S3
- Uses IAM least-privilege role
- 100% serverless and Free-Tier friendly

---

## 🏗 Architecture Diagram

```mermaid
flowchart TD

A[EventBridge Daily Trigger] --> B[Lambda Function]

B --> C[Fetch Cost Explorer Daily Data]

C --> D[Calculate Baseline Mean & Standard Deviation]

D --> E{Anomaly Detected?}

E -- Yes --> F[Generate JSON Report]
E -- Yes --> G[Send Slack/SNS Alerts]

F --> H[Upload Report to S3 Bucket]

E -- No --> I[Log 'No Anomaly' to CloudWatch]

G --> I
H --> I

I --> J[End]
