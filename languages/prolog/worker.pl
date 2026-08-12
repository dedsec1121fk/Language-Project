key(241).
hexval(C,V):-char_code(C,N),((N>=48,N=<57)->V is N-48;(N>=65,N=<70)->V is N-65+10;V is N-97+10).
transform([],[]). transform([A,B|T],Out):-hexval(A,X),hexval(B,Y),key(K),V is ((X*16+Y) xor K),format(atom(H),'~|~`0t~16r~2+',[V]),atom_chars(H,HC),transform(T,R),append(HC,R,Out).
main:-set_stream(user_output,buffer(line)),repeat,read_line_to_string(user_input,S),(S==end_of_file,!;S="QUIT",!;S="PING",writeln('PONG'),flush_output,fail;sub_string(S,0,2,_,P),member(P,["E ","D "]),sub_string(S,2,_,0,H),string_chars(H,C),transform(C,O),string_chars(R,O),writeln(R),flush_output,fail;writeln('ERR'),flush_output,fail).
