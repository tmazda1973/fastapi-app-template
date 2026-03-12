import re

REGEX = {
    "half_width": r"^[\x20-\x7E]+$",
    "number_integer": r"^[0-9]+$",
    "number_float": r"[+-]?[0-9]+(\.[0-9]+)?([Ee][+-]?[0-9]+)?",
}

# パスワードバリデーション: 8文字以上、英数字記号を含む
PASSWORD_REGEX = re.compile(r"^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$")

# 全角英数字記号
FULL_WIDTH_ALPHANUM_SYMBOL_CHARS = (
    # 記号: 44文字
    "（）［］｛｝＜＞＂＂＂＂＂＇＇＇＠＃＄％＆＊＋－−–—―／＝＾～｜、。，．：；！？＿￥　"
    # 英大文字: 26文字
    "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
    # 英小文字: 26文字
    "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ"
    # 数字: 10文字
    "０１２３４５６７８９"
)
# 半角英数字記号
HALF_WIDTH_ALPHANUM_SYMBOL_CHARS = (
    # 記号: 44文字
    '()[]{}<>"""""\'\'\'@#$%&*+-----/=^~|,.,.:;!?_\\ '
    # 英大文字: 26文字
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # 英小文字: 26文字
    "abcdefghijklmnopqrstuvwxyz"
    # 数字: 10文字
    "0123456789"
)
