package main
import("bufio";"fmt";"os";"strings";"encoding/hex")
const key byte=0xA1
func main(){in:=bufio.NewScanner(os.Stdin);out:=bufio.NewWriter(os.Stdout);defer out.Flush();for in.Scan(){s:=strings.TrimSuffix(in.Text(),"\r");if s=="PING"{fmt.Fprintln(out,"PONG");out.Flush();continue};if s=="QUIT"{break};if len(s)>=2&&(s[0]=='E'||s[0]=='D')&&s[1]==' '{b,e:=hex.DecodeString(s[2:]);if e!=nil{fmt.Fprintln(out,"ERR")}else{for i:=range b{b[i]^=key};fmt.Fprintln(out,hex.EncodeToString(b))};out.Flush()}else{fmt.Fprintln(out,"ERR");out.Flush()}}}
