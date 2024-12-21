<script lang="ts">
	import InstanceSelect from './InstanceSelect.svelte';
	import MultiSelect from './MultiSelect.svelte';
	import FilterSection from './FilterSection.svelte';

	let {
		orderBy = $bindable(),
		filters = $bindable(),
		descending: descending = $bindable()
	}: {
		orderBy: string;
		filters: { [name: string]: { [key: string]: boolean } };
		descending: boolean;
	} = $props();

	function resetFilter(filterObject: Record<string, boolean>, toState: boolean) {
		for (let key of Object.keys(filterObject)) {
			filterObject[key] = toState;
		}
	}
</script>

<form class="p-2">
	<FilterSection
		title="Instance Type"
		onClear={() => resetFilter(filters.instanceTypes, false)}
		onAll={() => resetFilter(filters.instanceTypes, true)}>
		<InstanceSelect bind:options={filters.instanceTypes} />
	</FilterSection>

	<FilterSection
		title="Operating System"
		onClear={() => resetFilter(filters.operatingSystems, false)}
		onAll={() => resetFilter(filters.operatingSystems, true)}>
		<MultiSelect bind:options={filters.operatingSystems} />
	</FilterSection>

	<FilterSection
		title="Region"
		onClear={() => resetFilter(filters.regions, false)}
		onAll={() => resetFilter(filters.regions, true)}>
		<MultiSelect bind:options={filters.regions} />
	</FilterSection>
</form>
