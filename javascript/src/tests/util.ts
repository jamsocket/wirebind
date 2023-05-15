import { Multiplexer } from "../multiplex"

export function neverCalled() {
    throw new Error("This function should never be called")
}

export function multiplexPair(): [Multiplexer, Multiplexer] {
    const server = new Multiplexer(neverCalled)
    const client = new Multiplexer(server.receive)
    server.sendFunction = client.receive

    return [server, client]
}

export class Queue<T> {
    queue: T[]

    constructor() {
        this.queue = []
    }

    put = (item: T) => {
        this.queue.push(item)
    }

    get = () => {
        if (this.queue.length == 0) {
            throw new Error("Queue is empty")
        }
        return this.queue.shift() as any
    }
}
