args = System.argv()
if args == [] or hd(args) == "--help" do
  IO.puts("Usage: log-stats FILE  # count common log levels")
  System.halt(if(args == [], do: 2, else: 0))
end
levels = %{"ERROR" => 0, "WARN" => 0, "WARNING" => 0, "INFO" => 0, "DEBUG" => 0, "TRACE" => 0}
{counts, total} = File.stream!(hd(args)) |> Enum.reduce({levels, 0}, fn line, {m, n} ->
  upper = String.upcase(line)
  m2 = Enum.reduce(Map.keys(m), m, fn k, acc ->
    if String.contains?(upper, k), do: Map.update!(acc, k, &(&1 + 1)), else: acc
  end)
  {m2, n + 1}
end)
IO.puts("lines=#{total}")
Enum.each(counts, fn {k, v} -> IO.puts("#{String.downcase(k)}=#{v}") end)
