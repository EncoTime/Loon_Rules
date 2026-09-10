#!/usr/bin/env python3
"""Loon 规则构建引擎：拉取上游名单 → 清洗 → 合并 → 输出 Loon 规则。

用法：python3 build.py <规则目录>（如 bybit），目录内须有 sources.json。
退出码：0=成功（有变化或无变化），1=构建失败（上游全部拉取失败等）。
"""

import json
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

HKT = timezone(timedelta(hours=8))
VALID_TYPES = {"DOMAIN", "DOMAIN-SUFFIX"}
RULE_RE = re.compile(r"^(DOMAIN(?:-SUFFIX)?),([a-z0-9._-]+)$")


def log(msg: str) -> None:
    """带 HKT 时间戳的进度日志。"""
    print(f"[{datetime.now(HKT).isoformat(timespec='seconds')}] {msg}", flush=True)


def fetch(url: str) -> str:
    """拉取上游规则文本，带 UA 与 30s 超时；失败抛异常。"""
    req = urllib.request.Request(url, headers={"User-Agent": "loon-rules-builder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse(text: str) -> set[str]:
    """从任意上游文本提取有效域名（兼容 clash/loon/surge 行格式）。"""
    domains = set()
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip().rstrip(",")
        if not line:
            continue
        m = RULE_RE.match(line)
        if m:
            domains.add(m.group(2))
    return domains


def excluded(domain: str, excl: set[str]) -> bool:
    """域名命中排除表（含父域匹配，如 appsflyersdk.com 下的子域）。"""
    parts = domain.split(".")
    return any(domain == e or domain.endswith("." + e) for e in excl)


def main() -> None:
    """构建单条规则：目录名来自 argv[1]，产物写 <目录>/<名字>.list。"""
    if len(sys.argv) != 2:
        sys.exit("用法: build.py <规则目录>")
    rule_dir = Path(__file__).parent.parent / sys.argv[1]
    cfg = json.loads((rule_dir / "sources.json").read_text(encoding="utf-8"))
    name, policy = cfg["name"], cfg["policy"]
    excl = {e.lower() for e in cfg.get("exclude", [])}

    domains: set[str] = set()
    ok_sources = 0
    for url in cfg["sources"]:
        try:
            got = parse(fetch(url))
            domains |= got
            ok_sources += 1
            log(f"OK  {url} -> {len(got)} 域名")
        except Exception as e:  # 单个上游失败不阻塞其余上游
            log(f"FAIL {url} -> {e}")
    if not ok_sources:
        sys.exit("全部上游拉取失败，保留旧产物不动")

    domains = {d for d in domains if not excluded(d, excl)}
    # 子域被父域覆盖时去重（有 bybit.com 就不再单列 x.bybit.com——本规则集目前无此情况，防御性保留）
    lines = [f"DOMAIN-SUFFIX,{d},{policy}" for d in sorted(domains)
             if not any(d.endswith("." + s) for s in domains if s != d)]
    header = (
        f"# {name} — Loon 规则（自动生成，勿手改）\n"
        f"# 上游 {ok_sources}/{len(cfg['sources'])} 个源，共 {len(lines)} 条\n"
        f"# 生成时间：{datetime.now(HKT).isoformat(timespec='seconds')}\n"
    )
    out = rule_dir / f"{name}.list"
    new_content = header + "\n".join(lines) + "\n"
    old = out.read_text(encoding="utf-8") if out.exists() else ""
    if new_content != old:
        out.write_text(new_content, encoding="utf-8")
        log(f"已更新 {out}（{len(lines)} 条）")
    else:
        log(f"无变化 {out}（{len(lines)} 条）")


if __name__ == "__main__":
    main()
