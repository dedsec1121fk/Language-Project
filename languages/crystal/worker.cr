KEY = 0x89
STDOUT.flush_on_newline = true
STDIN.each_line do |raw|
  line = raw.rstrip
  if line == "PING"
    puts "PONG"; next
  end
  break if line == "QUIT"
  unless line.matches?(/^[ED] [0-9A-Fa-f]*$/)
    puts "ERR"; next
  end
  h = line[2..]
  out = String.build do |io|
    i = 0
    while i < h.size
      v = h[i, 2].to_i(16) ^ KEY
      io << v.to_s(16).rjust(2, '0')
      i += 2
    end
  end
  puts out
end
