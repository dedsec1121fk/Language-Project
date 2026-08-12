#lang racket
(define a (current-command-line-arguments))
(when (or (= (vector-length a) 0) (equal? (vector-ref a 0) "--help")) (displayln "Usage: markdown-outline FILE") (exit (if (= (vector-length a) 0) 2 0)))
(for ([line (in-lines (open-input-file (vector-ref a 0)))]) (define m (regexp-match #px"^(#{1,6})\\s+(.+)$" line)) (when m (define level (string-length (list-ref m 1))) (printf "~a- ~a\n" (make-string (* 2 (- level 1)) #\space) (list-ref m 2))))
