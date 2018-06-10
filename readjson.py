import json

pa='D:/k_abc/YZC_DY_seq000_sc008_fileInfo.json'

a=json.loads(open(pa).read(),encoding='gbk')

print a.keys()