#!/usr/bin/env escript
main(_) -> loop().
loop() -> case io:get_line("") of eof -> ok; Line0 -> Line=string:trim(Line0,trailing,"\n\r"), case Line of "PING" -> io:format("PONG~n"), loop(); "QUIT" -> ok; _ -> case Line of [M,$\s|H] when M==$E; M==$D -> io:format("~s~n",[transform(H)]), loop(); _ -> io:format("ERR~n"), loop() end end end.
transform([])->[]; transform([A,B|T])-> io_lib:format("~2.16.0b",[(hex(A)*16+hex(B)) bxor 16#CF]) ++ transform(T).
hex(C) when C >= $0, C =< $9 -> C-$0; hex(C) when C >= $a, C =< $f -> C-$a+10; hex(C) when C >= $A, C =< $F -> C-$A+10.
