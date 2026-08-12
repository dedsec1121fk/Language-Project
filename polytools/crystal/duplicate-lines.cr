if ARGV.empty? || ARGV[0] == "--help"
  puts "Usage: duplicate-lines-crystal FILE"
  exit ARGV.empty? ? 2 : 0
end
counts = Hash(String, Int32).new(0)
File.each_line(ARGV[0]) { |line| counts[line.chomp] += 1 }
dups = counts.select { |_, v| v > 1 }.to_a.sort_by { |x| -x[1] }
puts "duplicate_unique_lines=#{dups.size}"
dups.first(50).each { |x| puts "#{x[1]}\t#{x[0]}" }
