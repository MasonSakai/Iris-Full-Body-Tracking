
export class EventDispatcher<T = void> {
    private listeners = new Set<(event: T) => void>();

    subscribe(listener: (event: T) => void) {
        this.listeners.add(listener);
        return () => { this.listeners.delete(listener) };
    }

    dispatch(event: T) {
        this.listeners.forEach(l => l(event));
    }
}