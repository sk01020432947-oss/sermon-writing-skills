# 24 run2: 120BPM, D minor, four-on-floor + offbeat open hat + clap 2/4 + 16th arp bass, sweeps into cuts
import wave, math, struct, random, array, sys
SR=44100; DUR=16.0; N=int(SR*DUR); B=0.5
buf=array.array('d',[0.0])*N
rnd=random.Random(24)
noise=[rnd.uniform(-1,1) for _ in range(SR)]
def add(t0,fn,length,gain):
    i0=int(t0*SR)
    for k in range(int(length*SR)):
        i=i0+k
        if 0<=i<N: buf[i]+=gain*fn(k/SR)
def kick(t): return math.sin(2*math.pi*(50*t+90*(1-math.exp(-t*38))/38))*math.exp(-t*7)
def clap(t):
    e=sum(math.exp(-max(0,t-d)*60)*(t>=d) for d in (0,0.011,0.022))/3+math.exp(-t*14)*0.6
    return noise[int(t*SR*1.7)%SR]*e
def ohat(t):
    i=int(t*SR); return (noise[(i*5)%SR]-noise[(i*5+2)%SR])*0.5*math.exp(-t*22)
def sq(f,t): return 1.0 if (f*t)%1<0.5 else -1.0
def saw(f,t): x=f*t; return 2*(x-math.floor(x+0.5))
roots=[73.42,58.27,87.31,65.41]   # D Bb F C
END=13.5
for b in range(int(END/B)):
    t=b*B
    add(t,kick,0.4,0.95)
    add(t+B/2,ohat,0.18,0.16)
    if b%2==1: add(t,clap,0.3,0.42)
    root=roots[(b//4)%4]
    for s,mul in enumerate((1,2,1.5,2)):  # 16th arp
        f=root*mul
        add(t+s*B/4,lambda x,f=f: (sq(f,x)*0.5+saw(f/2,x)*0.5)*math.exp(-x*14)*min(1,x*400),B/4*0.95,0.16)
cuts=[2,4,6,8,10,11.5,12.5,13.5]
for c in cuts:  # noise riser before, impact on cut
    add(c-0.5,lambda x: noise[int(x*SR*0.9)%SR]*(x/0.5)**2*0.6,0.5,0.22)
    add(c,lambda x: math.sin(2*math.pi*(38*x))*math.exp(-x*4)+noise[int(x*SR)%SR]*math.exp(-x*18)*0.5,0.6,0.5)
# final: low boom + Dm9 pad
add(END,lambda x: noise[int(x*SR*1.3)%SR]*math.exp(-x*1.8),2.0,0.22)
add(END,lambda x: sum(saw(146.83*m,x)+saw(146.83*m*1.004,x) for m in (1,1.189,1.498,2.245))/8*math.exp(-x*0.7)*min(1,x*30),DUR-END,0.3)
peak=max(abs(v) for v in buf) or 1
w=wave.open(sys.argv[1],'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
fade=int(0.5*SR)
w.writeframes(b''.join(struct.pack('<h',int(32000*0.9*buf[i]/peak*min(1,(N-i)/fade))) for i in range(N)))
w.close()
