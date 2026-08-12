import 'dart:io';
const key=0x57;String transform(String h){var o=StringBuffer();for(var i=0;i<h.length;i+=2){var v=int.parse(h.substring(i,i+2),radix:16)^key;o.write(v.toRadixString(16).padLeft(2,'0'));}return o.toString();}
void main(){stdin.transform(systemEncoding.decoder).transform(const LineSplitter()).listen((line){line=line.replaceFirst(RegExp(r'\r$'),'');if(line=='PING'){stdout.writeln('PONG');}else if(line=='QUIT'){exit(0);}else if(RegExp(r'^[ED] [0-9A-Fa-f]*$').hasMatch(line)){stdout.writeln(transform(line.substring(2)));}else{stdout.writeln('ERR');}});}
