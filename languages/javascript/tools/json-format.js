#!/usr/bin/env node
const fs=require('fs');
if(process.argv.length<3||process.argv[2]==='--help'){console.log('Usage: json-format FILE [pretty|minify]');process.exit(process.argv.length<3?2:0)}
const mode=process.argv[3]||'pretty';try{const obj=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));process.stdout.write(mode==='minify'?JSON.stringify(obj):JSON.stringify(obj,null,2)+'\n')}catch(e){console.error('invalid JSON:',e.message);process.exit(1)}
