def tx:
  explode
  | map(
      (if . >= 48 and . <= 57 then . - 48
       elif . >= 97 and . <= 102 then . - 87
       else error("non-hex") end)
      | (15 - .)
      | if . < 10 then . + 48 else . + 87 end
    )
  | implode;
if . == "PING" then "PONG"
elif . == "QUIT" then halt
elif startswith("E ") or startswith("D ") then .[2:] | tx
else "ERR"
end
