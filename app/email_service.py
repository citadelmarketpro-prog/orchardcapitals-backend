"""
Email service for Orchard Capitals
Handles all email sending functionality using SMTP
"""

import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Shared design constants
# ---------------------------------------------------------------------------
_BRAND_ORANGE  = "#c14e2a"
_BRAND_DARK    = "#a8401f"
_HEADER_BG     = "#1a0a04"
_BODY_BG       = "#f0f2f5"
_CARD_BG       = "#ffffff"
_TEXT_PRIMARY  = "#111827"
_TEXT_MUTED    = "#6b7280"
_BORDER        = "#e5e7eb"
_ACCENT_LIGHT  = "#fff4ee"


def _base_styles():
    """Return the shared inline-safe CSS block used by every template."""
    return f"""
        <style>
            @media only screen and (max-width: 600px) {{
                .email-container {{ width: 100% !important; }}
                .content-padding {{ padding: 24px 16px !important; }}
                .header-padding {{ padding: 32px 16px !important; }}
            }}
            body {{
                margin: 0; padding: 0;
                background-color: {_BODY_BG};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                -webkit-text-size-adjust: 100%;
                -ms-text-size-adjust: 100%;
            }}
            table {{ border-collapse: collapse; }}
            img {{ border: 0; display: block; }}
            a {{ color: {_BRAND_ORANGE}; text-decoration: none; }}
            .preheader {{
                display: none !important; visibility: hidden; mso-hide: all;
                font-size: 1px; line-height: 1px; max-height: 0; max-width: 0;
                opacity: 0; overflow: hidden;
            }}
        </style>
    """


def _header(title, subtitle="", preheader=""):
    """Render the dark branded email header."""
    subtitle_html = f'<p style="margin:8px 0 0; font-size:14px; color:#9ca3af; font-weight:400; letter-spacing:0.5px;">{subtitle}</p>' if subtitle else ""
    pre = f'<span class="preheader">{preheader}</span>' if preheader else ""
    return f"""
    {pre}
    <!-- Header -->
    <tr>
      <td align="center" style="background-color:{_HEADER_BG}; padding:0;">
        <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td class="header-padding" style="padding:40px 40px 36px;">
              <!-- Wordmark -->
              <table cellpadding="0" cellspacing="0" border="0" width="100%">
                <tr>
                  <td>
                    <table cellpadding="0" cellspacing="0" border="0">
                      <tr>
                        <td style="background-color:{_BRAND_ORANGE}; border-radius:6px; width:8px; height:28px;">&nbsp;</td>
                        <td style="padding-left:10px; vertical-align:middle;">
                          <span style="font-size:18px; font-weight:700; color:#ffffff; letter-spacing:-0.3px;">ORCHARD</span>
                          <span style="font-size:18px; font-weight:300; color:{_BRAND_ORANGE}; letter-spacing:-0.3px;">&nbsp;CAPITALS</span>
                          <span style="font-size:11px; font-weight:500; color:#6b7280; letter-spacing:2px; display:block; margin-top:1px;">INVESTMENT PLATFORM</span>
                        </td>
                      </tr>
                    </table>
                  </td>
                  <td align="right" valign="middle">
                    <span style="font-size:11px; color:#374151; background-color:#2d1508; padding:4px 10px; border-radius:20px; letter-spacing:1px; font-weight:600;">SECURE</span>
                  </td>
                </tr>
              </table>
              <!-- Divider -->
              <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:28px;">
                <tr><td style="height:1px; background:linear-gradient(to right, {_BRAND_ORANGE}, #7c2d12, transparent);"></td></tr>
              </table>
              <!-- Title -->
              <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:28px;">
                <tr>
                  <td>
                    <p style="margin:0; font-size:26px; font-weight:700; color:#ffffff; line-height:1.2; letter-spacing:-0.5px;">{title}</p>
                    {subtitle_html}
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    """


