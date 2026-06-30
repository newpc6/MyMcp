import { ref, reactive, type Ref } from 'vue';
import type { SearchParams, TableState } from '@/types/page';

export interface UseTableOptions<T = any> {
    /** 默认每页条数 */
    defaultPageSize?: number;
    /** 默认当前页 */
    defaultPage?: number;
    /** 数据请求函数：传入搜索参数，返回 { items, total } */
    fetchFn?: (params: SearchParams) => Promise<{ items: T[]; total: number }>;
    /** 搜索条件初始值 */
    initialCondition?: Record<string, any>;
}

export function useTable<T = any>(options: UseTableOptions<T> = {}) {
    const {
        defaultPageSize = 10,
        defaultPage = 1,
        fetchFn,
        initialCondition = {}
    } = options;

    const state = reactive<TableState<T>>({
        data: [],
        page: defaultPage,
        pageSize: defaultPageSize,
        total: 0,
        loading: false
    });

    const condition = ref<Record<string, any>>({ ...initialCondition });

    const buildParams = (): SearchParams => ({
        page: state.page,
        pageSize: state.pageSize,
        ...condition.value
    });

    const fetch = async (): Promise<void> => {
        if (!fetchFn) return;
        state.loading = true;
        try {
            const result = await fetchFn(buildParams());
            state.data = result.items as T[];
            state.total = result.total;
        } finally {
            state.loading = false;
        }
    };

    const query = async (): Promise<void> => {
        state.page = 1;
        await fetch();
    };

    const reset = async (): Promise<void> => {
        condition.value = { ...initialCondition };
        state.page = 1;
        await fetch();
    };

    const reload = async (): Promise<void> => {
        await fetch();
    };

    const handlePageChange = async (page: number): Promise<void> => {
        state.page = page;
        await fetch();
    };

    const handleSizeChange = async (size: number): Promise<void> => {
        state.pageSize = size;
        state.page = 1;
        await fetch();
    };

    const setCondition = (partial: Record<string, any>): void => {
        condition.value = { ...condition.value, ...partial };
    };

    return {
        state,
        condition,
        query,
        reset,
        reload,
        fetch,
        handlePageChange,
        handleSizeChange,
        setCondition,
        buildParams
    };
}
