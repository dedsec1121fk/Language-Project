#!/usr/bin/env perl
use strict; use warnings; use File::Find;
if(@ARGV<2 || $ARGV[0] eq '--help'){print "Usage: grep-context PATTERN FILE_OR_DIR [--ignore-case]\n";exit(@ARGV<2?2:0)}
my($pat,$root)=splice(@ARGV,0,2);my$ic=grep{$_ eq '--ignore-case'}@ARGV;my$re=eval{$ic?qr/$pat/i:qr/$pat/};die "bad regex: $@" if $@;my@files;
if(-d $root){
  find({wanted=>sub{
    if(-d $_ && ($_ eq '.git'||$_ eq 'build'||$_ eq 'node_modules'||$_ eq '.venv')){$File::Find::prune=1;return}
    push @files,$File::Find::name if -f $_ && !-B _;
  },no_chdir=>0},$root)
}else{@files=($root) if -f $root && !-B $root}
my$n=0;for my$f(@files){open my$h,'<',$f or next;my$ln=0;while(my$l=<$h>){$ln++;if($l=~$re){chomp$l;print "$f:$ln:$l\n";$n++}}close$h}print STDERR "matches=$n\n";
