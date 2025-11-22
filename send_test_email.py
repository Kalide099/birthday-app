from app import app, db, Friend, send_email, generate_birthday_message
from datetime import datetime

with app.app_context():
    # Get all friends
    friends = Friend.query.all()
    
    print(f"Found {len(friends)} friends\n")
    print("="*60)
    
    for friend in friends:
        print(f"\nFriend: {friend.name}")
        print(f"Email: {friend.email if friend.email else 'No email address'}")
        print(f"Birthday: {friend.birthday}")
        
        if friend.email:
            print("\nGenerating birthday message...")
            message = generate_birthday_message(friend.name, friend.relationship)
            print(f"Message: {message}\n")
            
            print("Sending email...")
            success = send_email(
                friend.email,
                f"🎉 Happy Birthday {friend.name}!",
                message
            )
            
            if success:
                print("✅ EMAIL SENT SUCCESSFULLY!")
            else:
                print("❌ Failed to send email. Check your SMTP settings in .env file")
        else:
            print("⚠️  No email address - skipping email send")
        
        print("="*60)