def _footer():
    """Render the shared branded footer."""
    year = timezone.now().year
    return f"""
    <!-- Footer -->
    <tr>
      <td align="center" style="background-color:{_HEADER_BG}; padding:0;">
        <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td style="padding:32px 40px; border-top:1px solid #2d1508;">
              <table cellpadding="0" cellspacing="0" border="0" width="100%">
                <tr>
                  <td align="center">
                    <p style="margin:0 0 6px; font-size:13px; font-weight:600; color:#9ca3af; letter-spacing:1px;">ORCHARD CAPITALS</p>
                    <p style="margin:0 0 16px; font-size:11px; color:#4b5563;">Professional Investment &amp; Trading Platform</p>
                    <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto 16px;">
                      <tr>
                        <td style="padding:0 10px;">
                          <a href="{settings.FRONTEND_URL}/privacy-policy" style="font-size:11px; color:#6b7280; text-decoration:none;">Privacy Policy</a>
                        </td>
                        <td style="color:#374151; font-size:11px;">|</td>
                        <td style="padding:0 10px;">
                          <a href="{settings.FRONTEND_URL}/terms-of-service" style="font-size:11px; color:#6b7280; text-decoration:none;">Terms of Service</a>
                        </td>
                        <td style="color:#374151; font-size:11px;">|</td>
                        <td style="padding:0 10px;">
                          <a href="{settings.FRONTEND_URL}/support" style="font-size:11px; color:#6b7280; text-decoration:none;">Support</a>
                        </td>
                      </tr>
                    </table>
                    <p style="margin:0; font-size:11px; color:#374151; line-height:1.6;">
                      &copy; {year} Orchard Capitals. All rights reserved.<br>
                      This is an automated message &mdash; please do not reply directly to this email.
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    """


def _info_row(label, value, value_color=None):
    """Render a single label/value table row."""
    color_style = f'color:{value_color}; font-weight:600;' if value_color else f'color:{_TEXT_PRIMARY};'
    return f"""
    <tr>
      <td style="padding:11px 0; border-bottom:1px solid {_BORDER}; font-size:13px; color:{_TEXT_MUTED}; width:42%; vertical-align:top;">{label}</td>
      <td style="padding:11px 0 11px 16px; border-bottom:1px solid {_BORDER}; font-size:13px; {color_style} text-align:right; word-break:break-all;">{value}</td>
    </tr>
    """


def _section_heading(text, color=None):
    color = color or _BRAND_ORANGE
    return f"""
    <p style="margin:0 0 12px; font-size:11px; font-weight:700; color:{color}; letter-spacing:1.5px; text-transform:uppercase;">{text}</p>
    """


def _card(content, padding="28px 32px", border_left=None):
    """Wrap content in a white card."""
    border = f"border-left:3px solid {border_left};" if border_left else ""
    return f"""
    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:{_CARD_BG}; border-radius:8px; {border} margin-bottom:16px;">
      <tr><td style="padding:{padding};">{content}</td></tr>
    </table>
    """


def generate_verification_code():
    """Generate a random 4-digit verification code"""
    return str(random.randint(1000, 9999))


def send_email(to_email, subject, html_content):
    """Send HTML email using SMTP"""
    try:
        smtp_host     = settings.EMAIL_HOST
        smtp_port     = settings.EMAIL_PORT
        smtp_username = settings.EMAIL_HOST_USER
        smtp_password = settings.EMAIL_HOST_PASSWORD
        from_email    = settings.DEFAULT_FROM_EMAIL

        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From']    = from_email
        message['To']      = to_email

        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)

        if settings.EMAIL_USE_TLS:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)

        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, message.as_string())
        server.quit()

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


# ---------------------------------------------------------------------------
# 1. Welcome Email
# ---------------------------------------------------------------------------

