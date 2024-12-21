import { client, getFilterOptionsFilterOptionsGet } from '$lib/api-client';
import type { LayoutLoad } from './$types';

export const load: LayoutLoad = async ({ fetch }) => {
	client.setConfig({
		fetch: fetch,
		baseUrl: 'http://localhost:8000'
	});

	return {
		// filterOptions: await (await fetch('http://localhost:8000/filterOptions')).json()
		filterOptions: (await getFilterOptionsFilterOptionsGet({ client: client })).data!
	};
};
