import { ElMessage } from 'element-plus';

/**
 * 复制文本到剪贴板（通用函数）
 * @param text 需要复制的文本
 * @param successMessage 复制成功提示消息，默认为"内容已复制到剪贴板"
 * @returns Promise 复制结果
 */
export function copyTextToClipboard(text: string, successMessage: string = '内容已复制到剪贴板'): Promise<boolean> {
  return new Promise((resolve) => {
    try {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text)
          .then(() => {
            ElMessage.success(successMessage);
            resolve(true);
          })
          .catch(() => {
            // 如果clipboard API失败，使用回退方法
            const result = fallbackMethod(text, successMessage);
            resolve(result);
          });
      } else {
        // 浏览器不支持Clipboard API，使用回退方法
        const result = fallbackMethod(text, successMessage);
        resolve(result);
      }
    } catch (err) {
      ElMessage.error('复制失败');
      console.error('复制失败:', err);
      resolve(false);
    }
  });
}

/**
 * 回退方式复制文本到剪贴板（向后兼容）
 * @param text 需要复制的文本
 */
export function fallbackCopyTextToClipboard(text: string): void {
  copyTextToClipboard(text);
}

/**
 * 通过创建临时textarea元素实现复制功能
 * @param text 需要复制的文本
 * @param successMessage 复制成功提示消息
 * @returns 复制是否成功
 */
function fallbackMethod(text: string, successMessage: string = '内容已复制到剪贴板'): boolean {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  
  // 避免滚动到底部
  textArea.style.top = '0';
  textArea.style.left = '0';
  textArea.style.position = 'fixed';
  textArea.style.opacity = '0';

  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    const successful = document.execCommand('copy');
    if (successful) {
      ElMessage.success(successMessage);
      return true;
    } else {
      ElMessage.error('复制失败');
      return false;
    }
  } catch (err) {
    ElMessage.error('复制失败');
    console.error('复制失败:', err);
    return false;
  } finally {
    document.body.removeChild(textArea);
  }
}