import System.Environment (getArgs)
import qualified Data.Map.Strict as M
import Data.List (sortOn)
import Data.Ord (Down(..))

main :: IO ()
main = do
  args <- getArgs
  case args of
    [] -> putStrLn "Usage: duplicate-lines FILE" >> fail "missing file"
    ("--help":_) -> putStrLn "Usage: duplicate-lines FILE"
    (file:_) -> do
      s <- readFile file
      let counts = M.fromListWith (+) [(x, 1 :: Int) | x <- lines s]
          dups = sortOn (Down . snd) [(x,n) | (x,n) <- M.toList counts, n > 1]
      putStrLn ("duplicate_unique_lines=" ++ show (length dups))
      mapM_ (\(x,n) -> putStrLn (show n ++ "\t" ++ x)) (take 50 dups)
