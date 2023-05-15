import { Multiplexer } from "./multiplex";

export interface AbstractSender<T> {
    send(message: T): void;
}

export class Sender<T> implements AbstractSender<T> {
    constructor(public callback: (message: T) => void) {
    }

    send = (message: T) => {
        this.callback(message);
    }
}

export class RemoteSender<T> implements AbstractSender<T> {
    constructor(public multiplexer: Multiplexer, public channel: number) {
    }

    send = (message: T) => {
        this.multiplexer.send(message, this.channel);
    }
}
