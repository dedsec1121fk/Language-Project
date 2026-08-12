#!/usr/bin/env ruby
if ARGV.empty? || ARGV[0]=='--help'; puts 'Usage: unique-lines FILE [--counts]'; exit(ARGV.empty? ? 2 : 0); end
path=ARGV[0]; counts=Hash.new(0); order=[]
File.foreach(path,chomp:true){|line| order << line unless counts.key?(line); counts[line]+=1 }
if ARGV.include?('--counts'); order.each{|x| puts "#{counts[x]}\t#{x}"}; else order.each{|x| puts x}; end
