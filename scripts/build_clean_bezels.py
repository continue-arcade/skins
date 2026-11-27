#!/usr/bin/env python3
"""制作不含按钮图案与控件的屏框预览。"""
from pathlib import Path
import json,shutil,hashlib
from PIL import Image
from build_platform_batch import ROOT,WORK,render,resource,metadata

source=Path('/Volumes/GM9000/Continue/assets/skins/libretro-common/2026-11-28')
slug='screen-bezels';cart=ROOT/'skins'/slug/'cart'
snapshot=json.loads((source/'snapshot.json').read_text());records=[]
for key,relative,title in [('gb','borders/img/gb-4k.png','GB 屏框'),('crt-horizontal','effects/crt-bezels/img/horizontal.png','横向 CRT 屏框'),('crt-vertical','effects/crt-bezels/img/vertical.png','纵向 CRT 屏框')]:
 src=source/relative;record=next(x for x in snapshot['files'] if x['path']==relative);assert hashlib.sha256(src.read_bytes()).hexdigest()==record['sha256']
 im=Image.open(src).convert('RGBA');w,h=im.size;x,y,x2,y2=im.getchannel('A').point(lambda a:255 if a==0 else 0).getbbox();x+=2;y+=2;x2-=2;y2-=2
 res=cart/'resources'/key;(res/'assets').mkdir(parents=True,exist_ok=True);shutil.copy2(src,res/'assets/border.png');lid=slug+'/'+key
 (res/'scene.continue-diorama').write_text(f'# 无按钮图案与触摸控件。\nDioramaRoot version="0.2" id="{lid}" mapping="{w},{h}"\n  Background img="assets/border.png"\n  Screen id="main" frame="{x},{y},{x2-x},{y2-y}"\n')
 resource(res,'screen-bezel-'+key,title,'CC-BY-4.0');render(slug,res,lid,(1600,900),key+'.png');records.append(dict(record,resource=key,aperture=[x,y,x2-x,y2-y]))
(cart/'provenance.json').write_text(json.dumps({'repository':snapshot['repository'],'commit':snapshot['commit'],'resources':records,'adaptation':'保持原图；将透明窗口登记为游戏画框。','controls':0},ensure_ascii=False,indent=2)+'\n')
metadata(slug,'简洁屏框集','为经典掌机和横竖屏游戏保留简洁屏框，不显示按钮图案或触摸控件，适合搭配实体手柄游玩。','Libretro common-overlays contributors；Continue 适配',source/'COPYING',['GB 屏框：只保留上半机身与屏幕边缘。','横向 CRT 屏框：适合家用机和横版游戏。','纵向 CRT 屏框：适合竖版游戏。','三款均不含按钮图案、Button、Dpad 或 Stick；不强制改变游戏比例。'],['gb.png','crt-horizontal.png','crt-vertical.png'],'# 来源\n\n来源为 Libretro common-overlays 的 GB 4K 与 CRT bezel 素材；CC BY 4.0。原始配置、精确版本与 SHA-256 均已留档，Continue 只转换场景和屏幕窗口。CRT 款为黑色屏幕边缘，适合与独立滤镜搭配；不自带扫描线或曲面滤镜。\n\nhttps://github.com/libretro/common-overlays\n','https://github.com/libretro/common-overlays')
