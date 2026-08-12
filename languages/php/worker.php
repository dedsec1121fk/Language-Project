<?php
const KEY=0x83; while(($line=fgets(STDIN))!==false){$line=rtrim($line,"\r\n");if($line==='PING'){echo "PONG\n";flush();continue;}if($line==='QUIT')break;if(preg_match('/^[ED] ([0-9a-fA-F]*)$/',$line,$m)){ $h=$m[1];$o='';for($i=0;$i<strlen($h);$i+=2)$o.=sprintf('%02x',hexdec(substr($h,$i,2))^KEY);echo "$o\n";flush();}else{echo "ERR\n";flush();}}
?>
