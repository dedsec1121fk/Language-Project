local a=arg
if #a<1 or a[1]=='--help' then print('Usage: kv-read FILE [KEY]  # read key=value configuration'); os.exit(#a<1 and 2 or 0) end
local f=io.open(a[1],'r'); if not f then io.stderr:write('open failed\n'); os.exit(2) end
local t={}; local order={}
for line in f:lines() do local s=line:match('^%s*(.-)%s*$'); if s~='' and not s:match('^[#;]') then local k,v=s:match('^([^=]+)=(.*)$'); if k then k=k:match('^%s*(.-)%s*$');v=v:match('^%s*(.-)%s*$'); if t[k]==nil then table.insert(order,k) end;t[k]=v end end end
f:close(); if a[2] then if t[a[2]]~=nil then print(t[a[2]]) else os.exit(1) end else for _,k in ipairs(order) do print(k..'='..t[k]) end end
