#!/bin/bash
# Usage: mail_bulk_delete.sh <keyword>
# Deletes all inbox emails whose subject or sender contains the keyword (case-insensitive).
# Useful for clearing out newsletters, ads, subscriptions.

KEYWORD="$*"

if [ -z "$KEYWORD" ]; then
    echo "Usage: mail_bulk_delete.sh <keyword>"
    echo "Example: mail_bulk_delete.sh unsubscribe"
    exit 1
fi

TMPFILE=$(mktemp)
printf '%s' "$KEYWORD" > "$TMPFILE"

osascript - "$TMPFILE" <<'EOF'
on run argv
    set tmpFile to item 1 of argv
    set keyword to do shell script "cat " & quoted form of tmpFile
    set keyword to (do shell script "echo " & quoted form of keyword & " | tr '[:upper:]' '[:lower:]'")
    set deletedCount to 0
    set deletedList to ""
    tell application "Mail"
        repeat with acct in accounts
            try
                set inboxMbx to mailbox "INBOX" of acct
                set msgs to every message of inboxMbx
                repeat with msg in msgs
                    set msgSubject to (do shell script "echo " & quoted form of (subject of msg) & " | tr '[:upper:]' '[:lower:]'")
                    set msgSender to (do shell script "echo " & quoted form of (sender of msg) & " | tr '[:upper:]' '[:lower:]'")
                    if msgSubject contains keyword or msgSender contains keyword then
                        set deletedList to deletedList & "  - " & subject of msg & " (" & sender of msg & ")" & linefeed
                        delete msg
                        set deletedCount to deletedCount + 1
                    end if
                end repeat
            end try
        end repeat
    end tell
    if deletedCount is 0 then
        return "No emails matched \"" & keyword & "\"."
    end if
    return "Deleted " & deletedCount & " email(s) matching \"" & keyword & "\":" & linefeed & deletedList
end run
EOF

rm -f "$TMPFILE"
