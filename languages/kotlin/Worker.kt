import java.io.BufferedReader
import java.io.InputStreamReader
fun main(){val key=0x31;val r=BufferedReader(InputStreamReader(System.`in`));while(true){val s=r.readLine()?:break;if(s=="PING"){println("PONG");System.out.flush();continue};if(s=="QUIT")break;if(s.matches(Regex("^[ED] [0-9A-Fa-f]*$"))){val h=s.substring(2);val o=StringBuilder();var i=0;while(i<h.length){o.append(((h.substring(i,i+2).toInt(16) xor key) and 255).toString(16).padStart(2,'0'));i+=2};println(o.toString());System.out.flush()}else{println("ERR");System.out.flush()}}}
