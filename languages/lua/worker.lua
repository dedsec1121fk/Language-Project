local KEY=0x7d
local function transform(h)local o={} for i=1,#h,2 do local v=tonumber(h:sub(i,i+1),16);o[#o+1]=string.format("%02x",v ~ KEY) end return table.concat(o) end
for line in io.lines() do line=line:gsub("\r$",""); if line=="PING" then print("PONG");io.flush() elseif line=="QUIT" then break elseif line:match("^[ED] [0-9A-Fa-f]*$") then print(transform(line:sub(3)));io.flush() else print("ERR");io.flush() end end
