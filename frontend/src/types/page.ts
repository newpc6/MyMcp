export interface PageParams {
    page: number;
    size: number;
}

export interface Page {
    paging: PageParams;
    condition: Record<string, any>;
}
    