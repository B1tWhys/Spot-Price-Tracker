<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { EventHandler } from 'svelte/elements';

	let {
		title,
		onClear,
		onAll,
		children
	}: { title: string; onClear: EventHandler; onAll: EventHandler; children: Snippet } = $props();
</script>

<div>
	<h2 class="font-bold">{title}</h2>
	<div class="mb-2 mt-2 max-h-52 w-full overflow-y-scroll rounded-md shadow-sm shadow-slate-400">
		{@render children()}
	</div>
	<div>
		<button class="btn btn-primary btn-sm inline-block w-20" onclick={onClear}> Clear </button>
		<button class="btn btn-primary btn-sm inline-block w-20" onclick={onAll}> All </button>
	</div>
</div>
