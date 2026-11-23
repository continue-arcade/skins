# Continue Skins

Continue 外壳的独立制作目录。各皮肤位于 skins/<name>/cart/，来源原件和许可位于 sources/，构建与原生验证位于 build/，发布包位于 releases/。发布配置位于 publishing/，持久发布状态位于排除版本控制的 state/。当前首张为 GBA 紫晶外壳。

每张 Cart 必须具备2:1真实封面、图标、带实际截图的README、独立Release Notes、来源署名与许可、可复核原包哈希。原始素材不覆盖；已发布版本字节不覆盖，修改后升版本。

构建和发布工具使用主工程 /Users/karma/krtek-v2 的 continue-cart 与 continue-cart-station；场景编译和原生预览使用 Dash CLI。皮肤源不放入主应用源码。后续各皮肤沿用此目录结构。
