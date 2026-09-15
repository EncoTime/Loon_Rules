#!/usr/bin/env python3
"""build.py 解析逻辑最小自检：python3 test_build.py，全过即静默退出码 0。"""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))

from build import parse, excluded

# 域名行统一归 DOMAIN-SUFFIX；IP 行保留地址族；裸 CIDR 兼容 v4/v6
assert parse("DOMAIN-SUFFIX,a.com") == {("DOMAIN-SUFFIX", "a.com")}
assert parse("DOMAIN,a.com,P") == {("DOMAIN-SUFFIX", "a.com")}
assert parse("IP-CIDR,1.2.3.0/24,no-resolve") == {("IP-CIDR", "1.2.3.0/24")}
assert parse("IP-CIDR6,2606:4700::/32") == {("IP-CIDR6", "2606:4700::/32")}
assert parse("104.16.0.0/13") == {("IP-CIDR", "104.16.0.0/13")}
assert parse("2606:4700::/32") == {("IP-CIDR6", "2606:4700::/32")}
# 畸形 CIDR / 垃圾行丢弃
assert parse("999.1.1.1/8") == set()
assert parse("") == set()
assert parse("# 全是注释") == set()
# exclude 含父域匹配；IP 不走 exclude（由 main() 分流）
assert excluded("x.mgid.com", {"mgid.com"})
assert not excluded("notmgid.com", {"mgid.com"})
print("selfcheck ok")
