"""Render a crossword grid as a self-contained interactive HTML file."""

from __future__ import annotations

import json
import os
from typing import Optional

from ._base import RenderConfig
from ..grid_generator import CrosswordGrid


_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  background:#f5f5f5;color:#222;padding:20px}
.container{max-width:1100px;margin:0 auto}
h1{text-align:center;margin-bottom:4px;font-size:1.6rem}
.subtitle{text-align:center;color:#666;margin-bottom:16px;font-size:1rem}
.main{display:flex;gap:24px;align-items:flex-start}
.grid-wrap{flex:0 0 auto}
.clues-wrap{flex:1 1 300px;min-width:250px}
table.grid{border-collapse:collapse;border:2px solid #000}
table.grid td{width:36px;height:36px;border:1px solid #999;text-align:center;
  vertical-align:middle;position:relative;font-size:18px;font-weight:bold;cursor:pointer;
  user-select:none;-webkit-user-select:none}
table.grid td.block{background:#000;cursor:default}
table.grid td .num{position:absolute;top:1px;left:2px;font-size:10px;font-weight:normal;color:#555}
table.grid td input{width:100%;height:100%;border:none;outline:none;background:transparent;
  text-align:center;font-size:18px;font-weight:bold;text-transform:uppercase;caret-color:transparent;
  cursor:pointer}
table.grid td.highlight{background:#b3d4fc}
table.grid td.active{background:#ffeb3b}
table.grid td.correct input{color:#2e7d32}
table.grid td.incorrect input{color:#c62828}
.clue-section{margin-bottom:16px}
.clue-section h3{font-size:1rem;border-bottom:2px solid #333;padding-bottom:4px;margin-bottom:6px}
.clue-list{list-style:none;font-size:0.9rem;line-height:1.5}
.clue-list li{padding:3px 4px;border-radius:3px;cursor:pointer}
.clue-list li:hover{background:#e0e0e0}
.clue-list li.active{background:#b3d4fc;font-weight:bold}
.controls{text-align:center;margin:16px 0}
.controls button{padding:8px 16px;margin:4px;border:1px solid #999;border-radius:4px;
  background:#fff;cursor:pointer;font-size:0.9rem}
.controls button:hover{background:#e0e0e0}
@media(max-width:700px){
  .main{flex-direction:column;align-items:center}
  table.grid td{width:28px;height:28px;font-size:14px}
  table.grid td .num{font-size:8px}
  table.grid td input{font-size:14px}
}
@media print{
  .controls{display:none}
  body{background:#fff;padding:0}
  table.grid td.highlight,table.grid td.active{background:#fff!important}
}
</style>
</head>
<body>
<div class="container">
<h1>{{TITLE}}</h1>
{{SUBTITLE_HTML}}
<div class="controls">
  <button id="btn-check">Check</button>
  <button id="btn-reveal">Reveal Word</button>
  <button id="btn-clear">Clear All</button>
</div>
<div class="main">
  <div class="grid-wrap"><table class="grid" id="grid"></table></div>
  <div class="clues-wrap">
    <div class="clue-section"><h3>Across</h3><ol class="clue-list" id="clues-across"></ol></div>
    <div class="clue-section"><h3>Down</h3><ol class="clue-list" id="clues-down"></ol></div>
  </div>
</div>
</div>
<script>
(function(){
"use strict";
var DATA = {{PUZZLE_JSON}};
var STORAGE_KEY = "cw_" + location.pathname;
var grid = DATA.grid, size = DATA.size, clues = DATA.clues;
var rows = size.rows, cols = size.cols;
var cells = {};        // "r,c" -> input element
var cellTds = {};      // "r,c" -> td element
var currentCell = null; // {r, c}
var currentDir = "across";
var currentClue = null; // clue object

// Build number map
var numMap = {};
function buildNumMap(){
  clues.across.concat(clues.down).forEach(function(cl){
    var key = cl.row+","+cl.col;
    if(!(key in numMap)) numMap[key] = cl.number;
  });
}
buildNumMap();

// Build answer map from clues
var answerMap = {}; // "r,c" -> letter
function buildAnswerMap(){
  clues.across.forEach(function(cl){
    for(var i=0;i<cl.length;i++){
      answerMap[cl.row+","+(cl.col+i)] = cl.answer[i];
    }
  });
  clues.down.forEach(function(cl){
    for(var i=0;i<cl.length;i++){
      answerMap[(cl.row+i)+","+cl.col] = cl.answer[i];
    }
  });
}
buildAnswerMap();

// Build cell-to-clues mapping
var cellClues = {}; // "r,c" -> {across: clue|null, down: clue|null}
function buildCellClues(){
  clues.across.forEach(function(cl){
    for(var i=0;i<cl.length;i++){
      var k = cl.row+","+(cl.col+i);
      if(!cellClues[k]) cellClues[k]={across:null,down:null};
      cellClues[k].across = cl;
    }
  });
  clues.down.forEach(function(cl){
    for(var i=0;i<cl.length;i++){
      var k = (cl.row+i)+","+cl.col;
      if(!cellClues[k]) cellClues[k]={across:null,down:null};
      cellClues[k].down = cl;
    }
  });
}
buildCellClues();

// Render grid
var table = document.getElementById("grid");
for(var r=0;r<rows;r++){
  var tr = document.createElement("tr");
  for(var c=0;c<cols;c++){
    var td = document.createElement("td");
    var val = grid[r][c];
    var key = r+","+c;
    if(val === "."){
      td.className = "block";
    } else {
      var num = numMap[key];
      if(num !== undefined){
        var sp = document.createElement("span");
        sp.className = "num";
        sp.textContent = num;
        td.appendChild(sp);
      }
      var inp = document.createElement("input");
      inp.setAttribute("maxlength","1");
      inp.setAttribute("data-r", r);
      inp.setAttribute("data-c", c);
      inp.setAttribute("autocomplete","off");
      inp.setAttribute("autocorrect","off");
      inp.setAttribute("spellcheck","false");
      td.appendChild(inp);
      cells[key] = inp;
      cellTds[key] = td;
    }
    tr.appendChild(td);
  }
  table.appendChild(tr);
}

// Render clues
function renderClues(direction, containerId){
  var list = document.getElementById(containerId);
  var arr = clues[direction];
  arr.forEach(function(cl){
    var li = document.createElement("li");
    li.setAttribute("data-dir", direction);
    li.setAttribute("data-num", cl.number);
    li.textContent = cl.number + ". " + cl.clue + " (" + cl.length + ")";
    li.addEventListener("click", function(){
      selectClue(cl, direction);
      var inp = cells[cl.row+","+cl.col];
      if(inp) inp.focus();
    });
    list.appendChild(li);
  });
}
renderClues("across","clues-across");
renderClues("down","clues-down");

// Highlighting
function clearHighlights(){
  Object.keys(cellTds).forEach(function(k){
    cellTds[k].classList.remove("highlight","active","correct","incorrect");
  });
  document.querySelectorAll(".clue-list li").forEach(function(li){
    li.classList.remove("active");
  });
}

function highlightClue(cl, dir){
  if(!cl) return;
  for(var i=0;i<cl.length;i++){
    var k = dir==="across" ? cl.row+","+(cl.col+i) : (cl.row+i)+","+cl.col;
    if(cellTds[k]) cellTds[k].classList.add("highlight");
  }
  // Highlight clue in list
  var sel = '.clue-list li[data-dir="'+dir+'"][data-num="'+cl.number+'"]';
  var li = document.querySelector(sel);
  if(li) li.classList.add("active");
}

function selectClue(cl, dir){
  clearHighlights();
  currentClue = cl;
  currentDir = dir;
  highlightClue(cl, dir);
  if(currentCell){
    var k = currentCell.r+","+currentCell.c;
    if(cellTds[k]) cellTds[k].classList.add("active");
  }
}

function selectCell(r, c){
  var k = r+","+c;
  if(!cells[k]) return;
  var cc = cellClues[k];
  if(!cc) return;
  // Toggle direction if clicking same cell
  if(currentCell && currentCell.r===r && currentCell.c===c){
    if(currentDir==="across" && cc.down) currentDir="down";
    else if(currentDir==="down" && cc.across) currentDir="across";
  } else {
    // Pick direction: prefer current, fallback to what's available
    if(currentDir==="across" && !cc.across && cc.down) currentDir="down";
    if(currentDir==="down" && !cc.down && cc.across) currentDir="across";
  }
  currentCell = {r:r, c:c};
  currentClue = cc[currentDir];
  clearHighlights();
  highlightClue(currentClue, currentDir);
  cellTds[k].classList.add("active");
}

// Input handling
table.addEventListener("click", function(e){
  var inp = e.target.closest("input");
  if(!inp) return;
  var r = parseInt(inp.getAttribute("data-r"));
  var c = parseInt(inp.getAttribute("data-c"));
  selectCell(r, c);
});

table.addEventListener("input", function(e){
  var inp = e.target;
  if(inp.tagName !== "INPUT") return;
  var val = inp.value.replace(/[^a-zA-Z]/g,"").toUpperCase();
  inp.value = val ? val[val.length-1] : "";
  if(val) moveNext();
  saveProgress();
});

table.addEventListener("keydown", function(e){
  if(!currentCell) return;
  var r = currentCell.r, c = currentCell.c;
  switch(e.key){
    case "ArrowRight":
      e.preventDefault();
      currentDir = "across";
      moveTo(r, c+1);
      break;
    case "ArrowLeft":
      e.preventDefault();
      currentDir = "across";
      moveTo(r, c-1);
      break;
    case "ArrowDown":
      e.preventDefault();
      currentDir = "down";
      moveTo(r+1, c);
      break;
    case "ArrowUp":
      e.preventDefault();
      currentDir = "down";
      moveTo(r-1, c);
      break;
    case "Backspace":
      e.preventDefault();
      var k = r+","+c;
      if(cells[k] && cells[k].value){
        cells[k].value = "";
      } else {
        movePrev();
        var pk = currentCell.r+","+currentCell.c;
        if(cells[pk]) cells[pk].value = "";
      }
      saveProgress();
      break;
    case "Tab":
      e.preventDefault();
      moveNextClue(e.shiftKey);
      break;
  }
});

function moveTo(r, c){
  var k = r+","+c;
  if(cells[k]){
    cells[k].focus();
    selectCell(r, c);
  }
}

function moveNext(){
  if(!currentCell) return;
  var r=currentCell.r, c=currentCell.c;
  if(currentDir==="across") moveTo(r, c+1);
  else moveTo(r+1, c);
}

function movePrev(){
  if(!currentCell) return;
  var r=currentCell.r, c=currentCell.c;
  if(currentDir==="across") moveTo(r, c-1);
  else moveTo(r-1, c);
}

function moveNextClue(backward){
  var all = clues.across.concat(clues.down);
  if(!currentClue){
    selectClue(all[0], "across");
    return;
  }
  var dirs = [];
  clues.across.forEach(function(cl){ dirs.push({cl:cl,dir:"across"}); });
  clues.down.forEach(function(cl){ dirs.push({cl:cl,dir:"down"}); });
  var idx = dirs.findIndex(function(d){ return d.cl.number===currentClue.number && d.dir===currentDir; });
  if(backward) idx = (idx - 1 + dirs.length) % dirs.length;
  else idx = (idx + 1) % dirs.length;
  selectClue(dirs[idx].cl, dirs[idx].dir);
  var inp = cells[dirs[idx].cl.row+","+dirs[idx].cl.col];
  if(inp) inp.focus();
}

// Buttons
document.getElementById("btn-check").addEventListener("click", function(){
  Object.keys(cells).forEach(function(k){
    var inp = cells[k];
    var td = cellTds[k];
    td.classList.remove("correct","incorrect");
    if(inp.value){
      if(inp.value.toUpperCase() === answerMap[k]){
        td.classList.add("correct");
      } else {
        td.classList.add("incorrect");
      }
    }
  });
  setTimeout(function(){
    Object.keys(cellTds).forEach(function(k){
      cellTds[k].classList.remove("correct","incorrect");
    });
  }, 2000);
});

document.getElementById("btn-reveal").addEventListener("click", function(){
  if(!currentClue) return;
  for(var i=0;i<currentClue.length;i++){
    var k = currentDir==="across"
      ? currentClue.row+","+(currentClue.col+i)
      : (currentClue.row+i)+","+currentClue.col;
    if(cells[k]) cells[k].value = answerMap[k] || "";
  }
  saveProgress();
});

document.getElementById("btn-clear").addEventListener("click", function(){
  Object.keys(cells).forEach(function(k){ cells[k].value = ""; });
  saveProgress();
});

// localStorage persistence
function saveProgress(){
  var state = {};
  Object.keys(cells).forEach(function(k){ state[k] = cells[k].value; });
  try{ localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }catch(e){}
}

function loadProgress(){
  try{
    var raw = localStorage.getItem(STORAGE_KEY);
    if(!raw) return;
    var state = JSON.parse(raw);
    Object.keys(state).forEach(function(k){
      if(cells[k]) cells[k].value = state[k];
    });
  }catch(e){}
}
loadProgress();

})();
</script>
</body>
</html>"""


def render_html(
    puzzle: CrosswordGrid,
    output_path: str,
    *,
    config: Optional[RenderConfig] = None,
) -> str:
    """Render the crossword as a self-contained interactive HTML file.

    Parameters
    ----------
    puzzle : CrosswordGrid
        The puzzle to render.
    output_path : str
        Destination HTML file path.
    config : RenderConfig, optional
        Rendering configuration (uses title/subtitle).

    Returns
    -------
    str
        Absolute path of the written HTML file.
    """
    if config is None:
        config = RenderConfig()

    puzzle_data = puzzle.to_json()
    title = config.title or "Crossword Puzzle"

    subtitle_html = ""
    if config.subtitle:
        subtitle_html = f'<p class="subtitle">{_escape(config.subtitle)}</p>'

    html = _HTML_TEMPLATE
    html = html.replace("{{TITLE}}", _escape(title))
    html = html.replace("{{SUBTITLE_HTML}}", subtitle_html)
    html = html.replace("{{PUZZLE_JSON}}", json.dumps(puzzle_data))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return os.path.abspath(output_path)


def _escape(s: str) -> str:
    """Minimal HTML-entity escaping."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
