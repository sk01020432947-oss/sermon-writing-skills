# 검증된 학자·작품 인용 안전 카탈로그

본 파일은 sermon-text-analysis-multimethod가 응답 안에 학자·작품·출판사·연도를 인용할 때 **참조할 수 있는 화이트리스트**다. 본 카탈로그에 *있는* 항목만 정확 인용한다. *없는* 항목은 회피하거나 "표준 학술 주석 직접 확인 권장"으로 우회한다.

데이터 원본: `references/data/verified_authors.json` (구조화된 JSON). 본 문서는 인간이 읽는 요약.

---

## 사용 원칙

1. **인용 전 항상 카탈로그 확인** — 학자명·작품·연도·출판사를 응답에 쓰기 전, 본 카탈로그에 있는지 확인.
2. **WARNING 항목 절대 준수** — 일부 학자에는 *특정 본문에 대한 인용 회피* 경고 있음 (예: Joanna Dewey는 마가 4:35-41 키아스무스 직접 옹호자 아님).
3. **없으면 우회** — 카탈로그에 없으면 *"BDAG/HALOT/표준 주석을 직접 확인 권장"*으로 대체.
4. **Python 검증 도구 호출** — 의심스러우면 `python3 references/tools/citation_verifier.py author "이름" "작품" 연도 출판사`로 검증.

---

## 주요 주석 시리즈 (출판사 검증)

| 약어 | 풀네임 | 출판사 | 전통 |
|------|-------|--------|------|
| NICOT | New International Commentary OT | Eerdmans | 복음주의 개혁 |
| NICNT | New International Commentary NT | Eerdmans | 복음주의 개혁 |
| NIGTC | New International Greek Testament Commentary | Eerdmans/Paternoster | 복음주의 비평 |
| BECNT | Baker Exegetical Commentary on the NT | Baker Academic | 복음주의 주해 |
| WBC | Word Biblical Commentary | Word Books(1982-2009) / Zondervan(2009-) | 복음주의 |
| PNTC | Pillar New Testament Commentary | Eerdmans/Apollos | 복음주의 |
| ICC | International Critical Commentary | T&T Clark | 학술 비평 |
| AB | Anchor Bible | Doubleday(1956-2007) / Yale UP(2008-) | 학술 비평 |
| Hermeneia | Hermeneia | Fortress Press | 학술 비평 |
| NIVAC | NIV Application Commentary | Zondervan | 복음주의 적용 |
| EBC | Expositor's Bible Commentary | Zondervan | 복음주의 |
| TNTC/TOTC | Tyndale NT/OT Commentary | IVP/Eerdmans | 복음주의 간결 |

**중요**: Anchor Bible 시리즈는 2007년까지 Doubleday, 2008년부터 Yale UP로 이전. 초판 인용 시 정확히 표기.

---

## 검증된 표준 원어 자료

- **NA28** Nestle-Aland Novum Testamentum Graece, 28th edition (Deutsche Bibelgesellschaft, 2012)
- **UBS5** United Bible Societies Greek NT, 5th edition (Deutsche Bibelgesellschaft, 2014)
- **BHS** Biblia Hebraica Stuttgartensia (Deutsche Bibelgesellschaft, 1977; rev. 1997)
- **BHQ** Biblia Hebraica Quinta (Deutsche Bibelgesellschaft, 2004- 진행중)
- **Rahlfs-Hanhart** Septuaginta (LXX) editio altera (Deutsche Bibelgesellschaft, 2006)
- **BDAG** Bauer-Danker Greek-English Lexicon, 3rd ed. (Univ. of Chicago Press, 2000)
- **HALOT** Hebrew and Aramaic Lexicon of the OT (Brill, 1994-2000, 5 vols.)
- **BDB** Brown-Driver-Briggs Hebrew and English Lexicon (Hendrickson reprint of 1906)
- **LSJ** Liddell-Scott-Jones Greek-English Lexicon (9th ed., Oxford, 1996)
- **TDNT** Theological Dictionary of the NT, eds. Kittel & Friedrich (Eerdmans, 1964-1976, 10 vols.)
- **TDOT** Theological Dictionary of the OT, eds. Botterweck & Ringgren (Eerdmans, 1974- 진행중)
- **NIDOTTE** New International Dictionary of OT Theology and Exegesis, ed. VanGemeren (Zondervan, 1997, 5 vols.)
- **NIDNTTE** New International Dictionary of NT Theology and Exegesis, ed. Silva (Zondervan, 2014, 5 vols.)

---

## 검증된 학자 인용 카탈로그

### 종교개혁·정통 핵심

