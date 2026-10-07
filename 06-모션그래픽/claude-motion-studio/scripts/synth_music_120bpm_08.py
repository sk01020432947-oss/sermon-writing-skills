# 08 one-liner showreel: 120BPM, Am-F-C-G, kick/hat/bass + riser into every chapter cut + impact on it
import wave, math, struct, random, array
SR=44100; DUR=16.0; N=int(SR*DUR); B=0.5
buf=array.array('d',[0.0])*N
rnd=random.Random(8)
noise=[rnd.uniform(-1,1) for _ in range(SR)]
def add(t0,fn,length,gain):
    i0=int(t0*SR)
    for k in range(int(length*SR)):
        i=i0+k
        if 0<=i<N: buf[i]+=gain*fn(k/SR)
def kick(t): return math.sin(2*math.pi*(48*t+80*(1-math.exp(-t*32))/32))*math.exp(-t*8)
def hat(t): i=int(t*SR); return (noise[(i*7)%SR]-noise[(i*7+1)%SR])*0.5*math.exp(-t*80)
def saw(f,t): x=f*t; return 2*(x-math.floor(x+0.5))
roots=[55.0,43.65,65.41,49.0]   # A F C G
END=13.5                         # drums stop on the logo
for b in range(int(END/B)):
    t=b*B
    add(t,kick,0.4,0.9)
    for h in (0.25,0.5,0.75): add(t+h*B,hat,0.05,0.16 if h==0.5 else 0.08)
    root=roots[(b//4)%4]
    for h,mul in ((0,1),(0.5,2)):
        f=root*mul
        add(t+h*B,lambda x,f=f: saw(f,x)*math.exp(-x*7)*min(1,x*300),B*0.45,0.2)
CUTS=[2,3.5,5.5,7.5,9.5,11,11.25,11.5,12,12.25,12.5,13,13.5]   # = CH starts in index.html
for c in CUTS:
    L=0.35 if c-0.35>=0 else c
    add(c-L,lambda x,L=L: noise[int(x*SR*1.9)%SR]*(x/L)**2,L,0.18)            # noise riser into the cut
    add(c,lambda x: math.sin(2*math.pi*(40*x+60*(1-math.exp(-x*20))/20))*math.exp(-x*6),0.5,0.55)  # impact
# logo: crash + long A-minor chord to the end
add(13.5,lambda x: noise[int(x*SR*1.3)%SR]*math.exp(-x*1.4),2.5,0.22)
add(13.5,lambda x: sum(saw(220*m,x) for m in (1,1.189,1.498))/3*math.exp(-x*0.8),DUR-13.5,0.2)
peak=max(abs(v) for v in buf) or 1
fade=int(0.5*SR)
with wave.open('music.wav','wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h',int(32000*0.9*buf[i]/peak*min(1,(N-i)/fade))) for i in range(N)))
