import subprocess,pathlib,json
R=pathlib.Path('/tmp/yf-exp001.dpIeDn')
for name,b in [('current','/opt/homebrew/bin/bd'),('historical',str(R/'older/bd'))]:
 d=R/name; repo=d/'repo'; env={'PATH':'/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin','HOME':str(d/'home'),'TMPDIR':str(d),'USER':'exp001','BD_NON_INTERACTIVE':'1'};logs=[]
 def run(label,args):
  p=subprocess.run(args,cwd=repo,env=env,text=True,capture_output=True);(d/(label+'.stdout')).write_text(p.stdout);(d/(label+'.stderr')).write_text(p.stderr);logs.append({'label':label,'argv':args,'cwd':str(repo),'exit':p.returncode});(d/'boundary-commands.json').write_text(json.dumps(logs,indent=2)); print(name,label,p.returncode,p.stdout[:110].replace('\n',' '));return p
 run('preflight',['/Users/james/.local/bin/yf','preflight','yf-beads-init','--json'])
 for case in ['early-close','resolve-wrapper']:
  p=run(case+'-pour',[b,'mol','pour','plan-execute','--var','objective=EXP001 '+case,'--var','plan_dir=docs/plans/exp001','--json']);m=json.loads(p.stdout)['id_mapping'];w=m['plan-execute.start-gate'];g=m['plan-execute.gate-start-gate']
  if case=='early-close':run(case+'-attempt',[b,'close',w,'--reason','EXP001 premature closure boundary','--json'])
  else:run(case+'-attempt',[b,'gate','resolve',w,'--reason','EXP001 wrong gate boundary','--json'])
  run(case+'-wrapper',[b,'show',w,'--json']);run(case+'-gate',[b,'show',g,'--json'])
