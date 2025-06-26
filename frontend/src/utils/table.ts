/**
 * 表格相关工具函数
 */

/**
 * 获取排名样式类
 * @param index 排名索引（从0开始）
 * @returns 排名样式类名
 */
export const getRankingClass = (index: number): string => {
  switch (index) {
    case 0:
      return 'ranking-first'
    case 1:
      return 'ranking-second'
    case 2:
      return 'ranking-third'
    default:
      return 'ranking-normal'
  }
} 