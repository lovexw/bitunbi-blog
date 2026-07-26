#!/usr/bin/env python3
"""
文章加密工具

用法:
  python3 encrypt_post.py "content/posts/文章文件.md" "密码"

效果:
  1. 读取文章 Markdown 正文
  2. 用 AES-ECB 加密（与 CryptoJS 兼容）
  3. 密文存入 front matter 的 encrypted 字段
  4. 正文清空（只保留 front matter + 注释）

解密:
  前端模板检测到 encrypted 字段 → 显示密码输入框
  访客输入密码 → CryptoJS AES 解密 → 渲染 HTML

注意:
  - 加密后正文 Markdown 会丢失，如需修改请先解密
  - 密码不会出现在文件中，只有密文
  - 不知道密码无法查看内容
"""

import os
import sys
import re
import hashlib

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
except ImportError:
    print("需要安装 pycryptodome: pip3 install pycryptodome")
    sys.exit(1)


def encrypt_aes_ecb(plaintext, password):
    """
    AES-128-ECB 加密，兼容前端 CryptoJS。
    CryptoJS: CryptoJS.AES.decrypt(cipher, CryptoJS.enc.Utf8.parse(key), {mode: ECB, padding: Pkcs7})
    key 直接用 password 的 UTF-8 字节，需 16 字节。
    不够 16 字节用 \0 补齐。
    """
    # 确保密钥 16 字节
    key_bytes = password.encode('utf-8')
    if len(key_bytes) < 16:
        key_bytes = key_bytes + b'\x00' * (16 - len(key_bytes))
    elif len(key_bytes) > 16:
        key_bytes = key_bytes[:16]

    cipher = AES.new(key_bytes, AES.MODE_ECB)
    padded = pad(plaintext.encode('utf-8'), AES.block_size)
    encrypted = cipher.encrypt(padded)

    # Base64 编码
    import base64
    return base64.b64encode(encrypted).decode('utf-8')


def encrypt_post(filepath, password):
    """加密文章"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析 front matter
    fm_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not fm_match:
        fm_match = re.match(r'^\+\+\+\n(.*?)\n\+\+\+\n(.*)$', content, re.DOTALL)
    if not fm_match:
        print("❌ 无法解析 front matter")
        return False

    fm = fm_match.group(1)
    body = fm_match.group(2).strip()

    if not body:
        print("❌ 文章正文为空")
        return False

    # 加密正文
    cipher = encrypt_aes_ecb(body, password)

    # 清理旧的加密字段
    fm = re.sub(r'^encrypted:.*$\n?', '', fm, flags=re.MULTILINE)
    fm = re.sub(r'^password:.*$\n?', '', fm, flags=re.MULTILINE)

    # 添加加密字段
    # 注意：密文中可能包含特殊字符，用双引号包裹
    fm = fm.rstrip() + f'\nencrypted: "{cipher}"'

    # 写入新内容：front matter + 空正文
    new_content = f"---\n{fm}\n---\n\n<!-- 此文章已加密 -->\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ 加密成功！")
    print(f"   文件: {filepath}")
    print(f"   密文长度: {len(cipher)} 字符")
    print(f"   密码不会存储在文件中，请妥善保管")
    return True


def main():
    if len(sys.argv) < 3:
        print("📝 文章加密工具")
        print("")
        print("用法:")
        print("  python3 encrypt_post.py <文章文件.md> <密码>")
        print("")
        print("示例:")
        print("  python3 encrypt_post.py content/posts/2025-01-01-my-post.md mypassword123")
        print("")
        print("效果:")
        print("  - 文章正文用 AES-128-ECB 加密")
        print("  - 密文存入 front matter 的 encrypted 字段")
        print("  - 原始正文清空")
        print("  - 访客需输入密码才能查看")
        sys.exit(1)

    filepath = sys.argv[1]
    password = sys.argv[2]

    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        sys.exit(1)

    if len(password) < 4:
        print("⚠️  密码太短，建议至少 6 个字符")
        proceed = input("继续？(y/n): ").strip().lower()
        if proceed != 'y':
            sys.exit(0)

    encrypt_post(filepath, password)


if __name__ == "__main__":
    main()
