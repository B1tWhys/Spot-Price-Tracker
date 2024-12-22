import type { PageLoad } from './$types';
import { client, getCurrentPricesCurrentGet } from '$lib/api-client';
import { env } from '$env/dynamic/public';

export const load: PageLoad = async ({ fetch }) => {
	client.setConfig({
		fetch: fetch,
		baseUrl: env.PUBLIC_API_URL
	});

	const currentPricingDataPromise = getCurrentPricesCurrentGet();
	return {
		currentPricingData: (await currentPricingDataPromise).data!
	};
};
