#!/bin/bash
# Usage: mail_reply.sh <msg_id> <reply text>
# Replies to an email. Pass reply text as second argument or via stdin.

MSG_ID=$1
shift

if [ -z "$MSG_ID" ]; then
    echo "Usage: mail_reply.sh <msg_id> <reply text>"
    exit 1
fi

if [ -n "$*" ]; then
    REPLY_TEXT="$*"
else
    REPLY_TEXT=$(cat)
fi

TMPFILE=$(mktemp)
printf '%s' "$REPLY_TEXT" > "$TMPFILE"

osascript - "$MSG_ID" "$TMPFILE" <<'EOF'
on run argv
    set msgId to item 1 of argv as integer
    set tmpFile to item 2 of argv
    set replyText to do shell script "cat " & quoted form of tmpFile
    tell application "Mail"
        repeat with acct in accounts
            try
                set inboxMbx to mailbox "INBOX" of acct
                set targetMsg to first message of inboxMbx whose id is msgId
                set origSender to sender of targetMsg
                set origSubject to subject of targetMsg
                set newMsg to make new outgoing message with properties {subject:"Re: " & origSubject, content:replyText}
                tell newMsg
                    make new to recipient with properties {address:origSender}
                end tell
                send newMsg
                return "Reply sent to " & origSender
            end try
        end repeat
        return "Error: message ID " & msgId & " not found."
    end tell
end run
EOF

rm -f "$TMPFILE"
