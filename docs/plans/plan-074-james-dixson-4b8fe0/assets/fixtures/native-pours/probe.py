import subprocess,os,json,pathlib,shutil
R=pathlib.Path('/tmp/yf-exp001.dpIeDn')
# Whitelist, not subtraction: no inherited BEADS_*, BD_*, GIT_*, XDG_*, PIM_* or tracker resolver values.
def probe(name, binary):
 d=R/name; d.mkdir(exist_ok=True); h=d/'home';h.mkdir(exist_ok=True); repo=d/'repo';repo.mkdir(exist_ok=True)
 env={'PATH':'/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin','HOME':str(h),'TMPDIR':str(d),'USER':'exp001','BD_NON_INTERACTIVE':'1'}
 log=[]
 def run(label,args):
  p=subprocess.run(args,cwd=repo,env=env,text=True,capture_output=True)
  (d/(label+'.stdout')).write_text(p.stdout);(d/(label+'.stderr')).write_text(p.stderr)
  log.append({'label':label,'argv':args,'cwd':str(repo),'exit':p.returncode})
  (d/'commands.json').write_text(json.dumps(log,indent=2))
  print(name,label,p.returncode,p.stdout[:170].replace('\n',' '))
  return p
 run('git-init',['git','init']);run('git-name',['git','config','user.name','EXP001']);run('git-email',['git','config','user.email','exp001@example.invalid'])
 run('version',[binary,'--version']);run('init',[binary,'init','--skip-hooks','--skip-agents','--prefix','probe'])
 run('local-only',[binary,'config','set','dolt.local-only','true'])
 p=run('status',[binary,'status','--json']);data=json.loads(p.stdout);assert not data.get('error')
 (repo/'.beads/formulas').mkdir(exist_ok=True)
 shutil.copyfile('/Users/james/.agents/skills/yf-plan/formulas/plan-execute.formula.toml',repo/'.beads/formulas/plan-execute.formula.toml')
 p=run('pour',[binary,'mol','pour','plan-execute','--var','objective=EXP001 owned native pour','--var','plan_dir=docs/plans/exp001','--json'])
 if p.returncode:return
 m=json.loads(p.stdout)['id_mapping']; w=m['plan-execute.start-gate'];g=m['plan-execute.gate-start-gate']
 run('list',[binary,'list','--all','--include-gates','--limit','0','--json'])
 for role,id in [('wrapper',w),('gate',g),('root',m['plan-execute'])]:run('show-'+role,[binary,'show',id,'--json'])
 run('gate-show-wrapper',[binary,'gate','show',w,'--json'])
 run('resolve-gate',[binary,'gate','resolve',g,'--reason','EXP001 scratch consent only','--json'])
 run('after-resolve-wrapper',[binary,'show',w,'--json'])
 run('after-resolve-gate',[binary,'show',g,'--json'])
 run('close-wrapper',[binary,'close',w,'--reason','EXP001 scratch wrapper closure','--json'])
 run('final-list',[binary,'list','--all','--include-gates','--limit','0','--json'])
if __name__=='__main__':
 import sys
 probe(sys.argv[1],sys.argv[2])
