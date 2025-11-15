import os
import json
import boto3
import datetime
import statistics
import urllib.request
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# -------- CONFIG via env vars (set in Lambda console) --------
REPORT_BUCKET = os.environ.get("REPORT_BUCKET", "rasika-cost-reports-rw1311")
S3_PREFIX = os.environ.get("S3_PREFIX", "cost-reports/")     # optional prefix
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK", "")          # leave empty to skip
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")          # leave empty to skip

# Settings (env)
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "30"))
WINDOW_DAYS = int(os.environ.get("WINDOW_DAYS", "7"))
Z_THRESHOLD = float(os.environ.get("Z_THRESHOLD", "2.0"))       # z-score threshold
PCT_THRESHOLD = float(os.environ.get("PCT_THRESHOLD", "0.5"))   # 0.5 == 50%

# boto3 clients
ce = boto3.client("ce")
s3 = boto3.client("s3")
sns = boto3.client("sns")

def get_daily_costs(start_date, end_date):
    """Return list of (date_str, amount_float) ordered oldest->newest."""
    try:
        resp = ce.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="DAILY",
            Metrics=["UnblendedCost"]
        )
    except Exception:
        logger.exception("Cost Explorer request failed")
        raise

    results = []
    for r in resp.get("ResultsByTime", []):
        date = r.get("TimePeriod", {}).get("Start")
        amt_str = r.get("Total", {}).get("UnblendedCost", {}).get("Amount", "0")
        try:
            amount = float(amt_str)
        except Exception:
            amount = 0.0
        results.append((date, amount))
    return results

def send_slack(msg):
    if not SLACK_WEBHOOK:
        logger.info("SLACK_WEBHOOK not set; skipping Slack")
        return
    data = json.dumps({"text": msg}).encode("utf-8")
    req = urllib.request.Request(SLACK_WEBHOOK, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            logger.info("Slack response %s", resp.status)
    except Exception:
        logger.exception("Slack send failed")

def notify_sns(subject, message):
    if not SNS_TOPIC_ARN:
        logger.info("SNS_TOPIC_ARN not set; skipping SNS")
        return
    try:
        sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)
    except Exception:
        logger.exception("SNS publish failed")

def lambda_handler(event, context):
    today = datetime.date.today()
    # CE 'End' is exclusive -> using today ensures last day returned is yesterday
    start = today - datetime.timedelta(days=LOOKBACK_DAYS)
    start_str = start.strftime("%Y-%m-%d")
    end_str = today.strftime("%Y-%m-%d")

    logger.info("Fetching costs from %s to %s", start_str, end_str)
    data = get_daily_costs(start_str, end_str)
    if not data:
        logger.warning("No cost data returned")
        return {"status": "no_data"}

    data.sort()
    dates = [d for d, a in data]
    amounts = [a for d, a in data]

    yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    if yesterday not in dates:
        logger.info("Yesterday's cost not available yet in Cost Explorer; available dates: %s", dates)
        return {"status": "not_ready", "available_dates": dates}

    idx = dates.index(yesterday)
    yesterday_cost = amounts[idx]

    # Baseline: previous WINDOW_DAYS ending the day before yesterday
    baseline_start_idx = max(0, idx - WINDOW_DAYS)
    baseline_end_idx = idx  # exclusive of yesterday
    baseline_amounts = amounts[baseline_start_idx:baseline_end_idx]

    if not baseline_amounts:
        logger.warning("Not enough baseline history; using all prior days")
        baseline_amounts = amounts[:idx]

    mean = statistics.mean(baseline_amounts) if baseline_amounts else 0.0
    stdev = statistics.stdev(baseline_amounts) if len(baseline_amounts) > 1 else 0.0

    # z-score: if stdev is zero, set to None and handle separately
    if stdev > 0:
        z_score = (yesterday_cost - mean) / stdev
    else:
        z_score = None

    # percent increase: handle mean == 0 specially
    if mean > 0:
        pct_increase = (yesterday_cost - mean) / mean
    else:
        if yesterday_cost > 0:
            pct_increase = float('inf')   # treat any positive cost vs zero baseline as infinite increase
        else:
            pct_increase = 0.0

    report = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "yesterday": {"date": yesterday, "cost": round(yesterday_cost, 6)},
        "baseline": {"window_days": len(baseline_amounts), "mean": round(mean, 6), "stdev": round(stdev, 6)},
        "z_score": None if z_score is None else round(z_score, 4),
        "pct_increase": None if pct_increase == float('inf') else round(pct_increase, 4),
        "raw_pct_increase_inf": pct_increase == float('inf'),
        "history": [{"date": d, "cost": a} for d, a in data[max(0, idx-30):idx+1]]
    }

    # write to S3
    key = f"{S3_PREFIX.rstrip('/')}/{yesterday}.json"
    try:
        s3.put_object(Bucket=REPORT_BUCKET, Key=key, Body=json.dumps(report).encode("utf-8"))
        logger.info("Saved report to s3://%s/%s", REPORT_BUCKET, key)
    except Exception:
        logger.exception("S3 put failed")

    # Decide anomaly
    is_anomaly = False
    reasons = []
    if z_score is not None and z_score >= Z_THRESHOLD:
        is_anomaly = True
        reasons.append(f"z_score >= {Z_THRESHOLD} ({z_score:.2f})")
    # If pct_increase is infinite, treat as anomaly
    if pct_increase == float('inf') or pct_increase >= PCT_THRESHOLD:
        is_anomaly = True
        pct_disp = "infinite" if pct_increase == float('inf') else f"{pct_increase*100:.1f}%"
        reasons.append(f"pct_increase >= {PCT_THRESHOLD*100:.0f}% ({pct_disp})")

    if is_anomaly:
        subject = f"[COST ALERT] anomaly for {yesterday}: ${yesterday_cost:.2f}"
        msg = f"{subject}\nReport: s3://{REPORT_BUCKET}/{key}\nReasons: {', '.join(reasons)}\n\nDetails:\n{json.dumps(report, indent=2)}"
        logger.info("Anomaly detected: %s", reasons)
        send_slack(msg)
        notify_sns(subject, msg)
    else:
        logger.info("No anomaly. yesterday=%s mean=%s z=%s pct=%s",
                    yesterday_cost, mean, z_score, ("infinite" if pct_increase == float('inf') else pct_increase))

    return {"status": "ok", "anomaly": is_anomaly, "z_score": z_score, "pct": pct_increase}
