# -*- coding: utf-8 -*-
"""扫描 src 下实际使用到的 @element-plus/icons-vue 图标名。

用途：main.ts 里曾是 `import * as Icons` 全量注册（1000+ 个），
把 icon chunk 撑到近 300KB gzip。改成显式白名单后需要这份清单。
新增图标时重跑本脚本，把新名字补进 main.ts 的 ICONS 列表。
"""
import json
import os
import re
import sys

ICON_PKG = "node_modules/@element-plus/icons-vue/dist/index.js"


def load_available() -> set[str]:
    src = open(ICON_PKG, encoding="utf-8").read()
    block = src[src.rfind("export {"):]
    return set(re.findall(r"as\s+([A-Za-z][A-Za-z0-9]*)\s*[,}\n]", block))


def scan_used(files: list[str]) -> dict[str, set[str]]:
    used: dict[str, set[str]] = {}

    def add(name: str, path: str) -> None:
        used.setdefault(name, set()).add(path.replace("\\", "/"))

    tag_re = re.compile(r"<([A-Z][A-Za-z0-9]*)[\s/>]")
    # :is 的值可能写成三元表达式（'Top' : 'Bottom'），要把里面每个字符串都抓出来。
    # 只取末尾一个会让另一个图标静默丢失，页面上表现为图标空白。
    is_attr_re = re.compile(r''':is="([^"]*)"''')
    quoted_re = re.compile(r"""'([A-Z][A-Za-z0-9]+)'|"([A-Z][A-Za-z0-9]+)\"""")
    icon_re = re.compile(r"""icon:\s*['"]([A-Z][A-Za-z0-9]+)['"]""")
    import_re = re.compile(
        r"""import\s*\{([^}]+)\}\s*from\s*['"]@element-plus/icons-vue['"]"""
    )

    for path in files:
        text = open(path, encoding="utf-8").read()
        tpl = re.search(r"<template>([\s\S]*)</template>", text)
        if tpl:
            body = tpl.group(1)
            for name in tag_re.findall(body):
                add(name, path)
            for expr in is_attr_re.findall(body):
                for single, double in quoted_re.findall(expr):
                    add(single or double, path)
        for name in icon_re.findall(text):
            add(name, path)
        for group in import_re.findall(text):
            for item in group.split(","):
                name = item.strip().split(" as ")[-1].strip()
                if name:
                    add(name, path)
    return used


def main() -> None:
    files = [
        os.path.join(root, name)
        for root, _, names in os.walk("src")
        for name in names
        if name.endswith((".vue", ".ts"))
    ]
    available = load_available()
    used = scan_used(files)
    hit = sorted(k for k in used if k in available)
    miss = sorted(k for k in used if k not in available)

    print(f"扫描文件 {len(files)} 个，命中图标 {len(hit)} 个\n")
    print(json.dumps(hit, ensure_ascii=False, indent=0))
    if miss:
        print("\n未命中（自定义组件或误报，无需注册）：")
        for name in miss:
            print(f"  {name:20s} {', '.join(sorted(used[name])[:2])}")
    # 供 CI 使用：--check 时把命中数写进 stdout 第一行之外不做事
    sys.exit(0)


if __name__ == "__main__":
    main()
