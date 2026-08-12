key=0xD5
transform=fn h -> h |> String.graphemes() |> Enum.chunk_every(2) |> Enum.map(fn [a,b] -> {v,""}=Integer.parse(a<>b,16); Integer.to_string(Bitwise.bxor(v,key),16)|>String.pad_leading(2,"0") end) |> Enum.join() end
loop = fn loop -> case IO.read(:stdio,:line) do :eof -> :ok; line -> line=String.trim_trailing(line)|>String.trim_trailing("\r"); cond do line=="PING" -> IO.puts("PONG");loop.(loop); line=="QUIT" -> :ok; String.match?(line,~r/^[ED] [0-9A-Fa-f]*$/) -> h=if String.length(line)>2, do: String.slice(line,2,String.length(line)-2), else: ""; IO.puts(transform.(h));loop.(loop); true -> IO.puts("ERR");loop.(loop) end end end
loop.(loop)
