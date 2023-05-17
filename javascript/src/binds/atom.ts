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
    serverValue: any = null
    localValue: any = null

    /** Invariant: if dirty is false, localValue and serverValue must point to the same value. */
    dirty: boolean = false

    setter: Sender<any>
    listeners: Array<(v: any) => void> = []
    updateLocalValueTimeout: ReturnType<typeof setTimeout> | null = null

    constructor(packed: Record<string, any>) {
        packed['get'].send(new Sender(this.update))
        this.setter = packed['set']
    }

    update = (value: any) => {
        this.serverValue = value
        this.dirty = true

        if (this.updateLocalValueTimeout === null) {
            this.updateLocalValue()
        }
    }

    updateLocalValue = () => {
        this.localValue = this.serverValue
        this.updateLocalValueTimeout = null
        
        if (this.dirty) {
            this.notifyListeners()
            this.dirty = false
        }
    }

    notifyListeners = () => {
        for (const listener of this.listeners) {
            listener(this.localValue)
        }
    }

    set = (value: any) => {
        this.localValue = value
        this.dirty = true
        this.setter.send(value)
        this.notifyListeners()
        if (this.updateLocalValueTimeout !== null) {
            clearTimeout(this.updateLocalValueTimeout)
        }
        this.updateLocalValueTimeout = setTimeout(this.updateLocalValue, 2_000)
    }

    get = () => {
        return this.localValue
    }

    addListener(listener: (value: any) => void) {
        this.listeners.push(listener)
    }
}
