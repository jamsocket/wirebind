import { MessageReceiver, Multiplexer } from "./multiplex";
import { Sender } from "./sender";

export class ReadyGuard {
    _promise: Promise<void> | null = null
    _resolve?: () => void
    _reject?: (err: any) => void

    constructor() {
        this.reset()
    }

    /** Mark as not ready. */
    reset() {
        this._promise = new Promise((resolve, reject) => {
            this._resolve = resolve
            this._reject = reject
        })
    }

    promise() {
        if (this._promise === null) {
            return Promise.resolve()
        }
        return this._promise
    }

    setReady() {
        this._resolve?.()
        this._promise = null
    }

    setFailed(err: any) {
        this._reject?.(err)
        this.reset()
    }
}

export class wirebindSocket {
    private socket: WebSocket | null = null;
    private multiplexer: Multiplexer;
    private readyGuard = new ReadyGuard();

    constructor() {
        this.multiplexer = new Multiplexer(this.recv);
    }

    connect(url: string) {
        const socket = new WebSocket(url);
        socket.binaryType = "arraybuffer";

        this.socket = socket;
        this.socket.onopen = this.onOpen;
        if (this.socket.readyState === WebSocket.OPEN) {
            this.onOpen();
        }
        this.socket.onmessage = this.onMessage;
        this.socket.onclose = this.onClose;
        this.socket.onerror = this.onError;
    }

    private onOpen = () => {
        console.log("Socket opened");
        this.readyGuard.setReady();
    }

    private onMessage = (event: MessageEvent) => {
        const data = new Uint8Array(event.data);
        this.multiplexer.receive(data);
    }

    private onClose = (event: CloseEvent) => {
        this.readyGuard.reset();
        console.log("Socket closed");
    }

    private onError = (event: Event) => {
        this.readyGuard.setFailed(event);
        console.log("Socket error", event);
    }

    private recv = (message: Uint8Array) => {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.socket.send(message);
        } else {
            console.warn("Message attempted when socket not open");
        }
    }

    waitReady(): Promise<void> {
        return this.readyGuard.promise()
    }

    sendRoot(message: any): void {
        this.multiplexer.sendRoot(message);
    }
}
