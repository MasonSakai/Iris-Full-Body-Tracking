interface Window {
	Modal: {
		stack: { el: HTMLDialogElement, load: (url: RequestInfo | URL, options?: RequestInit) => void }[]
		open(url: string): Promise<void>,
		register<K extends keyof HTMLElementEventMap>(link: HTMLElement, event?: K): void
	};
}