"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import { AtomReplica, RemoteObjectRequest, RpcMessage, wirebindSocket } from "wirebind";
import { Sender } from "wirebind/dist/sender";

const RemoteContext = createContext<wirebindSocket | null>(null)

export const useRemote = () => useContext(RemoteContext);

export const RemoteProvider = ({ children, endpoint }: { children: React.ReactNode, endpoint: string }) => {
    const remote = useRef<wirebindSocket>(new wirebindSocket())

    useEffect(() => {
        remote.current.connect(endpoint)
    }, [endpoint])

    return (
        <RemoteContext.Provider value={remote.current}>
            {children}
        </RemoteContext.Provider>
    )
}

// class RemoteObject {
//     sender?: Sender<RpcMessage>
//     state: Record<string, any>

//     /** State listeners. */
//     listeners: Record<string, ((value: any) => void)[]>
//     socket: wirebindSocket

//     constructor(socket: wirebindSocket) {
//         this.state = {}
//         this.listeners = {}
//         this.socket = socket
//     }

//     setSender(sender: Sender<RpcMessage>) {
//         this.sender = sender
//     }

//     addListener(name: string, listener: (value: any) => void) {
//         if (!this.listeners[name]) {
//             this.listeners[name] = []
//         }
//         this.listeners[name].push(listener)
//     }

//     removeListener(name: string, listener: (value: any) => void) {
//         if (!this.listeners[name]) {
//             return
//         }
//         this.listeners[name] = this.listeners[name].filter(l => l !== listener)
//     }

//     /** Call a function on the remote object. */
//     async call(name: string, args?: Record<string, any>): Promise<any> {
//         if (!this.sender) {
//             throw new Error("Something called before remote object is connected.")
//         }

//         let p = new WrappedPromise()
//         let replySender = new Sender(p.resolve)

//         await this.sender.send({
//             call: name,
//             args,
//             reply: replySender,
//         })
//     }
// }

class WrappedPromise {
    promise: Promise<any>
    _resolve?: (value: any) => void
    _reject?: (reason?: any) => void
    constructor() {
        this.promise = new Promise((resolve, reject) => {
            this._resolve = resolve
            this._reject = reject
        })
    }

    resolve = (value: any) => {
        this._resolve!(value)
    }

    reject = (reason?: any) => {
        this._reject!(reason)
    }
}

export const useRemoteObject = function (name: string, args?: Record<string, any>) {
    const remote = useRemote()! // TODO: handle null
    const [obj, setObj] = useState<any>(null)

    useEffect(() => {
        const p = new WrappedPromise();
        const replyChannel = new Sender(p.resolve);

        (async () => {
            await remote.waitReady()
            remote.sendRoot({
                typ: name,
                args: args,
                reply: replyChannel,
            } as RemoteObjectRequest<any>)

            const result = await p.promise
            setObj(result)
        })()

    }, [args, name, remote])

    return obj
}

export const useRemoteValue = (atom?: AtomReplica): any => {
    const [value, setValue] = useState(atom?.value)

    useEffect(() => {
        atom?.addListener(setValue)
    }, [atom])

    return value
}

