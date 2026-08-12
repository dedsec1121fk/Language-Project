import java.io.File

fun main(a: Array<String>) {
    if (a.isEmpty() || a[0] == "--help") {
        println("Usage: code-metrics FILE_OR_DIR")
        if (a.isEmpty()) kotlin.system.exitProcess(2)
        return
    }
    val root = File(a[0])
    val codeExt = setOf("py","c","h","cpp","hpp","cc","rs","go","java","kt","kts","js","ts","jsx","tsx","rb","php","lua","pl","pm","sh","zsh","fish","tcl","nim","zig","hs","d","scala","dart","f90","f95","rkt","cr","lisp","scm","ex","exs","erl","awk","sed","jq","json","yaml","yml","toml","md")
    val files = if (root.isDirectory) root.walkTopDown()
        .onEnter { it.name !in setOf(".git","build","node_modules",".venv","venv","dist") }
        .filter { it.isFile && it.length() <= 5_000_000 && it.extension.lowercase() in codeExt }
        .toList() else listOf(root)
    var lines = 0L; var blank = 0L; var comment = 0L
    val ext = mutableMapOf<String, Int>()
    for (f in files) {
        try {
            f.forEachLine { l ->
                lines++; val t=l.trim(); if(t.isEmpty()) blank++
                if(t.startsWith("//") || t.startsWith("#") || t.startsWith("/*") || t.startsWith("*")) comment++
            }
            val e=f.extension.lowercase().ifEmpty { "[none]" }; ext[e]=(ext[e]?:0)+1
        } catch (_: Exception) {}
    }
    println("files=${files.size}"); println("lines=$lines"); println("blank_lines=$blank"); println("comment_like_lines=$comment")
    println("extensions:"); ext.entries.sortedByDescending { it.value }.take(30).forEach { println("${it.value}\t${it.key}") }
}
