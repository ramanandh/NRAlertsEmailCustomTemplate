import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Configuration (Can also be set via Lambda Environment Variables) ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "oracleanz.digitalprime@gmail.com"
SENDER_PASSWORD = "ldlb gxuk gvkf kwlo"
RECEIVER_EMAIL = "ramanandh.balaji@gmail.com"

def lambda_handler(event, context):
    try:
        # API Gateway passing a stringified body vs direct test invokes
        if isinstance(event.get('body'), str):
            data = json.loads(event['body'])
        else:
            data = event.get('body', event) if event else {}

        # Extract details from the New Relic payload
        issue_title = data.get('issueTitle', 'No Title')
        priority = data.get('priority', 'UNKNOWN')
        permalink = data.get('issueUrl', '#')
        
        # Target Infrastructure & App Parameters (Primary Priority)
        impacted_app = data.get('impactedApplication', 'N/A')
        impacted_server = data.get('impactedServer', 'N/A')
        
        # Secondary Metadata
        policy_name = data.get('policyName', 'N/A')
        condition_name = data.get('conditionName', issue_title)
        details = data.get('details', 'No additional description provided.')
        incident_id = data.get('incidentId', 'N/A')
        timestamp = data.get('timestamp', 'N/A')
        account_name = data.get('accountName', 'flynas Production')
        runbook_url = data.get('runbookUrl', '#')

        # Logic for Brand/Severity Colors
        if priority == "CRITICAL":
            status_color = "#E30613"
            badge_text = "Critical Incident Active"
            severity_indicator = "🔴 CRITICAL"
        elif priority == "WARNING":
            status_color = "#FF8C00"
            badge_text = "Warning Incident Active"
            severity_indicator = "🟠 WARNING"
        else:
            status_color = "#61BB46"
            badge_text = "Incident Active"
            severity_indicator = f"🟢 {priority}"

        # Flynas Premium HTML Template Integration
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>flynas - New Relic Incident Alert</title>
            <style>
                body, table, td, p, a, li, blockquote {{
                    -webkit-text-size-adjust: 100%;
                    -ms-text-size-adjust: 100%;
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                }}
                table, td {{
                    mso-table-lspace: 0pt;
                    mso-table-rspace: 0pt;
                    border-collapse: collapse !important;
                }}
                body {{
                    height: 100% !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 100% !important;
                    background-color: #f3f5f6;
                }}
                .wrapper {{
                    width: 100%;
                    table-layout: fixed;
                    background-color: #f3f5f6;
                    padding: 24px 0;
                }}
                .main-card {{
                    width: 100%;
                    max-width: 600px;
                    background-color: #ffffff;
                    border-radius: 8px;
                    border: 1px solid #dce2e6;
                    overflow: hidden;
                    box-shadow: 0 4px 16px rgba(13, 31, 23, 0.06);
                }}
                .status-bar-flynas {{ background-color: {status_color}; height: 6px; }}
                
                .badge {{
                    display: inline-block;
                    padding: 5px 10px;
                    font-size: 11px;
                    font-weight: 700;
                    text-transform: uppercase;
                    border-radius: 4px;
                    letter-spacing: 0.5px;
                }}
                .badge-flynas-active {{ background-color: #EBF7E9; color: #1D7E11; }}
                
                .btn-action {{
                    display: inline-block;
                    background-color: #61BB46;
                    color: #ffffff !important;
                    font-weight: 600;
                    font-size: 14px;
                    text-decoration: none;
                    padding: 12px 24px;
                    border-radius: 4px;
                }}
                .meta-label {{
                    font-size: 11px;
                    text-transform: uppercase;
                    font-weight: 700;
                    color: #7A8B99;
                    padding-bottom: 4px;
                    letter-spacing: 0.5px;
                }}
                .meta-value {{
                    font-size: 14px;
                    color: #0F1E2C;
                    font-weight: 500;
                }}
                code {{
                    font-family: "SFMono-Regular", Consolas, Menlo, monospace;
                    background-color: #F1F3F5;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 13px;
                    color: #1D2D3A;
                }}
            </style>
        </head>
        <body>
            <center class="wrapper">
                <table class="main-card" width="100%" cellpadding="0" cellspacing="0" border="0" align="center">
                    <tr>
                        <td class="status-bar-flynas"></td>
                    </tr>
                    <tr>
                        <td style="padding: 24px 32px 16px 32px; background-color: #0F1E2C; border-bottom: 1px solid #1A2E3F;">
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td align="left" valign="middle">
                                        <img src="https://www.flynas.com/images/flynas-logo-en.png" alt="flynas" width="120" style="display: block; border: 0; max-height: 45px; width: auto; height: auto;" />
                                    </td>
                                    <td align="right" valign="middle">
                                        <span style="font-size: 11px; font-weight: 700; letter-spacing: 1px; color: #61BB46; text-transform: uppercase;">
                                            New Relic Alert Engine
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 28px 32px 20px 32px;">
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td style="padding-bottom: 12px;">
                                        <span class="badge badge-flynas-active">{badge_text}</span>
                                        <span style="font-size: 14px; color: #7A8B99; margin-left: 10px; font-weight: 500;">
                                            Policy: <strong>{policy_name}</strong>
                                        </span>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        <h1 style="font-size: 22px; font-weight: 700; color: #0F1E2C; line-height: 1.3; margin: 0;">
                                            {condition_name}
                                        </h1>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0 32px 24px 32px;">
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td style="background-color: #F7FAF6; border-left: 4px solid {status_color}; padding: 16px; border-radius: 0 6px 6px 0;">
                                        <p style="font-size: 14px; color: #1D2D3A; line-height: 1.5; margin: 0;">
                                            <strong>Details:</strong> {details}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding: 0 32px 24px 32px;">
                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top: 1px solid #E6EAEF; border-bottom: 1px solid #E6EAEF; padding: 18px 0;">
                                <tr>
                                    <td width="50%" valign="top" style="padding-bottom: 16px;">
                                        <p class="meta-label">Impacted Application</p>
                                        <p class="meta-value" style="color: #61BB46; font-weight: 600;">{impacted_app}</p>
                                    </td>
                                    <td width="50%" valign="top" style="padding-bottom: 16px;">
                                        <p class="meta-label">Impacted Server</p>
                                        <p class="meta-value"><code>{impacted_server}</code></p>
                                    </td>
                                </tr>
                                <tr>
                                    <td width="50%" valign="top" style="padding-bottom: 16px;">
                                        <p class="meta-label">Incident ID</p>
                                        <p class="meta-value">#{incident_id}</p>
                                    </td>
                                    <td width="50%" valign="top" style="padding-bottom: 16px;">
                                        <p class="meta-label">Trigger Time (UTC)</p>
                                        <p class="meta-value">{timestamp}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td width="50%" valign="top">
                                        <p class="meta-label">Severity Level</p>
                                        <p class="meta-value" style="font-weight: 600;">{severity_indicator}</p>
                                    </td>
                                    <td width="50%" valign="top">
                                        <p class="meta-label">Account</p>
                                        <p class="meta-value">{account_name}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding: 0 32px 28px 32px;">
                            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                <tr>
                                    <td>
                                        <p class="meta-label" style="padding-bottom: 6px;">Associated Runbook</p>
                                        <p style="font-size: 13px; color: #4A5661; line-height: 1.4; margin: 0;">
                                            📋 <a href="{run