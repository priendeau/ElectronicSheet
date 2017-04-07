
function GenerateSedFilter
{
  StrCmd="""for (( x=0 ; x <= \${#ArrayClean[@]}-1; x++  )) ; do 
  ArrayInfo[ASeg]=\"\${ArrayClean[\${x}]}\" ; 
  echo -ne \"ArrayInfo[ASeg] : \${ArrayInfo[ASeg]}\n\" > /dev/stderr ; 
  ArrayInfo[SedRepl]=\"\${ArrayInfo[SedTpl]}\" ;
  ArrayInfo[BSeg]=\"\${ArrayInfo[ASeg]/%;[a-zA-Z_+\/.-\ ]*}\" ;
  ArrayInfo[ASeg]=\"\${ArrayInfo[ASeg]/#\${ArrayInfo[BSeg]};}\" ; 
  echo -ne \"element\n\tASeg: \${ArrayInfo[ASeg]}.\n\tBSeg: \${ArrayInfo[BSeg]}\nPart Sed Filter\n\tSedRepl: \${ArrayInfo[SedRepl]}\n\n\" > /dev/stderr ;  
  ArrayInfo[BSeg]=\"\${ArrayInfo[BSeg]//\//\\\/}\" ; 
  ArrayInfo[SedRepl]=\"\${ArrayInfo[SedRepl]//__B__/\${ArrayInfo[ASeg]}}\" ; 
  ArrayInfo[SedRepl]=\"\${ArrayInfo[SedRepl]//__A__/\${ArrayInfo[BSeg]}}\" ; 
  ArrayInfo[SedFilter]=\"\${ArrayInfo[SedFilter]}\${ArrayInfo[SedRepl]};\" ; 
 done"""  ; 
 echo "${StrCmd}" ; 
}

function CleanMainHtml()
{
 local -a ArrayClean ; 
 ArrayClean[0]="file:///home/maxiste/bin/html/css/style.css;__CSS_STYLE_LOCATION__" ; 
 ArrayClean[1]="file:///home/maxiste/bin/html/calculator-interface.html;__CALCULATOR_INTERFACE__" ;
 local -A ArrayInfo ; 
 ArrayInfo[SedFilter]="" ; 
 ArrayInfo[SedTpl]="s/__A__/__B__/g" ; 
 ArrayInfo[SedRepl]="" ;
 ArrayInfo[ASeg]="" ; 
 ArrayInfo[BSeg]="" ; 
 
 eval $( GenerateSedFilter ) ; 
 echo -ne "Sed Filter:[${ArrayInfo[SedFilter]}]\n" > /dev/stderr ; 
 StrCmdEval="""/bin/sed '${ArrayInfo[SedFilter]}' $1 > $2 """ ; 
 echo -ne "CMD:[${StrCmdEval}]\n" > /dev/stderr ; 
 eval  """${StrCmdEval}""" ; 
  
}
function CleanModule()
{
 local -a ArrayClean ; 
 ArrayClean[0]="file:///home/maxiste/bin/html/css/style.css;__CSS_STYLE_LOCATION__" ; 
 ArrayClean[1]="file:///home/maxiste/bin/html/calculator-interface.html;__CALCULATOR_INTERFACE__" ;
 ArrayClean[2]="file:///home/maxiste/bin/html/js/LM317Formula-Handler.js;__FORMULA_HANDLER__" ;
 ArrayClean[3]="file:///home/maxiste/bin/html/images/labelled-lm317t-pinout.jpg;__IMAGE_LM317_PINOUT__" ;
 local -A ArrayInfo ; 
 ArrayInfo[SedFilter]="" ; 
 ArrayInfo[SedTpl]="s/__A__/__B__/g" ; 
 ArrayInfo[SedRepl]="" ;
 ArrayInfo[ASeg]="" ; 
 ArrayInfo[BSeg]="" ; 
 
 eval $( GenerateSedFilter ) ; 
 echo -ne "Sed Filter:[${ArrayInfo[SedFilter]}]\n" > /dev/stderr ; 
 StrCmdEval="""/bin/sed '${ArrayInfo[SedFilter]}' $1 > $2 """ ; 
 echo -ne "CMD:[${StrCmdEval}]\n" > /dev/stderr ; 
 eval  """${StrCmdEval}""" ;   
 
}

function CommitTemplate()
{
 local StrDate=$( date +"%Y-%m-%d, %H:%M"  ) ;
 local CurrentSubDir=$( pwd | cut -d '/' -f $(( $( pwd | sed 's/[^/]*//g' | wc -c ) )) ) ; 
 local StrTemplateCommit="""At date: __DATE__\nRepository __REPOSITORY__\nFrom Branch master\nfile: [ __FILE__ ], updating template to reflect local html and script of this project.""" ; 
 local StrCmdCommit ; 
 local StrCmdPush ;
 StrTemplateCommit=${StrTemplateCommit//__DATE__/${StrDate}} ; 
 StrTemplateCommit=${StrTemplateCommit//__REPOSITORY__/${CurrentSubDir}} ; 
 StrTemplateCommit=${StrTemplateCommit//__FILE__/$*} ; 
 StrCmdCommit="""git commit -m \"${StrTemplateCommit}\" $*""" ; 
 StrCmdPush="""git push origin master"""  ;
 echo -ne "Command to commit:[${StrCmdCommit}]\n" > /dev/stderr ;  
 echo -ne "Command to push:[${StrCmdPush}]\n" > /dev/stderr ;  
 eval ${StrCmdCommit} ; 
 eval ${StrCmdPush}
}

CleanMainHtml /home/maxiste/bin/html/Lm317-Calculator.html html/Lm317-Calculator.tpl ; 
CleanModule /home/maxiste/bin/html/calculator-interface.html html/calculator-interface.tpl;

CommitTemplate html/calculator-interface.tpl html/Lm317-Calculator.tpl 
