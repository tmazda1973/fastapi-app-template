/**
 * API関連フックの統一エクスポート
 *
 * 使用例:
 * import { useApi, useUserApi, useLocaleApi } from '@hooks/api';
 */

// 基本フックと型定義
export { useApi } from './useApi';
export type {
  ApiResponse,
  ApiError,
  UseApiOptions,
  ApiCallOptions,
} from './useApi';

// 特化したAPIフック
export { useUserApi } from './useUserApi';
export { useLocaleApi } from './useLocaleApi';
export { useAdminApi } from './useAdminApi';