- **Calvin, John (1509-1564)** — *Institutes of the Christian Religion* (1559 최종판) / 신·구약 주석 (Geneva corpus).
- **Augustine of Hippo (354-430)** — *Confessions* (Confessiones, 397-400) / *City of God* (De Civitate Dei, 413-426) / *On Christian Doctrine* (De Doctrina Christiana, 397/426) / *On the Trinity* (De Trinitate, 399-419) / *Tractates on the Gospel of John* / *Expositions of the Psalms* (Enarrationes in Psalmos).
- **Luther, Martin (1483-1546)** — *Lectures on Romans* (1515-1516, WA 56) / *Lectures on Galatians* (1535, WA 40) / *Bondage of the Will* (De servo arbitrio, 1525). Weimar Ausgabe(WA) 표준 비평본.
- **Bavinck, Herman (1854-1921)** — *Reformed Dogmatics* (Gereformeerde Dogmatiek 1895-1901; ET Baker Academic 2003-2008, 4권) / *Our Reasonable Faith* / *Christian Worldview*.
- **Lloyd-Jones, D. Martyn (1899-1981)** — *Studies in the Sermon on the Mount* (IVP, 1959-1960, 2권) / *Romans* 시리즈 (Banner of Truth, 1970-2003, 14권) / *Preaching and Preachers* (Hodder & Stoughton, 1971).
- **Murray, John (1898-1975)** — *The Epistle to the Romans* (NICNT, Eerdmans, 1959/1965) / *Principles of Conduct* (Eerdmans, 1957) / *Redemption Accomplished and Applied* (Eerdmans, 1955).

### 현대 복음주의 주석가

- **Wallace, Daniel B.** — *Greek Grammar Beyond the Basics* (Zondervan, 1996). 신약 헬라어 문법 표준 참조.
- **Carson, D.A.** — *Exegetical Fallacies* (Baker, 1984; 2판 1996) / *The Gospel According to John* (PNTC, Eerdmans/Apollos, 1991) / *Matthew* (EBC, Zondervan, 1984/2010 rev.).
- **Moo, Douglas J.** — *The Epistle to the Romans* (NICNT, Eerdmans, 1996; 2판 2018) / *Galatians* (BECNT, Baker Academic, 2013) / *The Letter of James* (PNTC, Eerdmans, 2000).
- **Schreiner, Thomas R.** — *Romans* (BECNT, Baker Academic, 1998; 2판 2018) / *Galatians* (ZECNT, Zondervan, 2010) / *1, 2 Peter, Jude* (NAC, B&H, 2003).
- **Bruce, F.F. (1910-1990)** — *The Epistle to the Galatians* (NIGTC, Eerdmans/Paternoster, 1982) / *The Book of Acts* (NICNT, Eerdmans, 1988 rev.) / *The Epistle to the Hebrews* (NICNT, Eerdmans, 1964; rev. 1990).
- **Morris, Leon (1914-2006)** — *The Gospel According to John* (NICNT, Eerdmans, 1971; rev. 1995) / *The Epistle to the Romans* (PNTC, Eerdmans, 1988).
- **Hoehner, Harold W.** — *Ephesians: An Exegetical Commentary* (Baker Academic, 2002).
- **Wenham, Gordon J.** — *Genesis 1-15* (WBC, Word, 1987) / *Genesis 16-50* (WBC, Word, 1994) / *Numbers* (TOTC, IVP, 1981).
- **France, R.T. (1938-2012)** — *The Gospel of Matthew* (NICNT, Eerdmans, 2007) / *The Gospel of Mark* (NIGTC, Eerdmans/Paternoster, 2002).
- **Stein, Robert H.** — *Mark* (BECNT, Baker Academic, 2008) / *Luke* (NAC, B&H, 1992).
- **Beale, G.K.** — *The Book of Revelation* (NIGTC, Eerdmans/Paternoster, 1999) / *A New Testament Biblical Theology* (Baker Academic, 2011).
- **Bauckham, Richard** — *The Climax of Prophecy* (T&T Clark, 1993) / *Jesus and the Eyewitnesses* (Eerdmans, 2006; 2판 2017).
- **McCarter, P. Kyle Jr.** — *I Samuel* (AB 8, Doubleday, 1980) / *II Samuel* (AB 9, Doubleday, 1984).
- **Tsumura, David Toshio** — *The First Book of Samuel* (NICOT, Eerdmans, 2007) / *The Second Book of Samuel* (NICOT, Eerdmans, 2019).
- **Cranfield, C.E.B. (1915-2015)** — *A Critical and Exegetical Commentary on the Epistle to the Romans* (ICC, T&T Clark, 1975/1979, 2권).
- **Davies, W.D. & Allison, Dale C.** — *Matthew* (ICC, T&T Clark, 1988-1997, 3권).
- **Allison, Dale C. Jr.** — *The Sermon on the Mount: Inspiring the Moral Imagination* (Crossroad, 1999) / *The New Moses: A Matthean Typology* (Fortress, 1993).
- **Lenski, R.C.H. (1864-1936)** — *Commentary on the New Testament* (Wartburg/Augsburg, 1933-1946, 12권).

### 비평 학계 (균형 인용)

