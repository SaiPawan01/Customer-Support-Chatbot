import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

import os
from dotenv import load_dotenv

load_dotenv()

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('EMAIL_API_KEY')

import logging
logger = logging.getLogger(__name__)


def build_conversation_html(messages, conversation_title):
    logger.info("Building conversation HTML for email")

    rows = ""

    for msg in messages:
        is_user = msg["role"] == "user"

        bg = "#e0f2fe" if is_user else "#f1f5f9"
        align = "right" if is_user else "left"
        label = "User" if is_user else "Assistant"

        rows += f"""
        <tr>
            <td align="{align}" style="padding:10px;">
                <table cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="
                            background:{bg};
                            padding:12px 16px;
                            border-radius:12px;
                            font-family: Arial, sans-serif;
                            font-size:14px;
                            color:#111827;
                            max-width:400px;
                        ">
                            <strong style="display:block; margin-bottom:6px; color:#2563eb;">
                                {label}
                            </strong>
                            {msg["content"]}
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """

    return f"""
    <h3 style="color:#111827; font-family: Arial, sans-serif; margin-bottom:20px;">Conversation title: {conversation_title}</h3>
    
    <table width="100%" cellpadding="0" cellspacing="0">
        {rows}
    </table>
    """


def send_email_to_agent(user_id, conversation_id, conversation_title, conversation_history, user_email, user_name):
    logger.info("Sending email to agent for escalation")
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": "pavansaiporapu@gmail.com", "name": "Support Team"}],

        sender={
            "email": "psai9519@gmail.com",
            "name": "Support Bot AI"
        },

        subject=f"Escalation Request - userId: {user_id}  |  ConversationId: {conversation_id}",

        html_content = f"""
                        <div style="background:#f8fafc; padding:20px;">
                            
                            <table width="100%" cellpadding="0" cellspacing="0" 
                                style="max-width:600px; margin:auto; background:white; border-radius:12px; padding:20px;">

                                <tr>
                                    <td style="font-family: Arial, sans-serif;">
                                        
                                        <h2 style="margin-bottom:10px; color:#111827;">
                                            🚨 Escalation Request
                                        </h2>

                                        <p style="color:#6b7280; font-size:14px;">
                                            A user has requested human assistance. Below is the conversation:
                                        </p>

                                        <hr style="margin:20px 0; border:none; border-top:1px solid #e5e7eb;" />

                                        {build_conversation_html(conversation_history, conversation_title)}

                                        <hr style="margin:20px 0; border:none; border-top:1px solid #e5e7eb;" />

                                        <p style="font-size:12px; color:#9ca3af;">
                                            This email was generated automatically by your chatbot system.
                                        </p>

                                    </td>
                                </tr>
                            </table>

                        </div>
                        """,

        reply_to={
            "email": user_email ,
            "name": user_name
        }
    )

    try:
        response = api_instance.send_transac_email(send_smtp_email)
        logger.info("Email sent successfully: %s", response)
        return True

    except ApiException as e:
        logger.error("Error sending email: %s", str(e))
        return False