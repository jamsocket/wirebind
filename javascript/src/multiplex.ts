import { SenderEncoder } from "./encoder";
import { Sender } from "./sender";
import { Message } from "./types";

type ByteReceiver = (data: Uint8Array) => void;
export type MessageReceiver<T> = (data: T) => void;

// Well-known hosts
export const SERVER = 0;
export const CLIENT = 1;

// Well-known channels
export const ROOT = 0;

export class Multiplexer {
    registry: Map<number, MessageReceiver<any>>;
    sendFunction: ByteReceiver;
    nextChannel: number = 1;
    encoder: SenderEncoder;

    constructor(sendFunction: ByteReceiver) {
        this.registry = new Map();
        this.encoder = new SenderEncoder(this);

        this.sendFunction = sendFunction;
    }

    /** Set the root handler for messages from the remote party. */
    setRoot<T>(root: MessageReceiver<T>): void {
        if (this.registry.get(0) !== undefined) {
            throw new Error("Root callback already set");
        }
        this.registry.set(ROOT, root);
    }

    /** Send a message to the remote multiplexer's root handler. */
    sendRoot(message: any): void {
        this.send(message, ROOT);
    }

    /** Send a message to a channel on the remote multiplexer. */
    send(message: any, ch: number): void {
        const msg: Message<any> = {message, ch};
        console.log("Sending", msg)
        const messageEnc = this.encoder.encode(msg);
        this.sendFunction(messageEnc);
    }

    /** Register a local handler, returning a handle to the channel. */
    registerSender<T>(sender: Sender<T>): number {
        const channel = this.nextChannel;
        this.nextChannel += 1;
        this.registry.set(channel, sender.callback);
        return channel;
    }

    /** Receive a message from the remote multiplexer. */
    receive = (messageBytes: Uint8Array) => {
        const message = this.encoder.decode(messageBytes);

        if (this.registry.get(message.ch) === undefined) {
            throw new Error(`No callback registered for channel ${message.ch}`);
        }

        this.registry.get(message.ch)!(message.message);
    }
}
