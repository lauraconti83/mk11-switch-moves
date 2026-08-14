import base64,gzip,json,re,urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
URL='https://icemantraveler.github.io/mkksg/mk11/combos_switch.htm'
CATS=['Basic Attacks','Jumping Attacks','Hop Attacks','Getup Attacks','Flawless Block Attacks','Throws','Roll Escapes','Air Escape','Combo Attacks']
DIRS=set('F B U D'.split()); BUTTONS=set('Y X B A L R ZL ZR'.split())
def parse_step(s):
 s=s.strip()
 if s.startswith('(') and s.endswith(')'): s=s[1:-1].strip()
 toks=[t.strip() for t in re.split(r'\+',s) if t.strip()]; dirs=[]; buttons=[]; misc=[]
 for t in toks:
  if t in DIRS or (t and set(t)<=DIRS): dirs.extend(list(t))
  elif t in BUTTONS: buttons.append(t)
  else: misc.append(t)
 return {'type':'simultaneous' if '+' in s else 'press','directions':dirs,'buttons':buttons,'misc':misc,'raw':s}
def parse_input(inp):
 inp=re.sub(r'\s*\[[^\]]*\]\s*$','',inp).strip(); parts=[]; cur=''; depth=0
 for ch in inp:
  if ch=='(': depth+=1
  elif ch==')': depth=max(0,depth-1)
  if ch=='/' and depth==0: parts.append(cur); cur=''
  else: cur+=ch
 parts.append(cur); out=[]
 for alt in parts:
  seq=[]; cur=''; depth=0
  for ch in alt:
   if ch=='(': depth+=1
   elif ch==')': depth=max(0,depth-1)
   if ch==',' and depth==0:
    if cur.strip(): seq.append(cur.strip())
    cur=''
   else: cur+=ch
  if cur.strip(): seq.append(cur.strip())
  out.append([parse_step(x) for x in seq if x.strip()])
 return out
def parse_document(text):
 soup=BeautifulSoup(text,'html.parser'); anchors=[a for a in soup.find_all('a',attrs={'name':True}) if a.find('img')]; chars=[]
 for a in anchors:
  name=a.get('name','').strip(); b=a.find_next('b')
  if not name or not b: continue
  display=b.get_text(' ',strip=True)
  if display=="D 'Vorah": display="D'Vorah"
  if not display or len(display)>40: continue
  moves=[]; cat=None
  for el in a.next_elements:
   if el is not a and getattr(el,'name',None)=='a' and el.get('name') and el.find('img'): break
   if getattr(el,'name',None)!='p' or 'combos' not in (el.get('class') or []): continue
   for frag in el.get('data-original','').split('<br>'):
    frag=frag.strip()
    if not frag: continue
    text=BeautifulSoup(frag,'html.parser').get_text('',strip=True)
    if not text: continue
    if text.endswith(':') and text[:-1] in CATS: cat=text[:-1]; continue
    if ':' not in text or not cat: continue
    mn,inp=text.split(':',1); mn=mn.strip(); inp=inp.strip()
    if not mn: continue
    starred=mn.startswith('*'); mn=mn.lstrip('*').strip(); damage=None
    md=re.search(r'\[([^\]]*%|N/A%)\]',inp)
    if md: damage=md.group(1)
    inp_clean=re.sub(r'\s*\[[^\]]*\]\s*',' ',inp).strip(); notes=[]
    for m in re.finditer(r'\(([^()]*(?:Hold|Release|Cancel|Delay|Amplify|Ability|Barrage|Parasite|Manhandled|Terraformer|Vice Grip|Cybernetic Override|Death Spear Kombo|Burning Hammer|Commando Ability)[^()]*)\)',inp_clean,re.I): notes.append(m.group(1).strip())
    note='; '.join(notes) if notes else None
    if notes: inp_clean=re.sub(r'\s*\([^()]*?(?:Hold|Release|Cancel|Delay|Amplify|Ability|Barrage|Parasite|Manhandled|Terraformer|Vice Grip|Cybernetic Override|Death Spear Kombo|Burning Hammer|Commando Ability)[^()]*\)','',inp_clean,flags=re.I).strip()
    moves.append({'name':mn,'category':cat,'input_raw':inp_clean,'alternatives':parse_input(inp_clean),'damage':damage,'note':note,'starred':starred})
  if moves: chars.append({'name':display,'moves':moves})
 return chars
def main():
 source=Path('combos_switch.htm')
 text=source.read_text(encoding='utf-8') if source.exists() else urllib.request.urlopen(URL,timeout=30).read().decode('utf-8','replace')
 chars=parse_document(text); total=sum(len(c['moves']) for c in chars)
 if len(chars)!=38 or total!=1595: raise SystemExit(f'Unexpected extraction: {len(chars)} characters, {total} moves')
 db={'game':'Mortal Kombat 11 (2019)','platform':'Nintendo Switch','source':URL,'source_updated':'2026-06-01','legend':{'Y':'Front Punch','X':'Back Punch','B':'Front Kick','A':'Back Kick','L':'Throw','R':'Stage Interaction / Amplify','ZL':'Flip Stance','ZR':'Block','F':'Forward','B_direction':'Back','U':'Up','D':'Down'},'characters':chars}
 out=Path('data'); out.mkdir(exist_ok=True); raw=json.dumps(db,ensure_ascii=False,separators=(',',':')).encode(); Path(out/'mk11-database.json').write_bytes(raw); encoded=base64.b64encode(gzip.compress(raw,9)).decode(); Path(out/'db.js').write_text("window.MK11_DB_GZIP_B64='"+encoded+"';\n",encoding='utf-8'); print(f'Built {len(chars)} characters / {total} moves')
if __name__=='__main__': main()