- **Brueggemann, Walter** — *Genesis* (Interpretation, John Knox, 1982) / *The Message of the Psalms* (Augsburg, 1984) / *Praying the Psalms* (Augsburg, 1982; rev. 2007) / *Theology of the Old Testament* (Fortress, 1997). 메인라인 개혁주의.
- **Marcus, Joel** — *Mark 1-8* (AB 27, Doubleday, 2000; reprinted Yale UP) / *Mark 8-16* (AB 27A, Yale UP, 2009). **WARNING: 초판 출판사 = Doubleday.**
- **Wellhausen, Julius (1844-1918)** — *Geschichte Israels I* (Berlin, 1878) / *Prolegomena zur Geschichte Israels* (Berlin, 1883; ET 1885). JEDP 자료가설.
- **Gunkel, Hermann (1862-1932)** — *Genesis* (HKAT, 1901) / *Einleitung in die Psalmen* (Vandenhoeck & Ruprecht, 1933; 사후, Joachim Begrich 완성·출판). 양식비평(Formgeschichte) 창시자.
- **Noth, Martin (1902-1968)** — *Überlieferungsgeschichtliche Studien* (Halle, 1943) — 신명기사가 가설.
- **Rost, Leonhard (1896-1979)** — *Die Überlieferung von der Thronnachfolge Davids* (Stuttgart, 1926). 왕위계승사화 가설.
- **Robinson, J.A.T. (1919-1983)** — *Redating the New Testament* (SCM Press, 1976). 초기 연대 가설.

### 한국 정통 핵심

- **박윤선 (1905-1988)** — 성경주석 (영음사, 1949-1979). 한국 보수 개혁주의 표준.
- **박형룡 (1897-1978)** — 교의신학 (한국기독교교육연구원, 1964-1978, 7권). 한국 장로교 합동 표준 조직신학.

### 철학·윤리 인용 (필요시)

- **Kierkegaard, Søren (1813-1855)** — *Fear and Trembling* (Frygt og Bæven, Copenhagen, 1843) / *The Sickness Unto Death* (Sygdommen til Døden, 1849).
- **O'Donovan, Oliver** — *Resurrection and Moral Order* (IVP/Eerdmans, 1986; 2판 1994).
- **Fletcher, Joseph (1905-1991)** — *Situation Ethics: The New Morality* (Westminster Press, 1966).
- **MacIntyre, Alasdair** — *After Virtue* (Univ. of Notre Dame Press, 1981; 2판 1984; 3판 2007).

---

## ⚠ 인용 회피·주의 학자 (작품 주제와 다른 본문에 적용 금지)

- **Joanna Dewey** *Markan Public Debate* (SBL Diss. 48, Scholars Press, 1980) — **마가 2:1-3:6 동심원 구조** 작품. 마가 4:35-41 키아스무스 직접 옹호자 *아님*. 본 작품을 4:35-41 키아스무스 옹호로 인용하지 말 것.
- **Mary Ann Beavis** *Mark's Audience* (JSNTSup 33, Sheffield, 1989) — **마가 4:11-12 비유 청중 설정** 작품. 마가 4:35-41과 직접 관련 *없음*. 본 작품을 4:35-41 키아스무스로 인용하지 말 것.
- **D. Winton Thomas (1901-1970)** — Cambridge Hebrew 교수. 시 23:4 צַלְמָוֶת 어원 분석으로 자주 인용되나, *1962년 특정 작품 정확 검증 어려움* — "학자들 일부의 후대 어원 분석으로 단일어원 tsalmut 제안"으로 일반화 권장.

---

## 카탈로그에 없는 학자·작품 처리 규약

본 카탈로그에 *없는* 학자·작품을 인용해야 할 때:

1. **검증 가능하면 우선 검증** — 출판사 공식 카탈로그, Worldcat, Library of Congress 등에서 확인 가능하면 본 카탈로그에 추가 권장.
2. **불확실하면 일반화** — "표준 학술 주석들" / "다수 학자들" / "현대 학계 다수설" 등으로 일반화. 특정 학자·연도 단정 금지.
3. **본문 자체로 후퇴** — 본문이 *자체로 명백히* 말하는 것에 집중. 학자 권위에 의존 줄임.
4. **솔직한 인정** — "이 본문에 대한 결정적 학술 인용은 직접 표준 주석을 확인 권장" 명시.

---

## 인용 양식 표준 (한국어 응답)

- 인명: 한국어(원어/영어, 연도) — 예: "어거스틴(Augustine, 354-430)", "칼빈(Calvin, 1509-1564)"
- 작품: *제목*(시리즈 약어, 출판사, 연도) — 예: "*Romans*(NICNT, Eerdmans, 1996)"
- 약어: 처음 등장 시 풀네임 — 예: "BDAG(Bauer-Danker Greek-English Lexicon)"
- 한국 학자: 한자·로마자 표기 가능시 — 예: "박윤선(朴允善, 1905-1988)"
