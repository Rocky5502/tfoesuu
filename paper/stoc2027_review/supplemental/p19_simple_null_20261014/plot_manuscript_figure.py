"""Create compact grayscale vector figure from hash-verified, frozen P19 CSV.
Requires: reportlab. No original experimental result or hash is modified.
"""
import csv, hashlib, json, math
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, Color
base=Path(__file__).resolve().parent
m=json.loads((base/'results/p19_audit_manifest.json').read_text(encoding='utf-8'))
p=base/'results/p19_sequential_observations.csv'
assert hashlib.sha256(p.read_bytes()).hexdigest()==m['csv_sha256']
rows=list(csv.DictReader(p.open(encoding='utf-8')))
W,H=504,254
outfile=base.parent.parent/'figures/p19_sequential_costs_20261014.pdf'
c=canvas.Canvas(str(outfile),pagesize=(W,H))
c.setTitle('Finite-grid replay-group execution costs')
L,B,R,T=65,49,480,227
xd=m['patch_sizes'];lo,hi=min(xd),max(xd); ymin,ymax=60,6500
def xmap(x): return L+(R-L)*(math.log(x)-math.log(lo))/(math.log(hi)-math.log(lo))
def ymap(y): return B+(T-B)*(math.log(y)-math.log(ymin))/(math.log(ymax)-math.log(ymin))
c.setLineWidth(.6)
for v in [100,250,500,1000,2500,5000]:
 y=ymap(v);c.setStrokeColor(Color(.87,.87,.87));c.line(L,y,R,y)
 c.setFillColor(black);c.setFont('Helvetica',8);c.drawRightString(L-8,y-3,str(v))
c.setStrokeColor(black);c.setLineWidth(.85);c.line(L,B,L,T);c.line(L,B,R,B)
c.setFont('Helvetica',8)
for x in xd:
 xx=xmap(x);c.line(xx,B,xx,B-3)
 c.drawCentredString(xx,B-14,f'{x:g}')
c.setFont('Helvetica',9)
c.drawCentredString((L+R)/2,15,'Differential patch size d')
c.saveState();c.translate(14,(B+T)/2);c.rotate(90);c.drawCentredString(0,0,'Mean charged executions under the null');c.restoreState()
for j,(mode,label) in enumerate([('matched','Matched control: fixed null horizon'),('boundary','Boundary-only: observed sequential stopping')]):
 v=sorted((r for r in rows if r['mode']==mode and r['truth']=='null'),key=lambda r:float(r['d']))
 col=Color(.12,.12,.12) if j==0 else Color(.40,.40,.40)
 c.setStrokeColor(col);c.setFillColor(col);c.setLineWidth(1.6)
 c.setDash([] if j==0 else [4,2])
 pts=[(xmap(float(r['d'])),ymap(float(r['mean_concrete_executions']))) for r in v]
 for (a,b),(d,e) in zip(pts,pts[1:]): c.line(a,b,d,e)
 c.setDash([])
 for r,(x,y) in zip(v,pts):
  if j==0: c.circle(x,y,2.7,stroke=1,fill=1)
  else:
   c.rect(x-2.6,y-2.6,5.2,5.2,stroke=1,fill=0)
   mid=float(r['mean_concrete_executions']); sem=float(r['sem_concrete_executions']);lo2=max(ymin,mid-1.96*sem);hi2=min(ymax,mid+1.96*sem)
   yl,yu=ymap(lo2),ymap(hi2);c.setLineWidth(.65);c.line(x,yl,x,yu);c.line(x-2.2,yl,x+2.2,yl);c.line(x-2.2,yu,x+2.2,yu)
  c.setLineWidth(1.6)
 ly=244-j*13
 c.setLineWidth(1.4);c.setDash([] if j==0 else [4,2]);c.line(143,ly,170,ly);c.setDash([]);c.setFillColor(black);c.setFont('Helvetica',8);c.drawString(176,ly-3,label)
c.showPage();c.save();print(outfile)
