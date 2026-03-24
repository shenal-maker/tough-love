#!/bin/bash
# Usage: mail_list.sh [limit]
# Lists recent emails across all accounts. Default limit: 50.

LIMIT=${1:-50}

osascript - "$LIMIT" <<'EOF'
on run argv
    set msgLimit to item 1 of argv as integer
    set output to ""
    set counter to 0
    tell application "Mail"
        repeat with acct in accounts
            try
                set inboxMbx to mailbox "INBOX" of acct
                set msgs to every message of inboxMbx
                repeat with msg in msgs
                    if counter < msgLimit then
                        set msgId to id of msg
                        set msgSubject to subject of msg
                        set msgSender to sender of msg
                        set msgDate to date received of msg as string
                        if read status of msg then
                            set readTag to "READ  "
                        else
                            set readTag to "UNREAD"
                        end if
                        set output to output & msgId & tab & readTag & tab & msgSender & tab & msgSubject & tab & msgDate & linefeed
                        set counter to counter + 1
                    end if
                end repeat
            end try
        end repeat
    end tell
    return output
end run
EOF
