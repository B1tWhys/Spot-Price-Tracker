<script lang="ts">
	import Controls from '$lib/components/Controls.svelte';
	import type { PageData } from './$types';
	import { getCurrentPricesPostCurrentPost } from '$lib/api-client';
	import Fa from 'svelte-fa';
	import {
		faAnglesLeft,
		faAnglesRight,
		faArrowDown,
		faArrowRight,
		faMagnifyingGlassMinus
	} from '@fortawesome/free-solid-svg-icons';
	import SortIndicator from '$lib/components/SortIndicator.svelte';

	function optionsToFilterState(strs: string[]) {
		return strs.reduce(
			(acc, cur: string) => {
				acc[cur] = true;
				return acc;
			},
			{} as { [name: string]: boolean }
		);
	}

	function toggleControls() {
		controlsVisible = !controlsVisible;
	}

	function handleColumnHeaderClick(fieldName: string) {
		if (orderBy === fieldName) {
			descending = !descending;
		} else {
			orderBy = fieldName;
			descending = false;
		}
	}

	let controlsVisible = $state(true);

	let { data }: { data: PageData } = $props();

	let filters = $state({
		instanceTypes: undefined,
		operatingSystems: undefined,
		regions: undefined,
		orderBy: 'price_usd_hourly'
	} as Record<string, any>);

	$effect(() => {
		filters.instanceTypes = optionsToFilterState(data.filterOptions.instance_types);
	});

	$effect(() => {
		filters.operatingSystems = optionsToFilterState(data.filterOptions.operating_systems);
	});

	$effect(() => {
		filters.regions = optionsToFilterState(data.filterOptions.regions);
	});

	let rows = $state.raw(data.currentPricingData);

	let orderBy = $state('femto_usd_per_v_core_cycle');
	let descending = $state(true);

	$effect(() => {
		let body: Record<string, any> = {};

		if (filters.instanceTypes !== undefined) {
			body['instance_types'] = Object.entries(filters.instanceTypes)
				.filter(([_, v]) => v)
				.map(([k, _]) => k);
		}

		if (filters.operatingSystems !== undefined) {
			body['operating_systems'] = Object.entries(filters.operatingSystems)
				.filter(([_, v]) => v)
				.map(([k, _]) => k);
		}

		if (filters.regions !== undefined) {
			body['regions'] = Object.entries(filters.regions)
				.filter(([_, v]) => v)
				.map(([k, _]) => k);
		}

		body['order_by'] = orderBy;
		body['ascending'] = !descending;

		const controller = new AbortController();
		const promise = getCurrentPricesPostCurrentPost({ body: body, signal: controller.signal });
		promise
			.then((response) => {
				const newRows = response.data;
				if (newRows !== undefined) {
					rows = newRows;
				}
			})
			.catch((reason) => {
				if (reason.name === 'AbortError') {
					return;
				}
				console.log(`Failed to fetch results: ${reason}`);
			});

		return () => {
			controller.abort();
		};
	});
</script>

<main class="static flex h-screen w-screen">
	<!-- Expanded controls -->
	<div class="relative w-80 border-r-[2px] border-r-slate-300" class:hidden={!controlsVisible}>
		{#if filters !== undefined}
			<button
				class="absolute right-2 top-2 z-50 cursor-pointer rounded-md border-[2px] border-black p-1"
				onclick={toggleControls}>
				<Fa icon={faAnglesLeft} />
			</button>
			<Controls
				bind:filters={filters as Record<string, Record<string, boolean>>}
				bind:orderBy
				bind:descending />
		{/if}
	</div>
	<!-- Collapsed controls -->
	<div class="h-full border-r-[2px] border-r-slate-300" class:hidden={controlsVisible}>
		<button
			class="right-2 top-2 z-50 m-2 cursor-pointer rounded-md border-[2px] border-black p-1"
			onclick={toggleControls}>
			<Fa icon={faAnglesRight} />
		</button>
	</div>
	<!-- Data -->
	<div class="relative h-screen flex-grow overflow-y-scroll">
		{#if rows !== undefined && rows.length !== 0}
			<table class="table table-zebra table-pin-cols">
				<thead>
					<tr>
						<th class="sticky top-0 w-32 shadow-sm">Instance Type</th>
						<th class="sticky top-0 w-40 shadow-sm">Operating System</th>
						<th class="sticky top-0 shadow-sm">Region</th>
						<th class="sticky top-0 shadow-sm">AZ</th>
						<th
							class="sticky top-0 cursor-pointer shadow-sm"
							onclick={() => handleColumnHeaderClick('price_usd_hourly')}>
							<SortIndicator
								columnName="price_usd_hourly"
								currentlyDescending={descending}
								currentOrderBy={orderBy} />
							Hourly spot price (USD)
						</th>
						<th
							class="sticky top-0 cursor-pointer shadow-sm"
							onclick={() => handleColumnHeaderClick('femto_usd_per_v_core_cycle')}>
							<div class="tooltip tooltip-bottom" data-tip="Units of USD×10⁻¹⁵">
								<SortIndicator
									columnName="femto_usd_per_v_core_cycle"
									currentlyDescending={descending}
									currentOrderBy={orderBy} />
								Price per 10¹⁵ clock cycles (V-cores)
							</div>
						</th>
						<th
							class="sticky top-0 cursor-pointer shadow-sm"
							onclick={() => handleColumnHeaderClick('femto_usd_per_p_core_cycle')}>
							<div class="tooltip tooltip-bottom" data-tip="Units of USD×10⁻¹⁵">
								<SortIndicator
									columnName="femto_usd_per_p_core_cycle"
									currentlyDescending={descending}
									currentOrderBy={orderBy} />
								Price per clock cycle (physical cores)
							</div>
						</th>
					</tr>
				</thead>
				<tbody>
					{#each rows as row}
						<tr>
							<td class="flex w-32 items-center justify-between">
								<div>
									{row.instance_type}
								</div>
								<button
									title="Exclude instance type"
									onclick={() => {
										if (filters.instanceTypes !== undefined) {
											filters.instanceTypes[row.instance_type] = false;
										}
									}}>
									<Fa class="inline" icon={faMagnifyingGlassMinus} />
								</button>
							</td>
							<td>{row.product_description}</td>
							<td>{row.region}</td>
							<td>{row.availability_zone}</td>
							<td>{row.price_usd_hourly}</td>
							<td>{row.femto_usd_per_v_core_cycle}</td>
							<td>{row.femto_usd_per_p_core_cycle}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{:else}
			<div class="flex h-full items-center justify-center">
				<h2 class="text-lg">No results found matching the provided filters</h2>
			</div>
		{/if}
	</div>
</main>
