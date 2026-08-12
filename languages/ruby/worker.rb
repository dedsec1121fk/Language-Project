STDOUT.sync=true; KEY=0x73
while (line=STDIN.gets)
 line=line.strip
 if line=='PING'; puts 'PONG'; next; end
 break if line=='QUIT'
 if line.match?(/\A[ED] [0-9a-fA-F]*\z/)
   h=line[2..]||''; puts h.scan(/../).map{|x| '%02x'%(x.to_i(16)^KEY)}.join
 else puts 'ERR' end
end
