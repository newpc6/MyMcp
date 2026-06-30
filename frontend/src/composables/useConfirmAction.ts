import { ref } from 'vue';
import { ElMessageBox } from 'element-plus';
import type { ElMessageBoxOptions } from 'element-plus';

export interface ConfirmActionOptions {
    /** 弹窗标题 */
    title?: string;
    /** 弹窗提示消息 */
    message?: string;
    /** 确认按钮文本 */
    confirmText?: string;
    /** 取消按钮文本 */
    cancelText?: string;
    /** 弹窗类型 */
    type?: ElMessageBoxOptions['type'];
    /** 执行前的额外校验，返回 false 则取消 */
    beforeAction?: () => boolean | Promise<boolean>;
}

export function useConfirmAction<Args extends any[] = []>(
    actionFn: (...args: Args) => Promise<void> | void,
    defaultOptions: ConfirmActionOptions = {}
) {
    const loading = ref(false);
    let locked = false;

    const {
        title = '操作确认',
        message = '确定要执行此操作吗？',
        confirmText = '确定',
        cancelText = '取消',
        type = 'warning',
        beforeAction
    } = defaultOptions;

    const execute = async (...args: Args): Promise<boolean> => {
        if (locked) return false;

        try {
            await ElMessageBox.confirm(message, title, {
                confirmButtonText: confirmText,
                cancelButtonText: cancelText,
                type
            });

            if (beforeAction) {
                const canProceed = await beforeAction();
                if (!canProceed) return false;
            }

            locked = true;
            loading.value = true;
            await actionFn(...args);
            return true;
        } catch (error: any) {
            if (error !== 'cancel' && error !== 'close') {
                throw error;
            }
            return false;
        } finally {
            loading.value = false;
            locked = false;
        }
    };

    return {
        loading,
        execute
    };
}
