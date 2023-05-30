import mysql.connector
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

smtp_username = os.environ.get('SMTP_USERNAME')
smtp_password = os.environ.get('SMTP_PASSWORD')
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
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_username': smtp_username,
    'smtp_password': smtp_password
}

def run_queries():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        query1 = "SELECT COUNT(*) as mail_total FROM pgbison_database.mail_result WHERE date_created >= CAST(NOW() - INTERVAL 1 DAY AS DATE) AND date_created <= CAST(NOW() AS DATE)"
        query2 = "SELECT COUNT(*) as sms_total FROM pgbison_database.sent_message WHERE receiver != '' AND sent_time >= CAST(NOW() - INTERVAL 1 DAY AS DATE) AND sent_time <= CAST(NOW() AS DATE)"

        cursor.execute(query1)
        result1 = cursor.fetchone()

        cursor.execute(query2)
        result2 = cursor.fetchone()

        cursor.close()
        connection.close()

        mail_total = result1[0]
        sms_total = result2[0]

        send_email(mail_total, sms_total)

    except mysql.connector.Error as err:
        print("Error executing queries:", err)

def send_email(mail_total, sms_total):
    email_body = f'''
    Good morning,

    Below is the daily report for {datetime.now( - timedelta(days=1)).strftime("%d %b %Y")}

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
        with smtplib.SMTP(email_config['smtp_host'], email_config['smtp_port']) as server:
            server.starttls()
            server.login(email_config['smtp_username'], email_config['smtp_password'])
            server.send_message(msg)
            print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"An error occurred while sending the email: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

run_queries()