<script lang="ts">
	let {
		columnName,
		currentOrderBy,
		currentlyDescending
	}: { columnName: string; currentOrderBy: string; currentlyDescending: boolean } = $props();

	let glyph = $derived.by(() => {
		if (currentOrderBy !== columnName) return '•';
		return currentlyDescending ? '▼' : '▲';
	});
</script>

<span class="w-5">{glyph}</span>
