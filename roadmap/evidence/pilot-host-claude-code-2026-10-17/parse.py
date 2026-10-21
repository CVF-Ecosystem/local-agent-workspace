import json,sys
for line in open(sys.argv[1],encoding='utf-8'):
    try: o=json.loads(line)
    except: continue
    t=o.get('type'); sub='SUB' if (o.get('parent_tool_use_id') or o.get('isSidechain')) else 'MAIN'
    m=o.get('message') or {}
    if t=='system' and o.get('subtype')=='init': print('INIT model=',o.get('model'))
    if t in ('assistant','user'):
        for b in (m.get('content') if isinstance(m.get('content'),list) else []):
            if b.get('type')=='tool_use' and b.get('name')=='Agent': print(sub,'CALL Agent:',json.dumps(b.get('input'),ensure_ascii=False)[:160])
            if b.get('type')=='text' and sub=='MAIN': print(sub,'TEXT:',b['text'][:200])
            if b.get('type')=='tool_use' and sub=='SUB' and b.get('name')!='ToolSearch': print(sub,'model=',m.get('model',''),'TOOL_USE:',b.get('name'))
            if b.get('type')=='tool_result' and 'InputValidation' in json.dumps(b.get('content'),ensure_ascii=False): print(sub,'TOOL_ERROR seen')
    if t=='result': print('RESULT:',str(o.get('result'))[:200],'| is_error=',o.get('is_error'),'| modelUsage:',list((o.get('modelUsage') or {}).keys()))
