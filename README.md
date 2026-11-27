# Continue Skins

Continue 外壳的独立制作仓库。各外壳位于 `skins/<name>/cart/`，精确来源和许可位于 `sources/`，本机构建与验收位于 `build/`，Cart 制品位于 `releases/`。

## 平台外壳与边框

本批 `0.1.0-preview.2` 包含八套触控外壳和两张边框合集：

| 类型 | 内容 |
| --- | --- |
| 触控外壳 | GB、GBC、NES、SNES、MD 六键、SMS、GG、PSP；各含手机、平板横竖屏 |
| [机种装饰边框](skins/platform-bezels/cart/README.md) | 十七款无触摸控件边框，部分底图含机身或手柄图案 |
| [简洁屏框](skins/screen-bezels/cart/README.md) | GB、横向 CRT、纵向 CRT；画面也不含按钮图案 |

52 个布局使用真实核心运行；触控款额外验证 A、方向、释放与旋转，共 60 个原生用例。封面、图标和 README 均来自实际核心截图。边框按实际运行的画面类别验证，图示机种不代表该机种的模拟核心已验收。

本批通过 Dash 场景开发入口预览，安装后不会自动应用；移动设备、跨系统实机和正式产品启用链路仍需后续验收。各包的使用范围、来源与截图见其 README。

发布到 [Continue 官方卡带源](https://cart-registry.continue.works/registry.json)，独立制品见 [GitHub Releases](https://github.com/continue-works/arcade-skins/releases)。构建摘要和标签见 `batch-20261128.json`，Station 配方见 `publishing/platform-batch.toml`。

## 制作与留档

每张 Cart 具备 2:1 真实封面、图标、带实机截图的 README、独立 Release Notes、来源署名与许可、可复核原包哈希。原始素材不覆盖，已发布版本字节不覆盖；后续修改必须升版本。`scripts/build_platform_batch.py` 与 `scripts/build_clean_bezels.py` 是下一轮初稿入口，初稿使用开发画面；发布必须替换为真实核心验收媒体。

AtomicPurple 在选用清单中仅保留一份，横竖屏与沉浸布局不重复上架。历史来源留档；已有 GBA 紫晶外壳保持原发布版本。选择与后置项见 `selection-20261128.json`。

本批验证、截图、失败输入对照及发布读回证据：`/Volumes/GM9000/Continue/work/2026-11-28/diorama-real-core-acceptance/`。原始素材位于 `sources/platform-batch-20261128/` 与 `/Volumes/GM9000/Continue/assets/skins/`。主项目的长期记录为 `docs/operations/diorama-platform-release-20261128.md`。
