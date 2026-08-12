function transform
    printf '%s\n' $argv[1] | tr '0123456789abcdefABCDEF' 'fedcba9876543210FEDCBA9876543210'
end
while read -l line
    if test "$line" = PING
        echo PONG
    else if test "$line" = QUIT
        exit 0
    else if string match -rq '^[ED] ' -- $line
        transform (string sub -s 3 -- $line)
    else
        echo ERR
    end
end
