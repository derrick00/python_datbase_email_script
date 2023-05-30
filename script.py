import mysql.connector
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging 


load_dotenv()

smtp_username = os.environ.get('SMTP_USERNAME')
smtp_password = os.environ.get('SMTP_PASSWORD')
smtp_host = os.environ.get('SMTP_HOST')
smtp_port = os.environ.get('SMTP_PORT')
receiver_username = os.environ.get('RECEIVER_USERNAME')


db_host = os.environ.get('DB_HOST')
db_user = os.environ.get('DB_USER')
db_password = os.environ.get('DB_PASSWORD')
db_name = os.environ.get('DB_NAME')


db_config = {
    'host': db_host,
    'user': db_user,
    'password': db_password,
    'database': db_name
}

email_config = {
    'smtp_host': smtp_host,
    'smtp_port': int(smtp_port),
    'smtp_username': smtp_username,
    'smtp_password': smtp_password
}

def run_queries():
    try:
        logger.warning("Connecting to database...")
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query1 = "SELECT COUNT(*) as mail_total FROM pgbison_database.mail_result WHERE date_created >= CAST(NOW() - INTERVAL 1 DAY AS DATE) AND date_created <= CAST(NOW() AS DATE)"
        query2 = "SELECT COUNT(*) as sms_total FROM pgbison_database.sent_message WHERE receiver != '' AND sent_time >= CAST(NOW() - INTERVAL 1 DAY AS DATE) AND sent_time <= CAST(NOW() AS DATE)"

        logger.warning("Fetching counts...")
        cursor.execute(query1)
        result1 = cursor.fetchone()

        cursor.execute(query2)
        result2 = cursor.fetchone()

        cursor.close()
        connection.close()

        mail_total = result1[0]
        sms_total = result2[0]
        
        logger.warning(f"Mail Count: {mail_total}")
        logger.warning(f"SMS Count: {sms_total}")

        send_email(mail_total, sms_total)

    except mysql.connector.Error as err:
        logger.warning("Error executing queries:", err)

def send_email(mail_total, sms_total):
    date = datetime.now() - timedelta(days=1)
    email_body = f'''
    Good morning,

    Below is the daily report for {date.strftime("%d %b %Y")}

    TOTAL EMAILS RECEIVED: {mail_total}
    TOTAL SMS SENT OUT: {sms_total}

    Regards,
    Onfon support
    ***This is an Auto-generated Email***
    '''

    msg = MIMEText(email_body)
    msg['Subject'] = f'''PGBison daily report for {datetime.now().strftime("%d %b %Y")}'''
    msg['From'] = email_config['smtp_username']
    msg['To'] = receiver_username

    try:
        logger.warning("Connecting to mail server...")
        logger.warning(f"Email Configs: {email_config}")
        with smtplib.SMTP(email_config['smtp_host'], email_config['smtp_port']) as server:
            server.startss()
            print("Logging in...")
            server.login(email_config['smtp_username'], email_config['smtp_password'])
            server.send_message(msg)
            logger.warning("Email sent successfully!")
    except smtplib.SMTPException as e:
        logger.warning(f"An error occurred while sending the email: {e}")
    except Exception as e:
        logger.warning(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    run_queries()
