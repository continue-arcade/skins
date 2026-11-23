#!/usr/bin/env python3
"""构建首张GBA外壳；截图由原生验证准备，不生成伪截图。"""
from pathlib import Path
import subprocess
root = Path(__file__).resolve().parents[1]
repo = Path('/Users/karma/krtek-v2')
cart = root / 'skins/gba-amethyst/cart'
build = root / 'build/gba-amethyst'
build.mkdir(parents=True, exist_ok=True)
cli = repo / 'dash/target/debug/continue-dash-cli'
subprocess.run([str(cli), 'scene', 'compile', str(cart / 'resource/scene.continue-diorama'), '--out', str(build / 'scene.ir.json')], check=True)
tool = repo / 'target/debug/continue-cart'
artifact = root / 'releases/gba-amethyst-0.1.0-preview.1.cart'
artifact.parent.mkdir(exist_ok=True)
subprocess.run([str(tool), 'inspect', str(cart)], check=True)
subprocess.run([str(tool), 'pack', str(cart), '--out', str(artifact)], check=True)
subprocess.run([str(tool), 'verify', str(artifact)], check=True)