def send_welcome_email(user):
    subject = "Your Orchard Capitals Account Is Ready"
    name = user.first_name or "Investor"

    steps = [
        ("01", "Complete KYC Verification",  "Submit your identification documents to unlock full investment capabilities and higher deposit limits."),
        ("02", "Fund Your Account",           "Make your first deposit and start building your portfolio with access to global markets."),
        ("03", "Copy a Pro Trader",           "Select from our curated roster of verified traders and mirror their positions automatically."),
        ("04", "Monitor &amp; Grow",          "Track your performance in real time, manage risk, and scale your investments with confidence."),
    ]

    steps_html = ""
    for num, title, desc in steps:
        steps_html += f"""
        <tr>
          <td style="padding:16px 0; border-bottom:1px solid {_BORDER}; vertical-align:top;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td style="width:36px; vertical-align:top; padding-top:2px;">
                  <span style="display:inline-block; width:28px; height:28px; background-color:{_BRAND_ORANGE}; border-radius:50%; text-align:center; line-height:28px; font-size:11px; font-weight:700; color:#fff;">{num}</span>
                </td>
                <td style="padding-left:14px; vertical-align:top;">
                  <p style="margin:0 0 4px; font-size:14px; font-weight:600; color:{_TEXT_PRIMARY};">{title}</p>
                  <p style="margin:0; font-size:13px; color:{_TEXT_MUTED}; line-height:1.6;">{desc}</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{subject}</title>
      {_base_styles()}
    </head>
    <body>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG}; padding:32px 0;">
      <tr><td align="center">
        <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG};">

          {_header("Welcome to Orchard Capitals", "Your account has been successfully created.", "Welcome! Your investment journey starts here.")}

          <!-- Body -->
          <tr>
            <td align="center" style="background-color:{_BODY_BG}; padding:0;">
              <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td class="content-padding" style="padding:32px 40px;">

                    <!-- Greeting card -->
                    {_card(f"""
                    <p style="margin:0 0 10px; font-size:22px; font-weight:700; color:{_TEXT_PRIMARY};">Hello, {name}.</p>
                    <p style="margin:0; font-size:15px; color:{_TEXT_MUTED}; line-height:1.7;">
                      Welcome to <strong style="color:{_TEXT_PRIMARY};">Orchard Capitals</strong> — a professional-grade investment platform giving you access to global markets, expert copy trading, and real-time market intelligence. We're glad to have you on board.
                    </p>
                    """, padding="28px 32px")}

                    <!-- Account details strip -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:{_ACCENT_LIGHT}; border:1px solid #fbd0b8; border-radius:8px; margin-bottom:16px;">
                      <tr>
                        <td style="padding:18px 24px;">
                          <table cellpadding="0" cellspacing="0" border="0" width="100%">
                            <tr>
                              <td>
                                <p style="margin:0 0 2px; font-size:11px; font-weight:600; color:{_BRAND_ORANGE}; letter-spacing:1px; text-transform:uppercase;">Registered Email</p>
                                <p style="margin:0; font-size:14px; font-weight:600; color:{_TEXT_PRIMARY};">{user.email}</p>
                              </td>
                              <td align="right">
                                <span style="background-color:{_BRAND_ORANGE}; color:#fff; font-size:11px; font-weight:700; padding:4px 12px; border-radius:20px; letter-spacing:0.5px;">ACTIVE</span>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>

                    <!-- Steps -->
                    {_card(f"""
                    {_section_heading("Getting Started — 4 Simple Steps")}
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                      {steps_html}
                    </table>
                    """, padding="28px 32px")}

                    <!-- CTA -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top:8px;">
                      <tr>
                        <td align="center" style="padding:8px 0 24px;">
                          <a href="{settings.FRONTEND_URL}/dashboard" style="display:inline-block; background-color:{_BRAND_ORANGE}; color:#ffffff; font-size:15px; font-weight:600; text-decoration:none; padding:14px 40px; border-radius:6px; letter-spacing:0.3px;">
                            Go to Dashboard &rarr;
                          </a>
                        </td>
                      </tr>
                    </table>

                    <p style="margin:0; font-size:13px; color:{_TEXT_MUTED}; text-align:center; line-height:1.7;">
                      Questions? Our support team is available 24/7.<br>
                      <a href="{settings.FRONTEND_URL}/support" style="color:{_BRAND_ORANGE}; font-weight:600;">Contact Support</a>
                    </p>

                  </td>
                </tr>
              </table>
            </td>
          </tr>

          {_footer()}

        </table>
      </td></tr>
    </table>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)


# ---------------------------------------------------------------------------
# 2. Email Verification Code
# ---------------------------------------------------------------------------

def send_verification_code_email(user, code):
    subject = "Your Email Verification Code — Orchard Capitals"
    name = user.first_name or "Investor"

    digits_html = "".join(
        f'<td style="width:52px; height:64px; background-color:#2d1508; border:2px solid #3d1f0a; border-radius:8px; text-align:center; vertical-align:middle; font-size:30px; font-weight:700; color:{_BRAND_ORANGE}; font-family:\'Courier New\',monospace; letter-spacing:0;">{d}</td>'
        f'<td style="width:8px;"></td>'
        for d in str(code)
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{subject}</title>
      {_base_styles()}
    </head>
    <body>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG}; padding:32px 0;">
      <tr><td align="center">
        <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG};">

          {_header("Email Verification", "Complete your account setup.", "Your verification code is inside.")}

          <!-- Body -->
          <tr>
            <td align="center" style="background-color:{_BODY_BG}; padding:0;">
              <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td class="content-padding" style="padding:32px 40px;">

                    {_card(f"""
                    <p style="margin:0 0 6px; font-size:16px; font-weight:600; color:{_TEXT_PRIMARY};">Hello, {name}.</p>
                    <p style="margin:0; font-size:14px; color:{_TEXT_MUTED}; line-height:1.7;">
                      To verify your email address and activate your Orchard Capitals account, enter the code below on the verification page.
                    </p>
                    """, padding="28px 32px")}

                    <!-- Code display -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:{_HEADER_BG}; border-radius:10px; margin-bottom:16px;">
                      <tr>
                        <td align="center" style="padding:36px 24px 28px;">
                          <p style="margin:0 0 24px; font-size:11px; font-weight:600; color:#6b7280; letter-spacing:2px; text-transform:uppercase;">Verification Code</p>
                          <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto;">
                            <tr>{digits_html}</tr>
                          </table>
                          <p style="margin:24px 0 0; font-size:12px; color:#6b7280;">
                            &#8987;&nbsp; Expires in <strong style="color:#f59e0b;">10 minutes</strong>
                          </p>
                        </td>
                      </tr>
                    </table>

                    <!-- Security notice -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#fffbeb; border:1px solid #fcd34d; border-radius:8px; margin-bottom:16px;">
                      <tr>
                        <td style="padding:16px 20px;">
                          <p style="margin:0 0 4px; font-size:12px; font-weight:700; color:#b45309; letter-spacing:0.5px;">&#9888; SECURITY NOTICE</p>
                          <p style="margin:0; font-size:13px; color:#78350f; line-height:1.6;">
                            Never share this code with anyone. Orchard Capitals staff will <strong>never</strong> request your verification code via phone, chat, or email.
                          </p>
                        </td>
                      </tr>
                    </table>

                    <p style="margin:0; font-size:13px; color:{_TEXT_MUTED}; text-align:center; line-height:1.7;">
                      If you didn't create an account, you can safely ignore this email.<br>
                      <a href="{settings.FRONTEND_URL}/support" style="color:{_BRAND_ORANGE};">Contact Support</a> if you have concerns.
                    </p>

                  </td>
                </tr>
              </table>
            </td>
          </tr>

          {_footer()}

        </table>
      </td></tr>
    </table>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)


# ---------------------------------------------------------------------------
# 3. Two-Factor Authentication Code
# ---------------------------------------------------------------------------

def send_2fa_code_email(user, code):
    subject = "Login Verification Code — Orchard Capitals"
    name = user.first_name or "Investor"
    timestamp = timezone.now().strftime('%B %d, %Y at %I:%M %p UTC')

    digits_html = "".join(
        f'<td style="width:52px; height:64px; background-color:#2d1508; border:2px solid #7c2d12; border-radius:8px; text-align:center; vertical-align:middle; font-size:30px; font-weight:700; color:#fb923c; font-family:\'Courier New\',monospace; letter-spacing:0;">{d}</td>'
        f'<td style="width:8px;"></td>'
        for d in str(code)
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{subject}</title>
      {_base_styles()}
    </head>
    <body>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG}; padding:32px 0;">
      <tr><td align="center">
        <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG};">

          {_header("Two-Factor Authentication", "A login attempt was detected on your account.", "Your 2FA login code is inside.")}

          <!-- Body -->
          <tr>
            <td align="center" style="background-color:{_BODY_BG}; padding:0;">
              <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td class="content-padding" style="padding:32px 40px;">

                    {_card(f"""
                    <p style="margin:0 0 6px; font-size:16px; font-weight:600; color:{_TEXT_PRIMARY};">Hello, {name}.</p>
                    <p style="margin:0; font-size:14px; color:{_TEXT_MUTED}; line-height:1.7;">
                      A sign-in request was made to your Orchard Capitals account. Use the code below to complete authentication.
                    </p>
                    """, padding="28px 32px")}

                    <!-- Code display -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:{_HEADER_BG}; border-radius:10px; margin-bottom:16px;">
                      <tr>
                        <td align="center" style="padding:36px 24px 28px;">
                          <p style="margin:0 0 24px; font-size:11px; font-weight:600; color:#6b7280; letter-spacing:2px; text-transform:uppercase;">2FA Login Code</p>
                          <table cellpadding="0" cellspacing="0" border="0" style="margin:0 auto;">
                            <tr>{digits_html}</tr>
                          </table>
                          <p style="margin:24px 0 0; font-size:12px; color:#6b7280;">
                            &#8987;&nbsp; Expires in <strong style="color:#f59e0b;">10 minutes</strong>
                          </p>
                        </td>
                      </tr>
                    </table>

                    <!-- Login detail strip -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:{_CARD_BG}; border-radius:8px; margin-bottom:16px;">
                      <tr>
                        <td style="padding:20px 24px;">
                          {_section_heading("Login Attempt Details", "#ea580c")}
                          <table cellpadding="0" cellspacing="0" border="0" width="100%">
                            {_info_row("Email", user.email)}
                            {_info_row("Time", timestamp)}
                          </table>
                        </td>
                      </tr>
                    </table>

                    <!-- Alert box -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#fff1f2; border:1px solid #fda4af; border-radius:8px; margin-bottom:16px;">
                      <tr>
                        <td style="padding:16px 20px;">
                          <p style="margin:0 0 4px; font-size:12px; font-weight:700; color:#be123c; letter-spacing:0.5px;">&#128680; DIDN'T ATTEMPT TO LOG IN?</p>
                          <p style="margin:0; font-size:13px; color:#9f1239; line-height:1.6;">
                            Immediately <a href="{settings.FRONTEND_URL}/settings" style="color:#be123c; font-weight:600;">change your password</a> and contact our security team. Do not share this code with anyone.
                          </p>
                        </td>
                      </tr>
                    </table>

                    <p style="margin:0; font-size:13px; color:{_TEXT_MUTED}; text-align:center;">
                      <a href="{settings.FRONTEND_URL}/support" style="color:{_BRAND_ORANGE};">Contact Support</a> &nbsp;|&nbsp;
                      <a href="{settings.FRONTEND_URL}/settings" style="color:{_BRAND_ORANGE};">Account Settings</a>
                    </p>

                  </td>
                </tr>
              </table>
            </td>
          </tr>

          {_footer()}

        </table>
      </td></tr>
    </table>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)


def is_code_valid(user):
    """Check if verification code is still valid (within 10 minutes)"""
    if not user.code_created_at or not user.verification_code:
        return False

    expiry_time = user.code_created_at + timedelta(minutes=10)
    return timezone.now() < expiry_time


# ---------------------------------------------------------------------------
# 4. Password Reset Email
# ---------------------------------------------------------------------------

def send_password_reset_email(user, token, uid):
    reset_link = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
    subject = "Password Reset Request — Orchard Capitals"
    name = user.first_name or "Investor"
    timestamp = timezone.now().strftime('%B %d, %Y at %I:%M %p UTC')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{subject}</title>
      {_base_styles()}
    </head>
    <body>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG}; padding:32px 0;">
      <tr><td align="center">
        <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG};">

          {_header("Password Reset", "We received a request to reset your password.", "Reset your Orchard Capitals password.")}

          <!-- Body -->
          <tr>
            <td align="center" style="background-color:{_BODY_BG}; padding:0;">
              <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td class="content-padding" style="padding:32px 40px;">

                    {_card(f"""
                    <p style="margin:0 0 6px; font-size:16px; font-weight:600; color:{_TEXT_PRIMARY};">Hello, {name}.</p>
                    <p style="margin:0; font-size:14px; color:{_TEXT_MUTED}; line-height:1.7;">
                      We received a password reset request for the Orchard Capitals account associated with <strong style="color:{_TEXT_PRIMARY};">{user.email}</strong>.
                      Click the button below to choose a new password. This link is valid for <strong>1 hour</strong>.
                    </p>
                    """, padding="28px 32px")}

                    <!-- CTA -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:{_HEADER_BG}; border-radius:10px; margin-bottom:16px;">
                      <tr>
                        <td align="center" style="padding:40px 32px;">
                          <a href="{reset_link}" style="display:inline-block; background-color:{_BRAND_ORANGE}; color:#ffffff; font-size:15px; font-weight:600; text-decoration:none; padding:16px 48px; border-radius:6px; letter-spacing:0.3px;">
                            Reset My Password &rarr;
                          </a>
                          <p style="margin:20px 0 0; font-size:12px; color:#6b7280;">
                            &#8987;&nbsp; Link expires at <strong style="color:#f59e0b;">{timestamp}</strong> + 1 hour
                          </p>
                        </td>
                      </tr>
                    </table>

                    <!-- Fallback link -->
                    {_card(f"""
                    {_section_heading("Button not working? Copy this link into your browser:")}
                    <p style="margin:0; font-size:12px; color:{_TEXT_MUTED}; word-break:break-all; background-color:{_BODY_BG}; padding:12px 14px; border-radius:6px; border:1px solid {_BORDER}; font-family:'Courier New',monospace; line-height:1.6;">{reset_link}</p>
                    """, padding="24px 28px")}

                    <!-- Warning -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#fffbeb; border:1px solid #fcd34d; border-radius:8px; margin-bottom:24px;">
                      <tr>
                        <td style="padding:16px 20px;">
                          <p style="margin:0 0 4px; font-size:12px; font-weight:700; color:#b45309; letter-spacing:0.5px;">&#9888; SECURITY NOTICE</p>
                          <p style="margin:0; font-size:13px; color:#78350f; line-height:1.6;">
                            If you did not request a password reset, ignore this email — your account remains secure.
                            For any concerns, <a href="{settings.FRONTEND_URL}/support" style="color:#b45309; font-weight:600;">contact our support team</a> immediately.
                          </p>
                        </td>
                      </tr>
                    </table>

                  </td>
                </tr>
              </table>
            </td>
          </tr>

          {_footer()}

        </table>
      </td></tr>
    </table>
    </body>
    </html>
    """

    return send_email(user.email, subject, html_content)


