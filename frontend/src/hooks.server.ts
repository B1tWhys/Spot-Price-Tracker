import type { Handle, HandleFetch } from '@sveltejs/kit';
// import { PUBLIC_API_URL } from '$env/dynamic/public';
// import { PRIVATE_API_URL } from '$env/dynamic/private';
import { env as privEnv } from '$env/dynamic/private';
import { env as pubEnv } from '$env/dynamic/public';

export const handle = (async ({ event, resolve }) => {
	return resolve(event, {
		filterSerializedResponseHeaders: () => true
	});
}) satisfies Handle;

export const handleFetch: HandleFetch = async ({ request, fetch }) => {
	if (request.url.startsWith(pubEnv.PUBLIC_API_URL)) {
		request = new Request(
			request.url.replace(pubEnv.PUBLIC_API_URL, privEnv.PRIVATE_API_URL),
			request
		);
	}
	return fetch(request);
};
