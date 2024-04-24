<script lang="ts">
	import { onMount } from 'svelte';
	import Accordion, { Panel, Header, Content } from '@smui-extra/accordion';
	import LinearProgress from '@smui/linear-progress';
	import Button, { Label } from '@smui/button';
	import Snackbar, { Actions } from '@smui/snackbar';
	import IconButton from '@smui/icon-button';
	let snackbarWithClose: Snackbar;
	let error: string;

	interface File {
		name: string;
		size: number;
		id: number;
		file_path: string;
	}

	interface Storage {
		used: number;
		total: number;
		free: number;
	}

	let files: File[] = [];

	let storage_stats: Storage = {
		used: 0,
		total: 0,
		free: 0
	};

	onMount(() => {
		update();
	});

	const fetchfiles = async () => {
		const response = await fetch(
			'http://127.0.0.1:8000/' + document.cookie.split('=')[1] + '/files',
			{
				method: 'get'
			}
		);
		const data = await response.json();
		if (data['status'] == 'error') {
			window.location.href = '/';
		} else {
			// example data
			// [
			// 	{
			// 		"size": 367,
			// 		"id": 1,
			// 		"file_path": "F:\\Project A\\server\\/files\\/test.zip",
			// 		"name": "test.zip"
			// 	}
			// ]
			console.log(data);
			files = data;
		}
	};

	const storage = async () => {
		const response = await fetch(
			'http://127.0.0.1:8000/' + document.cookie.split('=')[1] + '/storage',
			{
				method: 'get'
			}
		);
		const data = await response.json();
		if (data['status'] == 'error') {
			window.location.href = '/';
		} else {
			console.log(data);
			storage_stats = data;
		}
	};

	const update = async () => {
		fetchfiles();
		storage();
	};

	const download = async (id: number, name: string) => {
		const response = await fetch(
			'http://127.0.0.1:8000/' + document.cookie.split('=')[1] + '/file/' + id + '/download',
			{
				method: 'get'
			}
		);
		try {
			const blob = await response.blob();
			const url = window.URL.createObjectURL(blob);
			const a: HTMLAnchorElement = document.createElement('a');
			a.href = url;
			a.download = name;
			document.body.appendChild(a);
			a.click();
			window.URL.revokeObjectURL(url);
			console.log('success');
		} catch (error) {
			console.log(error);
		}
	};

	const upload = async () => {
		if ((document.getElementById('file') as HTMLInputElement).files != null) {
			const fileInput = document.getElementById('file') as HTMLInputElement;
			const file = fileInput?.files?.[0];
			const formData = new FormData();
			if (file) {
				files.forEach((x) => {
					if (x.name == file.name) {
						error = 'File already exists';
						snackbarWithClose.open();
						return;
					}
				});
				formData.append('file', file);
			}

			const response = await fetch(
				'http://127.0.0.1:8000/' + document.cookie.split('=')[1] + '/file/upload',
				{
					method: 'post',
					body: formData
				}
			);
			const data = await response.json();
			if (data['status'] == 'error') {
				console.log('error');
			} else {
				console.log('success');
				update();
			}
		}
	};

	const deleteFile = async (id: number) => {
		const response = await fetch(
			'http://127.0.0.1:8000/' + document.cookie.split('=')[1] + '/file/' + id + '/delete',
			{
				method: 'delete'
			}
		);
		const data = await response.json();
		if (data['status'] == 'error') {
			console.log('error');
		} else {
			console.log('success');
			update();
		}
	};
</script>

<html lang="en">
	<div class="page">
		<h1>Dimi File Share</h1>
		<div class="progresss-bar">
			<LinearProgress progress={storage_stats.used / storage_stats.total} />
		</div>
		<div class="accordion-container">
			{#if files.length > 0}
				<Accordion>
					{#each files as file}
						<Panel>
							<Header>
								{file.name}
							</Header>
							<Content>
								<div class="content">
									File size: {file.size} B
									<div class="buttons">
										<Button
											color="primary"
											on:click={() => download(file.id, file.name)}
											variant="raised"
										>
											<Label>Download</Label>
										</Button>
										<Button color="secondary" on:click={() => deleteFile(file.id)} variant="raised">
											<Label>Delete</Label>
										</Button>
									</div>
								</div>
							</Content>
						</Panel>
					{/each}
				</Accordion>
			{:else}
				<p>No files found</p>
			{/if}
		</div>
		<form class="upload">
			<input type="file" id="file" name="fileToUpload" required />
			<Button variant="raised" on:click={() => upload()}>
				<Label>Upload</Label>
			</Button>
		</form>
		<Snackbar bind:this={snackbarWithClose} class="demo-error">
			<Label>{error}</Label>
			<Actions>
				<IconButton class="material-icons" title="Dismiss">close</IconButton>
			</Actions>
		</Snackbar>
	</div>
</html>

<style>
	.page {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.progresss-bar {
		width: 50%;
		padding-bottom: 10px;
	}

	.accordion-container {
		width: 100%;
		max-width: 600px;
	}

	.content {
		display: flex;
		flex-direction: column;
	}

	.buttons {
		display: flex;
		flex-direction: row;
		margin-top: 10px;
	}

	.upload {
		margin-top: 10px;
		display: flex;
		flex-direction: column;
		align-items: center;
	}
</style>
