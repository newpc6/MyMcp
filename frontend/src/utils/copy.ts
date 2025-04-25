import { ElMessage } from 'element-plus';

/**
 * 回退方式复制文本到剪贴板
 * @param text 需要复制的文本
 */
export function fallbackCopyTextToClipboard(text: string): void {
  try {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(
        () => {
          ElMessage.success('内容已复制到剪贴板');
        },
        () => {
          // 如果剪贴板API失败，使用回退方法
          fallbackMethod(text);
        }
      );
    } else {
      // 浏览器不支持Clipboard API，使用回退方法
      fallbackMethod(text);
    }
  } catch (err) {
    ElMessage.error('复制失败');
    console.error('复制失败:', err);
  }
}

/**
 * 通过创建临时textarea元素实现复制功能
 * @param text 需要复制的文本
 */
function fallbackMethod(text: string): void {
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
      ElMessage.success('内容已复制到剪贴板');
    } else {
      ElMessage.error('复制失败');
    }
  } catch (err) {
    ElMessage.error('复制失败');
    console.error('复制失败:', err);
  }

  document.body.removeChild(textArea);
}