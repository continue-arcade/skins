#!/usr/bin/env python3
"""从冻结素材制作单屏外壳与纯边框；所有展示截图由 Dash Metal 实际渲染。"""
from pathlib import Path
import hashlib, json, shutil, subprocess, zipfile
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('/Users/karma/krtek-v2')
MANIC = Path('/Volumes/GM9000/Continue/assets/skins/manic/2026-11-23')
BEZELS = Path('/Volumes/GM9000/Continue/assets/skins/libretro/2026-11-28')
WORK = Path('/Volumes/GM9000/Continue/work/2026-11-28/diorama-platform-batch')
CLI = REPO / 'dash/target/debug/continue-dash-cli'
CART = REPO / 'target/debug/continue-cart'
VERSION = '0.1.0-preview.3'
PRESS = 'outQuad:70,scale=0.9,depth=1.5,shade=0.08'
BATCH = []

def run(args, log):
    p = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(p.stdout + p.stderr)
    if p.returncode:
        raise RuntimeError(f'{args[0]}: {log}\n{p.stdout}{p.stderr}')

def vector(frame):
    return ','.join(f'{frame[k]:g}' for k in ('x', 'y', 'width', 'height'))

def metadata(slug, title, summary, author, license_name, resources, screenshots, credits, source):
    cart = ROOT / 'skins' / slug / 'cart'
    presentation = cart / 'presentation'
    # 使用实际原生渲染截图生成货架封面，不另画模拟器画面。
    first = Image.open(presentation / screenshots[0]).convert('RGB')
    if len(screenshots) >= 3:
        cover = Image.new('RGB', (1200, 600), '#15151b')
        selected = screenshots[:6] if slug == 'platform-bezels' else screenshots[:3]
        tile_height = 300 if len(selected) == 6 else 600
        for i, name in enumerate(selected):
            im = Image.open(presentation / name).convert('RGB')
            im.thumbnail((390, tile_height-20))
            cover.paste(im, ((i%3) * 400 + (400-im.width)//2, (i//3)*tile_height + (tile_height-im.height)//2))
    else:
        cover = ImageOps.pad(first, (1200,600), color='#15151b')
    cover.save(presentation / 'cover.png')
    ImageOps.pad(first, (512,512), color='#15151b').save(presentation / 'icon.png')
    cid = 'org.continue.diorama.' + slug
    text = f'''schema = "continue.cartfile.v2"
id = "{cid}"
default_locale = "zh-CN"
version = "{VERSION}"
author = "{author}"
publisher = "Continue"
description = "{summary}"
tags = ["diorama", "{'bezels' if slug in ('platform-bezels','screen-bezels') else slug.split('-')[0]}", "{'controller' if slug in ('platform-bezels','screen-bezels') else 'touch-controls'}"]

[name]
zh-CN = "{title}"
en = "{slug.replace('-', ' ').title()}"

[summary]
zh-CN = "{summary}"
en = "{'Decorative platform borders without touch controls, preserving the game aspect ratio.' if slug in ('platform-bezels','screen-bezels') else 'Phone and tablet shells with native button feedback and original screen proportions.'}"

[presentation]
icon = "presentation/icon.png"
cover = "presentation/cover.png"
screenshots = {json.dumps(['presentation/'+s for s in screenshots])}

[links]
source = "{source}"

[artifact]
format = "cart.zip.v1"

[artifact.target]

[include]
paths = ["README.md", "CREDITS.md", "LICENSE.txt", "RELEASE_NOTES.md", "provenance.json", "presentation/", "resources/"]
'''
    (cart / 'cartfile.toml').write_text(text)
    (cart / 'CREDITS.md').write_text(credits)
    (cart / 'LICENSE.txt').write_bytes(license_name.read_bytes())
    (cart / 'RELEASE_NOTES.md').write_text(f'# {VERSION}\n\n- 首批场景、素材与原生渲染预览。\n- 本地预览版；尚未完成各平台真实核心与移动触控验收，未发布。\n')
    readme = f'# {title}\n\n{summary}\n\n'
    readme += '## 使用\n\n本版通过 Dash 场景开发入口预览，安装后不会自动应用。使用键盘或手柄操作纯边框版本。包内不包含游戏、BIOS 或核心。\n\n'
    readme += '## 包含内容\n\n' + '\n'.join('- '+r for r in resources) + '\n\n'
    readme += '## 原生预览\n\n截图由 Dash Metal 渲染，屏幕中是原创开发测试画面；用于核对外观和按压反馈，不代表对应平台核心或游戏已经验收。游戏按核心提供的比例居中放入画框，不拉伸；测试画面的比例与目标平台不同时会留黑边。\n\n'
    readme += '\n\n'.join(f'![{s.removesuffix(".png")}](presentation/{s})' for s in screenshots)
    readme += '\n\n## 来源\n\n见 CREDITS.md、LICENSE.txt 与 provenance.json。原始标识保留作为素材来源记录。\n'
    (cart / 'README.md').write_text(readme)
    build = ROOT / 'build' / slug
    for command in ('inspect','pack','verify'):
        artifact = ROOT / 'releases' / f'{slug}-{VERSION}.cart'
        artifact.parent.mkdir(exist_ok=True)
        args = [CART, command, artifact if command == 'verify' else cart]
        if command == 'pack': args += ['--out', artifact]
        run(args, build / f'{command}.json')
    BATCH.append({'slug':slug,'cart':str(cart),'artifact':str(artifact),'sha256':hashlib.sha256(artifact.read_bytes()).hexdigest(),'resources':resources,'screenshots':screenshots,'status':'native-demo-preview; not published; platform core acceptance pending'})
    print('PACKED',slug,flush=True)


def resource(path, rid, title, license_name):
    (path / 'continue.toml').write_text(f'''schema = "continue.resource.v1"
type = "diorama"
id = "org.continue.diorama.{rid}"
name = "{title}"
version = "{VERSION}"
author = "上游素材作者；Continue 适配"
license = "{license_name}"
description = "{title}，保留游戏比例。"
entrypoint = "scene.continue-diorama"

[diorama]
renderer = "continue.scene"
''')


def render(slug, res, layout, size, name, press=None):
    build = ROOT / 'build' / slug
    ir = build / (res.name + '.ir.json')
    run([CLI,'scene','compile',res/'scene.continue-diorama','--out',ir], build/(res.name+'-compile.log'))
    out = ROOT / 'skins' / slug / 'cart/presentation' / name
    out.parent.mkdir(parents=True,exist_ok=True)
    args = [CLI,'scene','render',ir,'--textures',res,'--layout',layout,'--width',size[0],'--height',size[1],'--out',out]
    if press: args += ['--press',press]
    run(args,build/(name+'.log'))


def touch(code, slug, title):
    src = next((MANIC/'official').rglob(code+'.manicskin'))
    comparison = json.loads((MANIC/'selection-20261124/archived-official-content-comparison.json').read_text())
    evidence = next(x for x in comparison if Path(x['file']).name == src.name and x['same_content'])
    # 唯一外部边界：重新核对冻结文件与许可仓库 Git blob 身份。
    blob = src.read_bytes()
    git_sha = hashlib.sha1(f'blob {len(blob)}\0'.encode()+blob).hexdigest()
    # LFS 包的旧树可能记录指针，允许精确匹配该包的 LFS 指针。
    pointer = f'version https://git-lfs.github.com/spec/v1\noid sha256:{hashlib.sha256(blob).hexdigest()}\nsize {len(blob)}\n'.encode()
    pointer_sha = hashlib.sha1(f'blob {len(pointer)}\0'.encode()+pointer).hexdigest()
    assert evidence['archive_blob_sha'] in (git_sha,pointer_sha), src
    cart = ROOT/'skins'/slug/'cart'; res=cart/'resources'/slug; assets=res/'assets'; assets.mkdir(parents=True,exist_ok=True)
    source = ROOT/'sources/platform-batch-20261128'/code; source.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,source/src.name)
    with zipfile.ZipFile(src) as z:
        data=json.loads(z.read('info.json'))
        layouts=[]
        for device, modes in data['representations'].items():
            mode='standard' if device=='ipad' else 'edgeToEdge'
            for orient,r in modes[mode].items():
                assert len(r['screens'])==1
                layouts.append((device,orient,r))
        needed=set()
        for _,_,r in layouts:
            needed.add(next(iter(r['assets'].values())))
            for item in r['items']:
                needed.add(item.get('thumbstick',{}).get('name') or item['asset']['normal'])
        assert all(p in z.namelist() for p in needed)
        for name in sorted(needed):
            raw=source/name; raw.parent.mkdir(parents=True,exist_ok=True);raw.write_bytes(z.read(name))
            output=assets/(Path(name).stem+'.png')
            if name.endswith('.pdf'):
                run(['pdftocairo','-png','-singlefile','-transp','-r','72',raw,output.with_suffix('')],WORK/'pdf-logs'/f'{code}-{Path(name).stem}.log')
            else: shutil.copy2(raw,output)
            image = Image.open(output)
            image.thumbnail((2400,2400), Image.Resampling.LANCZOS)
            image.save(output)
    lines=['# 单屏外壳；素材来源和许可身份见 provenance.json。']
    base={'a':'A','b':'B','x':'X','y':'Y','l':'L','r':'R','l1':'L','r1':'R','start':'Start','select':'Select','menu':'Menu','up':'Up','down':'Down','left':'Left','right':'Right'}
    if code=='MD': base.update(a='Y',b='B',c='A',x='L',y='X',z='R')
    shot_layouts={}
    for device,orient,r in layouts:
        form='tablet' if device=='ipad' else 'phone'; lid=f'{slug}/{form}/{orient}';shot_layouts[(form,orient)]=(lid,(r['mappingSize']['width'],r['mappingSize']['height']))
        lines += ['',f'DioramaRoot version="0.2" id="{lid}" mapping="{r["mappingSize"]["width"]},{r["mappingSize"]["height"]}" orientation="{orient}" form="{form}"',f'  Background img="assets/{Path(next(iter(r["assets"].values()))).stem}.png"',f'  Screen id="main" frame="{vector(r["screens"][0]["outputFrame"])}"']
        for index,item in enumerate(r['items']):
            inputs=item['inputs']; frame=vector(item['frame']);edges=item.get('extendedEdges',{});hit=','.join(str(edges.get(k,0)) for k in ('top','right','bottom','left'))
            image=Path(item.get('thumbstick',{}).get('name') or item['asset']['normal']).stem+'.png'
            if isinstance(inputs,dict):
                if 'thumbstick' in item:
                    assert code=='PSP'
                    scale=item['thumbstick']['width']/item['frame']['width']; state=f'stick_scale_{index}'
                    lines += [f'  State name="{state}" type="float" default="{scale}"',f'  Stick key="left-stick" bind="leftStick" frame="{frame}" hit="{hit}" deadzone="0.15" travel="20" img="assets/{image}" scale="{state}"']
                else:
                    assert set(inputs.values())=={'up','down','left','right'}
                    lines.append(f'  Dpad key="dpad" bind="dpad" frame="{frame}" hit="{hit}" mode="8way" deadzone="0.2" img="assets/{image}" press="{PRESS}"')
            else:
                assert len(inputs)==1 and inputs[0] in base,inputs
                key=inputs[0].capitalize() if inputs[0] in ('start','select','menu','up','down','left','right') else inputs[0].upper()
                lines.append(f'  Button key="{key}" bind="{base[inputs[0]]}" frame="{frame}" hit="{hit}" img="assets/{image}" press="{PRESS}"')
    (res/'scene.continue-diorama').write_text('\n'.join(lines)+'\n')
    resource(res,slug,title,'CC-BY-4.0')
    provenance={'source_file':str(src),'sha256':hashlib.sha256(blob).hexdigest(),'license_evidence':evidence,'input_mapping':base,'note':'MD 按 Genesis Plus GX 的 Libretro 六键契约；SMS/GG 保留右键 A、左键 B，对应核心的 2/1。未做实际核心输入验收。','layouts':len(layouts)}
    (cart/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
    shots=[]
    for form,orient,name,press in [('phone','portrait','phone-portrait.png',None),('phone','landscape','phone-landscape.png',None),('phone','portrait','pressed.png','A'),('tablet','landscape','tablet-landscape.png',None)]:
        lid,size=shot_layouts[(form,orient)];render(slug,res,lid,size,name,press);shots.append(name)
    summary=f'{title}，提供手机和平板横竖屏布局、独立按钮与方向操作反馈，保留游戏原比例。'
    notes='按压反馈不改变触摸范围。'
    if code=='MD': notes+='六键按 Genesis Plus GX 的 Libretro 契约配置；需核心开启六键手柄。原皮肤没有 Mode 键。'
    if code=='MS': notes+='Start 配置为 Libretro Start，实际暂停行为仍需对应核心验收。'
    credits=f'# 来源与适配\n\nManic EMU 官方 {code} Standard 素材，CC BY 4.0。旧许可仓库与本批精确文件身份比对见 provenance.json。Continue 转换 PNG、场景布局与按压反馈。{notes}\n\n来源：https://github.com/Manic-EMU/ManicEMUSkins\n\nMD 映射依据：https://github.com/libretro/Genesis-Plus-GX/blob/master/libretro/libretro.c\n'
    metadata(slug,title,summary,'Manic EMU；Continue 适配',ROOT/'sources/manic-official-archived/LICENSE',[f'{len(layouts)} 个布局：手机、平板横竖屏。',notes],shots,credits,'https://github.com/Manic-EMU/ManicEMUSkins')


def bezels():
    slug='platform-bezels';cart=ROOT/'skins'/slug/'cart'
    definitions=[('gb','Nintendo-Game-Boy','GB'),('gbc','Nintendo-Game-Boy-Color','GBC'),('gba','Nintendo-Game-Boy-Advance','GBA'),('nes','Nintendo-Entertainment-System','NES'),('snes','Super-Nintendo-Entertainment-System','SNES'),('md','Sega-Genesis','MD'),('sms','Sega-Master-System','SMS'),('gg','Sega-Game-Gear','GG'),('pce','NEC-PC-Engine','PCE'),('ps1','Sony-Playstation','PS1'),('n64','Nintendo-64','N64'),('saturn','Sega-Saturn','Saturn'),('arcade-horizontal','MAME-Horizontal','横版街机'),('arcade-vertical','MAME-Vertical','竖版街机'),('ngp','SNK-Neo-Geo-Pocket','NGP'),('ws-horizontal','Bandai-WonderSwan-Color-Horizontal','WS 横屏'),('ws-vertical','Bandai-WonderSwan-Color-Vertical','WS 竖屏')]
    snapshot=json.loads((BEZELS/'snapshot.json').read_text()); records=[]
    for key,filename,title in definitions:
        relative=f'16x9 Collections/Nosh01 1440 Plain/{filename}-Bezel-16x9-2560x1440.png'
        src=BEZELS/relative; record=next(x for x in snapshot['files'] if x['path']==relative)
        assert hashlib.sha256(src.read_bytes()).hexdigest()==record['sha256']
        im=Image.open(src).convert('RGBA');w,h=im.size
        # 只在导入边界读取透明窗口；保持源素材，运行时不做图片扫描。
        aperture=im.getchannel('A').point(lambda a:255 if a==0 else 0).getbbox()
        assert aperture is not None
        x,y,x2,y2=aperture
        # 全透明窗口外沿有抗锯齿：略向内收一个像素，避免画面盖住原边框。
        x+=1;y+=1;x2-=1;y2-=1
        res=cart/'resources'/key;(res/'assets').mkdir(parents=True,exist_ok=True);shutil.copy2(src,res/'assets/border.png')
        lid=f'{slug}/{key}'
        (res/'scene.continue-diorama').write_text(f'# 无按钮、无触控区域；仅贴图与游戏画框。\nDioramaRoot version="0.2" id="{lid}" mapping="{w},{h}" orientation="landscape"\n  Background img="assets/border.png"\n  Screen id="main" frame="{x},{y},{x2-x},{y2-y}"\n')
        resource(res,'bezel-'+key,title+' 边框','MIT')
        records.append(dict(record,resource=key,aperture=[x,y,x2-x,y2-y]))
        # 全部资源均编译、实际原生渲染，代表截图进入展示清单。
        render(slug,res,lid,(1600,900),key+'.png')
    (cart/'provenance.json').write_text(json.dumps({'repository':snapshot['repo'],'commit':snapshot['commit'],'author':'Nosh (Nosh01 collection)','resources':records,'controls':0,'screen_geometry':'原透明窗口内保留核心报告比例，不拉伸；不锁定像素宽高比。'},ensure_ascii=False,indent=2)+'\n')
    shots=[k+'.png' for k in ['gb','gba','nes','ps1','arcade-vertical','ws-vertical']]
    metadata(slug,'机种纯边框集','为掌机、家用机和横竖街机填充宽屏空白，包含十七款无按钮边框，保留游戏比例。','Nosh；Continue 适配',BEZELS/'LICENSE',[t+'：无按钮边框' for _,_,t in definitions],shots,'# 来源与适配\n\n原素材：Nosh，Libretro overlay-borders 的 Nosh01 1440 Plain 系列。冻结提交与逐图 SHA-256 见 provenance.json；上游仓库 MIT 声明随包保留。原图未经重绘；Continue 提取透明屏幕窗口并转换为静态 Diorama。无按钮节点、无命中区域。\n\nhttps://github.com/libretro/overlay-borders\n','https://github.com/libretro/overlay-borders')

if __name__=='__main__':
    WORK.mkdir(parents=True,exist_ok=True)
    for args in [('GB','gb-classic','GB 经典外壳'),('GBC','gbc-classic','GBC 彩色外壳'),('NES','nes-classic','NES 经典外壳'),('SNES','snes-classic','SNES 经典外壳'),('MD','md-sixbutton','MD 六键外壳'),('MS','sms-classic','SMS 经典外壳'),('GG','gg-classic','GG 经典外壳'),('PSP','psp-classic','PSP 经典外壳')]:
        touch(*args)
        (WORK/'batch.json').write_text(json.dumps(BATCH,ensure_ascii=False,indent=2)+'\n')
    bezels()
    (WORK/'batch.json').write_text(json.dumps(BATCH,ensure_ascii=False,indent=2)+'\n')