# ---------------------------------------------------------------------------
# 5. Admin — Payment Intent Notification
# ---------------------------------------------------------------------------

def send_admin_payment_intent_notification(user, currency, dollar_amount, currency_unit):
    admin_email = settings.ADMIN_NOTIFICATION_EMAIL if hasattr(settings, 'ADMIN_NOTIFICATION_EMAIL') else settings.EMAIL_HOST_USER
    subject = f"[DEPOSIT INTENT] {user.email} — ${dollar_amount}"
    timestamp = timezone.now().strftime('%B %d, %Y at %I:%M %p UTC')
    kyc_status = '&#9989; Verified' if user.is_verified else ('&#9203; Pending' if user.has_submitted_kyc else '&#10060; Not Submitted')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{subject}</title>
      {_base_styles()}
    </head>
    <body>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG}; padding:32px 0;">
      <tr><td align="center">
        <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG};">

          {_header("Deposit Intent Initiated", "A user has entered a deposit amount.", "A user is about to make a deposit.")}

          <tr>
            <td align="center" style="background-color:{_BODY_BG}; padding:0;">
              <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td class="content-padding" style="padding:32px 40px;">

                    <!-- Amount hero -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:{_HEADER_BG}; border-radius:10px; margin-bottom:16px; border-left:4px solid {_BRAND_ORANGE};">
                      <tr>
                        <td style="padding:28px 32px;">
                          <p style="margin:0 0 4px; font-size:11px; font-weight:600; color:#6b7280; letter-spacing:1.5px; text-transform:uppercase;">Intended Deposit Amount</p>
                          <p style="margin:0 0 6px; font-size:40px; font-weight:700; color:{_BRAND_ORANGE}; line-height:1.1;">${dollar_amount}</p>
                          <p style="margin:0; font-size:14px; color:#9ca3af;">{currency_unit} {currency}</p>
                        </td>
                        <td align="right" valign="middle" style="padding:28px 32px;">
                          <span style="display:inline-block; background-color:{_ACCENT_LIGHT}; color:{_BRAND_DARK}; font-size:11px; font-weight:700; padding:6px 14px; border-radius:20px; letter-spacing:0.5px;">INTENT</span>
                        </td>
                      </tr>
                    </table>

                    <!-- Info notice -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:{_ACCENT_LIGHT}; border:1px solid #fbd0b8; border-radius:8px; margin-bottom:16px;">
                      <tr>
                        <td style="padding:14px 20px;">
                          <p style="margin:0; font-size:13px; color:{_BRAND_DARK}; line-height:1.6;">
                            &#128276; The user has proceeded past the amount step. A receipt upload is expected shortly. The transaction record will be created upon receipt submission.
                          </p>
                        </td>
                      </tr>
                    </table>

                    <!-- Deposit details -->
                    {_card(f"""
                    {_section_heading("Deposit Details")}
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                      {_info_row("Currency", currency)}
                      {_info_row("Crypto Units", f"{currency_unit} {currency}")}
                      {_info_row("Initiated At", timestamp)}
                      {_info_row("Receipt", '<span style="color:#9ca3af;">Pending upload</span>')}
                    </table>
                    """, padding="24px 28px", border_left=_BRAND_ORANGE)}

                    <!-- User details -->
                    {_card(f"""
                    {_section_heading("Account Holder", "#3b82f6")}
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                      {_info_row("Full Name", f"{user.first_name} {user.last_name}")}
                      {_info_row("Email", user.email)}
                      {_info_row("Account ID", user.account_id or "N/A")}
                      {_info_row("Current Balance", f"${user.balance}")}
                      {_info_row("KYC Status", kyc_status)}
                    </table>
                    """, padding="24px 28px", border_left="#3b82f6")}

                  </td>
                </tr>
              </table>
            </td>
          </tr>

          {_footer()}

        </table>
      </td></tr>
    </table>
    </body>
    </html>
    """

    return send_email(admin_email, subject, html_content)


# ---------------------------------------------------------------------------
# 6. Admin — New Deposit Notification
# ---------------------------------------------------------------------------

def send_admin_deposit_notification(user, transaction):
    admin_email = settings.ADMIN_NOTIFICATION_EMAIL if hasattr(settings, 'ADMIN_NOTIFICATION_EMAIL') else settings.EMAIL_HOST_USER
    subject = f"[DEPOSIT] {user.email} — ${transaction.amount}"
    kyc_status = '&#9989; Verified' if user.is_verified else ('&#9203; Pending' if user.has_submitted_kyc else '&#10060; Not Submitted')
    receipt_html = (
        f'<a href="{transaction.receipt.url}" target="_blank" style="color:{_BRAND_ORANGE}; font-weight:600;">View Receipt &rarr;</a>'
        if transaction.receipt else '<span style="color:#9ca3af;">Not uploaded</span>'
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{subject}</title>
      {_base_styles()}
    </head>
    <body>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG}; padding:32px 0;">
      <tr><td align="center">
        <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG};">

          {_header("New Deposit Request", "Action required — pending approval.", "A deposit is awaiting your review.")}

          <!-- Body -->
          <tr>
            <td align="center" style="background-color:{_BODY_BG}; padding:0;">
              <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td class="content-padding" style="padding:32px 40px;">

                    <!-- Amount hero -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:{_HEADER_BG}; border-radius:10px; margin-bottom:16px; border-left:4px solid {_BRAND_ORANGE};">
                      <tr>
                        <td style="padding:28px 32px;">
                          <p style="margin:0 0 4px; font-size:11px; font-weight:600; color:#6b7280; letter-spacing:1.5px; text-transform:uppercase;">Deposit Amount</p>
                          <p style="margin:0 0 6px; font-size:40px; font-weight:700; color:{_BRAND_ORANGE}; line-height:1.1;">${transaction.amount}</p>
                          <p style="margin:0; font-size:14px; color:#9ca3af;">{transaction.unit} {transaction.currency}</p>
                        </td>
                        <td align="right" valign="middle" style="padding:28px 32px;">
                          <span style="display:inline-block; background-color:#fef3c7; color:#b45309; font-size:11px; font-weight:700; padding:6px 14px; border-radius:20px; letter-spacing:0.5px;">PENDING</span>
                        </td>
                      </tr>
                    </table>

                    <!-- Transaction details -->
                    {_card(f"""
                    {_section_heading("Transaction Details")}
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                      {_info_row("Reference ID", transaction.reference)}
                      {_info_row("Date &amp; Time", transaction.created_at.strftime('%B %d, %Y at %I:%M %p UTC'))}
                      {_info_row("Currency", transaction.currency)}
                      {_info_row("Units", f"{transaction.unit} {transaction.currency}")}
                      {_info_row("Receipt", receipt_html)}
                    </table>
                    """, padding="24px 28px", border_left=_BRAND_ORANGE)}

                    <!-- User details -->
                    {_card(f"""
                    {_section_heading("Account Holder", "#3b82f6")}
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                      {_info_row("Full Name", f"{user.first_name} {user.last_name}")}
                      {_info_row("Email", user.email)}
                      {_info_row("Account ID", user.account_id or "N/A")}
                      {_info_row("Current Balance", f"${user.balance}")}
                      {_info_row("KYC Status", kyc_status)}
                    </table>
                    """, padding="24px 28px", border_left="#3b82f6")}

                    <!-- Action prompt -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#fffbeb; border:1px solid #fcd34d; border-radius:8px; margin-bottom:24px;">
                      <tr>
                        <td style="padding:16px 20px;">
                          <p style="margin:0; font-size:13px; color:#78350f; line-height:1.6;">
                            <strong>&#9888; Action Required:</strong> Please log in to the admin dashboard to review the payment receipt and update the transaction status accordingly.
                          </p>
                        </td>
                      </tr>
                    </table>

                  </td>
                </tr>
              </table>
            </td>
          </tr>

          {_footer()}

        </table>
      </td></tr>
    </table>
    </body>
    </html>
    """

    return send_email(admin_email, subject, html_content)


