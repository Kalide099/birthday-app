from app import app, db, Friend, Alert, BirthdayMessage, generate_birthday_message
from datetime import datetime, timedelta

with app.app_context():
    today = datetime.now().date()
    print(f"Today's date: {today}\n")
    
    friends = Friend.query.all()
    print(f"Found {len(friends)} friends:\n")
    
    for friend in friends:
        print(f"Friend: {friend.name}")
        print(f"Birthday: {friend.birthday}")
        
        # Check if birthday is today
        birthday_this_year = friend.birthday.replace(year=today.year)
        
        if birthday_this_year == today:
            print(f"✅ {friend.name}'s birthday is TODAY!")
            
            # Check if message already sent this year
            existing = BirthdayMessage.query.filter_by(
                friend_id=friend.id,
                year=today.year
            ).first()
            
            if existing:
                print(f"Message already sent this year: {existing.message}")
            else:
                # Generate AI message
                print("Generating AI birthday message...")
                try:
                    ai_message = generate_birthday_message(friend.name, friend.relationship)
                    print(f"Generated message: {ai_message}\n")
                    
                    # Save message
                    message = BirthdayMessage(
                        friend_id=friend.id,
                        message=ai_message,
                        year=today.year
                    )
                    db.session.add(message)
                    
                    # Create alert
                    alert = Alert(
                        friend_id=friend.id,
                        alert_type='birthday',
                        message=f"🎂 {friend.name}'s birthday is today! Message: {ai_message}"
                    )
                    db.session.add(alert)
                    
                    db.session.commit()
                    print("✅ Message saved and alert created!\n")
                except Exception as e:
                    print(f"❌ Error generating message: {e}\n")
        
        elif birthday_this_year == today + timedelta(days=1):
            print(f"⏰ {friend.name}'s birthday is TOMORROW!")
            
            # Check for existing reminder
            existing_alert = Alert.query.filter_by(
                friend_id=friend.id,
                alert_type='reminder'
            ).filter(
                db.func.date(Alert.created_at) == today
            ).first()
            
            if not existing_alert:
                alert = Alert(
                    friend_id=friend.id,
                    alert_type='reminder',
                    message=f"⏰ Reminder: {friend.name}'s birthday is tomorrow!"
                )
                db.session.add(alert)
                db.session.commit()
                print("✅ Reminder alert created!\n")
            else:
                print("Reminder already sent today.\n")
        else:
            print(f"Not today or tomorrow.\n")
    
    # Show all messages and alerts
    all_messages = BirthdayMessage.query.all()
    all_alerts = Alert.query.all()
    
    print(f"\n{'='*60}")
    print(f"TOTAL MESSAGES: {len(all_messages)}")
    print(f"TOTAL ALERTS: {len(all_alerts)}")
    print(f"{'='*60}\n")
