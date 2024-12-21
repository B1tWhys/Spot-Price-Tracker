<script lang="ts">
	let { options = $bindable() }: { options: { [name: string]: boolean } } = $props();
	let checkboxTree: Map<string, Record<string, boolean>> = $derived.by(() => {
		const groups = new Map();
		if (options === undefined) {
			return groups;
		}
		for (let [k, v] of Object.entries(options)) {
			const group = k.split('.', 1)[0];
			if (!groups.has(group)) {
				groups.set(group, {});
			}
			groups.get(group)[k] = v;
		}
		return groups;
	});

	function setAllInGroup(group: string, toState: boolean) {
		for (let instanceType of Object.keys(checkboxTree.get(group)!)) {
			options[instanceType] = toState;
		}
	}
</script>

<div>
	{#if options !== undefined && checkboxTree !== undefined}
		{#each checkboxTree.entries() as [groupKey, group]}
			{@const allChildrenChecked = Object.values(group).every((i) => i)}
			{@const allChildrenUnchecked = Object.values(group).every((i) => !i)}
			{@const indeterminate = !allChildrenChecked && !allChildrenUnchecked}

			<div class="collapse collapse-arrow p-1">
				<input class="hidden" type="checkbox" id={`expand-${groupKey}`} />
				<label class="collapse-title min-h-0 p-0 leading-none" for={`expand-${groupKey}`}>
					<input
						type="checkbox"
						class="checkbox align-middle"
						{indeterminate}
						checked={allChildrenChecked}
						onchange={() => setAllInGroup(groupKey, !allChildrenChecked)} />
					{groupKey}
				</label>
				<div class="collapse-content pb-0">
					{#each Object.keys(group) as instanceType}
						<label class="my-0.5 block pl-3">
							<input
								type="checkbox"
								class="checkbox align-middle"
								bind:checked={options[instanceType]} />
							{instanceType}
						</label>
					{/each}
				</div>
			</div>
		{/each}
	{/if}
</div>
