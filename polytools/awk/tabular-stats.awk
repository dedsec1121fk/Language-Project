BEGIN {
  if (ARGV[1] == "--help") { print "Usage: gawk -f tabular-stats.awk FILE  # TSV/tabular summary"; exit 0 }
  FS="\t"; rows=0; maxcols=0; mincols=0
}
{
  rows++; if (NF>maxcols) maxcols=NF; if (mincols==0 || NF<mincols) mincols=NF;
  for(i=1;i<=NF;i++){ if($i=="") empty[i]++; nonempty[i]++ }
}
END {
  if (ARGV[1] == "--help") exit
  print "rows=" rows; print "min_columns=" mincols; print "max_columns=" maxcols;
  for(i=1;i<=maxcols;i++) printf("column_%d_nonempty=%d empty=%d\n",i,nonempty[i]+0,empty[i]+0)
}
