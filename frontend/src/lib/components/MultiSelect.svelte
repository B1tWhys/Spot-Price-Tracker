<script lang="ts">
	let { options = $bindable() }: { options: { [name: string]: boolean } } = $props();
</script>

<div>
	{#if options !== undefined}
		{#each Object.keys(options) as name}
			<label class="my-1 ml-1 block">
				<input type="checkbox" class="checkbox align-middle" bind:checked={options[name]} />
				{name}
			</label>
		{/each}
	{/if}
</div>
