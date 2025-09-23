import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';
import prettierConfig from 'eslint-config-prettier';

export default tseslint.config([
  { ignores: ['dist'] },
  {
    files: ['**/*.{ts,tsx}'],
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      // ===== フォーマット関連ルールはPrettierに移管 =====
      // quotes, jsx-quotes, comma-dangle, semi, eol-lastはPrettierが担当

      // ===== コード品質関連ルール（ESLint担当） =====
      // アンダーバー付き変数の未使用を許可
      '@typescript-eslint/no-unused-vars': [
        'error',
        {
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_',
          caughtErrorsIgnorePattern: '^_',
          destructuredArrayIgnorePattern: '^_',
        },
      ],
      // 特定の場合のany型使用を許可
      '@typescript-eslint/no-explicit-any': [
        'error',
        {
          ignoreRestArgs: true,
        },
      ],
      // React Hooks のルール
      ...reactHooks.configs.recommended.rules,
      // Context + hook パターンではReact Refresh警告を無効化
      'react-refresh/only-export-components': 'off',
    },
  },
  // Prettierと競合するルールを無効化（最後に配置）
  prettierConfig,
]);
