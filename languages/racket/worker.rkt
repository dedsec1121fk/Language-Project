#lang racket
(define KEY #x71)
(define (hex2 value)
  (define s (string-downcase (number->string (bitwise-and value #xff) 16)))
  (if (= (string-length s) 1) (string-append "0" s) s))
(define (transform h)
  (apply string-append
         (for/list ([i (in-range 0 (string-length h) 2)])
           (hex2 (bitwise-xor (string->number (substring h i (+ i 2)) 16) KEY)))))
(let loop ()
  (define line (read-line))
  (unless (eof-object? line)
    (cond [(equal? line "PING") (displayln "PONG") (flush-output) (loop)]
          [(equal? line "QUIT") (void)]
          [(regexp-match? #px"^[ED] [0-9A-Fa-f]*$" line)
           (displayln (transform (substring line 2))) (flush-output) (loop)]
          [else (displayln "ERR") (flush-output) (loop)])))
