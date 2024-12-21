import type { PageLoad } from './$types';
import { client, getCurrentPricesCurrentGet } from '$lib/api-client';

export const load: PageLoad = async ({ fetch }) => {
	client.setConfig({
		fetch: fetch,
		baseUrl: 'http://localhost:8000' // FIXME
	});

	const currentPricingDataPromise = getCurrentPricesCurrentGet();
	return {
		currentPricingData: (await currentPricingDataPromise).data!
	};
};
