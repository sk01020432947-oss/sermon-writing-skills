import wave, math, struct, random
SR=44100; BPM=94; B=60/BPM; DUR=38.5; N=int(SR*DUR)
buf=[0.0]*N; rnd=random.Random(94)
def add(t0, fn, length):
    i0=int(t0*SR)
    for i in range(int(length*SR)):
        j=i0+i
        if j>=N: break
        buf[j]+=fn(i/SR)
def kick(t): f=45+75*math.exp(-t*30); return 0.9*math.sin(2*math.pi*f*t)*math.exp(-t*9)
noise=[rnd.uniform(-1,1) for _ in range(SR*2)]
def snare(t): return (0.35*noise[int(t*SR)]+0.25*math.sin(2*math.pi*190*t))*math.exp(-t*22)
def hat(t): i=int(t*SR); return 0.12*(noise[i+5000]-noise[i+5001])*math.exp(-t*90)
def crash(t): i=int(t*SR)%len(noise); return 0.25*(noise[i]-noise[i-1])*math.exp(-t*1.8)
def saw(f,t): x=f*t; return 2*(x-math.floor(x+0.5))
ROOTS=[110.0,87.31,130.81,98.0]  # Am F C G
TRI={110.0:[220,261.63,329.63],87.31:[174.61,220,261.63],130.81:[261.63,329.63,392],98.0:[196,246.94,293.66]}
CUTS=[0,2,4,6,8,9,11,13,15,17,19,21,23,24,25,27,29,30,32,34,36,37,40,42,44,46,48,50,52,53,56]
END_DRUMS=56
nb=int(DUR/B)+1
for b in range(nb):
    t=b*B; root=ROOTS[(b//4)%4]
    if b<END_DRUMS:
        if b%2==0: add(t,kick,0.5)
        else: add(t,snare,0.3)
        for h in (0,0.5): add(t+h*B,hat,0.08)
        for h in (0,0.5):
            f=root/2*(2 if h else 1)
            add(t+h*B,lambda x,f=f:0.22*saw(f,x)*math.exp(-x*6),B/2)
    if b%4==0:
        ln=min(4*B,DUR-t)
        for f in TRI[root]: add(t,lambda x,f=f,ln=ln:0.035*math.sin(2*math.pi*f*x)*min(1,x*4,(ln-x)*4),ln)
for c in CUTS:
    root=ROOTS[(c//4)%4]
    for f in TRI[root]: add(c*B,lambda x,f=f:0.06*(1 if math.sin(2*math.pi*f*2*x)>0 else -1)*math.exp(-x*18),0.2)
add(36*B,crash,0.6)  # BOOM hit
# final card: crash + long chord to the end
add(53*B,crash,DUR-53*B)
ln=DUR-53*B
for f in [220,261.63,329.63,440]: add(53*B,lambda x,f=f:0.06*math.sin(2*math.pi*f*x)*math.exp(-x*0.25)*min(1,(ln-x)*2),ln)
m=max(abs(v) for v in buf); g=0.89/m
with wave.open('music.wav','wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h',int(v*g*32767)) for v in buf))
