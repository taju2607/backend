
from dao.modules.dao_modules_alll import *

class DAOFORGOTPASSWORD:
    def forgot_passwords(username):
       
        # Taking the username or email id from the user

        db, collection = DB.user_db()

        # Finding the user details in the database using username
        user = collection.find_one({'username': username}, {'_id': 0})
        if not user:
            message = {'message': 'User not found','status':'409'}
            return message

        # Function to generate OTP
        def generate_otp(length):
            digits = string.digits
            otp = ''.join(random.choice(digits) for i in range(length))
            return otp

        # Email configuration
        smtp_server = 'smtp.gmail.com' # taking smtp server
        smtp_port = 587 # taking smpt port 587
        sender_email = 'tajuddinpathan.com@gmail.com' # sending email
        receiver_email = username # # receiver email
        password = 'keev jwtx vcmj epvs' # app pasword to login while sending the mail

        # Generate OTP
        otp = generate_otp(6)
        subject = 'Your One-Time Password (OTP) for reset your password'
        body = f'''
Hi,

We've sent you this code to reset your password.

Your One-Time Password (OTP) is: {otp}

For your security purpose:

Dont share this code with anyone.

Thanks,
Tajuddin pathan'''

        # Create the email content
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Send the email
        try:
            session = smtplib.SMTP(smtp_server, smtp_port)
            session.starttls()  # Enable security
            session.login(sender_email, password)  # Login to the email server

            text = message.as_string()
            session.sendmail(sender_email, receiver_email, text)
            session.quit()
            
            # Save the OTP in the database
            collection.find_one_and_update({'username': username}, {'$set': {'otp': otp}})
            
            message = {'message': 'OTP sent successfully','status':'200'}
            return message
        except Exception as e:
            message = {'message': 'Failed to send OTP','status':'500'}
            return message

        

    ##################################################################################################################################

    def entered_otps(username , otp_entered , new_password , confirm_password):
        
        db, collection = DB.user_db()

        # Finding the user details in the database using username
        user = collection.find_one({'username': username}, {'_id': 0})
        if not user:
            return jsonify({'message': 'User not found','status':'404'})
        
        # Retrieve the stored OTP
        stored_otp = user.get('otp')
        old_password = user.get('password')

        # Checking if the OTP entered is correct
        if otp_entered != stored_otp:
            return jsonify({'message': 'OTP entered is incorrect','status':'400'})
        
        # Checking if the entered password is same as the old password
        if new_password == old_password:
            return jsonify({'message': 'Password cannot be the old password','status':'400'})
        
        # Checking if the new password and confirm password match
        if new_password != confirm_password:
            return jsonify({'message': 'Passwords do not match','status':'400'})
        
        # Updating the details in the database
        collection.find_one_and_update({'username': username}, {'$set': {'password': new_password, 'confirmPassword': confirm_password, 'otp': None}})
        message = {'message': 'Password successfully changed','status':'200'}
        return message
        