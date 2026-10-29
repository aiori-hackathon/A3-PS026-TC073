"""
Built-in test corpus. 105 cases with categories, expectations, and purposes.
Expected behavior is annotated by a human author; actual behavior is
computed at runtime by the test runner.
"""

CORPUS = [
    # --- valid basics (10) ---
    {"id":"V01","input":"at://did:plc:abc123/app.bsky.feed.post/3k2abc","category":"valid","expect":"valid","purpose":"canonical DID URI with collection and rkey"},
    {"id":"V02","input":"at://did:plc:abc123","category":"valid","expect":"valid","purpose":"bare DID authority, no path"},
    {"id":"V03","input":"at://did:plc:abc123/app.bsky.feed.post","category":"valid","expect":"valid","purpose":"collection but no rkey"},
    {"id":"V04","input":"at://alice.bsky.social/app.bsky.feed.post/3k2abc","category":"valid","expect":"valid","purpose":"handle authority"},
    {"id":"V05","input":"at://did:web:example.com/app.bsky.feed.post/3k2abc","category":"valid","expect":"valid","purpose":"did:web with dots in identifier"},
    {"id":"V06","input":"at://did:key:zQ3shokFTS3brHcDQrn82RUDfCZESWL1ZdCEJwekUDPQiYBme/app.bsky.feed.like/3k2abc","category":"valid","expect":"valid","purpose":"did:key authority"},
    {"id":"V07","input":"at://did:plc:abc123/app.bsky.feed.post/3k2abc-def","category":"valid","expect":"valid","purpose":"rkey with dash"},
    {"id":"V08","input":"at://did:plc:abc123/app.bsky.feed.post/3k2abc_def","category":"valid","expect":"valid","purpose":"rkey with underscore"},
    {"id":"V09","input":"at://did:plc:abc123/app.bsky.feed.post/3k2abc.def","category":"valid","expect":"valid","purpose":"rkey with dot"},
    {"id":"V10","input":"at://did:plc:abc123/app.bsky.feed.post/3k2abc:def","category":"valid","expect":"valid","purpose":"rkey with colon (allowed by grammar)"},

    # --- invalid basics (15) ---
    {"id":"I01","input":"http://example.com/app.bsky.feed.post/x","category":"invalid","expect":"invalid","purpose":"wrong scheme"},
    {"id":"I02","input":"at:/did:plc:abc123","category":"invalid","expect":"invalid","purpose":"single slash"},
    {"id":"I03","input":"at:","category":"invalid","expect":"invalid","purpose":"no authority"},
    {"id":"I04","input":"at://","category":"invalid","expect":"invalid","purpose":"empty authority"},
    {"id":"I05","input":"AT://did:plc:abc123/col/rkey","category":"invalid","expect":"invalid","purpose":"uppercase scheme"},
    {"id":"I06","input":"at:///app.bsky.feed.post/x","category":"invalid","expect":"invalid","purpose":"empty authority with path"},
    {"id":"I07","input":"at://did:plc:abc123/../rkey","category":"invalid","expect":"invalid","purpose":"path traversal in collection"},
    {"id":"I08","input":"at://did:plc:abc123/app.bsky.feed.post/x?foo=bar","category":"invalid","expect":"invalid","purpose":"query string not allowed"},
    {"id":"I09","input":"at://did:plc:abc123/app.bsky.feed.post/x#frag","category":"invalid","expect":"invalid","purpose":"fragment not allowed"},
    {"id":"I10","input":"at://did:plc:abc123//3k2abc","category":"invalid","expect":"invalid","purpose":"empty collection segment"},
    {"id":"I11","input":"at://did:plc:abc123/app.bsky.feed.post/","category":"invalid","expect":"invalid","purpose":"empty rkey"},
    {"id":"I12","input":"at://did:plc:abc123/app.bsky.feed.post/x/y","category":"invalid","expect":"invalid","purpose":"extra path segment"},
    {"id":"I13","input":"","category":"invalid","expect":"invalid","purpose":"empty string"},
    {"id":"I14","input":"at://did:plc:abc123/col/3k2abc/../","category":"invalid","expect":"invalid","purpose":"traversal with trailing slash"},
    {"id":"I15","input":"at://@handle.example.com/col/rkey","category":"invalid","expect":"invalid","purpose":"userinfo not allowed"},

    # --- DID internal colons (15) ---
    {"id":"D01","input":"at://did:plc:abc123/app.bsky.feed.post/x","category":"did_colon","expect":"valid","purpose":"one internal colon"},
    {"id":"D02","input":"at://did:web:example.com:8080/app.bsky.feed.post/x","category":"did_colon","expect":"review","purpose":"did:web with port-like segment — spec ambiguity"},
    {"id":"D03","input":"at://did:key:z6Mkabcdefghijklmnop/app.bsky.feed.post/x","category":"did_colon","expect":"valid","purpose":"did:key single colon"},
    {"id":"D04","input":"at://did:plc:abc123:extra/app.bsky.feed.post/x","category":"did_colon","expect":"review","purpose":"extra colon in did:plc identifier"},
    {"id":"D05","input":"at://did:ion:EiB:abc/app.bsky.feed.post/x","category":"did_colon","expect":"review","purpose":"did:ion internal colons"},
    {"id":"D06","input":"at://did:example:123:456:789/col/rkey","category":"did_colon","expect":"review","purpose":"did with many colons"},
    {"id":"D07","input":"at://did:plc:/app.bsky.feed.post/x","category":"did_colon","expect":"invalid","purpose":"empty DID identifier"},
    {"id":"D08","input":"at://did::abc/app.bsky.feed.post/x","category":"did_colon","expect":"invalid","purpose":"empty DID method"},
    {"id":"D09","input":"at://did:PLC:abc/app.bsky.feed.post/x","category":"did_colon","expect":"invalid","purpose":"uppercase DID method"},
    {"id":"D10","input":"at://did:plc:abc%20def/app.bsky.feed.post/x","category":"did_colon","expect":"review","purpose":"percent-encoded space in DID"},
    {"id":"D11","input":"at://did:plc:ABC-123_x.y/col/rkey","category":"did_colon","expect":"valid","purpose":"mixed case DID identifier"},
    {"id":"D12","input":"at://did:plc:.abc/col/rkey","category":"did_colon","expect":"invalid","purpose":"leading dot in DID"},
    {"id":"D13","input":"at://did:plc:abc./col/rkey","category":"did_colon","expect":"invalid","purpose":"trailing dot in DID"},
    {"id":"D14","input":"at://did:plc:abc-/col/rkey","category":"did_colon","expect":"invalid","purpose":"trailing dash in DID"},
    {"id":"D15","input":"at://did:plc:abc/col/rkey","category":"did_colon","expect":"valid","purpose":"minimal DID"},

    # --- handle authorities (10) ---
    {"id":"H01","input":"at://alice.bsky.social/app.bsky.feed.post/x","category":"handle","expect":"valid","purpose":"canonical handle"},
    {"id":"H02","input":"at://a.b.c/app.bsky.feed.post/x","category":"handle","expect":"valid","purpose":"short handle"},
    {"id":"H03","input":"at://alice.example/app.bsky.feed.post/x","category":"handle","expect":"valid","purpose":"two-segment handle"},
    {"id":"H04","input":"at://alice.bsky.social:8080/app.bsky.feed.post/x","category":"handle","expect":"invalid","purpose":"port in handle — not allowed"},
    {"id":"H05","input":"at://Alice.BSky.Social/app.bsky.feed.post/x","category":"handle","expect":"review","purpose":"uppercase handle — case handling"},
    {"id":"H06","input":"at://-alice.bsky.social/app.bsky.feed.post/x","category":"handle","expect":"invalid","purpose":"leading dash in handle label"},
    {"id":"H07","input":"at://alice-.bsky.social/app.bsky.feed.post/x","category":"handle","expect":"invalid","purpose":"trailing dash in handle label"},
    {"id":"H08","input":"at://alice/app.bsky.feed.post/x","category":"handle","expect":"invalid","purpose":"single-label handle"},
    {"id":"H09","input":"at://alice.bsky.social./app.bsky.feed.post/x","category":"handle","expect":"invalid","purpose":"trailing dot in handle"},
    {"id":"H10","input":"at://alice.bsky.social/app.bsky.feed.post/x/","category":"handle","expect":"invalid","purpose":"trailing slash"},

    # --- collection / rkey edge cases (10) ---
    {"id":"C01","input":"at://did:plc:abc123/app.bsky.feed.post/3k2abc","category":"path","expect":"valid","purpose":"standard NSID + rkey"},
    {"id":"C02","input":"at://did:plc:abc123/app/3k2abc","category":"path","expect":"invalid","purpose":"single-segment collection"},
    {"id":"C03","input":"at://did:plc:abc123/app.bsky.feed.post/3k2abc","category":"path","expect":"valid","purpose":"three-segment NSID"},
    {"id":"C04","input":"at://did:plc:abc123/App.Bsky.Feed.Post/3k2abc","category":"path","expect":"review","purpose":"uppercase NSID"},
    {"id":"C05","input":"at://did:plc:abc123/app.bsky.feed.post/"+"a"*513,"category":"path","expect":"invalid","purpose":"rkey over 512 chars"},
    {"id":"C06","input":"at://did:plc:abc123/app.bsky.feed.post/"+"a"*512,"category":"path","expect":"valid","purpose":"rkey exactly 512 chars"},
    {"id":"C07","input":"at://did:plc:abc123/app.bsky.feed.post/x?","category":"path","expect":"invalid","purpose":"trailing question mark"},
    {"id":"C08","input":"at://did:plc:abc123/app.bsky.feed.post/x#","category":"path","expect":"invalid","purpose":"trailing hash"},
    {"id":"C09","input":"at://did:plc:abc123/app.bsky.feed.post/ ","category":"path","expect":"invalid","purpose":"space in rkey"},
    {"id":"C10","input":"at://did:plc:abc123/app.bsky.feed.post/x/y/z","category":"path","expect":"invalid","purpose":"four path segments"},

    # --- percent encoding (10) ---
    {"id":"P01","input":"at://did:plc:abc123/app.bsky.feed.post/x%2Fy","category":"encoding","expect":"review","purpose":"encoded slash in rkey"},
    {"id":"P02","input":"at://did:plc:abc123/app.bsky.feed.post/x%ZZy","category":"encoding","expect":"invalid","purpose":"invalid percent escape"},
    {"id":"P03","input":"at://did:plc:abc123/app.bsky.feed.post/x%20y","category":"encoding","expect":"review","purpose":"encoded space"},
    {"id":"P04","input":"at://did:plc:abc123/app.bsky.feed.post/x%","category":"encoding","expect":"invalid","purpose":"truncated escape"},
    {"id":"P05","input":"at://did:plc:abc123/app.bsky.feed.post/x%3Ay","category":"encoding","expect":"review","purpose":"encoded colon"},
    {"id":"P06","input":"at://did:plc:abc123/app.bsky.feed.post/x%41","category":"encoding","expect":"valid","purpose":"encoded ASCII letter"},
    {"id":"P07","input":"at://did:plc:abc123/app.bsky.feed.post/x%2fy","category":"encoding","expect":"review","purpose":"lowercase encoded slash"},
    {"id":"P08","input":"at://did:plc:abc123/app.bsky.feed.post/x%00y","category":"encoding","expect":"review","purpose":"encoded null byte"},
    {"id":"P09","input":"at://did:plc:abc123/app.bsky.feed.post/x%2F%2F","category":"encoding","expect":"review","purpose":"double encoded slash"},
    {"id":"P10","input":"at://did:plc:abc123/app.bsky.feed.post/%E2%9C%93","category":"encoding","expect":"review","purpose":"encoded checkmark"},

    # --- unicode (10) ---
    {"id":"U01","input":"at://did:plc:abc123/app.bsky.feed.post/café","category":"unicode","expect":"review","purpose":"NFC vs NFD for café"},
    {"id":"U02","input":"at://did:plc:abc123/app.bsky.feed.post/cafe\u0301","category":"unicode","expect":"review","purpose":"NFD decomposed café"},
    {"id":"U03","input":"at://did:plc:abc123/app.bsky.feed.post/☃","category":"unicode","expect":"review","purpose":"snowman symbol"},
    {"id":"U04","input":"at://did:plc:abc123/app.bsky.feed.post/😀","category":"unicode","expect":"review","purpose":"emoji in rkey"},
    {"id":"U05","input":"at://did:plc:abc123/app.bsky.feed.post/\u4e2d\u6587","category":"unicode","expect":"review","purpose":"CJK characters"},
    {"id":"U06","input":"at://did:plc:abc123/app.bsky.feed.post/ñ","category":"unicode","expect":"review","purpose":"latin small letter n with tilde"},
    {"id":"U07","input":"at://did:plc:abc123/app.bsky.feed.post/ǆ","category":"unicode","expect":"review","purpose":"digraph (compatibility char)"},
    {"id":"U08","input":"at://did:plc:abc123/app.bsky.feed.post/ﬁ","category":"unicode","expect":"review","purpose":"ligature fi"},
    {"id":"U09","input":"at://did:plc:abc123/app.bsky.feed.post/é","category":"unicode","expect":"review","purpose":"NFC precomposed"},
    {"id":"U10","input":"at://did:plc:abc123/app.bsky.feed.post/e\u0301","category":"unicode","expect":"review","purpose":"NFD decomposed"},

    # --- malformed (10) ---
    {"id":"M01","input":"at://did:plc:abc123//","category":"malformed","expect":"invalid","purpose":"double trailing slash"},
    {"id":"M02","input":"at:///////","category":"malformed","expect":"invalid","purpose":"many slashes, no authority"},
    {"id":"M03","input":"at://did:plc:abc123/app.bsky.feed.post//x","category":"malformed","expect":"invalid","purpose":"double slash in path"},
    {"id":"M04","input":"at://did:plc:abc123\0/app.bsky.feed.post/x","category":"malformed","expect":"invalid","purpose":"null byte in authority"},
    {"id":"M05","input":"at://did:plc:abc123/app.bsky.feed.post/x\n","category":"malformed","expect":"invalid","purpose":"newline in rkey"},
    {"id":"M06","input":" at://did:plc:abc123/app.bsky.feed.post/x","category":"malformed","expect":"invalid","purpose":"leading space"},
    {"id":"M07","input":"at:// did:plc:abc123/app.bsky.feed.post/x","category":"malformed","expect":"invalid","purpose":"space after scheme"},
    {"id":"M08","input":"at://did:plc:abc123 /app.bsky.feed.post/x","category":"malformed","expect":"invalid","purpose":"space in authority"},
    {"id":"M09","input":"at://did:plc:abc123/app.bsky.feed.post/x ","category":"malformed","expect":"invalid","purpose":"trailing space"},
    {"id":"M10","input":"at:\\did:plc:abc123","category":"malformed","expect":"invalid","purpose":"backslash instead of slashes"},

    # --- conflict-inducing (10) ---
    {"id":"X01","input":"at://did:plc:abc123:8080/app.bsky.feed.post/x","category":"conflict","expect":"review","purpose":"DID identifier ending in digits may be mistaken for port"},
    {"id":"X02","input":"at://did:plc:123456/app.bsky.feed.post/x","category":"conflict","expect":"review","purpose":"all-numeric DID identifier"},
    {"id":"X03","input":"at://did:web:example.com:443/app.bsky.feed.post/x","category":"conflict","expect":"review","purpose":"did:web with real port"},
    {"id":"X04","input":"at://user:pass@host/col/rkey","category":"conflict","expect":"invalid","purpose":"userinfo syntax"},
    {"id":"X05","input":"at://host:notaport/col/rkey","category":"conflict","expect":"invalid","purpose":"non-numeric port"},
    {"id":"X06","input":"at://did:plc:abc123/col/rkey%2Fextra","category":"conflict","expect":"review","purpose":"encoded slash may be seen as path separator"},
    {"id":"X07","input":"at://did:plc:abc123/col/rkey%3Aextra","category":"conflict","expect":"review","purpose":"encoded colon"},
    {"id":"X08","input":"at://did:plc:abc123/col/rkey:extra","category":"conflict","expect":"valid","purpose":"literal colon allowed by rkey grammar"},
    {"id":"X09","input":"at://did:plc:abc123/col/%2e%2e","category":"conflict","expect":"review","purpose":"encoded parent directory"},
    {"id":"X10","input":"at://did:plc:abc123/col/%00","category":"conflict","expect":"review","purpose":"encoded null"},

    # --- boundary / unexpected (5) ---
    {"id":"B01","input":"at://did:plc:a/app.bsky.feed.post/x","category":"boundary","expect":"valid","purpose":"minimal DID identifier"},
    {"id":"B02","input":"at://a.co/col/rkey","category":"boundary","expect":"valid","purpose":"shortest possible handle"},
    {"id":"B03","input":"at://did:plc:abc123/col/x"*1,"category":"boundary","expect":"valid","purpose":"normal case"},
    {"id":"B04","input":"at://did:plc:abc123/"+("a"*63)+".example/x","category":"boundary","expect":"review","purpose":"63-char label (DNS limit)"},
    {"id":"B05","input":"at://did:plc:abc123/"+("a"*64)+".example/x","category":"boundary","expect":"invalid","purpose":"64-char label (exceeds DNS)"},
]


def load_corpus():
    return list(CORPUS)