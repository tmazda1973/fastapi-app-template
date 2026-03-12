import json
import logging
import re
from pathlib import Path
from typing import Any

from accessify import private

logger = logging.getLogger(__name__)

__all__ = [
    "i18n",
]


class I18nManager:
    """
    ローケーション管理
    """

    def __init__(self):
        """
        コンストラクタ
        """
        self._translations: dict[str, dict[str, Any]] = {}
        self._default_locale = "ja"
        self._load_translations()

    def translate(self, key: str, locale: str = None, **kwargs) -> str:
        """
        ローカライズされたテキストを取得します。

        :param key: 翻訳キー
        :param locale: ロケール（省略時はデフォルトのロケール）
        :param kwargs: フォーマット用のキーワード引数
        :return: 翻訳されたテキスト
        """

        locale = locale or self._default_locale
        if locale in self._translations:
            translation_text = self._get_translation_value(
                self._translations[locale], key
            )
            if translation_text:
                try:
                    return (
                        translation_text.format(**kwargs)
                        if kwargs
                        else translation_text
                    )
                except (KeyError, ValueError) as e:
                    logger.warning(f"Translation formatting error for key '{key}': {e}")
                    return translation_text

        # デフォルトロケールで再試行する
        if (
            locale != self._default_locale
            and self._default_locale in self._translations
        ):
            translation_text = self._get_translation_value(
                self._translations[self._default_locale], key
            )
            if translation_text:
                try:
                    return (
                        translation_text.format(**kwargs)
                        if kwargs
                        else translation_text
                    )
                except (KeyError, ValueError) as e:
                    logger.warning(
                        f"Translation formatting error for key '{key}' : {e}"
                    )
                    return translation_text

        logger.warning(f"Missing translation for key: {key} (locale: {locale})")
        return f"Missing translation: {key}"

    def t(self, key: str, locale: str = None, **kwargs) -> str:
        """
        エイリアスメソッド

        - translateと同じ機能を提供します。
        """
        return self.translate(key, locale, **kwargs)

    def get_available_locales(self) -> list[str]:
        """
        利用可能なロケール一覧を取得します。

        :return: ロケールのリスト
        """
        return list(self._translations.keys())

    def has_translation(self, key: str, locale: str = None) -> bool:
        """
        指定されたキーの翻訳が存在するかチェックします。

        :param key: 翻訳キー
        :param locale: ロケール
        :return: 翻訳が存在する場合True
        """
        locale = locale or self._default_locale

        if locale in self._translations:
            return (
                self._get_translation_value(self._translations[locale], key) is not None
            )

        return False

    @private
    def _extract_locale_and_category(
        self,
        filename: str,
    ) -> tuple[str | None, str | None]:
        """
        ファイル名からロケールとカテゴリを抽出します。

        パターン:
        - ja.json → ("ja", None)
        - message.ja.json → ("ja", "message")
        - label.en.json → ("en", "label")

        :param filename: ファイル名
        :return: (locale, category) のタプル
        """

        # 拡張子を除去
        name_without_ext = Path(filename).stem

        # パターン1: category.locale の形式
        if "." in name_without_ext:
            parts = name_without_ext.split(".")
            if len(parts) == 2:
                category, potential_locale = parts
                # ロケールが有効な形式かチェック（2-3文字の英数字）
                if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", potential_locale):
                    return potential_locale, category

        # パターン2: locale のみの形式
        if re.match(r"^[a-z]{2}(-[A-Z]{2})?$", name_without_ext):
            return name_without_ext, None

        return None, None

    @private
    def _load_translations(self) -> None:
        """
        翻訳ファイルを読み込みます。
        """

        locales_dir = Path(__file__).parent / "locales"
        if not locales_dir.exists():
            logger.warning(f"Locales directory not found: {locales_dir}")
            return

        loaded_count = 0
        skipped_count = 0
        for locale_file in locales_dir.glob("*.json"):
            locale, category = self._extract_locale_and_category(locale_file.name)
            if not locale:
                logger.debug(f"Skipping file with invalid format: {locale_file.name}")
                skipped_count += 1
                continue

            try:
                with open(locale_file, "r", encoding="utf-8") as f:
                    content = json.load(f)

                # 空のファイルをスキップ
                if not content:
                    logger.debug(f"Skipping empty file: {locale_file.name}")
                    skipped_count += 1
                    continue

                # ロケール辞書を初期化
                if locale not in self._translations:
                    self._translations[locale] = {}

                # カテゴリがある場合は階層化
                if category:
                    self._translations[locale][category] = content
                    logger.debug(f"Loaded {locale}.{category} from {locale_file.name}")
                else:
                    # カテゴリがない場合は直接マージ
                    self._translations[locale].update(content)
                    logger.debug(f"Loaded {locale}.{category} from {locale_file.name}")

                loaded_count += 1
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in {locale_file.name}: {e}")
                skipped_count += 1
            except Exception as e:
                logger.error(f"Error loading {locale_file.name}: {e}")
                skipped_count += 1

        logger.info(f"Loaded {loaded_count} translation files, skipped {skipped_count}")
        logger.info(f"Available locales: {self.get_available_locales()}")

    @private
    def _get_translation_value(self, data: dict, key: str) -> str | None:
        """
        キーに対応する翻訳値を取得します。

        - 例: "user.error.email_exists"

        :param data: 翻訳データ
        :param key: 翻訳キー

        """

        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current if isinstance(current, str) else None


# シングルトンインスタンスを生成する
i18n = I18nManager()
