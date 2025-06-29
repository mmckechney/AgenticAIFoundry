import json
import uuid
import random
from datetime import datetime, timedelta
import pytz

# Define technology areas and their details
tech_areas = [
    {
        "name": "Microsoft Teams",
        "issues": [
            ("Audio failure during meeting", "Users reported no audio output during Teams meetings.", "Updated Teams client to latest version.", ["https://docs.microsoft.com/en-us/microsoftteams/troubleshoot-audio-issues", "Teams Admin Guide"]),
            ("Video lag in large meetings", "Video stuttering reported in meetings with 100+ participants.", "Increased bandwidth allocation and updated client.", ["https://docs.microsoft.com/en-us/microsoftteams/optimize-performance", "Teams Network Guide"]),
            ("Chat sync issues", "Messages not syncing across devices in Teams.", "Cleared client cache and re-authenticated users.", ["https://docs.microsoft.com/en-us/microsoftteams/troubleshoot-chat", "Teams User Guide"])
        ]
    },
    {
        "name": "Slack",
        "issues": [
            ("API rate limit errors", "Custom Slack bot hitting API rate limits.", "Batched API requests and implemented retry logic.", ["https://api.slack.com/docs/rate-limits", "Slack Bot Development Guide"]),
            ("Notification delays", "Slack notifications delayed for critical alerts.", "Increased webhook priority and optimized bot logic.", ["https://api.slack.com/docs/webhooks", "Slack Admin Guide"]),
            ("Channel permission issues", "Users unable to access private channels.", "Updated channel roles via Slack Admin panel.", ["https://slack.com/help/articles/360044150211", "Slack Permissions Guide"])
        ]
    },
    {
        "name": "Microsoft Copilot",
        "issues": [
            ("Copilot not responding in Word", "Copilot fails to generate suggestions in Word.", "Reinstalled Copilot add-in and updated Office.", ["https://docs.microsoft.com/en-us/copilot/troubleshoot", "Copilot User Guide"]),
            ("Inaccurate code suggestions", "Copilot generating incorrect code snippets in VS Code.", "Updated Copilot model and cleared cache.", ["https://docs.github.com/en/copilot/troubleshooting", "Copilot Developer Guide"]),
            ("Access denied errors", "Users receiving access denied errors in Copilot.", "Updated Azure AD permissions for Copilot.", ["https://docs.microsoft.com/en-us/copilot/admin-guide", "Copilot Admin Guide"])
        ]
    },
    {
        "name": "Copilot Studio",
        "issues": [
            ("Bot deployment failure", "Copilot Studio bot fails to deploy to Teams.", "Corrected bot configuration in Copilot Studio.", ["https://docs.microsoft.com/en-us/copilot-studio/troubleshoot-deployment", "Copilot Studio Guide"]),
            ("Intent recognition issues", "Bot misinterpreting user intents.", "Retrained NLP model with updated dataset.", ["https://docs.microsoft.com/en-us/copilot-studio/nlp-guide", "Copilot Studio NLP Guide"]),
            ("Integration errors with Power Apps", "Bot not syncing with Power Apps data.", "Updated API connectors in Copilot Studio.", ["https://docs.microsoft.com/en-us/copilot-studio/integration", "Copilot Studio Integration Guide"])
        ]
    },
    {
        "name": "Azure",
        "issues": [
            ("Azure AD authentication failure", "Users unable to log in due to Azure AD errors.", "Corrected reply URL in Azure AD configuration.", ["https://docs.microsoft.com/en-us/azure/active-directory/troubleshoot-authentication", "Azure AD Admin Guide"]),
            ("Blob Storage access errors", "Users receiving 403 errors when accessing Blob Storage.", "Updated IAM roles and storage policies.", ["https://docs.microsoft.com/en-us/azure/storage/troubleshoot", "Azure Storage Guide"]),
            ("Kubernetes Service pod crashes", "AKS pods crashing due to resource limits.", "Increased CPU/memory limits in AKS cluster.", ["https://docs.microsoft.com/en-us/azure/aks/troubleshoot", "AKS Admin Guide"])
        ]
    },
    {
        "name": "GCP",
        "issues": [
            ("BigQuery query performance", "Slow query performance in BigQuery.", "Optimized queries with partitioned tables.", ["https://cloud.google.com/bigquery/docs/best-practices-performance", "BigQuery Optimization Guide"]),
            ("Cloud Functions timeout", "Cloud Functions timing out during execution.", "Increased timeout settings and optimized code.", ["https://cloud.google.com/functions/docs/troubleshooting", "Cloud Functions Guide"]),
            ("VPC network latency", "High latency in GCP VPC network.", "Optimized routing and firewall rules.", ["https://cloud.google.com/vpc/docs/troubleshoot", "GCP Networking Guide"])
        ]
    },
    {
        "name": "AWS",
        "issues": [
            ("Lambda timeout errors", "Lambda functions timing out during execution.", "Increased memory allocation and optimized code.", ["httpsetches://docs.aws.amazon.com/lambda/latest/dg/troubleshooting-execution.html", "AWS Lambda Best Practices"]),
            ("S3 bucket access denied", "Users unable to access S3 bucket due to permissions.", "Updated IAM policies for S3 bucket.", ["https://docs.aws.amazon.com/s3/troubleshoot", "S3 Admin Guide"]),
            ("EC2 instance failure", "EC2 instance not responding to requests.", "Restarted instance and updated security groups.", ["https://docs.aws.amazon.com/ec2/troubleshoot", "EC2 Admin Guide"])
        ]
    }
]

