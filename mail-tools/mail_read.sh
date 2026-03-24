#!/bin/bash
# Usage: mail_read.sh <msg_id>
# Reads full content of an email by its ID (from mail_list.sh output).

MSG_ID=$1

if [ -z "$MSG_ID" ]; then
    echo "Usage: mail_read.sh <msg_id>"
    exit 1
fi

osascript - "$MSG_ID" <<'EOF'
on run argv
    set msgId to item 1 of argv as integer
    tell application "Mail"
        repeat with acct in accounts
            try
                set inboxMbx to mailbox "INBOX" of acct
                set targetMsg to first message of inboxMbx whose id is msgId
                set msgSubject to subject of targetMsg
                set msgSender to sender of targetMsg
                set msgDate to date received of targetMsg as string
                set msgContent to content of targetMsg
                return "FROM:    " & msgSender & linefeed & "DATE:    " & msgDate & linefeed & "SUBJECT: " & msgSubject & linefeed & string id 10 & msgContent
            end try
        end repeat
        return "Error: message ID " & msgId & " not found."
    end tell
end run
EOF
