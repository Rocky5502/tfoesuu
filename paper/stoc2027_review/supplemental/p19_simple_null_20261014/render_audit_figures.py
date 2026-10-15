#!/usr/bin/env python3
"""Vector plots via ReportLab (no source-data modification)."""
import csv,hashlib,json,math
from pathlib import Path
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from scipy.stats import binomtest
root=Path(__file__).parent
out=root/'results'; manifest=json.loads((out/'p19_audit_manifest.json').read_text()); raw=(out/'p19_sequential_observations.csv').read_bytes()
assert hashlib.sha256(raw).hexdigest()==manifest['csv_sha256']
rows=list(csv.DictReader(raw.decode().splitlines()));assert len(rows)==24
W,H=540,330

def graph(name, error=False):
    file=out/name
    c=canvas.Canvas(str(file),pagesize=(W,H))
    c.setTitle('TFOESUU: independent P19 empirical audit')
    c.setFillColor(HexColor('#111827'));c.setFont('Helvetica-Bold',12)
    c.drawString(52,306,'P19: legal replay topology and finite-sample behavior')
    c.setFont('Helvetica',8);c.setFillColor(HexColor('#455268'))
    c.drawString(52,289,'Original synthetic CPU experiment; four concrete evaluations per replay round')
    X0,Y0,X1,Y1=72,60,505,264
    c.setStrokeColor(HexColor('#adb5bd'));c.setLineWidth(.65)
    c.line(X0,Y0,X0,Y1);c.line(X0,Y0,X1,Y0)
    ds=[.025,.035,.05,.07,.1,.14]
    xcoord=lambda d: X0+(math.log(d)-math.log(.02))/(math.log(.17)-math.log(.02))*(X1-X0)
    if not error:
        ymin,ymax=60,7000
        ycoord=lambda y:Y0+(math.log(y)-math.log(ymin))/(math.log(ymax)-math.log(ymin))*(Y1-Y0)
        ticks=[100,250,500,1000,2500,5000]
        c.setFont('Helvetica',8)
        for v in ticks:
            y=ycoord(v);c.setStrokeColor(HexColor('#e3e7eb'));c.line(X0,y,X1,y);c.setFillColor(HexColor('#455268'));c.drawRightString(X0-8,y-3,str(v))
        method=[('matched','#147d8a','Match + high control'),('boundary','#a45d32','Boundary only')]
        c.setFont('Helvetica',8)
        for mode,color,label in method:
            data=sorted((row for row in rows if row['mode']==mode and row['truth']=='null'),key=lambda z:float(z['d']))
            c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(color));c.setLineWidth(1.6)
            pts=[]
            for z in data:
                x=xcoord(float(z['d']));mean=float(z['mean_concrete_executions']); y=ycoord(mean)
                sem=float(z['sem_concrete_executions']); low=max(ymin,mean-1.96*sem);high=mean+1.96*sem
                c.setLineWidth(.7);c.line(x,ycoord(low),x,ycoord(high));c.line(x-2.5,ycoord(low),x+2.5,ycoord(low));c.line(x-2.5,ycoord(high),x+2.5,ycoord(high))
                c.circle(x,y,2.75,stroke=1,fill=1)
                pts.append((x,y))
            c.setLineWidth(1.6)
            for (x,y),(x2,y2) in zip(pts,pts[1:]):c.line(x,y,x2,y2)
        c.setFillColor(HexColor('#147d8a'));c.circle(275,260,3,stroke=0,fill=1);c.setFillColor(HexColor('#455268'));c.drawString(283,257,'Matched control (slope -1.03)')
        c.setFillColor(HexColor('#a45d32'));c.circle(420,260,3,stroke=0,fill=1);c.setFillColor(HexColor('#455268'));c.drawString(428,257,'Boundary (-1.87)')
        c.setFont('Helvetica',8);c.drawCentredString(16,174,'Mean concrete');c.drawCentredString(16,163,'executions (null)')
    else:
        ycoord=lambda y:Y0+y/.09*(Y1-Y0)
        ticks=[0,.02,.04,.06,.08]
        for v in ticks:
            y=ycoord(v);c.setStrokeColor(HexColor('#e3e7eb'));c.line(X0,y,X1,y);c.setFillColor(HexColor('#455268'));c.setFont('Helvetica',8);c.drawRightString(X0-8,y-2.7,str(round(v,2)))
        c.setStrokeColor(HexColor('#646464'));c.setDash(4,3);c.line(X0,ycoord(.05),X1,ycoord(.05));c.setDash()
        specs=[('matched','null','#147d8a'),('matched','alternative','#407a90'),('boundary','null','#a45d32'),('boundary','alternative','#c48b55')]
        for mode,truth,color in specs:
            c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(color));pts=[]
            for row in sorted((z for z in rows if z['mode']==mode and z['truth']==truth),key=lambda z:float(z['d'])):
                x=xcoord(float(row['d']));yy=float(row['observed_error_rate']);y=ycoord(yy)
                interval=binomtest(int(row['error_count']),int(row['n_trials'])).proportion_ci(.95,method='exact')
                lo=ycoord(interval.low);hi=ycoord(interval.high)
                c.setLineWidth(.65);c.line(x,lo,x,hi);c.line(x-2,lo,x+2,lo);c.line(x-2,hi,x+2,hi)
                c.circle(x,y,2.3,stroke=0,fill=1);pts.append((x,y))
            c.setLineWidth(.95)
            for (x,y),(x2,y2) in zip(pts,pts[1:]):c.line(x,y,x2,y2)
        c.setFont('Helvetica',8);c.setFillColor(HexColor('#455268'));c.drawString(84,248,'Dashed line: delta = 0.05; bars: exact binomial 95% CIs')
        c.drawCentredString(18,174,'Observed error')
        c.drawCentredString(18,162,'fraction')
    c.setFont('Helvetica',8);c.setFillColor(HexColor('#455268'))
    for d in ds:
        x=xcoord(d);c.drawCentredString(x,Y0-14,('%g'%d))
    c.setFont('Helvetica',9);c.drawCentredString((X0+X1)/2,24,'Differential patch size d (log-spaced positions)')
    c.save()
    p=fitz.open(str(file))[0]
    p.get_pixmap(matrix=fitz.Matrix(2.3,2.3),alpha=False).save(str(file.with_suffix('.png')))
    print('rendered',file.name)

graph('p19_executions_vs_patch_size.pdf')
graph('p19_observed_errors.pdf',error=True)
