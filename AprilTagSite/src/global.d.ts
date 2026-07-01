interface Window {
	Modal: {
		stack: []
		open(url: string): Promise<void>,
		register(link: HTMLElement): void
	};
}