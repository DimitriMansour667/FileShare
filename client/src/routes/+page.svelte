<script lang="ts">
	import Textfield from '@smui/textfield';
	import { Icon as CommonIcon } from '@smui/common';
	import Button, { Label } from '@smui/button';
	import { browser } from '$app/environment';
	import { onMount } from 'svelte';
	import Snackbar, { Actions } from '@smui/snackbar';
	import IconButton from '@smui/icon-button';

	let snackbarWithClose: Snackbar;
	let error: string;
	let valueElementsLabel: string = '';
	// define document

	onMount(() => {
		if (document.cookie.includes('id=')) {
			validate(document.cookie.split('=')[1]);
		}
	});

	const validate = async (id: string) => {
		const response = await fetch('http://127.0.0.1:8000/connect/' + id, {
			method: 'get'
		});
		const data = await response.json();
		if (data['status'] == 'connected') {
			window.location.href = '/files';
		} else {
			error = 'Could not validate your session. Please log in.';
			snackbarWithClose.open();
		}
	};

	const connect = async () => {
		const response = await fetch('http://127.0.0.1:8000/connect/' + valueElementsLabel, {
			method: 'get'
		});
		const data = await response.json();
		console.log(data);
		// set cookie
		if (browser && data['status'] == 'connected') {
			document.cookie = `id=${valueElementsLabel}; path=/`;
			console.log(document.cookie);
			window.location.href = '/files';
		} else {
			error = 'Could not connect. Please try again.';
			snackbarWithClose.open();
		}
	};

	if (browser) {
		document.addEventListener('keydown', (event) => {
			if (event.key === 'Enter') {
				connect();
			}
		});
	}
</script>

<head>
	<title>Dimi File Share</title>
</head>

<div class="page">
	<h1>Dimi File Share</h1>
	<div class="login">
		<div class="margins">
			<Textfield bind:value={valueElementsLabel} type="password">
				<svelte:fragment slot="label">
					<CommonIcon
						class="material-icons"
						style="font-size: 1em; line-height: normal; vertical-align: top;">lock</CommonIcon
					> Password
				</svelte:fragment>
			</Textfield>
		</div>
		<Button color="primary" on:click={connect} variant="raised">
			<Label>Log in</Label>
		</Button>
	</div>
	<Snackbar bind:this={snackbarWithClose} class="demo-error">
		<Label>{error}</Label>
		<Actions>
			<IconButton class="material-icons" title="Dismiss">close</IconButton>
		</Actions>
	</Snackbar>
</div>

<style>
	.page {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100vh;
	}
	.login {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		width: 100%;
	}
	.margins {
		margin: 0 0 1em 0;
	}
</style>
