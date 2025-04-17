// types/resources.ts
export interface ResourceInfo {
  path: string;
  name: string;
  description: string;
  lastModified: string;
}

export interface ResourceContent {
  content: string;
}

export interface ResourceCreate {
  path: string;
  content: string;
}

export interface ResourceUpdate {
  content: string;
} 