:- initialization(main, main).
:- use_module(library(readutil)).
main(Args):- (Args=[] -> writeln('Usage: word-count FILE'),halt(2); Args=['--help'|_] -> writeln('Usage: word-count FILE'); Args=[F|_] -> read_file_to_string(F,S,[]), string_length(S,Chars), split_string(S," \t\r\n"," \t\r\n.,;:!?()[]{}\"'",Ws0),exclude(=(""),Ws0,Ws),length(Ws,Words),split_string(S,"\n","",Ls),length(Ls,Lines),format('chars=~w~nwords=~w~nlines=~w~n',[Chars,Words,Lines])).
