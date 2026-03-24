#!/bin/bash
# Usage: mail_delete.sh <msg_id> [msg_id2 ...]
# Moves one or more emails to Trash by ID.

if [ -z "$1" ]; then
    echo "Usage: mail_delete.sh <msg_id> [msg_id2 ...]"
    exit 1
fi

IDS="$*"

osascript - $IDS <<'EOF'
on run argv
    set deleted to ""
    tell application "Mail"
        repeat with msgId in argv
            set msgId to msgId as integer
            repeat with acct in accounts
                try
                    set inboxMbx to mailbox "INBOX" of acct
                    set targetMsg to first message of inboxMbx whose id is msgId
                    set msgSubject to subject of targetMsg
                    delete targetMsg
                    set deleted to deleted & "Deleted: " & msgSubject & linefeed
                    exit repeat
                end try
            end repeat
        end repeat
    end tell
    if deleted is "" then return "No messages deleted."
    return deleted
end run
EOF
