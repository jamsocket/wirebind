import {Packable} from '../packable'
import { Sender } from '../sender'

export class Atom extends Packable {
    value: any
    listeners: Array<(v: any) => void> = []

    constructor(value: any) {
        super()
        this.value = value
        this.listeners = []
    }
    
    addListener(listener: (value: any) => void) {
        this.listeners.push(listener)
    }

    bind = (sender: Sender<any>) => {
        sender.send(this.value)
        this.addListener(sender.send)
    }

    set = (value: any) => {
        this.value = value
        for (const listener of this.listeners) {
            listener(value)
        }
    }

    pack(): Record<string, any> {
        const getter = new Sender(this.bind)
        const setter = new Sender(this.set)
        return {
            type: Atom.packType(),
            get: getter,
            set: setter,
        }
    }
    
    static fromPacked(packed: Record<string, any>): any {
        return new AtomReplica(packed)
    }

    static packType(): string {
        return 'atom'
    }
}

export class AtomReplica {
    value: any = null
    setter: Sender<any>
    listeners: Array<(v: any) => void> = []

    constructor(packed: Record<string, any>) {
        packed['get'].send(new Sender(this.update))
        this.setter = packed['set']
    }

    update = (value: any) => {
        this.value = value
        for (const listener of this.listeners) {
            listener(value)
        }
    }

    set = (value: any) => {
        this.setter.send(value)
    }

    addListener(listener: (value: any) => void) {
        this.listeners.push(listener)
    }
}
