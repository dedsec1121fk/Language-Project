import System.IO
import Numeric(readHex,showHex)
import Data.Bits(xor)
import Data.Char(toLower)
key::Int;key=0x1B
pad s=replicate (2-length s) '0'++s
transform []=[]
transform (a:b:t)=let [(v,_)]=readHex [a,b] in pad (map toLower (showHex (v `xor` key) ""))++transform t
transform _=""
loop=do eof<-isEOF;if eof then return() else do s<-getLine;case s of "PING"->putStrLn "PONG">>hFlush stdout>>loop;"QUIT"->return();_->if length s>=2 && head s `elem` "ED" && s!!1==' ' then putStrLn(transform(drop 2 s))>>hFlush stdout>>loop else putStrLn "ERR">>hFlush stdout>>loop
main=hSetBuffering stdout LineBuffering>>loop
