export interface PageParams {
    page: number;
    size: number;
}

export interface Page {
    paging: PageParams;
    condition: Record<string, any>;
}

export interface PageResult<T = any> {
    items: T[];
    total: number;
}

export interface TableState<T = any> {
    data: T[];
    page: number;
    pageSize: number;
    total: number;
    loading: boolean;
}

export interface SearchParams {
    page: number;
    pageSize: number;
    [key: string]: any;
}
