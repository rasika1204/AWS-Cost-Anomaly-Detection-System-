# Demo Script – AWS Cost Anomaly Detection System

This demo script walks through the architecture, setup, execution, and outputs of the **AWS Cost Anomaly Detection System**.  

Use this script for:
- GitHub project demo video  
- Interview walkthrough  
- Portfolio presentation  
- README-linked documentation  

---

# 🎬 1. Introduction (10–15 seconds)

**“Hi, this project is a fully serverless AWS Cost Anomaly Detection System that automatically monitors your daily AWS spending, detects unusual cost spikes using anomaly detection, and sends alerts via Slack or email. The system runs daily using EventBridge and stores detailed JSON reports in S3.”**

---

# 🏗 2. Architecture Overview (20–30 seconds)

Show the architecture diagram from your README.

Explain:

**“The workflow is simple:  
EventBridge triggers a Lambda function every day. The Lambda calls AWS Cost Explorer to fetch the previous day’s spending. It calculates whether the cost is abnormal using rolling averages, standard deviation, and percentage increase thresholds.  
If an anomaly is detected, the function sends alerts through Slack or SNS Email and stores a detailed report in S3. All logs go to CloudWatch.”**

---

# 🧩 3. Show Project Structure (10 seconds)

Display repo files:


Explain:

**“All logic lives inside `lambda_function.py`. Documentation is in the README. This demo script is here in `demo.md`.”**

---

# ⚙️ 4. Lambda Function Walkthrough (1 minute)

Open the Lambda console and explain these points:

### **a) Environment Variables**
Highlight:
- `S3_BUCKET`
- `SNS_TOPIC_ARN`
- `SLACK_WEBHOOK`
- `LOOKBACK_DAYS`
- `WINDOW_DAYS`
- `Z_THRESHOLD`
- `PCT_THRESHOLD`

**Explain**:  
“These values control where reports are stored and the sensitivity of anomaly detection. They make the system configurable without editing code.”

### **b) Key Python Logic inside lambda_function.py**

Walk through the important parts:
- Cost Explorer API call (`ce.get_cost_and_usage`)
- Baseline calculation (mean & stdev)
- Z-score & % increase thresholds
- S3 file upload
- Slack + SNS alerts

**Explain:**  
“Rolling baseline and thresholds help catch unexpected increases in cloud costs.”

---

# 🧪 5. Run a Manual Test (30–40 seconds)

In the Lambda console:

1. Click **Test**  
2. Run the function  
3. Open **CloudWatch Logs**

Describe the output:

**“The logs show yesterday’s cost, baseline mean, z-score, and a message indicating whether an anomaly was found.”**

---

# 📦 6. Check Outputs (30 seconds)

### **a) S3 Bucket**
Navigate to:

Show sample report content:
- yesterday’s cost
- baseline mean/stdev
- anomaly values
- z-score
- percentage increase

Explain:

**“Every run stores a JSON report so you can track spending over time.”**

### **b) Slack / SNS Email**
Show the alert message:

**“If an anomaly is detected, Slack/SNS sends an alert with the reason and the S3 location of the report.”**

---

# ⏰ 7. Show Scheduled Rule (20 seconds)

Open EventBridge → Rules → `daily-cost-anomaly-rule`

Explain:

**“This cron rule triggers the Lambda daily at 06:00 UTC. The system runs completely on its own, no servers needed.”**

---

# 🔐 8. Show IAM Role (optional but good for demo)

Open IAM role `lambda-cost-monitor-role`.

Explain least-privilege access:
- Cost Explorer read  
- S3 write  
- SNS publish  
- CloudWatch logs  

**“Only required permissions are granted. No admin permissions are used.”**

---

# 🎯 9. Wrap Up (10–15 seconds)

Final summary you can say:

**“This project demonstrates serverless automation, cost monitoring, anomaly detection, IAM, Python automation, and multi-service AWS integration. It is a practical CloudOps/DevOps project that provides real business value by preventing unexpected cloud bills.”**

---

# 🙌 End of Demo

Feel free to modify this script for your voice or demo style.
