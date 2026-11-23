"""将已验包的外壳条目合入现行官方目录；保留其他条目与内容寻址文件。"""
from pathlib import Path
import importlib.util,json,hashlib
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('catalog_registry','/Users/karma/krtek-v2/scripts/prepare-catalog-registry.py')
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
url='https://cart-registry.continue.works/registry.json'
before_bytes=helper.download(url);before=json.loads(before_bytes)
export=root/'build/station/export';station=json.loads((export/'registry.json').read_bytes())
candidate,=[x for x in station['carts'] if x['cart_id']=='org.continue.diorama.gba-amethyst']
assert before['schema']==station['schema']=='continue.cart-registry.v2'
assert before['id']==station['id']=='org.continue.cart-station'
assert all(x['cart_id']!=candidate['cart_id'] for x in before['carts']), '已有发布，请按版本更新流程处理'
public=root/'build/public';public.mkdir(parents=True,exist_ok=True)
visited=set();helper.carry_references(before,url,public,visited);helper.carry_references(candidate,export,public,visited)
after=dict(before,carts=[*before['carts'],candidate]);after.pop('revision',None)
after.setdefault('curation',{}).setdefault('order',[]).append(candidate['cart_id'])
after['revision']=hashlib.sha256(helper.object_bytes(after)).hexdigest()
(public/'registry.json').write_text(json.dumps(after,ensure_ascii=False,indent=2)+'\n')
(public/'_headers').write_bytes((export/'_headers').read_bytes())
(root/'build/base-registry.json').write_bytes(before_bytes)
(root/'build/registry-merge-verification.json').write_text(json.dumps({'preserved_cart_count':len(before['carts']),'result_cart_count':len(after['carts']),'preserved_rows_unchanged':after['carts'][:-1]==before['carts'],'new_cart':candidate['cart_id'],'new_revision':after['revision']},indent=2))
print('preserved',len(before['carts']),'added',candidate['cart_id'])
