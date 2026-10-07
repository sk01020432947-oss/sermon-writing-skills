import wave, math, struct, random, array
SR=44100; DUR=20.0; N=int(SR*DUR); B=60/94
buf=array.array('d',[0.0])*N
rnd=random.Random(7)
def add(t0,fn,length,gain):
    i0=int(t0*SR)
    for k in range(int(length*SR)):
        i=i0+k
        if 0<=i<N: buf[i]+=gain*fn(k/SR)
def kick(t):
    f=45+75*math.exp(-t*30); return math.sin(2*math.pi*(45*t+75*(1-math.exp(-t*30))/30))*math.exp(-t*9)
noise=[rnd.uniform(-1,1) for _ in range(SR)]
def snare(t):
    return (noise[int(t*SR)%SR]*0.8+0.4*math.sin(2*math.pi*190*t))*math.exp(-t*22)
def hat(t):
    i=int(t*SR); return (noise[(i*7)%SR]-noise[(i*7+1)%SR])*0.5*math.exp(-t*90)
def saw(f,t): x=f*t; return 2*(x-math.floor(x+0.5))
roots=[55.0,43.65,65.41,49.0]
nb=int(DUR/B)+1
for b in range(nb):
    t=b*B
    if b>=30: break  # drums stop for the final hold
    if b%2==0: add(t,kick,0.45,0.9)
    else: add(t,snare,0.25,0.45)
    for h in (0,0.5): add(t+h*B,hat,0.06,0.25 if h else 0.18)
    root=roots[(b//4)%4]
    for h,mul in ((0,1),(0.5,2 if b%2 else 1)):
        f=root*mul
        add(t+h*B,lambda x,f=f: saw(f,x)*math.exp(-x*6)*min(1,x*200),B*0.48,0.22)
cuts=[0,4,6,8,10,12,14,16,17,18,20,22,24,26,28]
for c in cuts:
    root=roots[(c//4)%4]*4
    def stab(x,r=root): return sum(saw(r*m,x) for m in (1,1.189,1.498))/3*math.exp(-x*9)*min(1,x*300)
    add(c*B,stab,0.35,0.28)
# crash + long chord on final card
add(28*B,lambda x: noise[int(x*SR*1.3)%SR]*math.exp(-x*1.6),2.2,0.25)
add(28*B,lambda x: sum(saw(220*m,x) for m in (1,1.189,1.498))/3*math.exp(-x*0.9),20-28*B,0.18)
peak=max(abs(v) for v in buf) or 1
w=wave.open('music.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
fade=int(0.6*SR)
w.writeframes(b''.join(struct.pack('<h',int(32000*0.9*buf[i]/peak*(min(1,(N-i)/fade)))) for i in range(N)))
w.close()
