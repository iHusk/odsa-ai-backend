# Outlook Calendar Sync — Migration Troubleshooting

## Known Issue: Post-Migration Calendar Sync

After the January 2025 Outlook migration, some users experience missing calendar events on desktop and mobile clients. Events may appear on Outlook Web (outlook.office.com) but not sync to local apps.

## Fix: Force Calendar Re-Sync

### Desktop (Windows/Mac)
1. Close Outlook completely
2. Open Outlook in Safe Mode:
   - Windows: Hold Ctrl while clicking the Outlook icon
   - Mac: Hold Option while clicking the Outlook icon
3. Go to File → Account Settings → Account Settings
4. Select your account → click "Repair"
5. Follow the prompts to re-sync
6. Restart Outlook normally

### Mobile (iOS/Android)
1. Remove your Northbrook account from the mail app
2. Wait 60 seconds
3. Re-add the account using your SSO credentials
4. Allow 5-10 minutes for full calendar sync

### Shared Calendars
Shared and team calendars may need to be manually re-subscribed:
1. In Outlook, go to "Add Calendar" → "From Address Book"
2. Search for the team calendar name
3. Re-add it to your calendar list

## Verification
After re-syncing, check that recurring meetings (especially standups and weekly 1:1s) appear correctly. Compare against the web version to confirm parity.

## Escalation
If the repair doesn't work, submit a ticket to IT with "Outlook Migration" in the subject. Include which events are missing and your Outlook version number (Help → About).
