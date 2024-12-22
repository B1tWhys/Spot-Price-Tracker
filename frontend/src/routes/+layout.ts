import { client, getFilterOptionsFilterOptionsGet } from '$lib/api-client';
import type { LayoutLoad } from './$types';
import { env } from '$env/dynamic/public';

export const load: LayoutLoad = async ({ fetch }) => {
	client.setConfig({
		fetch: fetch,
		baseUrl: env.PUBLIC_API_URL
	});

	return {
		// filterOptions: await (await fetch('http://localhost:8000/filterOptions')).json()
		filterOptions: (await getFilterOptionsFilterOptionsGet({ client: client })).data!
	};
};
