"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { AtomReplica, RemoteObjectRequest, WirebindSocket } from "wirebind";
import { Sender } from "wirebind/dist/sender";

const RemoteContext = createContext<WirebindSocket | null>(null)

export const useRemote = () => useContext(RemoteContext);

export const RemoteProvider = ({ children, endpoint }: { children: React.ReactNode, endpoint: string }) => {
    const remote = useRef<WirebindSocket>(new WirebindSocket())

    useEffect(() => {
        remote.current.connect(endpoint)
    }, [endpoint])

    return (
        <RemoteContext.Provider value={remote.current}>
            {children}
        </RemoteContext.Provider>
    )
}

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

function debounce(callback: (...args: any) => void, delay: number) {
    let lastCalled = 0;
    let lastValue: any = null;
    let timeout: any = null;

    return (...args: any) => {
        lastValue = args;

        if (timeout) {
            return
        }

        const now = Date.now();
        const timeSinceLastCall = now - lastCalled;
        
        if (timeSinceLastCall > delay) {
            callback(...lastValue);
            lastCalled = now;
        } else {
            timeout = setTimeout(() => {
                callback(...lastValue);
                lastCalled = Date.now();
                timeout = null;
            }, delay - timeSinceLastCall);
        }
    }
}

export const useRemoteMutable = (atom?: AtomReplica): any => {
    const [value, setValue] = useState(atom?.value)

    useEffect(() => {
        const onValueChage = (value: any) => {
            setValue(value)
        }

        atom?.addListener(onValueChage)
    }, [atom])

    const setter = useCallback((value: any) => {
        atom?.set(value)
    }, [atom])

    return [value, setter]
}