# ---------------------------------------------------------------------------
# 7. Admin — New Withdrawal Notification
# ---------------------------------------------------------------------------

def send_admin_withdrawal_notification(user, transaction, payment_method=None):
    admin_email = settings.ADMIN_NOTIFICATION_EMAIL if hasattr(settings, 'ADMIN_NOTIFICATION_EMAIL') else settings.EMAIL_HOST_USER
    subject = f"[WITHDRAWAL] {user.email} — ${transaction.amount}"

    payment_method_info = "Not specified"
    payment_address     = "N/A"
    bank_row            = ""

    if payment_method:
        payment_method_info = payment_method.method_type
        payment_address     = payment_method.address or payment_method.bank_account_number or "N/A"
        if payment_method.bank_name:
            bank_row = _info_row("Bank Name", payment_method.bank_name)

    kyc_status = '&#9989; Verified' if user.is_verified else ('&#9203; Pending' if user.has_submitted_kyc else '&#10060; Not Submitted')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{subject}</title>
      {_base_styles()}
    </head>
    <body>
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG}; padding:32px 0;">
      <tr><td align="center">
        <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0" style="background-color:{_BODY_BG};">

          {_header("Withdrawal Request", "Urgent — user balance has been deducted.", "A withdrawal is awaiting processing.")}

          <!-- Body -->
          <tr>
            <td align="center" style="background-color:{_BODY_BG}; padding:0;">
              <table width="600" class="email-container" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td class="content-padding" style="padding:32px 40px;">

                    <!-- Amount hero -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:{_HEADER_BG}; border-radius:10px; margin-bottom:16px; border-left:4px solid #ef4444;">
                      <tr>
                        <td style="padding:28px 32px;">
                          <p style="margin:0 0 4px; font-size:11px; font-weight:600; color:#6b7280; letter-spacing:1.5px; text-transform:uppercase;">Withdrawal Amount</p>
                          <p style="margin:0 0 6px; font-size:40px; font-weight:700; color:#ef4444; line-height:1.1;">${transaction.amount}</p>
                          <p style="margin:0; font-size:14px; color:#9ca3af;">Balance after deduction: <strong style="color:#f9fafb;">${user.balance}</strong></p>
                        </td>
                        <td align="right" valign="middle" style="padding:28px 32px;">
                          <span style="display:inline-block; background-color:#fee2e2; color:#b91c1c; font-size:11px; font-weight:700; padding:6px 14px; border-radius:20px; letter-spacing:0.5px;">PENDING</span>
                        </td>
                      </tr>
                    </table>

                    <!-- Urgent notice -->
                    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#fff1f2; border:1px solid #fda4af; border-radius:8px; margin-bottom:16px;">
                      <tr>
                        <td style="padding:16px 20px;">
                          <p style="margin:0; font-size:13px; color:#9f1239; line-height:1.6;">
                            <strong>&#128680; Urgent:</strong> The user's balance has already been deducted. Please process this withdrawal promptly, or reverse the transaction if unable to complete.
                          </p>
                        </td>
                      </tr>
                    </table>

                    <!-- Transaction details -->
                    {_card(f"""
                    {_section_heading("Transaction Details", "#ef4444")}
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                      {_info_row("Reference ID", transaction.reference)}
                      {_info_row("Date &amp; Time", transaction.created_at.strftime('%B %d, %Y at %I:%M %p UTC'))}
                      {_info_row("Amount", f"${transaction.amount}", "#ef4444")}
                    </table>
                    """, padding="24px 28px", border_left="#ef4444")}

                    <!-- User details -->
                    {_card(f"""
                    {_section_heading("Account Holder", "#3b82f6")}
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                      {_info_row("Full Name", f"{user.first_name} {user.last_name}")}
                      {_info_row("Email", user.email)}
                      {_info_row("Account ID", user.account_id or "N/A")}
                      {_info_row("Remaining Balance", f"${user.balance}")}
                      {_info_row("KYC Status", kyc_status)}
                    </table>
                    """, padding="24px 28px", border_left="#3b82f6")}

                    <!-- Payment destination -->
                    {_card(f"""
                    {_section_heading("Payment Destination", _BRAND_ORANGE)}
                    <table cellpadding="0" cellspacing="0" border="0" width="100%">
                      {_info_row("Method", payment_method_info)}
                      {_info_row("Address / Account", f'<span style="font-family:\'Courier New\',monospace; font-size:12px;">{payment_address}</span>')}
                      {bank_row}
                    </table>
                    """, padding="24px 28px", border_left=_BRAND_ORANGE)}

                  </td>
                </tr>
              </table>
            </td>
          </tr>

          {_footer()}

        </table>
      </td></tr>
    </table>
    </body>
    </html>
    """

    return send_email(admin_email, subject, html_content)
