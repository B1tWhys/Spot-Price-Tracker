// This file is auto-generated by @hey-api/openapi-ts

import { createClient, createConfig, type OptionsLegacyParser } from '@hey-api/client-fetch';
import type { GetCurrentPricesCurrentGetData, GetCurrentPricesCurrentGetError, GetCurrentPricesCurrentGetResponse, GetCurrentPricesPostCurrentPostData, GetCurrentPricesPostCurrentPostError, GetCurrentPricesPostCurrentPostResponse, GetFilterOptionsFilterOptionsGetError, GetFilterOptionsFilterOptionsGetResponse } from './types.gen';

export const client = createClient(createConfig());

/**
 * Get Current Prices
 * Fetch the latest spot instance price per instance type, availability zone and product description
 */
export const getCurrentPricesCurrentGet = <ThrowOnError extends boolean = false>(options?: OptionsLegacyParser<GetCurrentPricesCurrentGetData, ThrowOnError>) => {
    return (options?.client ?? client).get<GetCurrentPricesCurrentGetResponse, GetCurrentPricesCurrentGetError, ThrowOnError>({
        ...options,
        url: '/current'
    });
};

/**
 * Get Current Prices Post
 * Same as the GET version of this endpoint, but the filters are accepted in the request body to allow for very long
 * lists of instance types & whatnot
 */
export const getCurrentPricesPostCurrentPost = <ThrowOnError extends boolean = false>(options?: OptionsLegacyParser<GetCurrentPricesPostCurrentPostData, ThrowOnError>) => {
    return (options?.client ?? client).post<GetCurrentPricesPostCurrentPostResponse, GetCurrentPricesPostCurrentPostError, ThrowOnError>({
        ...options,
        url: '/current'
    });
};

/**
 * Get Filter Options
 */
export const getFilterOptionsFilterOptionsGet = <ThrowOnError extends boolean = false>(options?: OptionsLegacyParser<unknown, ThrowOnError>) => {
    return (options?.client ?? client).get<GetFilterOptionsFilterOptionsGetResponse, GetFilterOptionsFilterOptionsGetError, ThrowOnError>({
        ...options,
        url: '/filterOptions'
    });
};