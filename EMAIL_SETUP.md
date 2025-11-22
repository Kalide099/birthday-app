# 📧 Email Setup Guide

## ✅ What's New:
Your Birthday App can now **automatically send emails** to your friends on their birthdays!

## 🔧 Setup Instructions:

### Step 1: Configure Your Email in `.env` file

Edit the `.env` file and add these settings:

```
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Step 2: Get Gmail App Password (If using Gmail)

1. Go to your Google Account: https://myaccount.google.com
2. Enable **2-Step Verification** (if not already enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Create a new App Password:
   - Select app: **Mail**
   - Select device: **Windows Computer**
5. Click **Generate**
6. Copy the 16-character password (remove spaces)
7. Paste it as `SMTP_PASSWORD` in your `.env` file

### Step 3: Add Friend's Email Addresses

When adding friends in the app, make sure to fill in their **Email** field.

### Step 4: Test Email Sending

Run this command to send test emails:
```powershell
python send_test_email.py
```

## 🎯 How It Works:

1. **At midnight** on each friend's birthday:
   - AI generates a personalized message
   - Email is automatically sent to the friend's email address
   - Message is saved in the database
   - Alert is created in the app

2. **If email fails:**
   - The message is still saved
   - You can view it in the app
   - Alert will show email status

## 📧 Email Features:

✅ Beautiful HTML formatted emails  
✅ Personalized AI-generated messages  
✅ Automatic sending at midnight  
✅ Email delivery status in alerts  
✅ Works with Gmail, Outlook, Yahoo, etc.  

## 🔒 Security Tips:

- Never share your `.env` file
- Use App Passwords (not regular passwords)
- Keep your credentials private
- The `.env` file is already in `.gitignore`

## 📨 Using Other Email Providers:

### Outlook/Hotmail:
```
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_EMAIL=your_email@outlook.com
SMTP_PASSWORD=your_password
```

### Yahoo:
```
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_EMAIL=your_email@yahoo.com
SMTP_PASSWORD=your_app_password
```

## ❓ Troubleshooting:

**"Email credentials not configured"**
- Make sure you added SMTP settings to `.env` file

**"Error sending email: Authentication failed"**
- Check your email and password are correct
- For Gmail, make sure you're using an App Password

**"No email address provided"**
- Add email addresses to your friends' profiles

**Email not sent automatically**
- Make sure the app is running
- Check that the birthday date is correct
- Look at the alerts section for email status

## ✨ What Gets Sent:

Your friends will receive a beautiful HTML email with:
- 🎉 Birthday greeting header
- 🤖 AI-generated personalized message
- 🎨 Styled formatting
- 💌 Your signature

Enjoy never missing a birthday! 🎂