# Users for interactions
users = [
    "john.doe@org.com", "jane.smith@org.com", "alice.jones@org.com",
    "bob.wilson@org.com", "sarah.brown@org.com", "mike.taylor@org.com",
    "emma.white@org.com", "david.green@org.com", "chris.moore@org.com",
    "lisa.martin@org.com"
]

# Priorities and statuses
priorities = ["Low", "Medium", "High", "Critical"]
priority_weights = [0.3, 0.4, 0.2, 0.1]
statuses = ["New", "In Progress", "Resolved", "Closed"]
status_weights = [0.2, 0.3, 0.4, 0.1]

# Generate random timestamp
def random_timestamp(start_year=2024, end_year=2025):
    start = datetime(start_year, 1, 1, tzinfo=pytz.UTC)
    end = datetime(end_year, 6, 30, 23, 59, 59, tzinfo=pytz.UTC)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return (start + timedelta(seconds=random_seconds)).isoformat()

# Generate interactions
def generate_interactions(incident_id, start_time, num_interactions):
    interactions = []
    for i in range(num_interactions):
        interaction_time = random_timestamp(2024, 2025)
        if i > 0:
            interaction_time = (datetime.fromisoformat(start_time.replace("Z", "+00:00")) + timedelta(minutes=random.randint(15, 120))).isoformat()
        interactions.append({
            "interaction_id": f"INT{int(incident_id[3:]) * 1000 + i + 1:07d}",
            "timestamp": interaction_time,
            "user": random.choice(users),
            "comment": f"Interaction {i+1} for {incident_id}: {random.choice(['Investigating issue', 'Applied fix', 'Awaiting user feedback', 'Escalated to vendor', 'Monitoring performance'])}."
        })
    return interactions

# Generate incidents
incidents = []
for i in range(500):
    tech = random.choice(tech_areas)
    issue = random.choice(tech["issues"])
    status = random.choices(statuses, weights=status_weights)[0]
    start_time = random_timestamp()
    end_time = random_timestamp() if status in ["Resolved", "Closed"] else None
    solution = issue[2] if status in ["Resolved", "Closed"] else None
    num_interactions = random.randint(2, 5)
    
    incident = {
        "incident_id": f"INC{i+1:07d}",
        "priority": random.choices(priorities, weights=priority_weights)[0],
        "status": status,
        "start_time": start_time,
        "end_time": end_time,
        "short_description": f"{tech['name']} - {issue[0]}",
        "long_description": issue[1] + f" Affected {random.randint(10, 2000)} users. Issue reported in {tech['name']} environment.",
        "solution": solution,
        "documents_used": issue[3],
        "interactions": generate_interactions(f"INC{i+1:07d}", start_time, num_interactions)
    }
    incidents.append(incident)

# Save to JSON
with open("servicenow_incidents_full.json", "w") as f:
    json.dump({"incidents": incidents}, f, indent=2)

print("Generated 500 incidents in servicenow_incidents_full.json")