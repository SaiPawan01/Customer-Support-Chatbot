import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import os


configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv('EMAIL_API_KEY')

import logging

logger = logging.getLogger(__name__)

def send_otp(email, otp):
    logger.info("Attempting to send OTP to email: %s", email)

    try:
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        html_content = f"""<div style="background:#f8fafc; padding:20px;">
            <table width="100%" cellpadding="0" cellspacing="0" 
                style="max-width:600px; margin:auto; background:white; border-radius:12px; padding:20px;">
                <tr>
                    <td style="font-family: Arial, sans-serif;">
                        <h2 style="color:#111827;">🔐 Verify Your Email</h2>
                        <p style="color:#6b7280;">
                            Use the OTP below to complete verification.
                        </p>
                        <div style="text-align:center; margin:30px 0;">
                            <span style="background:#111827; color:white; font-size:28px;
                                padding:12px 24px; border-radius:8px;">
                                {otp}
                            </span>
                        </div>
                    </td>
                </tr>
            </table>
        </div>"""

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email}],
            sender={
                "email": "psai9519@gmail.com", 
                "name": "Support Bot AI"
            },
            subject="Email Verification - Support Bot AI",
            html_content=html_content
        )

        response = api_instance.send_transac_email(send_smtp_email)

        return True, response

    except ApiException as e:
        logger.error("API Exception while sending OTP email: %s", str(e))
        return False, str(e)

    except Exception as e:
        logger.error("Unexpected error:", exc_info=True)
        return False, str(e)
    
