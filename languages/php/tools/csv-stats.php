<?php
if ($argc < 2 || $argv[1] === '--help') { echo "Usage: csv-stats FILE\n"; exit($argc<2?2:0); }
$h=fopen($argv[1],'r'); if(!$h){fwrite(STDERR,"open failed\n");exit(2);} $rows=0;$max=0;$min=null;$empty=0;$header=null;
while(($r=fgetcsv($h))!==false){$rows++;$c=count($r);$max=max($max,$c);$min=$min===null?$c:min($min,$c);foreach($r as $v)if($v==='')$empty++;if($header===null)$header=$r;}fclose($h);
echo "rows=$rows\nmin_columns=".($min??0)."\nmax_columns=$max\nempty_cells=$empty\n";if($header!==null)echo "header=".implode(' | ',$header)."\n";
?>
