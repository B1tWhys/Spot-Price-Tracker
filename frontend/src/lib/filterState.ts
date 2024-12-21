import { writable } from 'svelte/store';

export const instanceTypes = writable<{ [key: string]: boolean } | undefined>(undefined);
export const operatingSystems = writable<{ [key: string]: boolean } | undefined>(undefined);
export const regions = writable<{ [key: string]: boolean } | undefined>(undefined);
